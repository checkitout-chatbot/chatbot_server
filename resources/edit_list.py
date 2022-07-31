from flask_restful import Resource, reqparse
from models.book_list import BookListModel
from resources.response import Response, BlockID
from resources.user import UserRegister
from copy import deepcopy
import re
import log


class SaveWanted(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveWanted.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        user_id = data['userRequest']['user']['id']
        UserRegister.check_id(user_id, user_id)

        isbn = data['action']['clientExtra']['isbn']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        try:
            # 리스트에 등록된 책인지 확인
            check_booklist = BookListModel.find_by_book(isbn, user_id)
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
                booklist = BookListModel(isbn, user_id, 0, None, None)
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
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveReview.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        user_id = data['userRequest']['user']['id']
        UserRegister.check_id(user_id, user_id)

        isbn = data['action']['clientExtra']['isbn']
        rate = data['action']['params']['rate']
        rate = re.sub("[^0-9]", "", rate)
        review = data['action']['params']['review']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        try:
            # 읽은 책 목록에 있는지 확인
            check_booklist = BookListModel.find_by_status_isbn(
                isbn, user_id, 1)
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
                quickReply3['blockId'] = blockid.list_review
                quickReplies.append(quickReply3)
                responseBody['template']['quickReplies'] = quickReplies

            else:
                booklist = BookListModel.find_by_status_isbn(
                    isbn, user_id, 0)

                # 읽고 싶은 책 목록에 있는지 확인
                # 있으면 UPDATE 없으면 INSERT
                if booklist:
                    booklist.status = 1
                    booklist.review = review
                    booklist.rate = int(rate)
                else:
                    booklist = BookListModel(
                        isbn, user_id, 1, review, int(rate))
                booklist.save_to_db()

                simpleText['simpleText']['text'] = '읽은 책 목록에 책을 저장했습니다.\n완독하시다니 정말 대단하신걸요?'
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


class ViewReview(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = ViewReview.parser.parse_args()
        log.info_log(data)

        isbn = data['action']['clientExtra']['isbn']
        user_id = data['userRequest']['user']['id']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        # 리스트에 등록된 책인지 확인
        book_review = BookListModel.find_by_status_isbn(
            isbn, user_id, 1).json()

        simpleText['simpleText']['text'] = f"평점: {book_review['rate']}\n리뷰: {book_review['review']}"
        outputs = [simpleText]
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
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveMenu.parser.parse_args()
        log.info_log(data)

        isbn = data['action']['clientExtra']['isbn']

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
        quickReply2['extra']['isbn'] = isbn
        quickReplies.append(quickReply2)

        quickReply3 = deepcopy(quickReply)
        quickReply3['action'] = 'block'
        quickReply3['label'] = '🙉 읽은 책으로'
        quickReply3['blockId'] = blockid.save_review
        quickReply3['extra']['isbn'] = isbn
        quickReplies.append(quickReply3)
        responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class EditMenu(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = EditMenu.parser.parse_args()
        log.info_log(data)

        isbn = data['action']['clientExtra']['isbn']

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
        quickReply2['extra']['isbn'] = isbn
        quickReplies.append(quickReply2)

        quickReply3 = deepcopy(quickReply)
        quickReply3['action'] = 'block'
        quickReply3['label'] = '리뷰(수정)하기'
        quickReply3['blockId'] = blockid.save_review
        quickReply3['extra']['isbn'] = isbn
        quickReplies.append(quickReply3)
        responseBody['template']['quickReplies'] = quickReplies

        return responseBody


class DeleteBook(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveReview.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        user_id = data['userRequest']['user']['id']
        UserRegister.check_id(user_id, user_id)

        isbn = data['action']['clientExtra']['isbn']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        booklist = BookListModel.find_by_status(isbn, user_id)
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

        responseBody['template']['quickReplies'] = quickReplies

        return responseBody
