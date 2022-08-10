from copy import deepcopy
from flask_restful import Resource, reqparse
from models.book import BookModel
from models.user import UserModel
from models.user_similar import UserSimilarModel
from models.book_similar import BookSimilarModel
from resources.user import UserRegister
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
                                           pubDate=pubDate, summary=books[i]['summary'], img=books[i]['img'], genre=books[i]['genre'], rate=books[i]['rate'], bestseller=(date+i))
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
        button2['extra']['book_id'] = book['id']
        buttons.append(button2)

        itemCard['itemCard']['buttons'] = buttons
        itemCard['itemCard']['imageTitle']['title'] = book['title']
        itemCard['itemCard']['imageTitle']['imageUrl'] = book['img']

        simpleText['simpleText']['text'] = '요즘엔 이 책이 그렇게 핫 해요🔥'

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

            # 추천 책이 나올 때까지 검색
            similar_books = []
            for i in input_books.keys():
                try:
                    book = BookModel.find_by_isbn(
                        input_books[i]['isbn']).json()
                    similar_books = BookSimilarModel.find_by_book_id(
                        book['id'])
                    break
                except:
                    pass

            # 유사도 id값들로 책 찾아 리스트로 저장
            books = []
            for similar_book in similar_books:
                similar_book = similar_book.json()
                books.append(BookModel.find_by_id(
                    similar_book['book_similar_id']).json())
            print('찾은 책의 정보', books)

            items = []
            for i, book in enumerate(books):
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
                button2['extra']['book_id'] = book['id']
                buttons.append(button2)
                item1['buttons'] = buttons

                items.append(item1)

                if i == 4:
                    break

            carousel_itemCard['carousel']['items'] = items
            simpleText['simpleText']['text'] = '이런 책들을 좋아하실 것 같아요🥰 어떠세요??'

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
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        """
        평점 기반 추천
        """
        data = Social.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        username = data['userRequest']['user']['id']
        UserRegister.check_id(username=username)
        user_id = UserModel.find_by_username(username).json()['id']

        blockid = BlockID()
        response = Response()
        itemList = response.itemList
        item = response.item
        button = response.button
        carousel_itemCard = response.carousel_itemCard
        simpleText = response.simpleText
        responseBody = response.responseBody

        rec_books = UserSimilarModel.find_by_user(user_id)
        # 리스트에 남긴 평점 없으면 추천 안되므로 미리 걸러내기
        if len(rec_books) == 0:
            simpleText['simpleText']['text'] = '평점을 남긴 책이 부족해요 한 권만 더 남겨주세잇끼!'
            outputs = [simpleText]
            responseBody['template']['outputs'] = outputs
        else:
            items = []
            for i, rec_book in enumerate(rec_books):
                book_id = rec_book.json()['book_id']
                book = BookModel.find_by_id(book_id).json()

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
                button2['extra']['book_id'] = book['id']
                buttons.append(button2)
                item1['buttons'] = buttons

                items.append(item1)

                if i == 10:
                    break

            carousel_itemCard['carousel']['items'] = items
            simpleText['simpleText']['text'] = '취향을 분석해 봤어요 어때요 잘했나요??'

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

        return responseBody
