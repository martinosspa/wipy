import riw
import json
# from urllib.request import urlopen
def main():
    all_items = riw.request_all_items(isShort=True)
    scanned_sets = []
    for item in all_items:
        item_url_name = "mesa%E2%80%99s_waltz" if item["url_name"] == "mesa’s_waltz" else item["url_name"].encode("ascii", "ignore").decode("ascii")
        item_name = item["item_name"]
        if riw.isInSet(item_url_name):
            set_name = riw.getSet(item["url_name"])
            if not set_name in scanned_sets:
                items_in_sets = riw.request_item_info(item_url_name)
                total_buy_price = 0
                total_sell_price = 0
                scanned_sets.append(set_name)
                for item_in_set in items_in_sets:
                    scanned_sets.append(item_in_set)
                    item_tags = riw.request_tags_single(item_in_set["url_name"])
                    if not "set" in item_tags:
                        # item_in_set is a part of the set
                        if not riw.request_item(item_in_set["url_name"], "sell")["isEmpty"]:
                            total_buy_price += riw.request_item(item_in_set["url_name"], "sell")["price"]
                    else:
                        # item_in_set is the set itself
                        if not riw.request_item(item_in_set["url_name"], "buy")["isEmpty"]:
                            total_sell_price = riw.request_item(item_in_set["url_name"], "buy")["price"]
                if total_buy_price < total_sell_price:
                    # got a set that is worth it
                    dif = total_sell_price - total_buy_price
                    print("{name} has {dif} plat profit".format(name=set_name, dif=total_sell_price-total_buy_price))
if __name__ == "__main__":
    main()