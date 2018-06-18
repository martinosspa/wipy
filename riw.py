from urllib.request import urlopen
import json
def request_all_items(isShort=False):
    if isShort:
        return json.loads(urlopen("https://api.warframe.market/v1/items").read())["payload"]["items"]["en"]
    else:
        return json.loads(urlopen("https://api.warframe.market/v1/items").read())

def request_item(item_name, order_type):
    html = urlopen("https://api.warframe.market/v1/items/{}/orders".format(item_name))
    data = json.loads(html.read())
    buyers = []
    prices = []
    buyer_name = ""
    buyer_region = ""
    for order in data["payload"]["orders"]:
        if order["order_type"] == order_type and order["user"]["status"] == "ingame":
            buyers.append(order)

    for buyer in buyers:
        prices.append(buyer["platinum"])
    if not prices:
        return {"isEmpty": True}
    else:
        if order_type == "buy":
            price = max(prices)
        elif order_type == "sell":
            price = min(prices)

        for buyer in buyers:
            if buyer["platinum"] == price:
                buyer_name = buyer["user"]["ingame_name"]
                buyer_region = buyer["region"]
        return {"isEmpty": False, "price":price, "name":buyer_name, "region":buyer_region}

def request_mod(mod_name, order_type, mod_rank):
    html = urlopen("https://api.warframe.market/v1/items/{}/orders".format(mod_name))
    data = json.loads(html.read())
    buyers = []
    prices = []
    buyer_name = ""
    for order in data["payload"]["orders"]:
        if "mod_rank" in order:
            current_mod_rank = order["mod_rank"]
        else:
            current_mod_rank = 0

        if order["order_type"] == order_type and order["user"]["status"] == "ingame" and current_mod_rank == mod_rank:
            buyers.append(order)
    for buyer in buyers:
        prices.append(buyer["platinum"])

    if not prices:
        return {"isEmpty": True}
    else:
        if order_type == "buy":
            price = max(prices)
        elif order_type == "sell":
            price = min(prices)
        for buyer in buyers:
            if buyer["platinum"] == price:
                buyer_name = buyer["user"]["ingame_name"]
                buyer_region = buyer["region"]
        return {"isEmpty": False, "price":price, "name":buyer_name, "region":buyer_region}

def request_item_info(item_name):
    html = urlopen("https://api.warframe.market/v1/items/{}".format(item_name))
    data = json.loads(html.read())
    return data["payload"]["item"]["items_in_set"]

def request_tags_single(item_name):
    html = urlopen("https://api.warframe.market/v1/items/{}".format(item_name))
    data = json.loads(html.read())
    for item_in_set in data["payload"]["item"]["items_in_set"]:
        if item_in_set["url_name"] == item_name:
            return item_in_set["tags"]

def request_tags(item_name):
    html = urlopen("https://api.warframe.market/v1/items/{}".format(item_name))
    data = json.loads(html.read())
    all_tags = []
    for item_in_set in data["payload"]["item"]["items_in_set"]:
        all_tags = all_tags + item_in_set["tags"]
    return all_tags

def isInSet(item_name):
    return len(request_item_info(item_name)) > 1

def getSet(item_name):
    item_info = request_item_info(item_name)
    for item in item_info:
        if "set" in item["tags"]:
            return item["url_name"]
    return None
