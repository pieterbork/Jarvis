import datetime
import requests
import logging
import base64
import redis
import email
import time
import json

from . import EmailMessage, TextMessage
from .base_module import BaseModule

logger = logging.getLogger(__name__)


class RedisModule(BaseModule):
    def __init__(self, conf):
        #super(self.__class__, self).__init__(*args, **kwargs)
        super(self.__class__,self).__init__(conf)
        self.__name__ = "RedisModule"
        self.message_consumer = False
        self.message_q = conf["message_q"]
        self.client = redis.Redis(host='redis', port=6379, db=0)
        self.pubsub = self.client.pubsub()
        self.process = True

    def parse_email_msgs(self, msgs):
        messages = []
        for msg in msgs:
            m = EmailMessage(msg)
            messages.append(m)
        return messages

    def parse_text_message(self, msg):
        data = msg['data'].decode()
        logger.info("Parsing message: {} of type {}".format(data, type(data)))
        m = TextMessage(data)
        return m

    def q_message(self, m):
        logger.info("Placing {} on message queue!".format(m))
        self.message_q.put(m)

    def run(self):
        self.pubsub.subscribe('messages')
        while True and self.process:
            msg = self.pubsub.get_message()
            if msg and msg['type'] == 'message':
                text_m = self.parse_text_message(msg)
                self.q_message(text_m)
            msgs = self.mailbox.get_unread_messages()
            messages = self.parse_email_msgs(msgs)
            for email_m in messages:
                self.q_message(email_m)
            time.sleep(0.1)

    def stop(self):
        logger.info('{} received stop request'.format(self.__name__))
        self.process = False

