from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.book_list import BookListModel


class BookList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('isbn', type=str)
    parser.add_argument('username', type=str, required=True,
                        help="You have to input the User ID!")
    parser.add_argument('review', type=str)
    parser.add_argument('rate', type=float)

    @jwt_required()
    def get(self, status):
        data = BookList.parser.parse_args()
        books = BookListModel.find_by_status(data['username'], status)
        if books:
            return {'books': [book.json() for book in books]}

        return {'message': f"읽기상태: {status}인 책들을 찾을 수 없습니다."}, 404

    def post(self, status):
        data = BookList.parser.parse_args()
        if BookListModel.find_by_book(data['isbn'], data['username']):
            return {'message': f"{data['isbn']}의 책은 이미 존재합니다."}, 400

        book = BookListModel(status=status, **data)

        try:
            book.save_to_db()
        except:
            return {"message": "책을 등록하는 중에 에러가 발생했습니다."}, 500

        return book.json(), 201

    def delete(self, status):
        data = BookList.parser.parse_args()
        book = BookListModel.find_by_book(data['isbn'], data['username'])
        if book:
            book.delete_from_db()
            return {'message': '책을 삭제했습니다.'}
        return {'message': '책을 찾을 수 없습니다.'}, 404

    def put(self, status):
        data = BookList.parser.parse_args()

        book = BookListModel.find_by_book(data['isbn'], data['username'])

        if book:
            book.status = status
        else:
            book = BookListModel(status=status, **data)

        book.save_to_db()

        return book.json()
