import datetime as dt
import jpholiday
import re, unicodedata

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

def go_to_top_page(browser, url="https://www.pa-reserve.jp/eap-rj/rsv_rj/core_i/init.asp?KLCD=119999&SBT=1&Target=_Top&LCD="):
    """
    埼玉県県営公園の施設予約サイトに遷移する

    Parameters
    ==========
    brawser : selenium.webdriver.chrome.webdriver.WebDriver
        seleniumで起動したChromeのブラウザドライバ

    url : str
        遷移先のURL
    """
    # 指定したURLに遷移させる
    browser.get(url=url)

    # サイトがframeタグで囲まれているので、frameに移動する
    frame = browser.find_element(by=By.TAG_NAME, value="frame")
    browser.switch_to.frame(frame)

def login(browser, id="", pwd=""):
    """
    一度、マイメニューに入ってログインする。後で抽選予約するときに、1回目の予約だけログイン情報を聞かれるのを避ける。

    Parameters
    ==========
    brawser : selenium.webdriver.chrome.webdriver.WebDriver
        seleniumで起動したChromeのブラウザドライバ

    id : str
        利用者ID
    
    pwd : str
        利用者パスワード
    """


if __name__ == "__main__":

    try:

        # 指定したURLに遷移させる
        browser = webdriver.Chrome()
        browser.get(url="https://www.pa-reserve.jp/eap-rj/rsv_rj/core_i/init.asp?KLCD=119999&SBT=1&Target=_Top&LCD=")

        # サイトがframeタグで囲まれているので、frameに移動する
        frame = browser.find_element(by=By.TAG_NAME, value="frame")
        browser.switch_to.frame(frame)
        # frameの切り替え
        frame = browser.find_element(by=By.TAG_NAME, value="frame")
        browser.switch_to.frame(frame)

        # 所在地ボタンを押してページ遷移
        button = browser.find_element(by=By.XPATH, value="//input[@alt='所在地']")
        button.click()
        #sleep(1)

        # 地域のテーブル取得
        tables = browser.find_elements(by=By.TAG_NAME, value="table")
        center_area_button = tables[7].find_elements(by=By.TAG_NAME, value="td")[2].find_element(by=By.TAG_NAME, value="a")
        center_area_button.click()

        # 地域検索開始
        tables[3].find_element(by=By.XPATH, value="//input[@alt='検索実行']").click()
        
        # 大宮第二公園の抽選予約画面へ
        to_lottery = browser.find_elements(by=By.CLASS_NAME, value="clsImage")
        to_lottery[-1].click()
        
        # 抽選したい、翌月のカレンダーに切り替える
        _today = dt.date.today()
        this_month = _today.month
        next_month = (this_month+1)%13
        next_month_element = browser.find_elements(by=By.CLASS_NAME, value="clsCalMonth")[next_month-1]
        next_month_link = next_month_element.find_element(by=By.TAG_NAME, value="a")
        next_month_url = next_month_link.get_attribute("href")
        browser.execute_script(next_month_url)

        # 既に申し込んでいる人数の表示ON
        browser.find_element(by=By.ID, value="radio01").click()
        sleep(3)

        # 土日祝日を抽選申し込み対象にする
        holidays = list()
        _year = _today.year + (_today.month+1)//13
        for d in range(1, 31):
            try:
                date = dt.date(_year, next_month, d)
                # 土日祝日
                if date.weekday() >= 5 or jpholiday.is_holiday(date):
                    holidays.append(date)
            
            except ValueError:
                break
        
        # 時間帯
        time_span = ["8", "9-11", "11-13", "13-15", "15-17"]

        # 後で使う正規表現
        pickup_courtno = re.compile(r"\s+第\dテニス")
        pickup_braket = re.compile(r"【 (\d+) 】")

        # 抽選コートに申し込んでいる人数を取り出す
        lottery_people = dict()
        for date in holidays:
            date_str = date.strftime("%Y%m%d")
            lottery_people[date_str] = dict()

            # 土日祝日で表示
            browser.execute_script(
                "javascript:set_data(" + date_str + ")"
            )
            sleep(1)
            # 第1コート~第22コートまでを調べる
            shisetu_title = browser.find_elements(by=By.CLASS_NAME, value="clsShisetuTitleOneDay")
            for one_court in shisetu_title:
                if "テニス" in one_court.text:
                    courtno = pickup_courtno.sub("", unicodedata.normalize("NFKC", one_court.text))
                    lottery_people[date_str][courtno] = dict()
                    # 時間帯で調べる
                    for i, one_timezone in enumerate(one_court.find_elements(by=By.XPATH, value="../td")):
                        if i != 0:
                            if num := pickup_braket.search(one_timezone.text):
                                lottery_people[date_str][courtno][time_span[i]] = num[1]
                            else:
                                lottery_people[date_str][courtno][time_span[i]] = ""

    finally:
        print(lottery_people)
        browser.close()