import random
from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.search import Searching
from resources.response import Response, BlockID


class Today(Resource):  # 오늘의 추천
    parser = reqparse.RequestParser()

    def post(self):
        # bestseller 목록 전체 가져와서 랜덤으로 한 권 뽑기
        books = BookModel.find_by_bestseller()
        randint = random.randint(0, len(books))
        book = books[randint].json()

        blockid = BlockID()
        response = Response()
        itemList = response.itemList
        button = response.button
        itemCard = response.itemCard
        simpleText = response.simpleText
        responseBody = response.responseBody
        kyobo_url = f"https://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={book['isbn']}&orderClick=LEa&Kc="

        itemLists = []
        itemList1 = itemList.copy()
        itemList1['title'] = '지은이'
        itemList1['description'] = book['author']
        itemLists.append(itemList1)

        itemList2 = itemList.copy()
        itemList2['title'] = '출판사'
        itemList2['description'] = book['publisher']
        itemLists.append(itemList2)

        itemList3 = itemList.copy()
        itemList3['title'] = '장르'
        itemList3['description'] = book['genre']
        itemLists.append(itemList3)
        itemCard['itemCard']['itemList'] = itemLists

        buttons = []
        button1 = button.copy()
        button1['action'] = 'webLinkUrl'
        button1['label'] = '책 정보'
        button1['webLinkUrl'] = kyobo_url
        buttons.append(button1)

        button2 = button.copy()
        button2['action'] = 'block'
        button2['label'] = '책 저장'
        button2['blockId'] = blockid.save_menu
        button2['extra']['isbn'] = book['isbn']
        buttons.append(button2)
        itemCard['itemCard']['buttons'] = buttons

        itemCard['itemCard']['imageTitle']['title'] = book['title']
        itemCard['itemCard']['imageTitle']['imageUrl'] = book['img']

        simpleText['simpleText']['text'] = '고심해서 고른 책이에요 어떠세요??'
        outputs = [simpleText, itemCard]
        responseBody['template']['outputs'] = outputs

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
