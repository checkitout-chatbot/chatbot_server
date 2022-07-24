from flask_restful import Resource, reqparse
from models.book import BookModel
from models.book_list import BookListModel

# extra value 값으로 isbn을 가져와 읽고 싶은 책 저장


class SaveWanted(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveWanted.parser.parse_args()
        print(data)
        isbn = data['action']['clientExtra']['isbn']
        user_id = data['userRequest']['user']['id']
        try:
            # 리스트에 등록된 책인지 확인
            check_booklist = BookListModel.find_by_book(isbn, user_id)
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
                                "label": "읽고 싶은 책 목록 확인하기",
                                "action": "block",
                                "blockId": "62bf084750b23b1e3a6e2655"
                            },
                            {
                                "label": "읽은 책 목록 확인하기",
                                "action": "block",
                                "blockId": "62bef98450b23b1e3a6e25ba"
                            }
                        ]
                    }
                }
            else:
                booklist = BookListModel(isbn, user_id, 0, None, None)
                booklist.save_to_db()
                responseBody = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "simpleText": {
                                    "text": "읽고 싶은 책 목록에 책을 저장했습니다.\n즐거운 독서 라이프 되세요~!"
                                }
                            }
                        ],
                        "quickReplies": [
                            {
                                "label": "목록 확인하기",
                                "action": "block",
                                "blockId": "62bf084750b23b1e3a6e2655"
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
                                "text": "오류가 발생했습니다. 개발자에게 문의해 주세요."
                            }
                        },
                    ],
                    "quickReplies": [
                        {
                            "label": "문의하기",
                            "action": "block",
                            "blockId": "62d2bef8903c8b5a8004f18c"
                        }
                    ]
                }
            }
        return responseBody


class SaveReview(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveReview.parser.parse_args()
        print(data)
        isbn = data['action']['clientExtra']['isbn']
        user_id = data['userRequest']['user']['id']
        rate = data['action']['params']['rate']
        review = data['action']['params']['review']
        try:
            # 리스트에 등록된 책인지 확인
            check_booklist = BookListModel.find_by_book(isbn, user_id)
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
                                "label": "읽고 싶은 책 목록 확인하기",
                                "action": "block",
                                "blockId": "62bf084750b23b1e3a6e2655"
                            },
                            {
                                "label": "읽은 책 목록 확인하기",
                                "action": "block",
                                "blockId": "62bef98450b23b1e3a6e25ba"
                            }
                        ]
                    }
                }
            else:
                booklist = BookListModel(isbn, user_id, 1, review, rate)
                booklist.save_to_db()
                responseBody = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "simpleText": {
                                    "text": "읽은 책 목록에 책을 저장했습니다.\n완독을 축하드려요~!"
                                }
                            }
                        ],
                        "quickReplies": [
                            {
                                "label": "목록 확인하기",
                                "action": "block",
                                "blockId": "62bef98450b23b1e3a6e25ba"
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
                                "text": "오류가 발생했습니다. 개발자에게 문의해 주세요."
                            }
                        },
                    ],
                    "quickReplies": [
                        {
                            "label": "문의하기",
                            "action": "block",
                            "blockId": "62d2bef8903c8b5a8004f18c"
                        }
                    ]
                }
            }
        return responseBody
