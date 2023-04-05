<h2 align="center">Scrap Western Union Currency</h2>
<h4 align="center">Twitter Bot</h4>
<h2 align="center">
<img alt="GitHub followers" src="https://img.shields.io/github/followers/Alfareiza?label=Follow%20me%20%3A%29&style=social">

![Python](https://img.shields.io/badge/Python-v3.8.3-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue) ![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat) ![Twitter](https://img.shields.io/twitter/url/https/twitter.com/AlfonsoAreizaG.svg?style=social&label=Follow%20%40AlfonsoAreizaG)
</h2>


I followed this documentation, [How to make a twitter bot for free](https://dylancastillo.co/how-to-make-a-twitter-bot-for-free/) in order to configure the lambda service that make the post of the tweet.

In the other hand, the main.py file is responsible for scraping the site, write the information into a file located at S3 Bucket, and call the AWS API Gateway. So, this module is executed on replit.com and stay alive thanks to uptimerobot.com. According to this, if the AWS API is triggered, the AWS Lambda function will be executed and the tweet will be posted.


#### Stack of Libraries
- Atexit: It is executed, in case of the interpreter stop (built-in library).
- Boto3: Read, Write and Update the information on the bucket.
- Httpx: Make a GET request to an AWS API Gateway in order to make the tweet.
- Selenium: Scrap the site.
- Rocketry: Schedule the task to make all the process.
- Tweepy: Handle the twitter api. So, It post the tweet.


#### Stack of Technologies
- Replit: Hold the project online.
- Uptimerobot: Keep the project alive using the replit url, previously generated with Flask.
- AWS Lambda: Handle the possibility of post the tweet, reading the bucket for updated information.
- AWS S3: Store the csv file with the scraped information.
- AWS API Gateway: Trigger that call de AWS Lambda function.

<h2 align="center">Illustrations</h4>

![scrap-western-currency-and-twee-page1](https://user-images.githubusercontent.com/63620799/230179700-b76388bb-7aae-40a4-b36f-6f636bb4ea1e.png)

![scrap-western-currency-and-twee-page2](https://user-images.githubusercontent.com/63620799/230179724-4691bc14-2ef7-462a-be15-6f37aaa5507b.png)

