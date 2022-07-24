from flask_restful import Resource, reqparse
from models.book import BookModel
from models.book_list import BookListModel
import requests
import json


class Searching:
    def __init__(self):
        self.REST_API_KEY = 'c8981be15dbb94247a93cce5e564653b'
        self.url = "https://dapi.kakao.com/v3/search/book"

    def book(self, query):
        queryString = {"query": query}
        header = {'Authorization': f'KakaoAK {self.REST_API_KEY}'}
        r = requests.get(self.url, headers=header, params=queryString)
        books = json.loads(r.text)
        isbn = books['documents'][0]['isbn'].split()[1]
        return isbn

    def isbn_book(self, query):
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
        data = Barcode.parser.parse_args()
        print(data)

        barcode = data['action']['params']['barcode']
        barcode = barcode.replace('}', '').split(':')[1]
        try:
            book = BookModel.find_by_isbn(barcode)
            if book == None:
                search = Searching()
                book = search.isbn_book(barcode)
                isbn = book['isbn'].split()[1]
                authors = ", ".join(book['authors'])
                book = BookModel(isbn, book['title'], authors, book['publisher'],
                                 book['contents'], book['thumbnail'], None, None, None)
                book.save_to_db()

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
                                                  "label": "무슨 내용일까?",
                                                  "messageText": book['summary']
                                    },
                                ]
                            }
                        }
                    ],
                    "quickReplies": [
                        {
                            "label": "별로야",
                            "action": "block",
                            "blockId": "62dc1254903c8b5a8005803f"
                        },
                        {
                            "label": "읽고 싶은 책이야",
                            "action": "block",
                            "blockId": "62dc1254903c8b5a8005803f"
                        },
                    ]
                }
            }

        except Exception as e:
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
                            "blockId": "62c90931903c8b5a8004448c"
                        },
                        {
                            "label": "책 추천 받기",
                            "action": "block",
                            "blockId": "62c7e7ade262a941bbdca4ea"
                        },
                    ]
                }
            }
        return responseBody


if __name__ == '__main__':
    #  title = input("찾고 싶은 책의 제목을 입력하세요: ")
    keyword = "미움 받을 용기 - 기시미 이치로"
    isbn = "9788996991342"
    search = Searching()
    print(search.book(keyword))
    print(search.isbn_book(isbn)['authors'])
    print(", ".join(search.isbn_book(isbn)['authors']))
