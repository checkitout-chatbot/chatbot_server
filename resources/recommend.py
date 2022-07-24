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
                                        "blockId": "62654c249ac8ed78441532de",
                                        "extra": {
                                            "key1": "value1",
                                            "key2": "value2"
                                        }
                                    },
                                    {
                                        "title": book2['title'],
                                        "description": ((book2['summary'][:50] + '...') if len(book2['summary']) > 50 else book2['summary']),
                                        "imageUrl": book2['img'],
                                        "action": "block",
                                        "blockId": "62654c249ac8ed78441532de",
                                        "extra": {
                                            "key1": "value1",
                                            "key2": "value2"
                                        }
                                    },
                                    {
                                        "title": book3['title'],
                                        "description": ((book3['summary'][:50] + '...') if len(book3['summary']) > 50 else book3['summary']),
                                        "imageUrl": book3['img'],
                                        "action": "block",
                                        "blockId": "62654c249ac8ed78441532de",
                                        "extra": {
                                            "key1": "value1",
                                            "key2": "value2"
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
                                "text": "죄송하지만 말씀하신 책을 찾을 수 없어요."
                            }
                        }
                    ]
                }
            }
            print(e)
        return responseBody


class Sense(Resource):  # 알잘딱깔센 추천
    parser = reqparse.RequestParser()

    def post(self):
        body = request.get_json()
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
        body = request.get_json()
        print(body)
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
