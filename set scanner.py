import riw
import json
from urllib.request import urlopen
def main():
    all_items = riw.request_all_items(isShort=True)
    scanned_items = []
    for item in all_items:
        item_url_name = "mesa%E2%80%99s_waltz" if item["url_name"] == "mesa’s_waltz" else item["url_name"].encode("ascii", "ignore").decode("ascii")
        item_name = item["item_name"]
        if riw.isInSet(item_url_name):
            items_in_sets = riw.request_item_info(item_url_name)
            #print(type(items_in_sets))
            #items_in_sets list
            for item_in_set in items_in_sets:
                #item_tags = riw.request_tags(item_in_set["url_name"])
                #print(item_in_set["url_name"])

                item_tags = riw.request_tags(item_in_set["url_name"])

if __name__ == "__main__":
    main()
