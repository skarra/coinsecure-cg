## 
## Created : Sun Jul 12 22:25:55 IST 2015
## 
## Copyright (C) 2015 Sriram Karra <karra.etc@gmail.com>
## All Rights Reserved
##
## Licenced under Affero GPL (AGPL) version 3
##

import demjson, jinja2, logging, os, urllib2, webapp2

from google.appengine.api   import urlfetch
from google.appengine.ext   import ndb

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)

URL_BASE = "https://api.coinsecureis.cool/v0/"
URL_BUYS = "auth/completeduserbids"
URL_SELLS = "auth/completeduserasks"

class CSHandler(webapp2.RequestHandler):
    def fetch_trades (self, url, apikey, body):
        ret = {}
        try:
            req = urllib2.Request(url, body,
                                   {'Content-Type': 'application/json'})
            resp = urllib2.urlopen(req)
            ret = demjson.decode(resp.read())
        except urllib2.URLError, e:
            logging.error("Could not fetch bid list: %s", e)

        return ret

    def fetch_buys (self, apikey):
        body = demjson.encode({'apiKey' : apikey})
        url = URL_BASE + URL_BUYS
        return self.fetch_trades(url, apikey, body)

    def fetch_sells (self, apikey):
        body = demjson.encode({'apiKey' : apikey})
        url = URL_BASE + URL_SELLS
        return self.fetch_trades(url, apikey, body)

class TradesHandler(CSHandler):
    """
    Fetch the asks and bids using the specified API Key and return it as a
    json
    """

    def get (self, apikey):
        buys  = self.fetch_buys(apikey)
        sells = self.fetch_sells(apikey)

        result = { 'buys' : buys, 'sells': sells }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(demjson.encode(result))

class MainPageHandler(webapp2.RequestHandler):
    def get (self):
        self.response.out.write("Hello World!")

app = webapp2.WSGIApplication([('/', MainPageHandler),
                               ('/trades/(.*)', TradesHandler)
                               ])
