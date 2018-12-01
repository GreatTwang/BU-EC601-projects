import tweepy
from tweepy import OAuthHandler
import json
import os
import urllib.request
import io
import pymysql
import pymongo
from datetime import datetime
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw, ImageFont

class tweettomovie(object):
    def __init__(self):
        '''
        mysql and mongodb configuration and connection
        '''
        # mysql
        mysql_Config = {
        'host' : '127.0.0.1',
        'port' : 3306,
        'user' : 'root',
        'password' : '1234',
        'database' : 'test1',
        }
        try:
            self.mysql = pymysql.Connect(**mysql_Config)
        except Exception as e:
            print('ERROR: mysql connection fails!')
            raise e

        # mongodb
        try:
            mongodb = pymongo.MongoClient('mongodb://localhost')
            self.mongo = mongodb['test1']
        except Exception as e:
            print('ERROR: mongodb connection fails!')
            raise e

        self.err = None

    def parse(cls, api, raw):
        status = cls.first_parse(api, raw)
        setattr(status, 'json', json.dumps(raw))
        return status
    
    def auth(self,consumer_key, consumer_secret,access_token, access_secret):
        '''
        authentication
        '''
        # Status() is the data model for a tweet
        tweepy.models.Status.first_parse = tweepy.models.Status.parse
        tweepy.models.Status.parse = self.parse
        # User() is the data model for a user profile
        tweepy.models.User.first_parse = tweepy.models.User.parse
        tweepy.models.User.parse = self.parse
        # You need to do it for all the models you need
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth)
        self.log('connected!')

    def get(self):
        '''
        get the timeline of specific name and 
        '''
        tweets = api.user_timeline(screen_name='WeAreMessi',
                           count=200, include_rts=False,
                           exclude_replies=True)
        last_id = tweets[-1].id
        media_files = set()
        for status in tweets:
            media = status.entities.get('media', [])
            if(len(media) > 0):
                media_files.add(media[0]['media_url'])
        num=0
        for media_file in media_files:
            save_name = 'img%03d.jpg'%num
            urllib.request.urlretrieve(media_file,save_name)
            num = num + 1
        self.log('downloading img%03d.jpg'%num)

    def visionLabel(self):
        '''
        using Google cloud vision to detect objects in the pictures
        '''
        # Instantiates a client
        client = vision.ImageAnnotatorClient()
        path = './'
        filelist = os.listdir(path)
        total_num = len(filelist)
        for file in filelist:
            if file.endswith('.jpg'):
                with io.open(file, 'rb') as image_file:
                    content = image_file.read()

                image = types.Image(content=content)

                response = client.label_detection(image=image)
                labels = response.label_annotations

                # Add label to image
                img = Image.open(file)
                draw = ImageDraw.Draw(img)
                labelword = ''
                for label in labels:
                    labelword += str(label.description)+'\n'
                (w, h) = img.size
                ttfont = ImageFont.truetype("C:/Windows/Fonts/Corbel.ttf", 30)
                draw.text((w/2-100, h/2-100), labelword, fill=(255, 255, 255), font=ttfont)
                img.save(file)
    
    def mysql_label(self, uname, label):
        sql = 'INSERT INTO twt_label(twtid, label, time) VALUES (%s,%s,%s)'
        try:
            with self.mysql.cursor() as cursor:
                cursor.execute(sql, (uname, label, datetime.now()))
        except Exception as e:
            self.err = e
            self.mysql_log()
            self.mysql.close()
            raise e


    def mongo_label(self, uname, label):
        try:
            labels = self.mongo['labels']
            cursor = labels.find({'userid': uname})
            count = 0
            for i in cursor:
                doc = i
                count += 1

            if count == 0:
                doc = {
                    'userid': uname,
                    'labels': [label],
                }
                labels.insert_one(doc)
            elif count == 1:
                assert isinstance(doc['labels'], list), 'doc[labels] not list'
                if label in doc['labels']:
                    return
                else:
                    doc['labels'].append(label)
                    new = {
                        '$set': {'labels': doc['labels']}
                    }
                    labels.update_one({'userid': uname}, new)
            else:
                raise Exception('error: count of uid in labels != 0 or 1')
        except Exception as e:
            self.err = e
            raise e


    def mysqlSearch(self, key):
        sql = 'SELECT twtid FROM twt_label WHERE label like "%{}%"'.format(key)
        try:
            with self.mysql.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
        except Exception as e:
            self.err = e
            self.mysql.close()
            raise e
        finally:
            self.log('search {} in mysql'.format(key))
        idlist = []
        for row in results:
            if not row[0] in idlist:
                idlist.append(row[0])
        return idlist


    def mongoSearch(self, key):
        idlist = []
        try:
            labels = self.mongo['labels']
            for col in labels.find():
                assert isinstance(col['labels'], list), 'col[labels] not list'
                assert isinstance(col['userid'], str), 'col[userid] not str'
                if key in col['labels']:
                    if col['userid'] in idlist:
                        print('warning: more than one same userid in mongo[lanels]')
                    else:
                        idlist.append(col['userid'])
            return idlist
        except Exception as e:
            self.err = e
            raise e
        finally:
            self.log('search {} in mongodb'.format(key))


    def log(self, logstr='Unknown action'):
        self.mysql_log(logstr)
        self.mongo_log(logstr)

    def mysql_log(self, logstr='Unknown action'):
        if self.err:
            logstr = 'ERROR: ' + str(self.err)

        sql = 'INSERT INTO twtapi_log(time, action) VALUES (%s, %s)'
        try:
            with self.mysql.cursor() as cursor:
                cursor.execute(sql, (datetime.now(), logstr))
            self.mysql.commit()
        except Exception as e:
            self.mysql.rollback()
            self.mysql.close()
            raise e

    def mongo_log(self, logstr='Unknown action'):
        if self.err:
            logstr = 'ERROR: ' + str(self.err)

        doc = {
            'time': datetime.now(),
            'action': logstr,
        }
        try:
            log = self.mongo['log']
            log.insert_one(doc)
        except Exception as e:
            print('ERROR: log into mongodb')
            raise e

    def mysqlSummary(self):
        sql = 'SELECT idtwtAPI_log FROM twtapi_log'
        try:
            with self.mysql.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
            return len(results)
        except Exception as e:
            self.err = e
            self.mysql.close()
            raise e
        finally:
            self.mysql_log('count total logs in mysql')

    def mongoSummary(self):
        try:
            log = self.mongo['log']
            count = 0
            for i in log.find():
                count += 1
            return count
        except Exception as e:
            self.err = e
            raise e
        finally:
            self.mongo_log('count total logs in mongodb')

    def toVideo(self):
        '''
        using ffmpeg to generate an movie
        '''
        os.popen('ffmpeg -r 1 -i img%03d.jpg -i bgm.mp3 -vf scale=500:500 -y -r 30 -t 60 messi.mp4')
        self.log('video generated!')

if __name__=='__main__':
    #tweet auths
    consumer_key = "2Z4KPpbKWYvOoVDNMbghMkyci"
    consumer_secret = "RqGunTxZnpjxPPSuOC70Lsgv1dFYY49OGbwv9JFfftxyz63fgj"
    access_token = "935062736723107840-boT3el7KcrGDYsios1sowntRMSSId0K"
    access_secret = "Mtc08PBSIdQ7V7GiCwVBg9drEyCQfHcJJKNd5ofd7R9KB"

    #GOOGLE_APPLICATION_CREDENTIALS
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']="C:/Users/Tian Wang/Downloads/EC601-project1/twitter result/My First Project-ffd6c4d58501.json"

    test = tweettomovie()

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

