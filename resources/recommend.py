from copy import deepcopy
import random
from flask_restful import Resource, reqparse
from models.book import BookModel
from resources.search import Searching
from resources.response import Response, BlockID
import log


class Today(Resource):  # 오늘의 추천
    parser = reqparse.RequestParser()

    def post(self):
        data = Today.parser.parse_args()
        log.info_log(data)

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
            input_books = search.get_book(input_title)

            # doc2vec으로 구한 유사도 가져오기
            # 유사도가 있는 책이 나올 때까지 검색
            similar_books = []
            for input_book in input_books:
                isbn = input_book['isbn'].split()
                if len(isbn) == 2:
                    isbn = isbn[1]
                else:
                    isbn = isbn[0]
                book = BookModel.find_by_isbn(isbn).json()
                log.info_log(book)
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
    parser.add_argument('action', type=dict)
    
    def post(self):
        data = Sense.parser.parse_args()
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
            # 카테고리별 도서 출력
            def recommend_sense(self, category):
                sense_books = BookModel.find_by_SenseCategory(category)
                for i in range(10):
                    randint = random.randint(0, len(sense_books))
                    books = sense_books[randint]
                return books
                
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

            simpleText['simpleText']['text'] = '오류가 발생했어요. 다시 시도해주세요.'
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
