from flask_restful import Resource, reqparse
from models.book import BookModel
from models.book_list import BookListModel
from models.user import UserModel
from resources.response import Response, BlockID


class BookList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userRequest', type=dict, required=True)

    def check_id(self, status):
        data = BookList.parser.parse_args()
        user_id = data['userRequest']['user']['id']
        checking = UserModel.find_by_username(user_id)
        return checking

    def post(self, status):
        data = BookList.parser.parse_args()
        print(data)
        user_id = data['userRequest']['user']['id']

        # 리스트 확인시 유저가 없을 경우 유저 등록
        if BookList.check_id(self, status) == None:
            user = UserModel(user_id, user_id)
            user.save_to_db()
            print("id를 db에 저장했습니다.")

        response = Response()
        blockid = BlockID()
        itemList = response.itemList
        listItem = response.listItem
        carousel_listCard = response.carousel_listCard
        simpleText = response.simpleText
        responseBody = response.responseBody
        listItems = []
        itemLists = []

        # 저장한 책이 존재하면
        books = BookListModel.find_by_status(user_id, status)
        cnt = 1
        if books:
            for book in books:
                book_info = BookModel.find_by_isbn(book.json()['isbn']).json()
                itemList1 = itemList.copy()
                itemList1['title'] = book_info['title']
                itemList1['description'] = book_info['author']
                itemList1['imageUrl'] = book_info['img']
                itemList1['action'] = 'block'
                itemList1['blockId'] = blockid.save_review
                extra = {'isbn': book_info['isbn']}
                itemList1['extra'] = extra
                itemLists.append(itemList1)

                if cnt % 5 == 0:
                    listItem1 = listItem.copy()
                    listItem1['items'] = itemLists
                    if status == '0':
                        listItem1['header']['title'] = f'읽고 싶은 책 목록{cnt//5}'
                    else:
                        listItem1['header']['title'] = f'읽은 책 목록{cnt//5}'
                    listItems.append(listItem1)
                    itemLists = []
                    if cnt == 25:
                        break
                cnt += 1

            if cnt < 21:
                listItem1 = listItem.copy()
                listItem1['items'] = itemLists
                if status == '0':
                    listItem1['header']['title'] = f'읽고 싶은 책 목록{cnt//5}'
                else:
                    listItem1['header']['title'] = f'읽은 책 목록{cnt//5}'
                listItems.append(listItem1)
                itemLists = []

            carousel_listCard['carousel']['items'] = listItems
            simpleText['simpleText']['text'] = '읽고 싶던 책을 읽으며\n기분 전환을 해보세요!'
            outputs = [simpleText, carousel_listCard]
            responseBody['template']['outputs'] = outputs
        else:
            simpleText['simpleText']['text'] = '아직 담은 책이 없네요.\n재밌는 책을 추천받아 보세요!'
            outputs = [simpleText, carousel_listCard]
            responseBody['template']['outputs'] = outputs
        return responseBody
