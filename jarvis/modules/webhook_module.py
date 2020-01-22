import cherrypy
import datetime
import requests
import logging
import base64
import time
import json

from . import *
from .base_module import BaseModule

logger = logging.getLogger(__name__)

class WebServer(object):
    def __init__(self, message_q):
        self.message_q = message_q

    @cherrypy.expose
    def default(self, *args, **kwargs):
        return ""

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def message(self):
        if cherrypy.request.method == "POST":
            input_json = cherrypy.request.json
            logger.info("Received: {}".format(input_json))
            self.message_q.put(input_json)
        return ""

    def handle_error(self, *args, **kwargs):
        try:
            logger.error("Request Error: {}".format(kwargs["message"]))
        except:
            logger.error("Unkown Error")
        return ""

class WebhookModule(BaseModule):
    def __init__(self, conf):
        #super(self.__class__, self).__init__(*args, **kwargs)
        super(self.__class__,self).__init__(conf)
        self.__name__ = "WebhookModule"
        self.message_consumer = False
        self.message_q = conf["message_q"]
        self.server = WebServer(self.message_q)

    def run(self):
        cherrypy.config.update({'server.socket_port': 5000, 
            'request.error_response': self.server.handle_error,
            'error_page.default': self.server.handle_error})
        cherrypy.quickstart(self.server)

    def stop(self):
        logger.info('WebhookModule received stop request')
        cherrypy.engine.exit()

