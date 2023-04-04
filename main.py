import atexit
import httpx
from decouple import config
from rocketry import Rocketry
from rocketry.conditions.api import time_of_day, time_of_week, daily, after_success
from rocketry.conds import weekly


from src.scrap import ScrapSelenium, value_changed
from src.tools import goodbye, read_file, weekly_graph
from keep_alive import keep_alive 

app = Rocketry()
atexit.register(goodbye)

# Another option is :
# @app.task(hourly & time_of_day.between("12:00", "16:00"))
@app.task(daily.at("00:00") | daily.at("08:00") | daily.at("13:00") | daily.at("18:00"))
def scrap_send_to_s3():
    """
    Scrap the site and write into tweets.csv file that is on a S3 Bucket
    """
    scrap = ScrapSelenium(url="https://www.westernunion.com/br/es/currency-converter/brl-to-cop-rate.html")
    scrap.execute()
    if scrap.did_i_write_last_time:
      print('Amazon file updated!')
    else:
      print('The value of the currency haven\t changed')
    

@app.task((daily.at("01:00") | daily.at("09:00") | daily.at("14:00") | daily.at("19:30")) & time_of_week.between("Mon", "Fri"))
def post_text_tweet():
    """
    Call the endpoint that will trigger the lambda service who
    read the tweets.csv that is on s3 and post the tweet.
    """
    resp = httpx.get(config("ENDPOINT_LAMBDA", default=''))
    print('Tweet -> ', resp.content.decode('utf-8'))
    print('Tweet posted successfully!')
    

@app.task((weekly.on("Saturday")) & (time_of_day.between("20:00", "21:00")))
def post_img_tweet_last_currencies():
    """
    Generate the image, upload it in S3 and call the Amazon API to
    trigger the lambda service who post the tweet.
    """
    weekly_graph()  # Generate img and upload it into s3
    resp = httpx.post(config("POST_IMAGE"))
    print(f"Response when the image was posted: {resp.headers.get('date')} -> {resp.text}")
  
if __name__ == '__main__':
  keep_alive()
  app.run()
    
