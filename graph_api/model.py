from elasticsearch import Elasticsearchfrom elasticsearch import helpersimport simplejson as jsonimport loggingimport tracebackimport requestsclass wrapper():    logger = logging.getLogger("fb_wrapper")    def __init__(self, es_server, index):        self.es = Elasticsearch([es_server])        self.index = index    #put page data to elasticsearch    def fb_page_wrapper(self, page_data):        doc = {}        doc['fan_count'] = page_data['fan_count']        doc['about'] = page_data['about']        doc['category'] = page_data['category']        doc['picture'] = page_data['picture']['data']['url']        try:            response = self.es.index(index = self.index, doc_type = 'page', id = page_data['id'], body = doc)            return  True        except Exception, error:            self.logger.warning(error)            return False    #put feeds into ES    def fb_feeds_wrapper(self, feeds_data, page_id):        actions = []        for feed_data in feeds_data:            try:                action = {}                action['_id'] = feed_data['id'].split("_")[1]                action['_index'] = self.index                action['_type'] = 'feeds'                action['parent'] = feed_data['id'].split("_")[0]                action['page_id'] = page_id                action['created_time'] = feed_data['created_time']                action['updated_time'] = feed_data['updated_time']                action['type'] = feed_data['type']                action['status_type'] = feed_data['status_type']                action['uid'] = feed_data['id']                if feed_data.has_key('message'):                    action['message'] = feed_data['message']                if feed_data.has_key('shares'):                    action['shares'] = feed_data['shares']['count']                if feed_data.has_key('full_picture'):                    action['full_picture'] = feed_data['full_picture']                actions.append(action)            except Exception, error:                traceback.print_exc()                self.logger.error("Bulk Put Document to ES : {0}".format(json.dumps(feed_data)))        actions = self.fb_get_sentiment(actions)        helpers.bulk(self.es, actions, request_timeout=120)    #put evetns into ES    def fb_events_wrapper(self, events_data, page_id):        actions = []        for event_data in events_data:            try:                action = {}                action['_id'] = event_data['id']                action['_index'] = self.index                action['_type'] = 'events'                action['uid'] = event_data['id']                action['parent'] = page_id                action['name'] = event_data['name']                action['description'] = event_data['description']                if event_data.has_key('category'):                    action['category'] = event_data['category']                action['interested_count'] = event_data['interested_count']                action['attend_count'] = event_data['attending_count']                action['maybe_count'] = event_data['maybe_count']                action['noreply_count'] = event_data['noreply_count']                action['created_time'] = event_data['start_time']                if event_data.has_key('end_time'):                    action['end_time'] = event_data['end_time']                if event_data.has_key('cover'):                    action['cover'] = event_data['cover']['source']                action['place'] = {}                if event_data.has_key('place'):                    place = event_data['place']                    action['place']['name'] = place['name']                    if place.has_key('location'):                        action['place']['city'] = place['location']['city']                        action['place']['country'] = place['location']['country']                        action['place']['state'] = place['location']['state']                        action['place']['location'] = {}                        action['place']['location']['lat'] = place['location']['latitude']                        action['place']['location']['lon'] = place['location']['longitude']                actions.append(action)            except Exception, error:                traceback.print_exc()                self.logger.error("Bulk Put Document to ES : {0}".format(json.dumps(event_data)))        helpers.bulk(self.es, actions, request_timeout=120)    #put posts into ES    def fb_post_wrapper(self, posts_data, page_id):        actions = []        for post_data in posts_data:            try:                action = {}                action['_id'] = post_data['id'].split("_")[1]                action['_index'] = self.index                action['_type'] = 'posts'                action['parent'] = page_id                action['created_time'] = post_data['created_time']                action['updated_time'] = post_data['updated_time']                action['type'] = post_data['type']                action['status_type'] = post_data['status_type']                action['uid'] = post_data['id']                if post_data.has_key('message'):                    action['message'] = post_data['message']                if post_data.has_key('shares'):                    action['shares'] = post_data['shares']['count']                if post_data.has_key('full_picture'):                    action['full_picture'] = post_data['full_picture']                actions.append(action)            except Exception, error:                traceback.print_exc()                self.logger.error("Bulk Put Document to ES : {0}".format(json.dumps(post_data)))        helpers.bulk(self.es, actions, request_timeout=120)    #put comments into elasticsearch    def fb_comments_wrapper(self, comments_data, object_id, page_id, comments_target):        actions = []        for comment_data in comments_data:            try:                action = {}                action['_id'] = comment_data['id'].split("_")[1]                action['_index'] = self.index                action['_type'] = 'comments'                action['parent'] = object_id                action['page_id'] = page_id                action['target'] = comments_target                action['created_time'] = comment_data['created_time']                action['uid'] = comment_data['id']                if comment_data.has_key('message'):                    action['message'] = comment_data['message']                action["like_count"] = comment_data["like_count"]                action["comment_count"] = comment_data['comment_count']                action["from_name"] = comment_data["from"]["name"]                action["from_id"] = comment_data["from"]["id"]                action['attachment'] = {}                if comment_data.has_key("attachment"):                    attachment = comment_data['attachment']                    if attachment.has_key("description"):                        action["attachment"]["description"] = attachment["description"]                    if attachment.has_key("title"):                        action["attachment"]["title"] = attachment["title"]                    action["attachment"]["target_url"] = attachment["url"]                    if attachment.has_key('media'):                        action["attachment"]["media"] = attachment["media"]                actions.append(action)            except Exception, error:                traceback.print_exc()                self.logger.error("Bulk Put comment to ES : {0}".format(json.dumps(comment_data)))        actions = self.fb_get_sentiment(actions)        helpers.bulk(self.es, actions, request_timeout=120)    def fb_get_sentiment(self, actions_data):        post_data = []        for action in actions_data:            item = {}            item['id'] = action['uid']            item['content'] = action['message']            post_data.append(item)        result_data = json.loads(requests.post(url = 'http://123.56.43.215:8080/sentiments', json = post_data).content)        for action in actions_data:            id = action['uid']            for item in result_data:                if item['id'] == id:                    action['sentiment'] = item['categorizerResult']['label']                    break        return actions_data