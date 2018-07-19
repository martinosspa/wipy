import riw
def main():
    items = ["Blind Rage", "Fleeting_Expertise", "Narrow_Minded", "Overextended", "Transient_Fortitude",
             "Critical Delay", "Heavy Caliber", "Vile Precision", "Tainted Mag", "Vile Acceleration", "Depleted Reload",
             "Burdened Magazine",
             "Vicious Spread", "Tainted Shell", "Frail Momentum", "Critical Deceleration", "Anemic Agility",
             "Creeping Bullseye", "Hollow Point", "Magnum Force", "Tainted Clip", "Spoiled Strike", "Corrupt Charge"]
    fixed_items = list(map(lambda string: string.lower().replace(" ", "_"), items))
    for item in fixed_items:
        info = riw.request_mod(item, "buy", 0)
        if info["isEmpty"]:
            print("no buyer for {}".format(item))
        else:
            price = info["price"]
            buyer_name = info["name"]
            print("{} buys {} for {} platinum".format(buyer_name, item, price))


if __name__ == "__main__":
    main()