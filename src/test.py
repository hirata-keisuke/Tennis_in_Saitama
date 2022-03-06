from time import sleep
import func

from selenium import webdriver

if __name__ == "__main__":
    options = webdriver.chrome.options.Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)

    func.go_to_top(browser=browser)

    func.login(browser=browser, id="070805keih", pwd="0785")

    competitors = func.get_other_competitors(browser=browser)
  
    hopes = dict()
    for i in ["20220402", "20220409", "20220416", "20220423", "20220429", "20220430"]:
        hopes[i] = dict()
        for j in range(1, 23):
            j = str(j)
            hopes[i][j] = list()
            for k in ["9-11", "11-13", "13-15", "15-17"]:
                hopes[i][j].append(k)
    
    competitors = func.reflect_hope(competitors=competitors, hopes=hopes)

    func.enter_drawing(browser=browser, competitors=competitors)
        
    browser.close()
