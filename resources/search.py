from copy import deepcopy
from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.response import Response, BlockID
import requests
import json
from hanspell import spell_checker
import log
from datetime import datetime
import os


class Searching:
    def __init__(self):
        self.key = os.environ.get('ALADIN_KEY', 'q1111')

    def json_to_dict(self, url, informs):
        cnt = 0
        try:
            # request 보내기
            response = requests.get(url)
            # 받은 response를 json 타입으로 바뀌주기
            contents = json.loads(response.text)
            for content in contents["item"]:
                isbn = content["isbn13"]
                title = content["title"]
                author = content["author"]
                publisher = content["publisher"]
                summary = content["description"]
                img = content["cover"]
                genre = content["categoryName"].split('>')[1]
                rate = content["customerReviewRank"]
                pubDate = content["pubDate"]
                inform = {'isbn': isbn, 'title': title, 'author': author, 'publisher': publisher,
                          'summary': summary, 'img': img, 'genre': genre, 'rate': rate, 'pubDate': pubDate}
                informs[cnt] = inform
                cnt += 1
        except Exception as e:
            log.error_log(e)
        return informs

    def search_keywords(self, query, num=10):
        url = f"http://www.aladin.co.kr/ttb/api/ItemSearch.aspx?ttbkey={self.key}&Query={query}&QueryType=Keyword&MaxResults={num}&start=1&SearchTarget=Book&output=js&Version=20131101"
        informs = {}
        informs = Searching.json_to_dict(self, url, informs)
        if len(informs) == 0:
            query = spell_checker.check(query)
            query = query.checked
            informs = {}
            informs = Searching.json_to_dict(self, url, informs)
        return informs

    def search_list(self, item_list='Bestseller', num=10):
        url = f"http://www.aladin.co.kr/ttb/api/ItemList.aspx?ttbkey={self.key}&QueryType={item_list}&MaxResults={num}&start=1&SearchTarget=Book&output=js&Version=20131101"
        informs = {}
        informs = Searching.json_to_dict(self, url, informs)
        return informs


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
        if book == None:
            search = Searching()
            book = search.search_keywords(barcode, 1)[0]
            pubDate = datetime.strptime(book['pubDate'], '%Y-%m-%d').date()
            book = BookModel(isbn=book['isbn'], title=book['title'], author=book['author'], publisher=book['publisher'],
                             pubDate=pubDate, summary=book['summary'], img=book['img'], genre=book['genre'], rate=book['rate'])
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
        button2['extra']['book_id'] = book['id']
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
        books = search.search_keywords(keyword, 10)

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
            for i in books.keys():
                check_book = BookModel.find_by_isbn(books[i]['isbn'])
                # books 테이블에 해당 책 없으면 저장
                if check_book == None:
                    pubDate = datetime.strptime(
                        books[i]['pubDate'], '%Y-%m-%d').date()
                    book = BookModel(isbn=books[i]['isbn'], title=books[i]['title'], author=books[i]['author'], publisher=books[i]['publisher'],
                                     pubDate=pubDate, summary=books[i]['summary'], img=books[i]['img'], genre=books[i]['genre'], rate=books[i]['rate'])
                    book.save_to_db()
                    book = book.json()
                else:
                    book = check_book.json()

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
                button2['extra']['book_id'] = book['id']
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
