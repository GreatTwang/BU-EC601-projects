import tweepy
from tweepy import OAuthHandler
import json
import os
import urllib.request
import io
#tweet auths
consumer_key = "2Z4KPpbKWYvOoVDNMbghMkyci"
consumer_secret = "RqGunTxZnpjxPPSuOC70Lsgv1dFYY49OGbwv9JFfftxyz63fgj"
access_token = "935062736723107840-boT3el7KcrGDYsios1sowntRMSSId0K"
access_secret = "Mtc08PBSIdQ7V7GiCwVBg9drEyCQfHcJJKNd5ofd7R9KB"

#GOOGLE_APPLICATION_CREDENTIALS
os.environ['GOOGLE_APPLICATION_CREDENTIALS']="C:/Users/Tian Wang/Downloads/EC601-project1/twitter result/My First Project-ffd6c4d58501.json"


@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status
# Status() is the data model for a tweet
tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse
# User() is the data model for a user profil
tweepy.models.User.first_parse = tweepy.models.User.parse
tweepy.models.User.parse = parse
# You need to do it for all the models you need
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#getting the timeline of given name
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


#using Google cloud vision to detect objects in the pictures
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw, ImageFont

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


#using ffmpeg to generate an movie
os.popen('ffmpeg -r 1 -i img%03d.jpg -i bgm.mp3 -vf scale=500:500 -y -r 30 -t 60 messi.mp4')
