from elasticsearch import Elasticsearch
from elasticsearch import helpers
import simplejson as json
import logging
import traceback

class driver():
    FORMAT = '[%(asctime)s -- %(levelname)s -- %(threadName)s -- %(funcName)s]:%(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger("fb_wrapper")

    def __init__(self, es_server, index):
        self.es = Elasticsearch([es_server])
        self.index = index

    def spider_comments_driver(self):
        self.es.search