from flask_restful import Resource, reqparse
from models.book import BookModel


class Book(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title',
                        type=str,
                        required=False,
                        )
    parser.add_argument('author',
                        type=str,
                        required=False,
                        )
    parser.add_argument('publisher',
                        type=str,
                        required=False,
                        )
    parser.add_argument('summary',
                        type=str,
                        required=False,
                        )
    parser.add_argument('img',
                        type=str,
                        required=False,
                        )
    parser.add_argument('genre',
                        type=str,
                        required=False,
                        )
    parser.add_argument('rate',
                        type=str,
                        required=False,
                        )
    parser.add_argument('bestseller',
                        type=str,
                        required=False,
                        )

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

