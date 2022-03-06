import datetime as dt
import jpholiday, calendar
import re, unicodedata
import numpy as np

from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from dateutil.relativedelta import relativedelta
from time import sleep

def go_to_top(browser, url="https://www.pa-reserve.jp/eap-rj/rsv_rj/core_i/init.asp?KLCD=119999&SBT=1&Target=_Top&LCD="):
    """
    埼玉県県営公園の施設予約サイトに遷移する

    Parameters
    ==========
    brawser : selenium.webdriver.chrome.webdriver.WebDriver
        seleniumで起動したChromeのブラウザドライバ

    url : str
        遷移先のURL
    """
    # 指定したURLに遷移する
    browser.get(url=url)

    # サイトがframeタグで囲まれているので、frameに移動する
    frame = browser.find_element(by=By.TAG_NAME, value="frame")
    browser.switch_to.frame(frame)

def login(browser, id="", pwd=""):
    """
    一度、マイメニューに入ってログインする。
    coockieを先に取得して、後で抽選予約するときに、1回目の予約だけログイン情報を聞かれるのを避ける。

    Parameters
    ==========
    brawser : selenium.webdriver.chrome.webdriver.WebDriver
        seleniumで起動したChromeのブラウザドライバ

    id : str
        利用者ID
    
    pwd : str
        利用者パスワード
    """

    # マイメニューへ遷移する
    button = browser.find_element(by=By.XPATH, value="//input[@alt='マイメニュー']")
    button.click()

    # 利用者IDを入力する項目を探し出して、入力する
    id_input = browser.find_element(by=By.NAME, value="txt_usr_cd")
    id_input.send_keys(id)

    # パスワードを入力する項目を探し出して、入力する
    pwd_input = browser.find_element(by=By.NAME, value="txt_pass")
    pwd_input.send_keys(pwd)

    # OKボタンを押下する
    button = browser.find_element(by=By.NAME, value="btn_ok")
    button.click()

    # ログインできたので再びメニューに戻る
    button = browser.find_element(by=By.XPATH, value="//input[@alt='メニューへ戻る']")
    button.click()

def get_other_competitors(browser, test):
    """
    大宮第二公園の施設抽選・予約ページに遷移して、抽選を既に申請している人数を、日ごと・コートごと・時間帯ごとで取り出す。

    Parameters
    ==========
    brawser : selenium.webdriver.chrome.webdriver.WebDriver
        seleniumで起動したChromeのブラウザドライバ

    Returns
    =======
    competitors : dict (of dict (of dict))
        日ごと・コートごと・時間帯ごとの申請者をまとめた辞書
    """

    # 所在地選択ページへ遷移する
    button = browser.find_element(by=By.XPATH, value="//input[@alt='所在地']")
    button.click()

    # 中央エリアを選択する
    browser.execute_script("javascript:onclick=cmdSelect_click('00001', '中央エリア');")
    button = browser.find_element(by=By.XPATH, value="//input[@alt='検索実行']")
    button.click()

    # 大宮第二公園の抽選ページに遷移する
    browser.execute_script("cmdLotYoyaku_click('000050', '00001');return false;")

    # 抽選したい、翌月のカレンダーに切り替える
    _today = dt.date.today()
    next_month = _today + relativedelta(months=1)
    next_month = next_month.replace(day=1)
    browser.execute_script(
        f"javascript:set_cal_cal({next_month.strftime('%Y%m%d')}, '00000000', '99999999')"
    )

    if test:
        return {
        '20220430': {'16': {'9-11': 99999, '11-13': 99999, '13-15': 99999, '15-17': 99999},
        '17': {'9-11': 10, '11-13': 8, '13-15': 8, '15-17': 7},
        '18': {'9-11': 26, '11-13': 7, '13-15': 6, '15-17': 6},
        '19': {'9-11': 26, '11-13': 12, '13-15': 17, '15-17': 17},
        '20': {'9-11': 27, '11-13': 9, '13-15': 10, '15-17': 8},
        '21': {'9-11': 28, '11-13': 22, '13-15': 8, '15-17': 16},
        '22': {'9-11': 22, '11-13': 16, '13-15': 19, '15-17': 3}}
    }

    # 既に申し込んでいる人数の表示ON
    browser.find_element(by=By.ID, value="radio01").click()

    # 土日祝日を抽選申し込み対象にする
    holidays = list()
    for days in range(calendar.monthrange(year=next_month.year, month=next_month.month)[1]):
        date = next_month + dt.timedelta(days=days)
        if date.weekday() >= 5 or jpholiday.is_holiday(date):
            holidays.append(date)
        
    # 時間帯
    time_span = ["8", "9-11", "11-13", "13-15", "15-17"]

    # 後で使う正規表現
    pickup_courtno = re.compile(r"\s+第\dテニス")
    pickup_braket = re.compile(r"【 (\d+) 】")

    # 抽選コートに申し込んでいる人数を取り出す
    competitors = dict()
    for date in holidays:
        date_str = date.strftime("%Y%m%d")
        competitors[date_str] = dict()

        # 土日祝日を切り替える
        browser.execute_script(f"javascript:set_data({date_str})")
        # 第1コート~第22コートまでを調べる
        shisetu_title = browser.find_elements(by=By.CLASS_NAME, value="clsShisetuTitleOneDay")
        for one_court in shisetu_title:
            if "テニス" in one_court.text:
                courtno = pickup_courtno.sub("", unicodedata.normalize("NFKC", one_court.text))
                competitors[date_str][courtno] = dict()
                # 時間帯で調べる
                for i, one_timezone in enumerate(one_court.find_elements(by=By.XPATH, value="../td")):
                    if i != 0:
                        if num := pickup_braket.search(one_timezone.text):
                            competitors[date_str][courtno][time_span[i]] = int(num[1])
                        else:
                            competitors[date_str][courtno][time_span[i]] = 99999
    return competitors

def enter_drawing(browser, competitors, topn=4):
    """
    申込数が少ない、日にち・時間帯・コート番号に抽選を申し込む。
    
    Parameters
    ==========
    competitors : dict (of dict (of dict))
        日ごと・コートごと・時間帯ごとの申請者をまとめた辞書

    topn : int
        少ない順から幾つを取り出すか
    """
    
    data = list()
    index = list()
    for k1, v1 in competitors.items():
        for k2, v2 in v1.items():
            for k3, v3 in v2.items():
                data.append(v3)
                index.append(k1 + "/" + k2 + "/" + k3)

    # 申請者の少ないコートを選ぶ
    targets = np.take(index, np.argsort(data)[:topn])
    timezones = {"9-11":0, "11-13":1, "13-15":2, "15-17":3}

    for target in targets:
        target = target.split("/")
        # 日付を合わせる
        browser.execute_script(f"javascript:set_data({target[0]})")
        tz = timezones[target[2]]
        # コートを選ぶ
        browser.execute_script(f"javascript:komaClicked(0,{tz},{int(target[1])+1})")
        # OK
        button = browser.find_element(by=By.NAME, value="btn_ok")
        button.click()
        # 次へ、次へ、抽選予約確定
        button = browser.find_element(by=By.NAME, value="btn_next")
        button.click()
        button = browser.find_element(by=By.NAME, value="btn_next")
        button.click()
        button = browser.find_element(by=By.NAME, value="btn_cmd")
        button.click()
        # ポップアップが表示されるまで待つ
        sleep(2)
        Alert(browser).accept()

        # コート表示画面まで戻る
        button = browser.find_element(by=By.NAME, value="btn_back")
        button.click()
