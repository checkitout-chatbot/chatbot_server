from flask_restful import Resource, reqparse
from models.book_list import BookListModel
from models.user import UserModel
from models.book import BookModel
from resources.response import Response, BlockID
from resources.user import UserRegister
from copy import deepcopy
import re
import log
from datetime import datetime


class SaveWanted(Resource):
    """
    읽고 싶은 책으로 저장
    """
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveWanted.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        username = data['userRequest']['user']['id']
        UserRegister.check_id(username=username)
        user_id = UserModel.find_by_username(username).json()['id']

        # extra의 책 id 값 받아오기
        book_id = data['action']['clientExtra']['book_id']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        try:
            # 리스트에 등록된 책인지 확인
            check_booklist = BookListModel.find_by_user_book(
                user_id=user_id, book_id=book_id)
            if check_booklist != None:
                simpleText['simpleText']['text'] = '이미 등록된 책입니다.'
                outputs = [simpleText]
                responseBody['template']['outputs'] = outputs

                quickReplies = []
                quickReply1 = deepcopy(quickReply)
                quickReply1['action'] = 'block'
                quickReply1['label'] = '뒤로가기'
                quickReply1['blockId'] = blockid.list_menu
                quickReplies.append(quickReply1)

                quickReply2 = deepcopy(quickReply)
                quickReply2['action'] = 'block'
                quickReply2['label'] = '도움말'
                quickReply2['blockId'] = blockid.howto
                quickReplies.append(quickReply2)

                quickReply3 = deepcopy(quickReply)
                quickReply3['action'] = 'block'
                quickReply3['label'] = '목록 확인하기'
                quickReply3['blockId'] = blockid.list_want
                quickReplies.append(quickReply3)
                responseBody['template']['quickReplies'] = quickReplies

            else:
                now = datetime.now()
                booklist = BookListModel(
                    user_id=user_id, book_id=book_id, status=0, created_dt=now)
                booklist.save_to_db()

                simpleText['simpleText']['text'] = '읽고 싶은 책 목록에 책을 저장했습니다.\n즐거운 독서 라이프 되세요~'
                outputs = [simpleText]
                responseBody['template']['outputs'] = outputs

                quickReplies = []
                quickReply1 = deepcopy(quickReply)
                quickReply1['action'] = 'block'
                quickReply1['label'] = '뒤로가기'
                quickReply1['blockId'] = blockid.list_menu
                quickReplies.append(quickReply1)

                quickReply2 = deepcopy(quickReply)
                quickReply2['action'] = 'block'
                quickReply2['label'] = '도움말'
                quickReply2['blockId'] = blockid.howto
                quickReplies.append(quickReply2)

                quickReply3 = deepcopy(quickReply)
                quickReply3['action'] = 'block'
                quickReply3['label'] = '목록 확인하기'
                quickReply3['blockId'] = blockid.list_want
                quickReplies.append(quickReply3)
                responseBody['template']['quickReplies'] = quickReplies

        except Exception as e:
            log.error_log(e)

            simpleText['simpleText']['text'] = '죄송합니다. 오류가 발생했습니다. 탈출해 주세요!'
            outputs = [simpleText]
            responseBody['template']['outputs'] = outputs

            quickReplies = []
            quickReply1 = deepcopy(quickReply)
            quickReply1['action'] = 'block'
            quickReply1['label'] = '뒤로가기'
            quickReply1['blockId'] = blockid.list_menu
            quickReplies.append(quickReply1)

            quickReply2 = deepcopy(quickReply)
            quickReply2['action'] = 'block'
            quickReply2['label'] = '도움말'
            quickReply2['blockId'] = blockid.howto
            quickReplies.append(quickReply2)
            responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class SaveReview(Resource):
    """
    읽은 책 목록으로 저장
    """
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveReview.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        username = data['userRequest']['user']['id']
        UserRegister.check_id(username=username)
        user_id = UserModel.find_by_username(username).json()['id']

        # extra의 책 id 값 받아오기
        book_id = data['action']['clientExtra']['book_id']
        rate = data['action']['params']['rate']
        rate = re.sub("[^0-9]", "", rate)
        review = data['action']['params']['review']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        now = datetime.now()
        booklist = BookListModel.find_by_user_book(
            user_id=user_id, book_id=book_id)
        # 책 목록 있으면 UPDATE 없으면 INSERT
        if booklist:
            booklist.status = 1
            booklist.review = review
            booklist.rate = int(rate)
            booklist.modified_dt = now
        else:
            booklist = BookListModel(user_id=user_id, book_id=book_id, status=1,
                                     review=review, rate=rate, created_dt=now)
        booklist.save_to_db()

        simpleText['simpleText']['text'] = '저장을 완료했습니다!'
        outputs = [simpleText]
        responseBody['template']['outputs'] = outputs

        quickReplies = []
        quickReply1 = deepcopy(quickReply)
        quickReply1['action'] = 'block'
        quickReply1['label'] = '뒤로가기'
        quickReply1['blockId'] = blockid.list_menu
        quickReplies.append(quickReply1)

        quickReply2 = deepcopy(quickReply)
        quickReply2['action'] = 'block'
        quickReply2['label'] = '도움말'
        quickReply2['blockId'] = blockid.howto
        quickReplies.append(quickReply2)

        quickReply3 = deepcopy(quickReply)
        quickReply3['action'] = 'block'
        quickReply3['label'] = '목록 확인하기'
        quickReply3['blockId'] = blockid.list_review
        quickReplies.append(quickReply3)
        responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class ViewReview(Resource):
    """
    저장한 리뷰 보기
    """
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = ViewReview.parser.parse_args()
        log.info_log(data)

        username = data['userRequest']['user']['id']
        user_id = UserModel.find_by_username(username).json()['id']

        # extra의 책 id 값 받아오기
        book_id = data['action']['clientExtra']['book_id']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        basicCard = response.basicCard
        responseBody = response.responseBody
        quickReply = response.quickReply

        # 리스트에 등록된 책인지 확인
        book = BookModel.find_by_id(book_id).json()
        book_review = BookListModel.find_by_user_book(
            user_id=user_id, book_id=book_id).json()
        if book_review['status'] == 0:
            simpleText['simpleText']['text'] = "아직 남긴 평점이 없습니다. 평점을 남겨 보세요!"
        else:
            basicCard['basicCard']['title'] = book['title']
            basicCard['basicCard']['description'] = f"평점: {book_review['rate']}\n리뷰: {book_review['review']}"
            basicCard['basicCard']['thumbnail']['imageUrl'] = book['img']
        outputs = [basicCard]
        responseBody['template']['outputs'] = outputs

        quickReplies = []
        quickReply1 = deepcopy(quickReply)
        quickReply1['action'] = 'block'
        quickReply1['label'] = '뒤로가기'
        quickReply1['blockId'] = blockid.list_review
        quickReplies.append(quickReply1)

        quickReply2 = deepcopy(quickReply)
        quickReply2['action'] = 'block'
        quickReply2['label'] = '도움말'
        quickReply2['blockId'] = blockid.howto
        quickReplies.append(quickReply2)

        responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class SaveMenu(Resource):
    """
    저장 메뉴 출력
    """
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveMenu.parser.parse_args()
        log.info_log(data)

        book_id = data['action']['clientExtra']['book_id']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        # 리스트에 등록된 책인지 확인
        simpleText['simpleText']['text'] = '어디로 저장할까요??'
        outputs = [simpleText]
        responseBody['template']['outputs'] = outputs

        quickReplies = []
        quickReply1 = deepcopy(quickReply)
        quickReply1['action'] = 'block'
        quickReply1['label'] = '뒤로가기'
        quickReply1['blockId'] = blockid.list_menu
        quickReplies.append(quickReply1)

        quickReply2 = deepcopy(quickReply)
        quickReply2['action'] = 'block'
        quickReply2['label'] = '🙈 읽고 싶은 책으로'
        quickReply2['blockId'] = blockid.save_want
        quickReply2['extra']['book_id'] = book_id
        quickReplies.append(quickReply2)

        quickReply3 = deepcopy(quickReply)
        quickReply3['action'] = 'block'
        quickReply3['label'] = '🙉 읽은 책으로'
        quickReply3['blockId'] = blockid.save_review
        quickReply3['extra']['book_id'] = book_id
        quickReplies.append(quickReply3)
        responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class EditMenu(Resource):
    """
    읽고 싶은 책 목록에서 책 item을 누르면 편집할 수 있는 메뉴
    """
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = EditMenu.parser.parse_args()
        log.info_log(data)

        book_id = data['action']['clientExtra']['book_id']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        # 리스트에 등록된 책인지 확인
        simpleText['simpleText']['text'] = '이 책을 어떻게 할까요?'
        outputs = [simpleText]
        responseBody['template']['outputs'] = outputs

        quickReplies = []
        quickReply1 = deepcopy(quickReply)
        quickReply1['action'] = 'block'
        quickReply1['label'] = '뒤로가기'
        quickReply1['blockId'] = blockid.list_menu
        quickReplies.append(quickReply1)

        quickReply2 = deepcopy(quickReply)
        quickReply2['action'] = 'block'
        quickReply2['label'] = '삭제하기'
        quickReply2['blockId'] = blockid.delete_book
        quickReply2['extra']['book_id'] = book_id
        quickReplies.append(quickReply2)

        quickReply3 = deepcopy(quickReply)
        quickReply3['action'] = 'block'
        quickReply3['label'] = '리뷰(수정)하기'
        quickReply3['blockId'] = blockid.save_review
        quickReply3['extra']['book_id'] = book_id
        quickReplies.append(quickReply3)

        quickReply4 = deepcopy(quickReply)
        quickReply4['action'] = 'block'
        quickReply4['label'] = '리뷰보기'
        quickReply4['blockId'] = blockid.view_review
        quickReply4['extra']['book_id'] = book_id
        quickReplies.append(quickReply4)
        responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class DeleteBook(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        """
        해당 책 삭제하기
        """
        data = DeleteBook.parser.parse_args()
        log.info_log(data)

        username = data['userRequest']['user']['id']
        user_id = UserModel.find_by_username(username).json()['id']
        book_id = data['action']['clientExtra']['book_id']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        booklist = BookListModel.find_by_user_book(
            user_id=user_id, book_id=book_id)
        booklist.delete_from_db()

        simpleText['simpleText']['text'] = '해당 책을 삭제했습니다.'
        outputs = [simpleText]
        responseBody['template']['outputs'] = outputs

        quickReplies = []
        quickReply1 = deepcopy(quickReply)
        quickReply1['action'] = 'block'
        quickReply1['label'] = '뒤로가기'
        quickReply1['blockId'] = blockid.list_menu
        quickReplies.append(quickReply1)

        quickReply2 = deepcopy(quickReply)
        quickReply2['action'] = 'block'
        quickReply2['label'] = '도움말'
        quickReply2['blockId'] = blockid.howto
        quickReplies.append(quickReply2)

        quickReply3 = deepcopy(quickReply)
        quickReply3['action'] = 'block'
        quickReply3['label'] = '읽고 싶은 책 목록'
        quickReply3['blockId'] = blockid.list_want
        quickReplies.append(quickReply3)

        quickReply4 = deepcopy(quickReply)
        quickReply4['action'] = 'block'
        quickReply4['label'] = '읽은 책 목록'
        quickReply4['blockId'] = blockid.list_review
        quickReplies.append(quickReply4)

        responseBody['template']['quickReplies'] = quickReplies

        return responseBody
