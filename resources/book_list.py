from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.book import BookModel
from models.book_list import BookListModel
from models.user import UserModel


class BookList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userRequest', type=dict, required=True)

    def check_id(self, status):
        data = BookList.parser.parse_args()
        user_id = data['userRequest']['user']['id']
        checking = UserModel.find_by_username(user_id)
        return checking

    def post(self, status):
        data = BookList.parser.parse_args()
        print(data)
        user_id = data['userRequest']['user']['id']

        if BookList.check_id(self, status) == None:
            user = UserModel(user_id, user_id)
            user.save_to_db()
            print("id를 db에 저장했습니다.")

        books = BookListModel.find_by_status(user_id, status)
        if books:
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "listCard": {
                                "header": {
                                    "title": "읽고  싶은 책 리스트"
                                },
                                "items": [
                                ],
                                "buttons": [
                                    {
                                        "label": "마이페이지로 돌아가기",
                                        "action": "block",
                                        "blockId": "62dc1254903c8b5a8005803f"
                                    }
                                ]
                            }
                        }
                    ],
                    "quickReplies": [
                        {
                            "label": "뒤로",
                            "action": "block",
                            "blockId": "62c90931903c8b5a8004448c",
                        },
                        {
                            "label": "바코드로 책 추가",
                            "action": "block",
                            "blockId": "62dc1254903c8b5a8005803f",
                        },
                        {
                            "label": "책 추천 받기",
                            "action": "block",
                            "blockId": "62c7e7ade262a941bbdca4ea",
                        }
                    ]
                }
            }
            item = {
                "title": "",
                "description": "",
                "imageUrl": "",
                "action": "block",
                "blockId": "62654c249ac8ed78441532de",
            }
            outputs = responseBody['template']['outputs']
            items = outputs[0]['listCard']['items']
            # 보기
            for book in books:
                book_info = BookModel.find_by_isbn(book.json()['isbn']).json()
                item['title'] = book_info['title']
                description = (book_info['summary'][:50] + '...') if len(
                    book_info['summary']) > 50 else book_info['summary']
                item['description'] = description
                item['imageUrl'] = book_info['img']
                items.append(item.copy())
        else:
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                            {
                                "simpleText": {
                                    "text": "아직 저장한 책이 없으신가요? 책을 추천받아 저장해 보세요!"
                                }
                            },
                    ],
                    "quickReplies": [
                        {
                            "label": "뒤로가기",
                            "action": "block",
                            "blockId": "62dc1254903c8b5a8005803f"
                        },
                        {
                            "label": "책 추천 받기",
                            "action": "block",
                            "blockId": "62dc1254903c8b5a8005803f"
                        },
                    ]
                }
            }
        return responseBody


class Barcode(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)

    def post(self, status):
        data = Barcode.parser.parse_args()
        print(data)
        user_id = data['action']['id']
        barcode = data['action']['params']['barcode']
        barcode = barcode.replace('}', '').split(':')[1]
        try:
            book = BookModel.find_by_isbn(barcode).json()
            check_booklist = BookListModel.find_by_book(barcode, user_id)

            # 리스트에 등록된 책인지 확인
            if check_booklist != None:
                responseBody = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                                {
                                    "simpleText": {
                                        "text": "이미 등록된 책입니다."
                                    }
                                },
                        ],
                        "quickReplies": [
                            {
                                "label": "뒤로가기",
                                "action": "block",
                                "blockId": "62bef96a50b23b1e3a6e25b6"
                            },
                            {
                                "label": "책 추천 받기",
                                "action": "block",
                                "blockId": "62dc1254903c8b5a8005803f"
                            },
                        ]
                    }
                }
            else:
                description = (book['summary'][:50] + '...') if len(
                    book['summary']) > 50 else book['summary']
                booklist = BookListModel(
                    book['isbn'], user_id, status, None, None)
                booklist.save_to_db()
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
                                }
                            },
                            {
                                "simpleText": {
                                    "text": "책을 저장했습니다."
                                }
                            }
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
                            "blockId": "62bef96a50b23b1e3a6e25b6"
                        },
                        {
                            "label": "책 추천 받기",
                            "action": "block",
                            "blockId": "62dc1254903c8b5a8005803f"
                        },
                    ]
                }
            }
        return responseBody
