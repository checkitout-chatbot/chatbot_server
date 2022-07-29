from flask_restful import Resource, reqparse
from models.book import BookModel
from models.book_list import BookListModel
from resources.response import Response, BlockID
from copy import deepcopy
import re

# extra value 값으로 isbn을 가져와 읽고 싶은 책 저장


class SaveWanted(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=dict, required=True)
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = SaveWanted.parser.parse_args()
        print(data)
        isbn = data['action']['clientExtra']['isbn']
        user_id = data['userRequest']['user']['id']

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
            print(e)
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
        print(data)

        isbn = data['action']['clientExtra']['isbn']
        user_id = data['userRequest']['user']['id']
        rate = data['action']['params']['rate']
        rate = re.sub("[^0-9]", "", rate)
        review = data['action']['params']['review']

        response = Response()
        blockid = BlockID()
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply

        try:
            # 리스트에 등록된 책인지 확인
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
                booklist = BookListModel(isbn, user_id, 1, review, int(rate))
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

        except Exception:
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
