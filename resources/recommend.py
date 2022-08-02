from copy import deepcopy
from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.search import Searching
from resources.response import Response, BlockID
import log
from datetime import datetime


class Today(Resource):  # 오늘의 추천
    parser = reqparse.RequestParser()

    def post(self):
        data = Today.parser.parse_args()
        log.info_log(data)

        now = datetime.now()
        # 매달 1일에 베스트셀러 갱신하여 0부터 30까지 저장
        # 그 날짜에 해당하는 책 추천 22800 -> 22년 8월 1번째 베스트셀러
        date = now.year % 100*1000 + now.month*100
        if now.day == 1 and BookModel.find_by_bestseller(date) == None:
            search = Searching()
            books = search.search_list("Bestseller", 50)
            for i in books.keys():
                check_book = BookModel.find_by_isbn(books[i]['isbn'])
                if check_book == None:
                    pubDate = datetime.strptime(
                        books[i]['pubDate'], '%Y-%m-%d').date()
                    check_book = BookModel(isbn=books[i]['isbn'], title=books[i]['title'], author=books[i]['author'], publisher=books[i]['publisher'],
                                           summary=books[i]['summary'], img=books[i]['img'], pubDate=pubDate,
                                           genre=books[i]['genre'], rate=books[i]['rate'], bestseller=(date+i), similarity=None)
                    check_book.save_to_db()
                else:
                    check_book.bestseller = date+i
                    check_book.save_to_db()

        book = BookModel.find_by_bestseller(date+now.day-1).json()

        blockid = BlockID()
        response = Response()
        itemList = response.itemList
        button = response.button
        itemCard = response.itemCard
        simpleText = response.simpleText
        responseBody = response.responseBody
        kyobo_url = f"https://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={book['isbn']}&orderClick=LEa&Kc="

        itemLists = []
        itemList1 = deepcopy(itemList)
        itemList1['title'] = '지은이'
        itemList1['description'] = book['author']
        itemLists.append(itemList1)

        itemList2 = deepcopy(itemList)
        itemList2['title'] = '출판사'
        itemList2['description'] = book['publisher']
        itemLists.append(itemList2)

        itemList3 = deepcopy(itemList)
        itemList3['title'] = '출판일'
        itemList3['description'] = str(book['pubDate'])
        itemLists.append(itemList3)
        itemCard['itemCard']['itemList'] = itemLists

        buttons = []
        button1 = deepcopy(button)
        button1['action'] = 'webLink'
        button1['label'] = '책 정보'
        button1['webLinkUrl'] = kyobo_url
        buttons.append(button1)

        button2 = deepcopy(button)
        button2['action'] = 'block'
        button2['label'] = '책 저장'
        button2['blockId'] = blockid.save_menu
        button2['extra']['isbn'] = book['isbn']
        buttons.append(button2)

        itemCard['itemCard']['buttons'] = buttons
        itemCard['itemCard']['imageTitle']['title'] = book['title']
        itemCard['itemCard']['imageTitle']['imageUrl'] = book['img']

        simpleText['simpleText']['text'] = '심사숙고해서 골랐어요!! 어떠세요??'

        outputs = [simpleText, itemCard]
        responseBody['template']['outputs'] = outputs

        quickReplies = []
        quickReply = response.quickReply

        quickReply1 = deepcopy(quickReply)
        quickReply1['action'] = 'block'
        quickReply1['label'] = '뒤로가기'
        quickReply1['blockId'] = blockid.recom_menu
        quickReplies.append(quickReply1)

        quickReply2 = deepcopy(quickReply)
        quickReply2['action'] = 'block'
        quickReply2['label'] = '도움말'
        quickReply2['blockId'] = blockid.howto
        quickReplies.append(quickReply2)

        responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class Similar(Resource):  # 비슷한 책 추천
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict)

    def post(self):
        data = Similar.parser.parse_args()
        log.info_log(data)

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
            input_books = search.search_keywords(input_title, 30)

            # doc2vec으로 구한 유사도 가져오기
            # 유사도가 있는 책이 나올 때까지 검색
            similar_books = []
            for i in input_books.keys():
                book = BookModel.find_by_isbn(input_books[i]['isbn']).json()
                if book['similarity'] != None:
                    similar_books = book['similarity'].split(",")
                    break

            # 유사도 isbn값들로 책 찾아 리스트로 저장
            books = [BookModel.find_by_isbn(isbn).json()
                     for isbn in similar_books]

            items = []
            for book in books:
                item1 = deepcopy(item)
                item1['imageTitle']['title'] = book['title']
                item1['imageTitle']['imageUrl'] = book['img']

                itemLists = []
                itemList1 = deepcopy(itemList)
                itemList1['title'] = '지은이'
                itemList1['description'] = book['author']
                itemLists.append(itemList1)

                itemList2 = deepcopy(itemList)
                itemList2['title'] = '출판사'
                itemList2['description'] = book['publisher']
                itemLists.append(itemList2)

                itemList3 = deepcopy(itemList)
                itemList3['title'] = '출판일'
                itemList3['description'] = str(book['pubDate'])
                itemLists.append(itemList3)
                item1['itemList'] = itemLists

                buttons = []
                button1 = deepcopy(button)
                button1['action'] = 'webLink'
                button1['label'] = '책 정보'
                kyobo_url = f"https://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={book['isbn']}&orderClick=LEa&Kc="
                button1['webLinkUrl'] = kyobo_url
                buttons.append(button1)

                button2 = deepcopy(button)
                button2['action'] = 'block'
                button2['label'] = '책 저장'
                button2['blockId'] = blockid.save_menu
                button2['extra']['isbn'] = book['isbn']
                buttons.append(button2)
                item1['buttons'] = buttons

                items.append(item1)

            carousel_itemCard['carousel']['items'] = items
            simpleText['simpleText']['text'] = '심사숙고해서 골랐어요!! 어떠세요??'

            outputs = [simpleText, carousel_itemCard]
            responseBody['template']['outputs'] = outputs

            quickReplies = []
            quickReply = response.quickReply

            quickReply1 = deepcopy(quickReply)
            quickReply1['action'] = 'block'
            quickReply1['label'] = '뒤로가기'
            quickReply1['blockId'] = blockid.recom_menu
            quickReplies.append(quickReply1)

            quickReply2 = deepcopy(quickReply)
            quickReply2['action'] = 'block'
            quickReply2['label'] = '도움말'
            quickReply2['blockId'] = blockid.howto
            quickReplies.append(quickReply2)

            responseBody['template']['quickReplies'] = quickReplies

        except Exception as e:
            log.error_log(e)

            simpleText['simpleText']['text'] = '비슷한 책을 찾지 못했어요 죄송해요ㅠㅠ'
            outputs = [simpleText]
            responseBody['template']['outputs'] = outputs

        return responseBody


class Sense(Resource):  # 알잘딱깔센 추천
    parser = reqparse.RequestParser()

    def post(self):
        data = Similar.parser.parse_args()
        log.info_log(data)

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
        log.info_log(data)

        response = Response()
        simpleText = response.simpleText
        responseBody = response.responseBody

        simpleText['simpleText']['text'] = '개발 예정입니다.'
        outputs = [simpleText]
        responseBody['template']['outputs'] = outputs
        return responseBody
