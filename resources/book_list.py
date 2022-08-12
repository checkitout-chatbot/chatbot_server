from copy import deepcopy
from flask_restful import Resource, reqparse
from models.book import BookModel
from models.user import UserModel
from models.book_list import BookListModel
from resources.user import UserRegister
from resources.response import Response, BlockID
import log


class BookListWant(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        """
        읽고 싶은 책 리스트 출력
        """
        data = BookListWant.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        username = data['userRequest']['user']['id']
        UserRegister.check_id(username=username)
        user_id = UserModel.find_by_username(username).json()['id']

        response = Response()
        blockid = BlockID()
        itemList = response.itemList
        listItem = response.listItem
        carousel_listCard = response.carousel_listCard
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply
        listItems = []
        itemLists = []

        # 저장한 책이 존재하는지 확인
        books = BookListModel.find_by_status(user_id, 0)
        cnt = 0
        if books:
            for book in books:
                cnt += 1

                # book_list 테이블에서 book_id로 books 테이블의 책 데이터를 가져오기
                book_info = BookModel.find_by_id(book.json()['book_id']).json()
                itemList1 = deepcopy(itemList)
                itemList1['title'] = book_info['title']
                itemList1['description'] = book_info['author']
                itemList1['imageUrl'] = book_info['img']
                itemList1['action'] = 'block'
                itemList1['blockId'] = blockid.edit_menu
                # 해당 item을 누르면 book_id 넘기기
                itemList1['extra']['book_id'] = book_info['id']
                itemLists.append(itemList1)

                # 리스트형 아이템 최대 5개까지 출력
                if cnt % 5 == 0:
                    listItem1 = deepcopy(listItem)
                    listItem1['items'] = itemLists
                    listItem1['header']['title'] = f'읽고 싶은 책 목록'
                    listItems.append(listItem1)
                    itemLists = []
                    # 케로셀 리스트형 카드 최대 5개까지 출력
                    if cnt == 25:
                        break

            # for문에서는 5로 나눠질 때만 리스트를 만들기 때문에 추가 리스트 필요
            # 5 번째 리스트에서는 추가 필요x / 딱 맞을 때도 필요x
            if cnt < 25 and cnt % 5 != 0:
                listItem1 = deepcopy(listItem)
                listItem1['items'] = itemLists
                listItem1['header']['title'] = f'읽고 싶은 책 목록'
                listItems.append(listItem1)
                itemLists = []

            carousel_listCard['carousel']['items'] = listItems
            simpleText['simpleText']['text'] = '책을 누르면 목록에서 삭제하거나 리뷰를 남길 수 있어요!'
            outputs = [simpleText, carousel_listCard]
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

        else:
            simpleText['simpleText']['text'] = '아직 담은 책이 없네요.\n재밌는 책을 추천받아 보세요!'
            outputs = [simpleText, carousel_listCard]
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
            quickReply3['label'] = '추천 받기'
            quickReply3['blockId'] = blockid.recom_menu
            quickReplies.append(quickReply3)
            responseBody['template']['quickReplies'] = quickReplies

        return responseBody


# 읽은 책 리스트 보기
class BookListReview(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userRequest', type=dict, required=True)

    def post(self):
        data = BookListReview.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        username = data['userRequest']['user']['id']
        UserRegister.check_id(username=username)
        user_id = UserModel.find_by_username(username).json()['id']

        response = Response()
        blockid = BlockID()
        itemList = response.itemList
        listItem = response.listItem
        carousel_listCard = response.carousel_listCard
        simpleText = response.simpleText
        responseBody = response.responseBody
        quickReply = response.quickReply
        listItems = []
        itemLists = []

        # 저장한 책이 존재하면
        books = BookListModel.find_by_status(user_id, 1)
        cnt = 0
        if books:
            for book in books:
                cnt += 1

                book_info = BookModel.find_by_id(book.json()['book_id']).json()
                itemList1 = deepcopy(itemList)
                itemList1['title'] = book_info['title']
                itemList1['description'] = book_info['author']
                itemList1['imageUrl'] = book_info['img']
                itemList1['action'] = 'block'
                itemList1['blockId'] = blockid.edit_menu
                itemList1['extra']['book_id'] = book_info['id']
                itemLists.append(itemList1)

                # 리스트형 아이템 최대 5개까지 출력
                if cnt % 5 == 0:
                    listItem1 = deepcopy(listItem)
                    listItem1['items'] = itemLists
                    listItem1['header']['title'] = f'읽은 책 목록'
                    listItems.append(listItem1)
                    itemLists = []
                    # 케로셀 리스트형 카드 최대 5개까지 출력
                    if cnt == 25:
                        break

            # for문에서는 5로 나눠질 때만 리스트를 만들기 때문에 추가 리스트 필요
            # 5 번째 리스트에서는 추가 필요x / 딱 맞을 때도 필요x
            if cnt < 25 and cnt % 5 != 0:
                listItem1 = deepcopy(listItem)
                listItem1['items'] = itemLists
                listItem1['header']['title'] = f'읽은 책 목록'
                listItems.append(listItem1)
                itemLists = []

            carousel_listCard['carousel']['items'] = listItems
            simpleText['simpleText']['text'] = '책을 누르면 삭제하거나 남긴 리뷰를 볼 수 있어요!'
            outputs = [simpleText, carousel_listCard]
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

        else:
            simpleText['simpleText']['text'] = '아직 담은 책이 없네요.\n재밌는 책을 추천받아 보세요!'
            outputs = [simpleText, carousel_listCard]
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
            quickReply3['label'] = '추천 받기'
            quickReply3['blockId'] = blockid.recom_menu
            quickReplies.append(quickReply3)
            responseBody['template']['quickReplies'] = quickReplies

        return responseBody
