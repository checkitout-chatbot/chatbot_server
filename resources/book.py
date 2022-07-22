from flask_restful import Resource, reqparse
from models.book import BookModel
import random


class Book(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', type=str)
    parser.add_argument('author', type=str)
    parser.add_argument('publisher', type=str)
    parser.add_argument('summary', type=str)
    parser.add_argument('img', type=str)
    parser.add_argument('genre', type=str)
    parser.add_argument('rate', type=str)
    parser.add_argument('bestseller', type=str)

    def get(self, isbn):
        book = BookModel.find_by_isbn(isbn)
        if book:
            return book.json()
        return {'message': '책을 찾을 수 없습니다.'}, 404

    def post(self, isbn):
        if BookModel.find_by_isbn(isbn):
            return {'message': f"{isbn} 책은 이미 존재합니다."}, 400

        data = Book.parser.parse_args()
        book = BookModel(isbn, **data)
        try:
            book.save_to_db()
        except:
            return {"message": "책 데이터를 저장하는 중 에러가 발생했습니다."}, 500

        return book.json(), 201

    def delete(self, isbn):
        book = BookModel.find_by_isbn(isbn)
        if book:
            book.delete_from_db()

        return {'message': '책을 삭제했습니다.'}


class Today(Resource):  # 오늘의 추천
    def post(self):
        # bestseller 목록 전체 가져와서 랜덤으로 한 권 뽑기
        books = BookModel.find_by_bestseller()
        randint = random.randint(0, len(books))
        book = books[randint].json()
        # 책 설명 10자 이상 넘어가면 요약
        description = (
            book['summary'][:50] + '...') if len(book['summary']) > 50 else book['summary']
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "basicCard": {
                            "title": book['title'],
                            "description": description,
                            "thumbnail": {
                                "imageUrl": book['img']
                            },
                            "profile": {
                                "imageUrl": book['img'],
                                "nickname": book['title']
                            },
                            "social": {
                                "like": 1238,
                                "comment": 8,
                                "share": 780
                            },
                            "buttons": [
                                {
                                    "action": "message",
                                    "label": "읽고 싶어요(저장)",
                                    "messageText": "내가 읽고 싶은 책 목록에 저장했습니다(개발예정)"
                                },
                                {
                                    "action":  "message",
                                    "label": "읽은 책입니다(저장+평점)",
                                    "messageText": "내가 읽은 책 목록에 저장하고 평점 남기기(개발예정)"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return responseBody
