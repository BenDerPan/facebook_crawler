import facebook
import requests
from threading import Thread
import logging
import json

#Facebook Spider used graph API v2.7
#2016-10-17 GongMeng


class spider():
    FORMAT = '%(asctime) %(levelname)s %(threadName)s %(funcName)s %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger("fb_spider")

    def __init__(self, app_id, app_secret, facebook_name):
        self.app_id = app_id
        self.app_secret = app_secret
        self.facebook_name = facebook_name
        self.refresh_token()


    #Fetch basic info from facebook fan page
    def get_base_info(self):
        try:
            result = self.graph.get_object(id=self.facebook_name, fields="fan_count,about,category,picture{url}")
            if result.has_key("error"):
                raise "Error in Return JSON"
            return True
        except Exception, error:
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, json.dumps(result, sort_keys=False)))
            return False

    #Get Post and basic info about this post
    def get_fb_post(self):
        try:
            result = self.graph.get_object(id=self.facebook_name,
                                           fields="posts{shares,full_picture,message,from,created_time,updated_time,status_type,type}")
            if result.has_key("error"):
                raise "Error in Return JSON"
            result = self.graph.request(result['paging']['next'])
            print result
        except Exception, error:
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, json.dumps(result, sort_keys=False)))
            return False

    #get comments to one post and basic info about this comments --> pagination
    def get_fb_comments_of_post(self, postID):
        try:
            result = self.graph.get_object(id=postID,
                                           fields="comments{like_count,message,from,created_time,attachment,comment_count}")
            if result.has_key("error"):
                raise "Error in Return JSON"
            return result
        except Exception, error:
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, json.dumps(result, sort_keys=False)))
            return False

    #get reply to the comment
    def get_fb_reply_of_comment(self, commentID):
        try:
            result = self.graph.get_object(id=commentID,
                                           fields="comments{like_count,message,from,created_time,attachment,comment_count}")
            if result.has_key("error"):
                raise "Error in Return JSON"
            return result
        except Exception, error:
            self.logger.warning(
                "name:{0}\n\t message: {1}".format(self.facebook_name, json.dumps(result, sort_keys=False)))
            return False

    #Likes of one post, which people like this post -->pagination
    def get_fb_likes_of_post(self, id):
        try:
            result = self.graph.get_object(id=self.facebook_name,
                                           fields="posts.limit(10){shares,full_picture,message,from,created_time,updated_time,status_type,type}")
            if result.has_key("error"):
                raise "Error in Return JSON"
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
        result = file.text.split("=")[1]
        # print file.text #to test the TOKEN
        self.graph = facebook.GraphAPI(access_token=result, version='2.7')


class fb_spider_thread(Thread):
    def __init__(self):
        super(fb_spider_thread, self).__init__()

#faker unit test!
if __name__ == '__main__':
    s = spider("1642551832703431", "70e0c263ebfa1acd7b9b230f4f49a82f", "southpark")
    s.get_fb_post()


