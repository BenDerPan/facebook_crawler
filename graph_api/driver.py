import logging
import settings
from spider import Spider
from cursor import cursor

class driver():
    FORMAT = '[%(asctime)s -- %(levelname)s -- %(threadName)s -- %(funcName)s]:%(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger("fb_wrapper")

    def __init__(self, page_name):
        self.page_name = page_name
        self.s = Spider(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET, self.page_name,
                        settings.ELASTIC_SEARCH_SERVER,
                        settings.ELASTIC_SEARCH_INDEX)
        self.spider_basic_pageinfo()
        self.cursor = cursor(settings.ELASTIC_SEARCH_SERVER, settings.ELASTIC_SEARCH_INDEX, self.page_id)

    def spider_basic_pageinfo(self):
        self.page_id = self.s.get_base_info()
        if self.page_id == False:
            exit()

    #Get newest posts or get one year posts relative to one page
    def spider_posts_driver(self):
        end_time = self.cursor.get_newest_posts()
        self.s.get_fb_post(end_time)

    # Feeds for fan page and Feeds for Events
    def spider_feeds_driver_to_page(self):
        end_time = self.cursor.get_newest_feeds(self.page_id)
        spider_res = self.s.get_fb_feed(end_time, self.page_id)
        print spider_res

    def spider_comments_to_post_driver(self):
        query_index = 0
        while(True):
            result = self.cursor.get_newest_comments_to_post(query_index)
            for iteam in result:
                spider_res = self.s.get_fb_comments(page_id=self.page_id, object_id=iteam['post_id'], end_time=iteam['end_time'], target_type="post")
                print spider_res
            if len(result) < 30:
                return True
            else:
                query_index = query_index + 30
                if query_index > 200:
                    return True

    def spider_events_driver(self):
        end_time = self.cursor.get_newest_event()
        res = self.s.get_fb_events(end_time)
        print res

    def spider_photos_driver(self):
        end_time = self.cursor.get_newest_photo('tagged')
        res = self.s.get_fb_photos(page_id=self.page_id, end_time=end_time, object_id = self.page_id, type='tagged')
        print res
        end_time = self.cursor.get_newest_photo('profile')
        res = self.s.get_fb_photos(page_id=self.page_id, end_time=end_time, object_id=self.page_id, type='profile')
        print res
        end_time = self.cursor.get_newest_photo('uploaded')
        res = self.s.get_fb_photos(page_id=self.page_id, end_time=end_time, object_id=self.page_id, type='uploaded')
        print res

if __name__ == '__main__':
    driver = driver("lululemon")
    driver.spider_feeds_driver_to_page()
    driver.spider_posts_driver()
    driver.spider_comments_to_post_driver()
    driver.spider_events_driver()
    driver.spider_photos_driver()
