import random
from datetime import datetime
from time import sleep

import boto3
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


def write_file(to_put: str):
    """
    Append information into a file located in an S3 Bucket
    Ex.: '19/08/2022 13:44:01;899,26'
    """

    bucket_name = "archivos-alfonso"
    path_file = "tweets/tweets.csv"
    s3 = boto3.client("s3",
                      aws_access_key_id=config('ACCESS_KEY_ID_AMAZON'),
                      aws_secret_access_key=config('SECRET_ACCESS_KEY_AMAZON')
                      )
    content_file = s3.get_object(Bucket=bucket_name, Key=path_file)['Body'].read()
    new_content = to_put + '\n'
    appended_data = content_file + new_content.encode('utf8')
    return s3.put_object(Bucket=bucket_name, Key=path_file, Body=appended_data)


def get_brl(txt: str):
    """
    Receive an expression like this '1.00 BRL = 905.8228 Colombian Peso (COP)'
    and returns the currency as a float.
    >>> get_brl('1.00 BRL = 905.8228 Colombian Peso (COP)')
    905.8228
    """
    try:
        return float(txt.split()[3])
    except ValueError:
        return


class ScrapSelenium:
    def __init__(self, url):
        self.url = url
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument("--single-process")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument("--remote-debugging-port=9230")
        self.browser = webdriver.Chrome(
            service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
            options=options
        )

    def open_url(self):
        self.browser.get(self.url)
        self.browser.maximize_window()
        sleep(self.time_wait())

    def time_wait(self, start=10, end=20):
        return random.randint(start, end)

    def get_value_by_id(self, ide):
        return WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.ID, ide)))

    def next_screen(self):
        btn = self.get_value_by_id('home-get-started')
        btn.click()
        sleep(self.time_wait())

    def digit_info(self, info='100'):
        btn = self.get_value_by_id('wu-input-BRL')
        btn.clear()
        btn.send_keys(info)

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

    def get_info_second_screen(self):
        'wu-smoExchangeRate-BRL'
        try:
            element = self.get_value_by_id('smoExchangeRate')
            return element.text
        except TimeoutException:
            return ''

    def info_is_valid(self, info):
        try:
            num = float(info)
            return round(num / 100, 4) if num else False
        except ValueError:
            if not info or info.find('Colombian') < 12:
                return False
            else:
                return get_brl(info)

    def main(self, attempts=3):
        while attempts:
            attempts -= 1
            self.digit_info()
            captured = self.info_is_valid(self.get_info_first_screen())
            if captured:
                return captured  # Info capturada al primer intento
            self.next_screen()
            captured = self.info_is_valid(self.get_info_second_screen())
            if captured:
                return captured  # Info capturada al segundo intento
            else:
                self.browser.back()
                sleep(self.time_wait(2, 10))
                self.digit_info('2000')
                captured = self.info_is_valid(self.get_info_first_screen())
                if not captured:
                    sleep(self.time_wait(20, 40))
                    self.main(attempts)
                return captured  # Info capturada al tercer intento
        return ''

    def execute(self):
        self.open_url()
        brl = self.main()
        self.browser.stop_client()
        self.browser.close()
        self.browser.quit()
        dt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if brl:
            # write_file(f"{dt};{brl}")
            print(f'{dt} Información enviada con éxito')
            print(f"\n====> {dt};{brl}")
        else:
            print(f'{dt} No fue posible capturar información')

if __name__ == '__main__':
    scrap = ScrapSelenium(url="https://www.westernunion.com/br/es/currency-converter/brl-to-cop-rate.html")
    scrap.execute()
