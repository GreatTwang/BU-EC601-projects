import tweettomovie
import os

#tweet auths
consumer_key = "2Z4KPpbKWYvOoVDNMbghMkyci"
consumer_secret = "RqGunTxZnpjxPPSuOC70Lsgv1dFYY49OGbwv9JFfftxyz63fgj"
access_token = "935062736723107840-boT3el7KcrGDYsios1sowntRMSSId0K"
access_secret = "Mtc08PBSIdQ7V7GiCwVBg9drEyCQfHcJJKNd5ofd7R9KB"

#GOOGLE_APPLICATION_CREDENTIALS
os.environ['GOOGLE_APPLICATION_CREDENTIALS']="C:/Users/Tian Wang/Downloads/EC601-project1/twitter result/My First Project-ffd6c4d58501.json"

test = tweettomovie.tweettomovie()

# set keys and secrets of twitter api
test.auth(consumer_key, consumer_secret,access_token, access_secret)

# get images
test.get()

#label
test.visionLabel()

keyword = 'messi'
mysqlResults = test.mysqlSearch(keyword)
print('MySQL: These twitter account owns keyword {}'.format(keyword))
for each in mysqlResults:
    print(each)

mongoResults = test.mongoSearch(keyword)
print('MongoDB: These twitter account owns keyword {}'.format(keyword))
for each in mongoResults:
    print(each)

log_mysql_count = test.mysqlSummary()
print('There are', log_mysql_count[0], 'logs in MySQL.')
log_mongo_count = test.mongoSummary()
print('There are', log_mongo_count, 'logs in MongoDB.')

test.toVideo()
