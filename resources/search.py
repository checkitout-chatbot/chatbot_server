from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.response import Response, BlockID
import requests
import json


class Searching:
    def __init__(self):
        self.REST_API_KEY = 'c8981be15dbb94247a93cce5e564653b'
        self.url = "https://dapi.kakao.com/v3/search/book"

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
        books = json.loads(r.text)
        book = books['documents'][0]
        return book


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

            # 책 데이터 카드형으로 출력
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

            button2 = button.copy()
            button2['action'] = 'block'
            button2['label'] = '읽고 싶은 책으로'
            button2['blockId'] = blockid.save_want
            button2['extra']['isbn'] = book['isbn']
            buttons.append(button2)
            itemCard['itemCard']['buttons'] = buttons

            itemCard['itemCard']['imageTitle']['title'] = book['title']
            itemCard['itemCard']['imageTitle']['imageUrl'] = book['img']

            simpleText['simpleText']['text'] = '찾으시는 책이 맞나요?'
            outputs = [simpleText, itemCard]
            responseBody['template']['outputs'] = outputs

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

            button2 = button.copy()
            button2['action'] = 'block'
            button2['label'] = '읽고 싶은 책으로'
            button2['blockId'] = blockid.save_want
            button2['extra']['isbn'] = book['isbn']
            buttons.append(button2)
            itemCard['itemCard']['buttons'] = buttons

            itemCard['itemCard']['imageTitle']['title'] = book['title']
            itemCard['itemCard']['imageTitle']['imageUrl'] = book['img']

            simpleText['simpleText']['text'] = '찾으시는 책이 맞나요?'
            outputs = [simpleText, itemCard]
            responseBody['template']['outputs'] = outputs

        except Exception:
            simpleText['simpleText']['text'] = '책을 찾지 못했어요..\n다시 한 번 정확하게 입력해 보세요!'
            outputs = [simpleText]
            responseBody['template']['outputs'] = outputs

        return responseBody


if __name__ == '__main__':
    #  title = input("찾고 싶은 책의 제목을 입력하세요: ")
    keyword = "미움 받을 용기 - 기시미 이치로"
    isbn = "9788996991342"
    search = Searching()
    print(search.get_isbn(keyword))
    print(search.get_book(isbn)['authors'])
    print(", ".join(search.get_book(isbn)['authors']))
