import random
from datetime import datetime
from pathlib import Path
import json
import boto3
import tweepy
from decouple import config

bucket_name = "my-bucket-name"
path_file = "tweets/tweets.csv"
s3 = boto3.client("s3",
                  aws_access_key_id=config('ACCESS_KEY_ID_AMAZON'),
                  aws_secret_access_key=config('SECRET_ACCESS_KEY_AMAZON')
                  )
# tweets_file = Path(__file__).resolve().parent / "tweets.csv"

def read_file(bucket_name, path_file):
    """Get the content of a file within S3"""
    return s3.get_object(Bucket=bucket_name, Key=path_file)["Body"].read()


def is_today(fecha):
    return datetime.strptime(fecha, "%m/%d/%y %H:%M:%S").date() == datetime.now().date()


def get_tweet():
    """Get tweet from a csv file"""
    file_content = read_file(bucket_name, path_file)
    content = file_content.decode("utf-8")
    lines = content.split("\n")
    new_fecha, new_value = lines[-2].split(';')  # ['04/02/23 18:01:00', '902.9838']
    last_fecha, last_value = lines[-3].split(';')  # ['04/01/23 18:00:50', '902.9838']
    brl_currency = new_value if is_today(new_fecha) else 0
    # brl_currency = value
    if brl_currency:
        phrases_changed = (
            "Hoy cuesta R${} enviar Reales a Colombia",
            "A R$ {} está el Real, si se envía por Western Union.",
            "R$ {} es el valor del Real hoy según Western Union.",
            "Hoy $ 1.000 Pesos colombianos, equivalen a R$ {}",
            "Si estás en Brasil y deseas reales a Colombia, multiplica la cantidad "
            "que deseas enviar por {} y sabrás cuanto se recibirá en Colombia."
        )
        if brl_currency == last_value:
            phrases_equal = (
                "El valor del real continúa en R$ {}."
                "No ha cambiado el valor del real desde el último tweet. R$ {}."
                "Aún se mantiene el valor del real con respecto al peso. R$ {}."
                "El valor de la moneda no ha cambiado. Aún se mantiene igual. R$ {}"
                )
            phrase = random.choice(phrases_equal)
            return phrase.format(round(float(brl_currency), 2))
            
        elif float(brl_currency) > float(last_value):
            phrase = random.choice(phrases_changed)
            return phrase.format(f"{round(float(brl_currency), 2)} 👍")
            
        elif float(brl_currency) < float(last_value):
            phrase = random.choice(phrases_changed)
            return phrase.format(f"{round(float(brl_currency), 2)} 👎")
    else:
        return ''

def lambda_handler(event, context):
    tweet = get_tweet()
    if tweet:
        consumer_key = config("consumer_key")
        consumer_secret = config("consumer_secret")
        access_token = config("access_token")
        access_token_secret = config("access_token_secret")
    
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
    
        api = tweepy.API(auth)
        try:
            # Do the tweet
            api.update_status(tweet)
        except Exception as e:
            print(e)
        
        return {"statusCode": 200, "body": json.dumps(tweet)}
    return {"statusCode": 200, "body": json.dumps("Last currency is not from today")}
