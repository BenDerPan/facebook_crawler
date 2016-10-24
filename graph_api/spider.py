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
from model import wrapper

#Facebook Spider used graph API v2.7
#2016-10-17 GongMeng


class spider():
    FORMAT = '[%(asctime)s -- %(levelname)s -- %(threadName)s -- %(funcName)s]:%(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger("fb_spider")

    def __init__(self, app_id, app_secret, facebook_name, es_server, es_index):
        self.app_id = app_id
        self.app_secret = app_secret
        self.facebook_name = facebook_name
        self.refresh_token()
        self.wrapper = wrapper(es_server, index='facebook')

    #Fetch basic info from facebook fan page
    def get_base_info(self):
        try:
            result = self.graph.get_object(id=self.facebook_name, fields="fan_count,about,category,picture{url}")
            if result.has_key("error"):
                raise "Error in Return JSON"
            if self.wrapper.fb_page_wrapper(result):
                return True
            else:
                raise "Page Update to Ealsticsearch Error"
        except Exception, error:
            self.logger.error(
                "name:{0}\n\t message: {1}".format(self.facebook_name, error))
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
            page_id = result['id']
            next_page = result['posts']['paging']['next']
            retry_num = 0
            #get more posts
            while(True):
                #Have failed too many times?
                if retry_num == 5:
                    return False

                #Try to put all the posts data into elasticsearch
                self.wrapper.fb_post_wrapper(posts_data, page_id)

                #no more posts?
                if len(posts_data) < 25:
                    return True

                #Have pull every new posts??
                oldestDate = posts_data[24]['created_time']

                self.logger.debug("name:{0} fetch oldeset post {1}".format(self.facebook_name, oldestDate))
                timestamp = time.mktime(datetime.datetime.strptime(oldestDate, "%Y-%m-%dT%H:%M:%S+0000").timetuple())
                print oldestDate
                print timestamp
                if timestamp <= endTime:
                    return True

                #Paginator to next 25 posts
                self.logger.debug(next_page)
                result = json.loads(requests.request("GET", next_page).content)

                #Error when try to paginator??
                if result.has_key("error"):
                    self.refresh_token()
                    retry_num = retry_num + 1
                    continue

                #Fetch new data
                posts_data = result['data']
                next_page = result['paging']['next']
            return True
        except Exception, error:
            traceback.print_exc()
            self.logger.error(
                "name:{0}\t message: {1}".format(self.facebook_name,  error))
            return False

    #get comments relate to one post
    def get_fb_comments_of_post(self, postID, endTime):
        try:
            result = self.graph.get_object(id=postID,
                                           fields="comments.limit(25){like_count,message,from,created_time,attachment,comment_count}")
            #check error
            if result.has_key("error"):
                raise "Error in Return JSON"

            # get all comments
            comments_data = result['comments']['data']
            next_page = result['comments']['paging']['next']
            retry_num = 0

            while (True):
                # Have failed too many times?
                if retry_num == 5:
                    return False

                # Try to put all the posts data into elasticsearch
                self.wrapper.fb_comments_wrapper(comments_data, postID)

                # no more posts?
                if len(comments_data) < 25:
                    return True

                # Have pull every new posts??
                oldestDate = comments_data[14]['created_time']

                self.logger.debug("name:{0} fetch oldeset post {1}".format(self.facebook_name, oldestDate))
                timestamp = time.mktime(datetime.datetime.strptime(oldestDate, "%Y-%m-%dT%H:%M:%S+0000").timetuple())
                print oldestDate + " : " + postID
                if timestamp <= endTime:
                    return True

                # Paginator to next 15 comments
                self.logger.debug(next_page)
                result = json.loads(requests.request("GET", next_page).content)

                # Error when try to paginator??
                if result.has_key("error"):
                    self.refresh_token()
                    retry_num = retry_num + 1
                    continue

                # Fetch new data
                comments_data = result['data']
                if result['paging'].has_key('next'):
                    next_page = result['paging']['next']
                else:
                    return True
            return result

        except Exception, error:
            traceback.print_exc()
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, error))
            return False

    #get reply to the comment
    def get_fb_reply_of_comment(self, commentID):
        try:
            result = self.graph.get_object(id=commentID,
                                           fields="comments{like_count,message,from,created_time,attachment,comment_count}")

            return True
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
    s = spider("1642551832703431", "70e0c263ebfa1acd7b9b230f4f49a82f", "southpark", '47.88.84.232:9200', 'facebook')
    s.get_fb_comments_of_post(postID="6708787004_10154033092692005", endTime=0)


