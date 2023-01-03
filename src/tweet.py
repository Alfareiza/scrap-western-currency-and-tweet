import random
from datetime import datetime
from pathlib import Path

import boto3
import tweepy
from decouple import config

bucket_name = "archivos-alfonso"
path_file = "tweets/tweets.csv"


# tweets_file = Path(__file__).resolve().parent / "tweets.csv"

def get_file_content(bucket_name, path_file):
    """Get the content of a file within S3"""
    bucket_name = "archivos-alfonso"
    path_file = "tweets/tweets.csv"
    s3 = boto3.client("s3",
                      aws_access_key_id=config('ACCESS_KEY_ID_AMAZON'),
                      aws_secret_access_key=config('SECRET_ACCESS_KEY_AMAZON')
                      )
    return s3.get_object(Bucket=bucket_name, Key=path_file)["Body"].read()


def is_today(fecha):
    return datetime.strptime(fecha, "%d/%m/%Y %H:%M:%S").date() == datetime.now().date()


def get_tweet():
    """Get tweet from a csv file"""
    file_content = get_file_content(bucket_name, path_file)
    content = file_content.decode("utf-8")
    lines = content.split("\n")
    fecha, value = lines[-2].split(';')
    brl_currency = value if is_today(fecha) else 0
    # brl_currency = value
    if brl_currency:
        phrases = (
            "Hoy cuesta R${} enviar Reales a Colombia",
            "A R${} está el Real, si se envía por Western Union.",
            "R$ {} es el valor del Real hoy según Western Union.",
            "Hoy $ 1.000 Pesos colombianos, equivalen a R$ {}",
            "Si estás en Brasil y deseas reales a Colombia, multiplica la cantidad"
            "que deseas enviar por {} y sabrás cuanto se recibirá en Colombia."
        )

        phrase = random.choice(phrases)
        return phrase.format(brl_currency)
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
        # Do the tweet
        api.update_status(tweet)
        return {"statusCode": 200, "tweet": tweet}
    else:
        return {"statusCode": 404, "msg": "Última cotización no es de hoy"}


if __name__ == '__main__':
    # print(get_file_content("archivos-alfonso", "tweets/tweets.csv"))
    print(get_tweet())
