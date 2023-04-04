from datetime import datetime, timedelta
import boto3
from decouple import config

from src.graphs import generate_graph

bucket_name = "my-bucket-name"
path_file = "tweets/tweets.csv"
s3 = boto3.client("s3",
                  aws_access_key_id=config('ACCESS_KEY_ID_AMAZON'),
                  aws_secret_access_key=config('SECRET_ACCESS_KEY_AMAZON')
                  )


def log(f):
    def wrapper(*args, **kwargs):
        print(format(datetime.now(), '%D %T'), f"Executing {f.__name__}()")
        return f(*args, **kwargs)

    return wrapper


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


@log
def brl_is_different(to_put, content_file):
    """Verifies if the scraped currency value is different than the last value"""
    new_brl = float(to_put.split(';')[-1])
    last_line = content_file.decode('utf-8').split('\n')[-2]
    last_brl = float(last_line.split(';')[-1])
    return new_brl != last_brl


def write_file(to_put: str):
    """
    Append information into a file located in an S3 Bucket
    Ex.: '19/08/2022 13:44:01;899,26'
    """
    hour_scrapped = to_put.split(' ')[1][:2]
    content_file = read_file()
    if brl_is_different(to_put, content_file) or hour_scrapped == '18':
        new_content = to_put + '\n'
        appended_data = content_file + new_content.encode('utf8')
        s3.put_object(Bucket=bucket_name, Key=path_file, Body=appended_data)
        return True
    else:
        return False


def read_file():
    return s3.get_object(Bucket=bucket_name, Key=path_file)['Body'].read()


def goodbye():
    print(format(datetime.now(), '%D %T'), "I\'m leaving the server")


def file_as_dict():
    """
    Dictionary with information of the tweet.csv
    located at Amazon S3 Bucket.
    """
    content = read_file().decode('utf-8')
    lines = content.split("\n")[1:-1]
    dict_lines = {}
    for line in lines:
        k, v = line.split(';')
        dict_lines[k] = v
    return dict_lines


def calc_last_n_datetimes(n_days: int) -> list:
    """
    List with n last datetime objects from today
    :param n_days: Number of days to be calculated
    :return: List of datetime objects
    """
    dt = datetime.now()
    return [dt - timedelta(days=day) for day in range(n_days)]


def date_in_list_of_dates(to_check: datetime, lst_dates) -> bool:
    """
    Validate if a date is in a list of dates
    :param to_check: datetime.datetime(2023, 1, 27, 17, 37, 11, 803825)
    :param lst_dates: [datetime.datetime(2023, 1, 20, 17, 37, 11, 803825),
                        datetime.datetime(2023, 1, 21, 17, 37, 11, 803825),
                        datetime.datetime(2023, 1, 22, 17, 37, 11, 803825),
                        ...]
    :return: True or False
    """
    return any(to_check == dt.date() for dt in lst_dates)


def clean_empty_days(last_n_days: dict) -> dict:
    """
    Exclude the days wich has zero on his value
    :param last_n_days: {
                           '21-Ene': 0, '22-Ene': 0,
                           '23-Ene': 882.1914, '24-Ene': 866.3992,
                           '25-Ene': 883.4571, '26-Ene': 883.0917,
                           '27-Ene': 876.7687
                         }
    :return: Return a dict where there is no value with 0.
            Ex.:{'23-Ene': 882.1914, '24-Ene': 866.3992,
                 '25-Ene': 883.4571, '26-Ene': 883.0917,
                 '27-Ene': 876.7687}
    """
    return dict(filter(lambda item: item[1] > 0, last_n_days.items()))


def high_value_last_n_days(n_days=7) -> dict:
    """
    Calculate high currency in the last n days according to a
    file located in a S3 Bucket.
    :param n_days: Number of days to be considered.
    :return: {
               '21-Ene': 0, '22-Ene': 0,
               '23-Ene': 882.1914, '24-Ene': 866.3992,
               '25-Ene': 883.4571, '26-Ene': 883.0917,
               '27-Ene': 876.7687
             }
    """
    months = ['', 'Enero', 'Febrero', 'Marzo', 'Abril',
              'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
              'Octubre', 'Noviembre', 'Diciembre']

    dts = calc_last_n_datetimes(n_days)[::-1]

    last_n_days = {f"{dt.day}-{months[dt.month][:3]}": 0 for dt in dts}

    content = file_as_dict()
    reversed_dict = {key: content[key] for key in reversed(list(content.keys()))}
    for k, v in reversed_dict.items():
        dt_k = datetime.strptime(k, "%m/%d/%y %H:%M:%S").date()
        if date_in_list_of_dates(dt_k, dts):
            currency_k_day = last_n_days[f"{dt_k.day}-{months[dt_k.month][:3]}"]
            if float(v) > currency_k_day:
                last_n_days[f"{dt_k.day}-{months[dt_k.month][:3]}"] = float(v)

    return clean_empty_days(last_n_days)


@log
def send_img_to_s3(img: str) -> None:
    """
    Send the image (img) to the bucket to the img folder
    :param img: name of the img.
    :return: None
    """
    s3.upload_file(img, bucket_name, f'img/{img}')


@log
def weekly_graph():
    """
    Calculate the last n high values and generate an image
    with the information, then is sent to the bucket.
    :return: None
    """
    days_currencies = high_value_last_n_days(6)
    days, currencies = list(days_currencies.keys()), list(days_currencies.values())
    img = generate_graph(days, currencies)
    # print(img)
    send_img_to_s3(img)


if __name__ == '__main__':
    import json

    # Reading the file and returning a json
    content = read_file().decode('utf-8')
    lines = content.split("\n")[1:-1]
    dict_lines = {}
    for line in lines:
        k, v = line.split(';')
        dict_lines[k] = v
    print(json.dumps(dict_lines))
