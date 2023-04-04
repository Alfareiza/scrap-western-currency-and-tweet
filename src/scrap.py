import random
from datetime import datetime
from time import sleep
import httpx

from decouple import config
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

from src.tools import log, get_brl, write_file

value_changed = False

class ScrapSelenium:
    def __init__(self, url):
        self.url = url
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument("--remote-debugging-port=9230")
        # Doesn't work on replit.com
        # self.browser = webdriver.Chrome(
            # service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
            # options=options
        # )
        # Works on replit.com
        self.browser = webdriver.Chrome(options=options)

    def open_url(self):
        self.browser.get(self.url)
        self.browser.maximize_window()
        sleep(self.time_wait())

    def kill(self):
        self.browser.stop_client()
        self.browser.close()
        self.browser.quit()

    def time_wait(self, start=5, end=10):
        return random.randint(start, end)

    def get_value_by_id(self, ide):
      try:
        return WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.ID, ide)))
      except Exception as e:
        print(f'No se pudo encontrar el botón con id {e}')

    @log
    def next_screen(self):
        btn = self.get_value_by_id('home-get-started')
        try:
            btn.click()
        except Exception as e:
            print('Error al darle click al btn continuar en home')
            self.browser.execute_script("arguments[0].click();", btn)
        finally:
            sleep(self.time_wait())

    @log
    def digit_info(self, info='100'):
        btn = self.get_value_by_id('wu-input-BRL')
        btn.clear()
        btn.send_keys(info)

    @log
    def get_info_first_screen(self):
        try:
            col_btn = self.get_value_by_id('wu-input-receiver-gets-BRL')
            col_btn.click()
            col_btn.send_keys(Keys.CONTROL + 'a')
            col_btn.send_keys(Keys.CONTROL + 'c')

            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # to hide the window
            variable = root.clipboard_get()
            return variable
        except Exception:
            return ''

    @log
    def get_info_second_screen(self):
        'wu-smoExchangeRate-BRL'
        try:
            element = self.get_value_by_id('smoExchangeRate')
            return element.text
        except TimeoutException:
            return ''

    @log
    def info_is_valid(self, info):
        try:
            num = float(info)
            if num:
                return round(num / 100, 4)
            else:
                False
        except ValueError:
            if not info or info.find('Colombian') < 12:
                return False
            else:
                return get_brl(info)

    @log
    def main(self, attempts=3):
        while attempts:
            attempts -= 1
            self.digit_info()
            captured = self.info_is_valid(self.get_info_first_screen())
            if captured:
                return captured  # First strike to scrap the site
            self.next_screen()
            captured = self.info_is_valid(self.get_info_second_screen())
            if captured:
                return captured  # Second strike to scrap the site
            else:
                self.browser.back()
                sleep(self.time_wait(2, 6))
                self.digit_info()
                captured = self.info_is_valid(self.get_info_first_screen())
                if not captured:
                    sleep(self.time_wait(20, 40))
                    self.main(attempts)
                return captured  # Third strike to scrap the site
        return ''

    @log
    def execute(self):
        self.open_url()
        brl = self.main()
        self.kill()
        self.send_info(brl)

    @log
    def send_info(self, brl):
      """
      Send the information to the tweets.csv if the last currency changed
      """
      dt = format(datetime.now(), '%D %T')
      if brl:
        self.did_i_write_last_time = write_file(f"{dt};{brl}")
      else:
        print(f'{dt} It wasn\'t possible to capture information')
