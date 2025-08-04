import requests
import json
from typing import Optional
import math

headers = {"User-Agent": "Old School GE margin checker test - @Vegimit on Discord"}
tax = 0.98

class RsItem:
    def __init__(self, name=None, item_id=None, buy_limit=None, price_high=None, price_low=None, volume_high_price=None, volume_low_price=None, high_alch=None, members=None, margin=None, roi=None, daily_profit=None, cost_to_buy=None):

        self.name = name
        self.item_id = item_id
        self.buy_limit = buy_limit
        self.price_high = price_high
        self.price_low = price_low
        self.volume_high_price = volume_high_price
        self.volume_low_price = volume_low_price
        self.high_alch = high_alch
        self.members = members
        self.margin = margin
        self.roi = roi
        self.daily_profit = daily_profit
        self.cost_to_buy = cost_to_buy

    def to_dict(self):
        return{
            "name": self.name,
            "item_id": self.item_id,
            "buy_limit": self.buy_limit,
            "price_high": self.price_high,
            "price_low": self.price_low,
            "volume_high_price": self.volume_high_price,
            "volume_low_price": self.volume_low_price,
            "high_alch": self.high_alch,
            "members": self.members,
            "margin": self.margin,
            "roi": self.roi,
            "daily_profit": self.daily_profit,
            "cost_to_buy": self.cost_to_buy
        }


item_data = []
top10 = []

#requests item id, instant sell price high and low values in gp
response = requests.get('https://prices.runescape.wiki/api/v1/osrs/5m', headers=headers)

if response.status_code == 200:
    # Convert JSON response to dictionary
    pull = response.json().get("data", {}) # stores the data from the api in an accessible variable
    for key, value in pull.items(): # formats pull data into local variables
        int_key = int(key) # converts numeric strings to true integers
        item_data.append(RsItem(item_id=[int_key], price_high=value.get("avgHighPrice"), price_low=value.get("avgLowPrice"), volume_high_price=value.get("highPriceVolume"), volume_low_price=value.get("lowPriceVolume")))

    for RsItem in item_data:
        RsItem.item_id = RsItem.item_id[0] # reformats dictionary to ignore the initial redundant key from api

    #requests static information about the items
    response = requests.get('https://prices.runescape.wiki/api/v1/osrs/mapping', headers=headers)
    if response.status_code == 200:
        # Convert JSON response to dictionary
        pull = response.json()  # stores the data from the api in an accessible variable
        # check item id of stored items and fill in missing data to the dictionary
        for item in pull:
            item_id = item.get("id")
            i=0
            for RsItem in item_data:
                if RsItem.item_id == item_id:
                    item_data[i].name = item.get("name")
                    item_data[i].buy_limit = item.get("limit")
                    item_data[i].high_alch = item.get("highalch")
                    item_data[i].members = item.get("members")
                i = i + 1

    for RsItem in item_data:
        RsItem.margin = (RsItem.price_high or 1) - (RsItem.price_low or 1) #gets price margin
        # if there's more supply than buy limit
        if (RsItem.volume_low_price or 1) > (RsItem.buy_limit or 300000):
            # cost is capped by buy limit
            # if demand limits profit
            if(RsItem.volume_high_price or 1) < (RsItem.volume_low_price or 1):
                # profit is capped by demand
                RsItem.cost_to_buy = (RsItem.price_low or 1) * (RsItem.volume_high_price or 1)
                RsItem.daily_profit = RsItem.margin * (RsItem.volume_high_price or 1)
            # profit is not capped by demand
            else:
                RsItem.cost_to_buy = (RsItem.price_low or 1) * (RsItem.buy_limit or 300000)
                RsItem.daily_profit = RsItem.margin * (RsItem.buy_limit or 300000)

        # if there's less supply than buy limit
        else:
            # cost is capped by supply
            # if demand limits profit
            if (RsItem.volume_high_price or 1) < (RsItem.volume_low_price or 1):
                # profit is capped by demand
                RsItem.cost_to_buy = (RsItem.price_low or 1) * (RsItem.volume_high_price or 1)
                RsItem.daily_profit = RsItem.margin * (RsItem.volume_high_price or 1)
                # profit is not capped by demand
            else:
                RsItem.cost_to_buy = (RsItem.price_low or 1) * (RsItem.volume_low_price or 1)
                RsItem.daily_profit = RsItem.margin * (RsItem.volume_low_price or 1)

        # if item will be taxed
        if (RsItem.price_high or 1) >= 50:
            RsItem.daily_profit = RsItem.daily_profit * tax

        # get return on investment as %
        RsItem.roi = RsItem.daily_profit / RsItem.cost_to_buy * 100

        # if item is affordable and has enough supply
        if (RsItem.cost_to_buy < 1000000) & (RsItem.volume_low_price > 3) & (RsItem.volume_high_price > 3):
            # if top10 is empty, automatically include item
            if range(len(top10)) == 0:
                top10.append(RsItem)
            # if top10 is not empty, check if the item is more profitable than other items in top10
            else:
                insertValue = 0
                for i in range(len(top10)):
                    if top10[i].daily_profit < RsItem.daily_profit:
                        insertValue = insertValue + 1
                    else:
                        break
                if (insertValue > 0 or len(top10)) < 10:
                    top10.insert(insertValue, RsItem)
                if len(top10) > 10:
                    top10.pop(0)



for RsItem in top10:
    print(RsItem.name,"\n","Buy Price: ",RsItem.price_low,"\n","Sell Price: ",RsItem.price_high,"\n","Low Price Volume (5min): ",RsItem.volume_low_price,"\n","High Price Volume (5min)",RsItem.volume_high_price,"\n","Daily Profit: ",RsItem.daily_profit,"\n","ROI: ",RsItem.roi, "%")

if input("Press Enter to exit"):
    exit()




