import sys
import pandas as pd
import requests
import json
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


ua = UserAgent()
headers_ = {"User-Agent": ua.random}


class Item:
    name = ""
    steam_price = 0
    steam_link = ""
    cs_money_price = 0
    cs_money_link = ""
    overstock_diff = ""
    steam_qty = 0

    def __init__(self, name_, s_price, s_link, cs_price, cs_link, over_diff, s_qty):
        self.name = name_
        self.steam_price = s_price
        self.steam_link = s_link
        self.cs_money_price = cs_price
        self.cs_money_link = cs_link
        self.overstock_diff = over_diff
        self.steam_qty = s_qty

    def s_cs_profit(self):
        return  self.cs_money_price * 0.9 - self.steam_price

    def cs_s_profit(self):
        return  self.steam_price * 0.87 - self.cs_money_price

    def s_cs_benefit(self):
        try:
            return ( self.cs_money_price * 0.9 / self.steam_price ) * 100 - 100
        except ZeroDivisionError:
            return None

    def cs_s_benefit(self):
        try:
            return ( self.steam_price * 0.87 / self.cs_money_price ) * 100 - 100
        except ZeroDivisionError:
            return None

    def print(self):
        print(f"Name: \033[1;35m{self.name}\033[0m\n"
              f"Steam price: \033[1;32m{self.steam_price} $\033[0m\n"
              f"Steam link: {self.steam_link}\n"
              f"CS.money price: \033[1;32m{self.cs_money_price} $\033[0m\n"
              f"CS.money link: {self.cs_money_link}\n",
              f"Steam Qty: \033[1;32m{self.steam_qty}\033[0m\n"
              if self.steam_qty >= 20 else
              f"Steam Qty: \033[1;31m{self.steam_qty}\033[0m\n",
              f"CS.money overstock difference: \033[1;32m{self.overstock_diff}\033[0m\n"
              if self.overstock_diff > 10 else
              f"CS.money overstock difference: \033[1;31m{self.overstock_diff}\033[0m\n",
              f"Steam -> CS.money profit: \033[1;32m{'%.2f' % self.s_cs_profit()} $\033[0m\n"
              if self.s_cs_profit() >= 0 else
              f"Steam -> CS.money profit: \033[1;31m{'%.2f' % self.s_cs_profit()} $\033[0m\n",
              f"CS.money -> Steam profit: \033[1;32m{'%.2f' % self.cs_s_profit()} $\033[0m\n"
              if self.cs_s_profit() >= 0 else
              f"CS.money -> Steam profit: \033[1;31m{'%.2f' % self.cs_s_profit()} $\033[0m\n",
              f"Steam -> CS.money benefit: \033[1;32m{'%.2f' % self.s_cs_benefit()} %\033[0m\n"
              if self.s_cs_benefit() >= 0 else
              f"Steam -> CS.money benefit: \033[1;31m{'%.2f' % self.s_cs_benefit()} %\033[0m\n",
              f"CS.money -> Steam benefit: \033[1;32m{'%.2f' % self.cs_s_benefit()} %\033[0m\n\n"
              if self.cs_s_benefit() >= 0 else
              f"CS.money -> Steam benefit: \033[1;31m{'%.2f' % self.cs_s_benefit()} %\033[0m\n\n")

    def Name(self):
        return self.name

    def SteamPrice(self):
        return self.steam_price

    def SteamLink(self):
        return self.steam_link

    def CSmoneyPrice(self):
        return self.cs_money_price

    def CSMoneyLink(self):
        return self.cs_money_link

    def OverstockDiff(self):
        return self.overstock_diff

    def SteamQty(self):
        return self.steam_qty
    

def LoadData(items_list, file_name):
    data_frame_ = pd.DataFrame({
        'NAME': [item.Name() for item in items_list],
        'STEAM PRICE': [item.SteamPrice() for item in items_list],
        'CS.MONEY PRICE': [item.CSmoneyPrice() for item in items_list],
        'CS -> STEAM': [str('%.2f' % item.cs_s_benefit()).replace('.', ',') for item in items_list],
        'STEAM -> CS': [str('%.2f' % item.s_cs_benefit()).replace('.', ',') for item in items_list],
        'STEAM LINK': [item.SteamLink() for item in items_list],
        'CS.MONEY LINK': [item.CSMoneyLink() for item in items_list],
        'OVERSTOCK': [item.OverstockDiff() for item in items_list],
        'STEAM QTY': [item.SteamQty() for item in items_list]})
    data_frame_.to_excel(f'{file_name}.xlsx')


def Collector(page, items_list):

    request = requests.get(
        url=f"https://steamcommunity.com/market/search/render/?query=&start={page - 1}00&count=100&search_descriptions=0&"
            f"sort_column=price&sort_dir=asc&appid=730&category_730_ItemSet%5B%5D=any&category_730_ProPlayer"
            f"%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon"
            f"%5B%5D=any&category_730_Type%5B%5D=tag_CSGO_Type_Pistol&category_730_Type%5B%5D=tag_CSGO_Type_SMG"
            f"&category_730_Type%5B%5D=tag_CSGO_Type_Rifle&category_730_Type%5B%5D=tag_CSGO_Type_Shotgun"
            f"&category_730_Type%5B%5D=tag_CSGO_Type_SniperRifle&category_730_Type%5B%5D=tag_CSGO_Type_Machinegun"
            f"&category_730_Type%5B%5D=tag_Type_CustomPlayer&category_730_Type%5B%5D=tag_CSGO_Type_Knife"
            f"&category_730_Type%5B%5D=tag_CSGO_Tool_Sticker&category_730_Type%5B%5D=tag_Type_Hands&category_730_Type"
            f"%5B%5D=tag_CSGO_Type_Spray&category_730_Type%5B%5D=tag_CSGO_Type_MusicKit&category_730_Type"
            f"%5B%5D=tag_CSGO_Tool_Patch&category_730_Type%5B%5D=tag_CSGO_Type_Ticket",
        headers=headers_
    )

    print(f"\033[1;35mSteam parsing status: {request.status_code}\033[0m\n\n")

    for i in range(5):
        overstock = requests.get(
            url="https://cs.money/list_overstock?appId=730",
            headers=headers_
        )
        if overstock.status_code != 200 and i == 4:
            print("\033[1;31mUnsuccessful parse overstock: \033[0m", overstock.status_code)
            sys.exit()
        if overstock.status_code != 200:
            print("\033[1;31mUnsuccessful parse overstock: \033[0m", overstock.status_code)
            time.sleep(5)
            continue
        break

    time.sleep(2)
    unavailable = requests.get(
        url="https://cs.money/list_unavailable?appId=730",
        headers=headers_
    )

    for i in range(5):

        unavailable = requests.get(
            url = "https://cs.money/list_unavailable?appId=730",
            headers = headers_,
        )
        if unavailable.status_code != 200 and i == 4:
            print("\033[1;31mUnsuccessful parse overstock: \033[0m", unavailable.status_code)
            sys.exit()
        if unavailable.status_code != 200:
            print("\033[1;31mUnsuccessful parse overstock: \033[0m", unavailable.status_code)
            time.sleep(5)
            continue
        break

    over = []
    unav = []

    try:
        with open("overstock.txt", 'w', encoding="utf-16") as file:
            overstock_list = overstock.text[1:-1].replace("},{", "};{").split(';')
            for item in overstock_list:
                # file.write(item.json()["market_hash_name"], " = ", item.json()["overstock_difference"])
                item_json = (eval(item))
                name = item_json["market_hash_name"]
                over.append(name)
                count = str(item_json["overstock_difference"])
                file.write(name + " = " + count + '\n')

        with open("unavailable.txt", 'w', encoding="utf-16") as file:
            unavailable_list = unavailable.text[1:-1].replace("},{", "};{").split(';')
            for item in unavailable_list:
                item_json = (eval(item))
                name = item_json["market_hash_name"]
                unav.append(name)
                file.write(name + '\n')

    except Exception as exception_:
        print(f'\033[1;31mЯ хер знает, че делать: {exception_}\033[0m')

    data = BeautifulSoup(request.json()["results_html"], "lxml")

    # with open("steam.txt", "r", encoding="utf-16") as file:
    #     req = json.load(file)["results_html"]
    #     file.close()
    #
    # data = BeautifulSoup(req, "lxml")

    pr = data.find_all(class_="normal_price")[1::2]
    nm = data.find_all(class_="market_listing_row market_recent_listing_row market_listing_searchresult")
    lnk = data.find_all(class_="market_listing_row_link")
    qty = data.find_all(class_="market_listing_num_listings_qty")

    counter = 0
    tryes = 0
    i = 0
    data_info = {
        'request_counter': 0,
        'found_items': 0
    }
    if len(nm) != len(lnk) != len(pr):
        print("\033[1;31mError with parsing Steam. . .\033[0m")
        return
    amount = len(nm)
    while(i < amount):
        steam_price = pr[i].get_text()
        try:
            steam_price = float(steam_price[steam_price.find('$') + 1:steam_price.find(' ')])
        except Exception:
            print(f"CANT FLOAT: {steam_price[steam_price.find('$') + 1:steam_price.find(' ')]}")
        steam_name = nm[i].get_text()
        steam_name = steam_name[
                     steam_name.find("\n\n\n\n\n\n\n") + 7:steam_name.find("\n\nCounter-Strike: Global Offensive"):]
        steam_link = lnk[i].get("href").replace(' ', '')
        steam_qty = qty[i].get_text()
        steam_qty = int(steam_qty.replace(',', ''))
        i += 1
        exterior = steam_name[steam_name.find('(') + 1: steam_name.find(')')]
        cs_name = steam_name.replace(' ', '%20').replace('StatTrak™', 'StatTrak%E2%84%A2').replace('★', '')
        cs_name = cs_name.replace('(', '&exterior=')
        cs_name = cs_name.replace(')', '')
        cs_link = f"https://cs.money/ru/csgo/trade/?utm_source=google&utm_medium=cpc&" \
                  f"utm_campaign=Search_Brand_RU_Desktop_Act&network=g&utm_term=%2Bcsmoney&" \
                  f"utm_content=ads_1&" \
                  f"gclid=Cj0KCQiArt6PBhCoARIsAMF5wajjdx0O5pOFaBfDgZfpGs0Qj3xXngZ2qIjtV-z-P_JM5iTn2LLUjI0aApW8EALw_wcB&" \
                  f"search={cs_name}&sort=price&" \
                  f"order=desc&isMarket=false&hasRareFloat=false&hasRareStickers=false&" \
                  f"hasRarePattern=false&hasTradeLock=false&hasTradeLock=true"
        request_cs = requests.get(
            url=f"https://inventories.cs.money/5.0/load_bots_inventory/730?hasRareFloat=false&hasRarePattern=false&" \
                f"hasRareStickers=false&hasTradeLock=false&hasTradeLock=true&isMarket=false&limit=60&" \
                f"name={steam_name}&offset=0&order=asc&priceWithBonus=30&" \
                f"sort=price&tradeLockDays=1&tradeLockDays=2&tradeLockDays=3&tradeLockDays=4&tradeLockDays=5&" \
                f"tradeLockDays=6&tradeLockDays=7&tradeLockDays=0&withStack=true",
            headers=headers_
        )
        counter += 1
        if (request_cs.status_code == 429):
            print(f"\033[1;31mtoo many requestes: {counter}\033[0m")
            if tryes: print(f"\033[1;31mtryes: {tryes}\033[0m")
            tryes += 1
            time.sleep(60)
            continue
        elif (request_cs.status_code != 200):
            print(f"\033[1;31munknown error, requestes: {counter}\033[0m")
            break
        tryes = 0
        info = request_cs.json()
        try:
            info = info["items"]
        except KeyError:
            try:
                # print(f"No such items: {steam_name}\n\n")
                continue
            except KeyError as exception:
                print(f"\033[1;31mError: {exception}\033[0m\n\n")
                continue
        ID = info[0]["assetId"]

        item_info = requests.get(
            url=f"https://cs.money/skin_info?appId=730&id={ID}&isBot=true&botInventory=true",
            headers=headers_
        )

        if (item_info.status_code == 429):
            print(f"\033[1;31mtoo many requestes: {counter}\033[0m")
            tryes += 1
            time.sleep(60)
            continue
        if (item_info.status_code == 504):
            print(f"\033[1;31mserver gateway timeout\033[0m")
            tryes += 1
            time.sleep(5)
            continue
        if (item_info.status_code != 200):
            print(f"\033[1;31munknown error, requestes: {counter}\n"
                  f"status code = {item_info.status_code}\n\033[0m")
            break
        try:
            name = item_info.json()['steamName']
        except KeyError:
            try:
                print(f"\033[1;31mbad gateway: {item_info.json()['message']}\033[0m")
            except KeyError as ex:
                print(f"\033[1;31munknown error: {ex}\033[0m")
            continue
        counter += 1
        if name != steam_name:
            # print(f"No such items: {steam_name}\n\n")
            continue

        if unav.count(steam_name) or over.count(steam_name):
            # print(f"Item is overstocked or unavailable: {steam_name}\n\n")
            continue
        cs_money_price = item_info.json()
        cs_money_price = cs_money_price["defaultPrice"]


        over_status = requests.get(
            url=f"https://cs.money/check_skin_status?appId=730&name={steam_name.replace(' ', '+').replace('|', '%7C')}"
        )

        try:
            overstock_diff = over_status.json()['overstockDiff']
        except KeyError as ex:
            print(f"\033[1;31munknown error: {ex}\033[0m")
            continue

        item = Item(name_=steam_name,
                    s_price=steam_price,
                    s_link=steam_link,
                    cs_price=cs_money_price,
                    cs_link=cs_link,
                    over_diff=overstock_diff,
                    s_qty=steam_qty)

        if(item.s_cs_benefit() > 10 or item.cs_s_benefit() > -10):
            print(f"{i+1})")
            item.print()
            items_list.append(item)
            data_info['found_items'] += 1

        time.sleep(0.5)

    print(f"\n\nFinished with page: {page}\n"
          f"Counter of requests: {counter}\n")
    data_info['request_counter'] += counter
    return data_info


if __name__ == '__main__':
    start_time = time.time()
    items_list_ = []
    data_info_ ={
        'request_counter': 0,
        'found_items': 0
    }

    break_phase = 0
    for page_ in range(90, 170):       #100:170
        print(f"\033[1;35m{page_}0 страница. . .\033[0m")
        try:
            dictionary = Collector(page=page_, items_list=items_list_)
            data_info_['request_counter'] += dictionary['request_counter']
            data_info_['found_items'] += dictionary['found_items']
        except Exception as exception_:
            print(f"\033[1;31mUNEXPECTED ERROR: {exception_}\n"
                  f"PAGE: {page_}\033[0m")
        break_phase += 1
        if (break_phase == 5):
            time.sleep(300)
            break_phase = 0
    end_time = time.time()
    print(f"\033[1;32mFinished, count of requests: {data_info_['request_counter']}\n"
          f"count of found items: { data_info_['found_items']}\n"
          f"executing time:",
          f"{'%.2f' % ((end_time-start_time)/60)} minutes\033[0m"
          if end_time-start_time < 3600 else
          f"{'%.2f' % ((end_time-start_time)/3600)} hours\033[0m")

    try:
        local_time = time.localtime(time.time())
        # print(f"{local_time.tm_mday}.{local_time.tm_mon}={local_time.tm_hour}h{local_time.tm_min}m")
        LoadData(items_list = items_list_, file_name = f"parse_data_"
                                                       f"{local_time.tm_mday}."
                                                       f"{local_time.tm_mon}="
                                                       f"{local_time.tm_hour}h{local_time.tm_min}m")
        print("\033[1;32mData successfully loaded in xlsx file!\033[0m\n")
    except Exception as exception_:
        print(f"\n\033[1;31mUNEXPECTED ERROR WITH LOAD DATA IN FILE: {exception_}\033[0m\n")


# end of file
