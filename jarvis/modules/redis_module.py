import datetime
import requests
import logging
import base64
import redis
import time
import json

from . import *
from .base_module import BaseModule

logger = logging.getLogger(__name__)


class RedisModule(BaseModule):
    def __init__(self, conf):
        #super(self.__class__, self).__init__(*args, **kwargs)
        super(self.__class__,self).__init__(conf)
        self.__name__ = "RedisModule"
        self.message_consumer = False
        self.message_q = conf["message_q"]
        self.client = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.client.pubsub()
        self.stopped = False

    def run(self):
        self.pubsub.subscribe('messages')
        while True and not self.stopped:
            msg = self.pubsub.get_message()
            if msg:
                logger.info("Placing {} on message queue!".format(msg))
                self.message_q.put(msg)
            time.sleep(0.1)

    def stop(self):
        logger.info('{} received stop request'.format(self.__name__))
        self.stopped = True

