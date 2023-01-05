import httpx
from decouple import config
from rocketry import Rocketry
from rocketry.conditions.api import time_of_week, daily

from src.scrap import ScrapSelenium, value_changed

app = Rocketry()


# Another option is :
# @app.task(hourly & time_of_day.between("12:00", "16:00"))
@app.task((daily.at("00:00") | daily.at("08:01") | daily.at("13:15") | daily.at("19:54")) & time_of_week.between("Mon", "Fri"))
def scrap_send_to_s3():
    scrap = ScrapSelenium(url="https://www.westernunion.com/br/es/currency-converter/brl-to-cop-rate.html")
    scrap.execute()


@app.task("after task 'scrap_send_to_s3'")
def make_tweet():
    if value_changed:
        resp = httpx.get(config("ENDPOINT_LAMBDA", default=''))
        print(resp.content.decode('utf-8'))


if __name__ == '__main__':
    app.run()
