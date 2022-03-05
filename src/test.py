from time import sleep
import func

from selenium import webdriver

if __name__ == "__main__":
    browser = webdriver.Chrome()

    func.go_to_top(browser=browser)

    func.login(browser=browser, id="070805keih", pwd="0785")

    try:
        func.get_other_competitors(browser=browser)
        sleep(3)
    finally:
        browser.close()
