import facebook
import requests
import logging
import simplejson as json
import traceback
from model import wrapper
from dateutil.parser import parse
import time

class spider_events():
    FORMAT = '[%(asctime)s -- %(levelname)s -- %(threadName)s -- %(funcName)s]:%(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger("fb_spider")

    def __init__(self, app_id, app_secret, facebook_name, es_server, es_index):
        self.app_id = app_id
        self.app_secret = app_secret
        self.facebook_name = facebook_name
        self.refresh_token()
        self.wrapper = wrapper(es_server, es_index)


    #Get Events
    def get_fb_events(self, end_time):
        try:
            result = self.graph.get_object(id=self.facebook_name,
                                           fields="events.limit(25){attending_count,description,start_time,end_time,category,cover,place,interested_count,name,maybe_count,noreply_count}")
            if result.has_key("error"):
                raise "Error in Return JSON"

            #get more events unitl endTime
            events_data = result['events']['data']
            page_id = result['id']
            next_page = result['events']['paging']['next']
            retry_num = 0
            #get more events
            while(True):
                #Have failed too many times?
                if retry_num == 3:
                    return False

                #Try to put all the posts data into elasticsearch
                self.wrapper.fb_events_wrapper(events_data, page_id)

                #no more posts?
                if len(events_data) < 25:
                    return True
                print events_data[24]['start_time']
                print end_time
                #Have pull every new posts??
                event_date = time.mktime(parse(events_data[24]['start_time']).timetuple())
                self.logger.debug("name:{0} fetch oldeset event {1}".format(self.facebook_name, event_date))

                if event_date <= time.mktime(end_time.timetuple()):
                    return True

                #Paginator to next 25 events
                self.logger.debug(next_page)
                result = json.loads(requests.request("GET", next_page).content)

                #Error when try to paginator??
                if result.has_key("error"):
                    self.logger.error("Fetch Evetns error : {0}".format(json.dumps(result)))
                    self.refresh_token()
                    retry_num = retry_num + 1
                    continue

                #Fetch new data
                events_data = result['data']
                next_page = result['paging']['next']

            return True
        except Exception, error:
            traceback.print_exc()
            self.logger.error(
                "name:{0}\t message: {1}".format(self.facebook_name,  error))
            return False


    # Refresh Token if got Oauth Error
    def refresh_token(self):
        payload = {'grant_type': 'client_credentials', 'client_id': self.app_id,
                'client_secret': self.app_secret}
        file = requests.post('https://graph.facebook.com/oauth/access_token?', params=payload)
        # print file.text #to test what the FB api responded with
        token = file.text.split("=")[1]
        # print file.text #to test the TOKEN
        self.graph = facebook.GraphAPI(access_token=token)