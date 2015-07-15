## 
## Created : Sun Jul 12 22:25:55 IST 2015
## 
## Copyright (C) 2015 Sriram Karra <karra.etc@gmail.com>
## All Rights Reserved
##
## Licenced under Affero GPL (AGPL) version 3
##

import demjson, jsonpickle, jinja2, logging, os, time, urllib2, webapp2
from datetime import datetime

from google.appengine.api   import urlfetch
from google.appengine.ext   import ndb

import cg
from   cg import ts_ms_from_dt, Txn, Portfolio, BUY, SELL

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)

URL_BASE = "https://api.coinsecureis.cool/v0/"
URL_BUYS = "auth/completeduserbids"
URL_SELLS = "auth/completeduserasks"

ONEDAY = 86400000                         # Delta in Unix timestamps for 1 Day

jsonpickle.set_preferred_backend('demjson')

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
        js = self.fetch_trades(url, apikey, body)
        ret = []
        for txn in js['result']:
            ret.append(Txn(BUY, **txn))

        return ret

    def fetch_sells (self, apikey):
        body = demjson.encode({'apiKey' : apikey})
        url = URL_BASE + URL_SELLS
        js = self.fetch_trades(url, apikey, body)

        ret = []
        for txn in js['result']:
            ret.append(Txn(SELL, **txn))

        return ret

class TradesHandler(CSHandler):
    """
    Fetch the asks and bids using the specified API Key and return it as a
    json
    """

    def get (self):
        apikey = self.request.get('apikey', None)
        if apikey in [None, ""]:
            txns  = False
            buys  = []
            sells = []
        else:
            txns  = True
            buys  = self.fetch_buys(apikey)
            sells = self.fetch_sells(apikey)

        template = JENV.get_template('transactions.html')
        self.response.write(template.render({
            'txns'  : txns,
            'buys'  : buys,
            'sells' : sells,
            'cgmod' : cg,
            'error' : None
            }))

class CGActualHandler(CSHandler):
    def get (self):
        apikey    = self.request.get('apikey', None)
        date_from = self.request.get('from', None)
        date_to   = self.request.get('to', None)
        debug     = self.request.get('debug', False)

        if not (apikey or date_from or date_to):
            template = JENV.get_template('cg-actual.html')
            self.response.write(template.render({
                'cgs' : None,
                'error' : None
                }))
            return

        if not (apikey and date_from and date_to):
            template = JENV.get_template('cg-actual.html')
            self.response.write(template.render({
                'cgs' : None,
                'error' : "All form fields are mandatory"
                }))
            return

        buys  = self.fetch_buys(apikey)
        sells = self.fetch_sells(apikey)

        p = Portfolio(buys, sells)

        dt = datetime.strptime(date_from, "%Y-%m-%d")
        from_ts = ts_ms_from_dt(dt)
        dt = datetime.strptime(date_to, "%Y-%m-%d")
        to_ts = ts_ms_from_dt(dt) + ONEDAY

        cgs = p.cg(from_ts, to_ts)
        result = {
            'cgs' : cgs,
            'cgmod' : cg,
            'error' : None
            }

        if debug:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(jsonpickle.encode(result))
        else:
            template = JENV.get_template('cg-actual.html')
            self.response.write(template.render(result))

class MainPageHandler(CSHandler):
    def get (self):
        template = JENV.get_template('index.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([('/', MainPageHandler),
                               ('/trades', TradesHandler),
                               ('/cgActual', CGActualHandler),
                               ])

