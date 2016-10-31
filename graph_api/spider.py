import facebook
import requests
import logging
import simplejson as json
import traceback
from model import wrapper
from dateutil.parser import parse


#Facebook Spider used graph API v2.7
#2016-10-17 GongMeng


class spider():
    logger = logging.getLogger("fb_spider")

    def __init__(self, app_id, app_secret, facebook_name, es_server, es_index):
        self.app_id = app_id
        self.app_secret = app_secret
        self.facebook_name = facebook_name
        self.refresh_token()
        self.wrapper = wrapper(es_server, es_index)

    #Fetch basic info from facebook fan page
    def get_base_info(self):
        try:
            result = self.graph.get_object(id=self.facebook_name, fields="fan_count,about,category,picture{url}")
            if result.has_key("error"):
                raise "Error in Return JSON"
            if self.wrapper.fb_page_wrapper(result):
                return result['id']
            else:
                raise "Page Update to Ealsticsearch Error"
        except Exception, error:
            self.logger.error(
                "name:{0}\n\t message: {1}".format(self.facebook_name, error))
            return False

    #get fb feed
    def get_fb_feed(self, end_time, object_id):
        try:
            result = self.graph.get_object(id = object_id,
                                           fields = "feed.limit(25){shares,from,message,attachments{media},type,created_time,updated_time,status_type,full_picture}")
            if result.has_key("error"):
                raise "Error in Return JSON"

            #get more posts unitl target endTime
            feed_data = result['feed']['data']
            page_id = result['id']
            next_page = result['feed']['paging']['next']
            retry_num = 0
            #get more posts
            while(True):
                #Have failed too many times?
                if retry_num == 3:
                    return False

                #Try to put all the posts data into elasticsearch
                self.wrapper.fb_feeds_wrapper(feed_data, page_id)

                #no more posts?
                if len(feed_data) < 25:
                    return True

                event_date = parse(feed_data[24]['created_time'])
                self.logger.info("name:{0} fetch oldeset feed {1}".format(self.facebook_name, event_date))

                if event_date <= end_time:
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
                feed_data = result['data']
                next_page = result['paging']['next']
            return True
        except Exception, error:
            traceback.print_exc()
            self.logger.error(
                "name:{0}\t message: {1}".format(self.facebook_name,  error))
            return False
    #Get Posts
    def get_fb_post(self, end_time):
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
                if retry_num == 3:
                    return False

                #Try to put all the posts data into elasticsearch
                self.wrapper.fb_post_wrapper(posts_data, page_id)

                #no more posts?
                if len(posts_data) < 25:
                    return True

                #Have pull every new posts??
                post_date = parse(posts_data[24]['created_time'])
                self.logger.debug("name:{0} fetch oldeset post {1}".format(self.facebook_name, post_date))

                if post_date <= end_time:
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
    def get_fb_comments(self, object_id, page_id, target_type, end_time):
        try:
            result = self.graph.get_object(id = object_id,
                                           fields = "comments.limit(25){like_count,message,from,created_time,attachment,comment_count}")
            #check error
            if result.has_key("error"):
                raise "Error in Return JSON"

            # get all comments
            comments_data = result['comments']['data']
            if result['comments']['paging'].has_key("next"):
                next_page = result['comments']['paging']['next']
            else:
                return True
            retry_num = 0

            while (True):
                # Have failed too many times?
                if retry_num == 5:
                    return False

                # Try to put all the posts data into elasticsearch
                self.wrapper.fb_comments_wrapper(comments_data = comments_data, object_id = object_id, page_id = page_id, comments_target = target_type)
                # no more posts?
                if len(comments_data) < 25:
                    return True

                # Have pull every new posts??
                comment_date = parse(comments_data[14]['created_time'])
                self.logger.debug("name:{0} fetch oldeset comment {1}".format(self.facebook_name, comment_date))

                if comment_date <= end_time:
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

    def get_fb_events(self, end_time):
        try:
            result = self.graph.get_object(id=self.facebook_name,
                                           fields="events.limit(25){attending_count,description,start_time,end_time,category,cover,place,interested_count,name,maybe_count,noreply_count}")
            if result.has_key("error"):
                raise "Error in Return JSON"
            # get more events unitl endTime
            events_data = result['events']['data']
            page_id = result['id']
            next_page = result['events']['paging']['next']
            retry_num = 0
            # get more events
            while (True):
                # Have failed too many times?
                if retry_num == 3:
                    return False
                # Try to put all the posts data into elasticsearch
                self.wrapper.fb_events_wrapper(events_data, page_id)
                # no more posts?
                if len(events_data) < 25:
                    return True
                # Have pull every new posts??
                event_date = parse(events_data[24]['start_time'])
                self.logger.debug("name:{0} fetch oldeset event {1}".format(self.facebook_name, event_date))
                if event_date <= end_time:
                    return True
                # Paginator to next 25 events
                self.logger.debug(next_page)
                result = json.loads(requests.request("GET", next_page).content)
                # Error when try to paginator??
                if result.has_key("error"):
                    self.logger.error("Fetch Evetns error : {0}".format(json.dumps(result)))
                    self.refresh_token()
                    retry_num = retry_num + 1
                    continue
                # Fetch new data
                events_data = result['data']
                next_page = result['paging']['next']
            return True
        except Exception, error:
            traceback.print_exc()
            self.logger.error(
                "name:{0}\t message: {1}".format(self.facebook_name, error))
            return False

    #Refresh Token if got Oauth Error
    def refresh_token(self):
        payload = {'grant_type': 'client_credentials', 'client_id': self.app_id, 'client_secret': self.app_secret}
        file = requests.post('https://graph.facebook.com/oauth/access_token?', params=payload)
        # print file.text #to test what the FB api responded with
        token = file.text.split("=")[1]
        # print file.text #to test the TOKEN
        self.graph = facebook.GraphAPI(access_token=token)


