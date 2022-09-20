from pprint import pprint


class Response:
    def __init__(self):
        self.responseBody = {
            "version": "2.0",
            "template": {
                "outputs": []
            }
        }
        self.simpleText = {
            "simpleText": {
                "text": ""
            }
        }
        self.itemList = {
            "title": "",
            "description": "",
            "extra": {
            }
        }
        self.button = {
            "label": "",
            "action": "",
            "extra": {
            }
        }
        self.item = {
            "imageTitle": {
                "title": "",
                "imageUrl": ""
            },
            "itemList": [
            ],
            "itemListAlignment": "right",
            "buttons": [
            ]
        }
        self.carousel_itemCard = {
            "carousel": {
                "type": "itemCard",
                "items": [
                ]
            }
        }
        self.quickReply = {
            "action": "",
            "label": "",
            "extra": {
            }
        }
        self.itemCard = {
            "itemCard": {
                "imageTitle": {
                    "title": "",
                    "imageUrl": "",
                },
                "itemList": [
                ],
                "itemListAlignment": "right",
                "buttons": [
                ],
                "buttonLayout": "horizontal"
            }
        }
        self.carousel_listCard = {
            "carousel": {
                "type": "listCard",
                "items": [
                ]
            }
        }
        self.listItem = {
            "header": {
                "title": ""
            },
            "items": [
            ],
            "buttons": [
            ]
        }
        self.basicCard = {
            "basicCard": {
                "title": "",
                "description": "",
                "thumbnail": {
                    "imageUrl": ""
                }
            }
        }


class BlockID:
    def __init__(self):
        self.home = '62c9057128d63278024c16a2'
        self.list_menu = '62c90931903c8b5a8004448c'
        self.recom_menu = '62c7e7ade262a941bbdca4ea'
        self.search_menu = '62dd372c28d63278024d6104'
        self.save_want = '62dd402d903c8b5a80058543'
        self.save_review = '62dd404bc7d05102c2ccffb4'
        self.howto = '62dd3d75c7d05102c2ccffa4'
        self.save_menu = '62e28d6e0326e262b80b4183'
        self.list_want = '62bf084750b23b1e3a6e2655'
        self.list_review = '62bef98450b23b1e3a6e25ba'
        self.view_review = '62e465e7fa3e133a938dd091'
        self.edit_menu = '62e5e6e2331a5d11fe4c3da2'
        self.delete_book = '62e5f4abfa3e133a938dd65e'


if __name__ == "__main__":
    response = Response()
    itemList = response.itemList
    listItem = response.listItem
    button = response.button
    carousel_listCard = response.carousel_listCard
    simpleText = response.simpleText
    responseBody = response.responseBody

    itemLists = []
    itemList1 = itemList.copy()
    itemList1['title'] = '경영의 모험'
    itemList1['description'] = '존 브룩스'
    itemList1['imageUrl'] = 'http://이미지 주소'
    itemList1['action'] = 'block'
    itemList1['blockId'] = '48198249018209'
    extra = {'isbn': '1232131'}
    itemList1['extra'] = extra
    itemLists.append(itemList1)
    listItem['itemList'] = itemLists

    listItems = []
    listItem1 = listItem.copy()
    listItem1['header']['title'] = '읽고 싶은 책 목록1'
    listItems.append(listItem1)
    carousel_listCard['carousel']['items'] = listItems

    simpleText['simpleText']['text'] = '고심해서 고른 책이에요 어떠세요??'
    outputs = [simpleText, carousel_listCard]
    responseBody['template']['outputs'] = outputs

    pprint(responseBody, depth=10, indent=2, sort_dicts=False)
