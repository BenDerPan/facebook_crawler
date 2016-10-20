import facebook
import requests
from threading import Thread
import logging
import json
from kafka import KafkaProducer
import simplejson as json
import datetime
import time
import traceback

#Facebook Spider used graph API v2.7
#2016-10-17 GongMeng


class spider():
    FORMAT = '%(asctime)s %(levelname)s %(threadName)s %(funcName)s %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger("fb_spider")

    def __init__(self, app_id, app_secret, facebook_name, kafka_server, proc_topic):
        self.app_id = app_id
        self.app_secret = app_secret
        self.facebook_name = facebook_name
        self.refresh_token()
        self.producer = KafkaProducer(bootstrap_servers=kafka_server, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.topic = proc_topic

    #Fetch basic info from facebook fan page
    def get_base_info(self):
        try:
            result = self.graph.get_object(id=self.facebook_name, fields="fan_count,about,category,picture{url}")
            if result.has_key("error"):
                raise "Error in Return JSON"

            #send result to kafka
            self.producer.send(self.topic, result)
            return True
        except Exception, error:
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, json.dumps(result, sort_keys=False)))
            return False

    #Get Post and basic info about this post
    def get_fb_post(self, endTime):
        try:
            result = self.graph.get_object(id=self.facebook_name,
                                           fields="posts.limit(25){shares,full_picture,message,created_time,updated_time,status_type,type}")
            if result.has_key("error"):
                raise "Error in Return JSON"

            #get more posts unitl target endTime
            posts_data = result['posts']['data']
            parent_id = result['id']
            next_page = result['posts']['paging']['next']
            retry_num = 0
            #get more posts
            while(True):
                if retry_num == 3:
                    return False
                self.producer.send(self.topic, result)
                print len(posts_data)
                if len(posts_data) < 25:
                    return True
                oldestDate = posts_data[24]['created_time']
                print oldestDate
                timestamp = time.mktime(datetime.datetime.strptime(oldestDate, "%Y-%m-%dT%H:%M:%S+0000").timetuple())
                if timestamp <= endTime:
                    return True
                print next_page
                result = json.loads(requests.request("GET", next_page).content)
                if result.has_key("error"):
                    self.refresh_token()
                    retry_num = retry_num + 1
                    continue
                posts_data = result['data']
                next_page = result['paging']['next']
                result.clear()
                result['posts'] = posts_data
                result['id'] = parent_id
            return True
        except Exception, error:
            traceback.print_exc()
            self.logger.error(
                "name:{0}\t message: {1}".format(self.facebook_name,  error))
            return False

    #get comments to one post and basic info about this comments --> pagination
    def get_fb_comments_of_post(self, postID):
        try:
            result = self.graph.get_object(id=postID,
                                           fields="comments{like_count,message,from,created_time,attachment,comment_count}")
            # send result to kafka
            # self.producer.send(self.topic, result)
            if result.has_key("error"):
                raise "Error in Return JSON"
            return result
        except Exception, error:
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, result['error']['message']))
            return False

    #get reply to the comment
    def get_fb_reply_of_comment(self, commentID):
        try:
            result = self.graph.get_object(id=commentID,
                                           fields="comments{like_count,message,from,created_time,attachment,comment_count}")
            if result.has_key("error"):
                raise "Error in Return JSON"
            # send result to kafka
            self.producer.send(self.topic, result)
            return result
        except Exception, error:
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, json.dumps(result, sort_keys=False)))
            return False

    #Likes of one post, which people like this post -->pagination
    def get_fb_likes_of_post(self, postID):
        try:
            result = self.graph.get_object(id=postID,
                                           fields="likes{name,pic,profile_type}")
            if result.has_key("error"):
                raise "Error in Return JSON"

            self.producer.send(self.topic, result)
            return result
        except Exception, error:
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, json.dumps(result, sort_keys=False)))
            return False

    #Refresh Token if got Oauth Error
    def refresh_token(self):
        payload = {'grant_type': 'client_credentials', 'client_id': self.app_id, 'client_secret': self.app_secret}
        file = requests.post('https://graph.facebook.com/oauth/access_token?', params=payload)
        # print file.text #to test what the FB api responded with
        token = file.text.split("=")[1]
        # print file.text #to test the TOKEN
        self.graph = facebook.GraphAPI(access_token=token)


class fb_spider_thread(Thread):
    def __init__(self):
        super(fb_spider_thread, self).__init__()

#faker unit test!
if __name__ == '__main__':
    s = spider("1642551832703431", "70e0c263ebfa1acd7b9b230f4f49a82f", "southpark", 'localhost:9092', 'test2')
    s.get_fb_post(1470000000)


