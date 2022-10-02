from copy import deepcopy
from flask_restful import Resource, reqparse
from models.book import BookModel
from models.user import UserModel
from models.music import MusicModel
from models.user_similar import UserSimilarModel
from models.book_similar import BookSimilarModel
from models.music_similar import MusicSimilarModel
from models.book_list import BookListModel
from models.movie import MovieModel
from resources.user import UserRegister
from resources.search import Searching
from resources.response import Response, BlockID
import log
from datetime import datetime
import random


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
    parser.add_argument('action', type=dict)

    def post(self, category):  # category 변수 추가
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

        sense_books = []
        # 주제별로 도서 목록 다르게 출력
        if category == 'love':
            sense_books = BookModel.find_by_sense('love')
        elif category == 'killingtime':
            sense_books = BookModel.find_by_sense('killingtime')
        elif category == 'healing':
            sense_books = BookModel.find_by_sense('healing')
        elif category == 'improvement':
            sense_books = BookModel.find_by_sense('improvement')

        sense_book = None
        books = []
        # 주제별 도서 목록 중 랜덤으로 5개 저장
        for i in range(5):
            randint = random.randint(0, len(sense_books)-1)
            sense_book = sense_books[randint].json()
            books.append(sense_book)

        # JSON 포맷
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

            if i == 6:
                break

        carousel_itemCard['carousel']['items'] = items
        simpleText['simpleText']['text'] = '이럴 땐, 이런 책!'

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

        # 해당 유저의 읽은 책을 가져옴
        check_read_list = BookListModel.find_by_user_status(
            user_id=user_id, status=1)
        if len(check_read_list) < 6:  # 평점을 남긴 책이 5권 이하일 경우
            # 해당 유저의 책 전부를 가져옴
            check_book_list = BookListModel.find_by_user(user_id=user_id)
            if len(check_book_list) == 0:  # 저장한 책이 아예 없을 경우
                simpleText['simpleText']['text'] = '담긴 책이 하나도 없어요! 책을 추천 받아 내 서재에 저장해 보세요!'

                outputs = [simpleText]
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
            else:
                rec_books = []
                cnt = 0  # 무한루프 방지용 최대 5번 검색
                while len(rec_books) == 0:
                    # 저장한 책 중 랜덤으로 한 권 뽑기
                    random_num = random.randint(0, len(check_book_list)-1)
                    check_book = check_book_list[random_num].json()
                    print(f'랜덤으로 한 권 뽑은 책: {check_book}')

                    # 뽑은 책과 유사한 책 가져오기
                    rec_books = BookSimilarModel.find_by_book_id(
                        check_book['book_id'])
                    print(f'뽑은 책과 유사한 책들: {rec_books}')
                    if cnt == 5:
                        break
                    cnt += 1

                items = []
                for i, rec_book in enumerate(rec_books):
                    book_id = rec_book.json()['book_similar_id']
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

        else:
            rec_books = UserSimilarModel.find_by_user(user_id)
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


class Movie(Resource):  # 책과 비슷한 영화 추천
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
            input_movies = search.search_keywords(input_title, 30)

            # 추천 책이 나올 때까지 검색
            similar_movies = []
            for i in input_movies.keys():
                try:
                    book = MovieModel.find_by_isbn(
                        input_movies[i]['isbn']).json()
                    similar_movies = BookSimilarModel.find_by_book_id(
                        book['id'])
                    break
                except:
                    pass

            # 유사도 id값들로 책 찾아 리스트로 저장
            movies = []
            for similar_movie in similar_movies:
                similar_movie = similar_movie.json()
                movies.append(MovieModel.find_by_id(
                    similar_movie['book_similar_id']).json())

            items = []
            for i, movie in enumerate(movies):
                item1 = deepcopy(item)
                item1['imageTitle']['title'] = movie['title']
                item1['imageTitle']['imageUrl'] = movie['img']

                itemLists = []
                itemList1 = deepcopy(itemList)
                itemList1['title'] = '지은이'
                itemList1['description'] = movie['author']
                itemLists.append(itemList1)

                itemList2 = deepcopy(itemList)
                itemList2['title'] = '출판사'
                itemList2['description'] = movie['publisher']
                itemLists.append(itemList2)

                itemList3 = deepcopy(itemList)
                itemList3['title'] = '출판일'
                itemList3['description'] = str(movie['pubDate'])
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
                button2['extra']['book_id'] = movie['id']
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


class Music(Resource):  # 책과 비슷한 음악 추천
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict)

    def post(self):
        data = Music.parser.parse_args()
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
            # 알라딘 책 검색으로 제목입력하여 ISBN 추출
            input_title = data['action']['params']['title']
            search = Searching()
            input_books = search.search_keywords(input_title, 30)
            # 여기서 출력값 비어 있음
            # print(input_title)
            # print(input_books)

            # 해당 책이 나올 때까지 검색
            similar_musics = []
            for i in input_books.keys():
                try:
                    book = BookModel.find_by_isbn(
                        input_books[i]['isbn']).json()
                    similar_musics = MusicSimilarModel.find_by_book_id(
                        book['id']+6526)
                    break
                except:
                    pass
            print(similar_musics)


            # 유사도 id값들로 책 찾아 리스트로 저장
            musics = []
            for similar_music in similar_musics:
                similar_music = similar_music.json()
                print(similar_music)
                musics.append(MusicModel.find_by_id(
                    similar_music['music_id']).json())
            
            print(musics)

            items = []
            for i, music in enumerate(musics):
                item1 = deepcopy(item)
                item1['imageTitle']['title'] = music['title']
                # item1['imageTitle']['imageUrl'] = music['img']
                item1['imageTitle']['imageUrl'] = "https://cdnimg.melon.co.kr/cm2/album/images/110/63/665/11063665_20220926110109_500.jpg"

                itemLists = []
                itemList1 = deepcopy(itemList)
                itemList1['title'] = '가수'
                itemList1['description'] = music['singer']
                itemLists.append(itemList1)

                itemList2 = deepcopy(itemList)
                itemList2['title'] = '장르'
                itemList2['description'] = music['genre']
                itemLists.append(itemList2)

                # itemList3 = deepcopy(itemList)
                # itemList3['title'] = '가사'
                # itemList3['description'] = music['lyric']
                # itemLists.append(itemList3)
                # item1['itemList'] = itemLists

                buttons = []
                button1 = deepcopy(button)
                button1['action'] = 'webLink'
                button1['label'] = '책 정보'
                # f"https://www.melon.com/song/detail.htm?songId={music['melon_music_code']}" 
                melon_url = f"https://www.melon.com/song/detail.htm?songId={music['melon_music_code']}"
                button1['webLinkUrl'] = melon_url
                buttons.append(button1)

                items.append(item1)

                if i == 5:
                    break

            carousel_itemCard['carousel']['items'] = items
            simpleText['simpleText']['text'] = '이 노래와 함께 들어보세요 🎧 어떠세요??'

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
   