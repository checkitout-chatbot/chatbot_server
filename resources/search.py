from copy import deepcopy
from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.response import Response, BlockID
import requests
import json
from hanspell import spell_checker


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
            if len(books) == 0:
                books = ['NULL']
        return books[0]

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
        print(data)
        barcode = data['action']['params']['barcode']
        barcode = re.sub("[^0-9]", "", barcode)

        response = Response()
        simpleText = response.simpleText
        responseBody = response.responseBody

        try:
            book = BookModel.find_by_isbn(barcode)
            # 가져온 ISBN의 책이 DB에 없는 경우 카카오 API로 검색하여 저장
            if book == None:
                search = Searching()
                book = search.get_book(barcode)
                if len(book['authors']) > 1:
                    authors = ", ".join(book['authors'])
                else:
                    authors = book['authors'][0]
                book = BookModel(barcode, book['title'], authors, book['publisher'],
                                 book['contents'], book['thumbnail'], None, None, None, None)
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
            itemList3['title'] = '장르'
            itemList3['description'] = book['genre']
            itemLists.append(itemList3)
            itemCard['itemCard']['itemList'] = itemLists

            buttons = []
            button1 = button.copy()
            button1['action'] = 'webLink'
            button1['label'] = '책 정보'
            button1['webLinkUrl'] = kyobo_url
            buttons.append(button1)

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

            quickReply3 = deepcopy(quickReply)
            quickReply3['action'] = 'block'
            quickReply3['label'] = '읽고 싶은 책으로'
            quickReply3['blockId'] = blockid.save_want
            quickReply3['extra']['isbn'] = book['isbn']
            quickReplies.append(quickReply3)

            quickReply4 = deepcopy(quickReply)
            quickReply4['action'] = 'block'
            quickReply4['label'] = '읽은 책으로'
            quickReply4['blockId'] = blockid.save_review
            quickReply4['extra']['isbn'] = book['isbn']
            quickReplies.append(quickReply4)

            responseBody['template']['quickReplies'] = quickReplies

        except Exception:
            simpleText['simpleText']['text'] = '책을 찾지 못했어요..\n다시 한 번 정확하게 입력해 보세요!'
            outputs = [simpleText]
            responseBody['template']['outputs'] = outputs

        return responseBody


class Keyword(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)

    def post(self):
        data = Barcode.parser.parse_args()
        print(data)

        keyword = data['action']['params']['keyword']
        search = Searching()
        book = search.get_book(keyword)
        isbn = book['isbn'].split()[1]

        response = Response()
        simpleText = response.simpleText
        responseBody = response.responseBody

        try:
            check_book = BookModel.find_by_isbn(isbn)
            # 가져온 ISBN의 책이 DB에 없는 경우 카카오 API로 검색하여 저장
            if check_book == None:
                if len(book['authors']) > 1:
                    authors = ", ".join(book['authors'])
                else:
                    authors = book['authors'][0]
                book = BookModel(isbn, book['title'], authors, book['publisher'],
                                 book['contents'], book['thumbnail'], None, None, None, None)
                book.save_to_db()
                book = book.json()
            else:
                book = check_book.json()

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
            itemList3['title'] = '장르'
            itemList3['description'] = book['genre']
            itemLists.append(itemList3)
            itemCard['itemCard']['itemList'] = itemLists

            buttons = []
            button1 = button.copy()
            button1['action'] = 'webLink'
            button1['label'] = '책 정보'
            button1['webLinkUrl'] = kyobo_url
            buttons.append(button1)

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

            quickReply3 = deepcopy(quickReply)
            quickReply3['action'] = 'block'
            quickReply3['label'] = '읽고 싶은 책으로'
            quickReply3['blockId'] = blockid.save_want
            quickReply3['extra']['isbn'] = book['isbn']
            quickReplies.append(quickReply3)

            quickReply4 = deepcopy(quickReply)
            quickReply4['action'] = 'block'
            quickReply4['label'] = '읽은 책으로'
            quickReply4['blockId'] = blockid.save_review
            quickReply4['extra']['isbn'] = book['isbn']
            quickReplies.append(quickReply4)

            responseBody['template']['quickReplies'] = quickReplies

        except Exception:
            simpleText['simpleText']['text'] = '책을 찾지 못했어요..\n다시 한 번 정확하게 입력해 보세요!'
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
