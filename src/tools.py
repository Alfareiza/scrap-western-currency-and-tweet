from datetime import datetime

import boto3
from decouple import config

bucket_name = "archivos-alfonso"
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
    content_file = read_file()
    if brl_is_different(to_put, content_file):
        new_content = to_put + '\n'
        appended_data = content_file + new_content.encode('utf8')
        s3.put_object(Bucket=bucket_name, Key=path_file, Body=appended_data)
        return True
    else:
        return False


def read_file():
    return s3.get_object(Bucket=bucket_name, Key=path_file)['Body'].read()

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