import random
from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.search import Searching
from resources.response import Response, BlockID


class Today(Resource):  # 오늘의 추천
    parser = reqparse.RequestParser()

    def post(self):
        data = Today.parser.parse_args()
        print(data)

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
        button1['action'] = 'webLink'
        button1['label'] = '책 정보'
        button1['webLinkUrl'] = kyobo_url
        buttons.append(button1)

        button2 = button.copy()
        button2['action'] = 'block'
        button2['label'] = '읽고 싶은 책으로'
        button2['blockId'] = blockid.save_want
        button2['extra']['isbn'] = book['isbn']
        buttons.append(button2)
        itemCard['itemCard']['buttons'] = buttons

        itemCard['itemCard']['imageTitle']['title'] = book['title']
        itemCard['itemCard']['imageTitle']['imageUrl'] = book['img']

        simpleText['simpleText']['text'] = '심사숙고해서 골랐어요!! 어떠세요??'
        outputs = [simpleText, itemCard]
        responseBody['template']['outputs'] = outputs

        return responseBody


class Similar(Resource):  # 비슷한 책 추천
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict)

    def post(self):
        data = Similar.parser.parse_args()
        print(data)

        blockid = BlockID()
        response = Response()
        itemList = response.itemList
        item = response.item
        button = response.button
        carousel_itemCard = response.carousel_itemCard
        simpleText = response.simpleText
        responseBody = response.responseBody

        try:
            # kakao 책 검색으로 제목입력하여 ISBN 추출
            input_title = data['action']['params']['title']
            search = Searching()
            input_isbn = search.get_isbn(input_title)

            # doc2vec 모델로 유사도 구한 후 비슷한 책 중 랜덤으로 6개 뽑기
            book = BookModel.find_by_isbn(input_isbn).json()
            similar_books = book['similarity'].split(",")
            rand_ints = random.sample(range(0, 9), 6)

            # 랜덤으로 책 6개 books에 넣기
            books = [BookModel.find_by_isbn(
                similar_books[rand_ints[i]]).json() for i in range(6)]
            #  for i in range(0, 6):
            #      globals()[f'book{i}'] = BookModel.find_by_isbn(
            #          similar_books[rand_ints[i]]).json()

            items = []
            for book in books:
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
                item['itemList'] = itemLists

                buttons = []
                button1 = button.copy()
                button1['action'] = 'webLink'
                button1['label'] = '책 정보'
                kyobo_url = f"https://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={book['isbn']}&orderClick=LEa&Kc="
                button1['webLinkUrl'] = kyobo_url
                buttons.append(button1)

                button2 = button.copy()
                button2['action'] = 'block'
                button2['label'] = '읽고 싶은 책으로'
                button2['blockId'] = blockid.save_want
                button2['extra']['isbn'] = book['isbn']
                buttons.append(button2)
                item['buttons'] = buttons

                item1 = item.copy()
                item1['imageTitle']['title'] = book['title']
                item1['imageTitle']['imageUrl'] = book['img']
                items.append(item1)

            carousel_itemCard['carousel']['items'] = items
            simpleText['simpleText']['text'] = '심사숙고해서 골랐어요!! 어떠세요??'
            outputs = [simpleText, carousel_itemCard]
            responseBody['template']['outputs'] = outputs

        except Exception:
            simpleText['simpleText']['text'] = '비슷한 책을 찾지 못했어요 죄송해요ㅠㅠ'
            outputs = [simpleText]
            responseBody['template']['outputs'] = outputs

        return responseBody


class Sense(Resource):  # 알잘딱깔센 추천
    parser = reqparse.RequestParser()

    def post(self):
        data = Similar.parser.parse_args()
        print(data)

        response = Response()
        simpleText = response.simpleText
        responseBody = response.responseBody

        simpleText['simpleText']['text'] = '개발 예정입니다.'
        outputs = [simpleText]
        responseBody['template']['outputs'] = outputs

        return responseBody


class Social(Resource):  # 소셜 추천
    parser = reqparse.RequestParser()

    def post(self):
        data = Similar.parser.parse_args()
        print(data)

        response = Response()
        simpleText = response.simpleText
        responseBody = response.responseBody

        simpleText['simpleText']['text'] = '개발 예정입니다.'
        outputs = [simpleText]
        responseBody['template']['outputs'] = outputs
        return responseBody
