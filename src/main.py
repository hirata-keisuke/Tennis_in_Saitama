from time import sleep
import func

from selenium import webdriver

if __name__ == "__main__":
    options = webdriver.chrome.options.Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)

    func.go_to_top(browser=browser)

    # 自分のIDとパスワードが必要
    func.login(browser=browser, id="", pwd="")

    competitors = func.get_other_competitors(browser=browser)
  
    # 自分の希望を作る
    hopes = dict()
    # 日付
    for i in ["20220402", "20220409", "20220416", "20220423", "20220429", "20220430"]:
        hopes[i] = dict()
        # コート番号
        for j in range(1, 23):
            j = str(j)
            hopes[i][j] = list()
            # 時間帯
            for k in ["9-11", "11-13", "13-15", "15-17"]:
                hopes[i][j].append(k)
    
    competitors = func.reflect_hope(competitors=competitors, hopes=hopes)

    func.enter_drawing(browser=browser, competitors=competitors)
        
    browser.close()
