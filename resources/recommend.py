import random
from flask import request
from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.search import Searching


class Today(Resource):  # 오늘의 추천
    parser = reqparse.RequestParser()

    def post(self):
        # bestseller 목록 전체 가져와서 랜덤으로 한 권 뽑기
        books = BookModel.find_by_bestseller()
        randint = random.randint(0, len(books))
        book = books[randint].json()
        # 책 설명 50자 이상 넘어가면 요약
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
        return responseBody


class Similar(Resource):  # 비슷한 책 추천
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict)

    def post(self):
        data = Similar.parser.parse_args()
        print(data)
        try:
            # kakao 책 검색으로 제목입력하여 ISBN 추출
            input_title = data['action']['params']['title']
            search = Searching()
            input_isbn = search.get_isbn(input_title)

            # doc2vec 모델로 유사도 구한 후 비슷한 책 중 랜덤으로 3개 뽑기
            book = BookModel.find_by_isbn(input_isbn).json()
            similar_books = book['similarity'].split(",")
            rand_ints = random.sample(range(0, 9), 3)
            book1 = BookModel.find_by_isbn(similar_books[rand_ints[0]]).json()
            book2 = BookModel.find_by_isbn(similar_books[rand_ints[1]]).json()
            book3 = BookModel.find_by_isbn(similar_books[rand_ints[2]]).json()

            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "listCard": {
                                "header": {
                                    "title": "이런 책은 어떠세요?"
                                },
                                "items": [
                                    {
                                        "title": book1['title'],
                                        "description": ((book1['summary'][:50] + '...') if len(book1['summary']) > 50 else book1['summary']),
                                        "imageUrl": book1['img'],
                                        "action": "block",
                                        "blockId": "62dd402d903c8b5a80058543",
                                        "extra": {
                                            "isbn": book['isbn'],
                                        }
                                    },
                                    {
                                        "title": book2['title'],
                                        "description": ((book2['summary'][:50] + '...') if len(book2['summary']) > 50 else book2['summary']),
                                        "imageUrl": book2['img'],
                                        "action": "block",
                                        "blockId": "62dd402d903c8b5a80058543",
                                        "extra": {
                                            "isbn": book['isbn'],
                                        }
                                    },
                                    {
                                        "title": book3['title'],
                                        "description": ((book3['summary'][:50] + '...') if len(book3['summary']) > 50 else book3['summary']),
                                        "imageUrl": book3['img'],
                                        "action": "block",
                                        "blockId": "62dd402d903c8b5a80058543",
                                        "extra": {
                                            "isbn": book['isbn'],
                                        }
                                    },
                                ],
                                "buttons": [
                                    {
                                        "label": "다른 책으로 한 번 더!",
                                        "action": "block",
                                        "blockId": "62bef96a50b23b1e3a6e25b6",
                                    }
                                ]
                            }
                        },
                        {
                            "simpleText": {
                                "text": "위의 책 중 읽고 싶은 책이 있다면?\n책을 누르면 읽고 싶은 책으로 저장됩니다!"
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
                                "text": "죄송하지만 말씀하신 책을 찾을 수 없어요."
                            }
                        }
                    ]
                }
            }
        return responseBody


class Sense(Resource):  # 알잘딱깔센 추천
    parser = reqparse.RequestParser()

    def post(self):
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "개발 예정입니다."

                        }

                    }

                ]

            }
        }
        return responseBody


class Social(Resource):  # 소셜 추천
    parser = reqparse.RequestParser()

    def post(self):
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "개발 예정입니다."

                        }

                    }

                ]

            }
        }
        return responseBody
