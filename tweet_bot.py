import boto3
import json
import os
import time
import tweepy

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date


consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
aws_access_key = os.environ.get("AWS_ACCESS_KEY")
aws_secret_key = os.environ.get("AWS_SECRET_KEY")

sched = BlockingScheduler()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

client = boto3.client('s3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key)

def get_s3_bucket(bucket, file_path):
    response = client.get_object(Bucket=bucket, Key=file_path)
    return response

def update_s3_bucket(bucket, file_path):
    client.put_object(Body=binary_body, Bucket=bucket, Key=file_path)

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=12)
def job():

    acount = json.loads(get_s3_bucket("philosched", "aristotle_count")['Body'].read())
    print (acount)

    if acount["date"] == str(date.today()):
        print ("Already tweeted today")

    if acount["date"] < str(date.today()):
        aquotes = json.loads(get_s3_bucket("philodata", "aristotle.json")['Body'].read())

        line_count = acount["count"]
        if len(aquotes)-acount["count"] == 2:
            print("Switch over to something else tomorrow")
        if len(aquotes)-acount["count"] == 1:
            print("End of the line")
        else:
            line_count+=1
            while aquotes[line_count]["quote"]==None:
                line_count+=1

            tweet = aquotes[line_count]["quote"]
            tweet = "\n".join([tweet, "-Aristotle"])

            api.update_status(tweet)
            print (tweet)
            #TODO: Limit length of tweet

            acount["date"] = str(date.today())
            acount["count"] = line_count

            acount = bytes(json.dumps(acount), "utf-8")
            update_s3_bucket("philosched", "aristotle_count")

sched.start()
