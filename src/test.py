from time import sleep
import func

from selenium import webdriver

if __name__ == "__main__":
    browser = webdriver.Chrome()

    func.go_to_top(browser=browser)

    func.login(browser=browser, id="070805keih", pwd="0785")

    competitors = func.get_other_competitors(browser=browser, test=True)

    try:
        func.enter_drawing(browser=browser, competitors=competitors)
        
    finally:
        browser.close()
