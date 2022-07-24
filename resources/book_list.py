from flask_restful import Resource, reqparse
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

        # 리스트 확인시 유저가 없을 경우 유저 등록
        if BookList.check_id(self, status) == None:
            user = UserModel(user_id, user_id)
            user.save_to_db()
            print("id를 db에 저장했습니다.")

        # 읽고 싶은 책 응답형
        if status == 0:
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "listCard": {
                                "header": {
                                    "title": "읽고 싶은 책 리스트"
                                },
                                "items": [
                                ],
                                "buttons": [
                                    {
                                        "label": "리스트 더보기",
                                        "action": "message",
                                        "messageText": "개발 예정입니다."
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
                            "label": "검색하여 추가",
                            "action": "block",
                            "blockId": "62dd372c28d63278024d6104",
                        },
                        {
                            "label": "읽은 책으로 변경",
                            "action": "message",
                            "messageText": "개발 예정입니다.",
                        }
                    ]
                }
            }
        # 읽은 책 응답형
        else:
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "listCard": {
                                "header": {
                                    "title": "읽은 책 리스트"
                                },
                                "items": [
                                ],
                                "buttons": [
                                    {
                                        "label": "리스트 더보기",
                                        "action": "message",
                                        "messageText": "개발 예정입니다."
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
                            "label": "검색하여 추가",
                            "action": "block",
                            "blockId": "62dd372c28d63278024d6104",
                        }
                    ]
                }
            }
        # 공통 책 리스트
        item = {
            "title": "",
            "description": "",
            "imageUrl": "",
            "action": "message",
            "messageText": "개발 예정입니다.",
        }

        # 저장한 책이 존재하면
        books = BookListModel.find_by_status(user_id, status)
        if books:
            outputs = responseBody['template']['outputs']
            items = outputs[0]['listCard']['items']
            # 보기
            cnt = 0
            for book in books:
                book_info = BookModel.find_by_isbn(book.json()['isbn']).json()
                item['title'] = book_info['title']
                description = (book_info['summary'][:50] + '...') if len(
                    book_info['summary']) > 50 else book_info['summary']
                item['description'] = description
                item['imageUrl'] = book_info['img']
                items.append(item.copy())
                cnt += 1
                if cnt == 5:
                    break
        # 아직 저장한 책이 없다면
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
                            "label": "뒤로",
                            "action": "block",
                            "blockId": "62c90931903c8b5a8004448c",
                        },
                        {
                            "label": "검색하여 추가",
                            "action": "block",
                            "blockId": "62dd372c28d63278024d6104",
                        },
                        {
                            "label": "책 추천 받기",
                            "action": "block",
                            "blockId": "62c7e7ade262a941bbdca4ea",
                        }
                    ]
                }
            }
        return responseBody
