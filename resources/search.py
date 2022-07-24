from flask_restful import Resource, reqparse
from models.book import BookModel
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
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "basicCard": {
                                "title": book['title'],
                                "description": book['author'],
                                "thumbnail": {
                                    "imageUrl": book['img']
                                },
                                "buttons": [
                                    {
                                        "action": "message",
                                                  "label": "책 소개 보기",
                                                  "messageText": book['summary']
                                    }
                                ]
                            }
                        }
                    ],
                    "quickReplies": [
                        {
                            "label": "뒤로가기",
                            "action": "block",
                            "blockId": "62dd372c28d63278024d6104"
                        },
                        {
                            "label": "읽고 싶은 책으로 저장",
                            "action": "block",
                            "blockId": "62dd402d903c8b5a80058543",
                            "extra": {
                                "isbn": book['isbn'],
                            }
                        },
                        {
                            "label": "읽은 책으로 저장",
                            "action": "block",
                            "blockId": "62dd404bc7d05102c2ccffb4",
                            "extra": {
                                "isbn": book['isbn'],
                            }
                        }
                    ]
                }
            }
        except Exception:
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                            {
                                "simpleText": {
                                    "text": "죄송하지만 찾는 책이 없습니다."
                                }
                            },
                    ],
                    "quickReplies": [
                        {
                            "label": "뒤로가기",
                            "action": "block",
                            "blockId": "62dd372c28d63278024d6104"
                        }
                    ]
                }
            }
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

            # 책 데이터 카드형으로 출력
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "basicCard": {
                                "title": book['title'],
                                "description": book['author'],
                                "thumbnail": {
                                    "imageUrl": book['img']
                                },
                                "buttons": [
                                    {
                                        "action": "message",
                                                  "label": "책 소개 보기",
                                                  "messageText": book['summary']
                                    }
                                ]
                            }
                        }
                    ],
                    "quickReplies": [
                        {
                            "label": "뒤로가기",
                            "action": "block",
                            "blockId": "62dd372c28d63278024d6104"
                        },
                        {
                            "label": "읽고 싶은 책으로 저장",
                            "action": "block",
                            "blockId": "62dd402d903c8b5a80058543",
                            "extra": {
                                "isbn": book['isbn']
                            }
                        },
                        {
                            "label": "읽은 책으로 저장",
                            "action": "block",
                            "blockId": "62dd404bc7d05102c2ccffb4",
                            "extra": {
                                "isbn": book['isbn']
                            }
                        }
                    ]
                }
            }
        except Exception:
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                            {
                                "simpleText": {
                                    "text": "죄송하지만 찾는 책이 없습니다."
                                }
                            },
                    ],
                    "quickReplies": [
                        {
                            "label": "뒤로가기",
                            "action": "block",
                            "blockId": "62dd372c28d63278024d6104"
                        }
                    ]
                }
            }
        return responseBody


if __name__ == '__main__':
    #  title = input("찾고 싶은 책의 제목을 입력하세요: ")
    keyword = "미움 받을 용기 - 기시미 이치로"
    isbn = "9788996991342"
    search = Searching()
    print(search.get_isbn(keyword))
    print(search.get_book(isbn)['authors'])
    print(", ".join(search.get_book(isbn)['authors']))
