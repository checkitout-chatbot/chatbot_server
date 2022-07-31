from copy import deepcopy
from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.response import Response, BlockID
import requests
import json
from hanspell import spell_checker
import log
from datetime import datetime


class Searching:
    def __init__(self):
        self.REST_API_KEY = 'c8981be15dbb94247a93cce5e564653b'
        self.url = "https://dapi.kakao.com/v3/search/book"
        self.ClientID = 'lxpEmdQK9H4_K82OcTP4'
        self.ClientPW = 'p8veOL4_q7'

    def get_isbn(self, query):
        queryString = {"query": query}
        header = {'Authorization': f'KakaoAK {self.REST_API_KEY}'}
        r = requests.get(self.url, headers=header, params=queryString)
        books = json.loads(r.text)
        if len(books) == 0:
            query = spell_checker.check(query)
            query = query.checked
            queryString = {"query": query}
            header = {'Authorization': f'KakaoAK {self.REST_API_KEY}'}
            r = requests.get(self.url, headers=header, params=queryString)
            books = json.loads(r.text)['documents']
        isbn = books['documents'][0]['isbn'].split()[1]
        return isbn

    def get_book(self, query):
        queryString = {"query": query}
        header = {'Authorization': f'KakaoAK {self.REST_API_KEY}'}
        r = requests.get(self.url, headers=header, params=queryString)
        books = json.loads(r.text)['documents']
        if len(books) == 0:
            query = spell_checker.check(query)
            query = query.checked
            queryString = {"query": query}
            header = {'Authorization': f'KakaoAK {self.REST_API_KEY}'}
            r = requests.get(self.url, headers=header, params=queryString)
            books = json.loads(r.text)['documents']
        return books

    def get_book_by_naver(self, query):
        url = 'https://openapi.naver.com/v1/search/book.json'
        queryString = {"query": query}
        header = {'X-Naver-Client-Id': self.ClientID,
                  'X-Naver-Client-Secret': self.ClientPW}
        r = requests.get(url, headers=header, params=queryString)
        books = json.loads(r.text)
        return books


class Barcode(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)

    def post(self):
        import re
        data = Barcode.parser.parse_args()
        log.info_log(data)
        barcode = data['action']['params']['barcode']
        barcode = re.sub("[^0-9]", "", barcode)

        response = Response()
        simpleText = response.simpleText
        responseBody = response.responseBody

        book = BookModel.find_by_isbn(barcode)
        # 가져온 ISBN의 책이 DB에 없는 경우 카카오 API로 검색하여 저장
        if book == None:
            search = Searching()
            book = search.get_book(barcode)
            pubDate = book['datetime'].split('T')[0]
            pubDate = datetime.strptime(pubDate, '%Y-%m-%d').date()
            if len(book['authors']) > 1:
                authors = ", ".join(book['authors'])
            else:
                authors = book['authors'][0]
            book = BookModel(barcode, book['title'], authors, book['publisher'],
                             book['contents'], book['thumbnail'], None, None, None, None, pubDate)
            book.save_to_db()

        book = book.json()

        blockid = BlockID()
        itemList = response.itemList
        button = response.button
        itemCard = response.itemCard
        kyobo_url = f"https://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={book['isbn']}&orderClick=LEa&Kc="

        itemLists = []
        itemList1 = itemList.copy()
        itemList1['title'] = '지은이'
        itemList1['description'] = book['author']
        itemLists.append(itemList1)

        itemList2 = itemList.copy()
        itemList2['title'] = '출판사'
        itemList2['description'] = book['publisher']
        itemLists.append(itemList2)

        itemList3 = itemList.copy()
        itemList3['title'] = '출판일'
        itemList3['description'] = str(book['pubDate'])
        itemLists.append(itemList3)
        itemCard['itemCard']['itemList'] = itemLists

        buttons = []
        button1 = button.copy()
        button1['action'] = 'webLink'
        button1['label'] = '책 정보'
        button1['webLinkUrl'] = kyobo_url
        buttons.append(button1)

        button2 = deepcopy(button)
        button2['action'] = 'block'
        button2['label'] = '책 저장'
        button2['blockId'] = blockid.save_menu
        button2['extra']['isbn'] = book['isbn']
        buttons.append(button2)

        itemCard['itemCard']['buttons'] = buttons
        itemCard['itemCard']['imageTitle']['title'] = book['title']
        itemCard['itemCard']['imageTitle']['imageUrl'] = book['img']

        simpleText['simpleText']['text'] = '찾으시는 책이 맞나요?'
        outputs = [simpleText, itemCard]
        responseBody['template']['outputs'] = outputs

        quickReplies = []
        quickReply = response.quickReply

        quickReply1 = deepcopy(quickReply)
        quickReply1['action'] = 'block'
        quickReply1['label'] = '뒤로가기'
        quickReply1['blockId'] = blockid.search_menu
        quickReplies.append(quickReply1)

        quickReply2 = deepcopy(quickReply)
        quickReply2['action'] = 'block'
        quickReply2['label'] = '도움말'
        quickReply2['blockId'] = blockid.howto
        quickReplies.append(quickReply2)

        responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class Keyword(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)

    def post(self):
        data = Barcode.parser.parse_args()
        log.info_log(data)

        keyword = data['action']['params']['keyword']
        search = Searching()
        books = search.get_book(keyword)

        blockid = BlockID()
        response = Response()
        itemList = response.itemList
        item = response.item
        button = response.button
        carousel_itemCard = response.carousel_itemCard
        simpleText = response.simpleText
        responseBody = response.responseBody

        try:
            items = []
            for book in books:
                isbn = book['isbn'].split()[1]
                check_book = BookModel.find_by_isbn(isbn)
                # books 테이블에 해당 책 없으면 저장
                if check_book == None:
                    pubDate = book['datetime'].split('T')[0]
                    pubDate = datetime.strptime(pubDate, '%Y-%m-%d').date()
                    if len(book['authors']) > 1:
                        authors = ", ".join(book['authors'])
                    else:
                        authors = book['authors'][0]
                    book = BookModel(isbn, book['title'], authors, book['publisher'],
                                     book['contents'], book['thumbnail'], None, None, None, None, book['pubDate'])
                    book.save_to_db()
                    book = book.json()
                else:
                    book = check_book.json()

                log.info_log(book)
                item1 = deepcopy(item)
                item1['imageTitle']['title'] = book['title']
                item1['imageTitle']['imageUrl'] = book['img']

                itemLists = []
                itemList1 = deepcopy(itemList)
                itemList1['title'] = '지은이'
                itemList1['description'] = book['author']
                itemLists.append(itemList1)

                itemList2 = deepcopy(itemList)
                itemList2['title'] = '출판사'
                itemList2['description'] = book['publisher']
                itemLists.append(itemList2)

                itemList3 = deepcopy(itemList)
                itemList3['title'] = '출판일'
                itemList3['description'] = str(book['pubDate'])
                itemLists.append(itemList3)
                item1['itemList'] = itemLists

                buttons = []
                button1 = deepcopy(button)
                button1['action'] = 'webLink'
                button1['label'] = '책 정보'
                kyobo_url = f"https://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={book['isbn']}&orderClick=LEa&Kc="
                button1['webLinkUrl'] = kyobo_url
                buttons.append(button1)

                button2 = deepcopy(button)
                button2['action'] = 'block'
                button2['label'] = '책 저장'
                button2['blockId'] = blockid.save_menu
                button2['extra']['isbn'] = book['isbn']
                buttons.append(button2)
                item1['buttons'] = buttons

                items.append(item1)

            carousel_itemCard['carousel']['items'] = items
            simpleText['simpleText']['text'] = '이 중에 찾으시는 책이 있을까요??'

            outputs = [simpleText, carousel_itemCard]
            responseBody['template']['outputs'] = outputs

            quickReplies = []
            quickReply = response.quickReply

            quickReply1 = deepcopy(quickReply)
            quickReply1['action'] = 'block'
            quickReply1['label'] = '뒤로가기'
            quickReply1['blockId'] = blockid.search_menu
            quickReplies.append(quickReply1)

            quickReply2 = deepcopy(quickReply)
            quickReply2['action'] = 'block'
            quickReply2['label'] = '도움말'
            quickReply2['blockId'] = blockid.howto
            quickReplies.append(quickReply2)

            responseBody['template']['quickReplies'] = quickReplies

        except Exception as e:
            log.error_log(e)
            simpleText['simpleText']['text'] = '죄송합니다. 찾는 책이 없습니다 :('
            outputs = [simpleText]
            responseBody['template']['outputs'] = outputs

        return responseBody


if __name__ == '__main__':
    search = Searching()
    keyword = '연어'

    #  print('여기는 네이버')
    #  books = search.get_book_by_naver(keyword)
    #  for book in books['items']:
    #      print(book['title'])
    #      print(book['author'])

    print('여기는 카카오')
    books = search.get_book(keyword)
    for book in books:
        print(book['title'])
        print(", ".join(book['authors']))

    #  keyword = "맞춤법 틀리면 외 않되? 쓰고싶은대로쓰면돼지 "
    #  print(search.get_book(keyword))
    #  print(search.get_book(keyword))
    #  print(search.get_book(isbn)['authors'])
    #  print(", ".join(search.get_book(isbn)['authors']))
