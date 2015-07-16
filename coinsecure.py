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

class CSError(Exception):
    pass

class CSHandler(webapp2.RequestHandler):
    def fetch_trades (self, url, apikey, body):
        ret = {}
        req = urllib2.Request(url, body,
                              {'Content-Type': 'application/json'})
        resp = urllib2.urlopen(req)
        content = resp.read()

        c = demjson.decode(content)
        if 'error' in c:
            raise CSError(c[u'error'])

        return demjson.decode(content)

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

        txns  = False
        buys  = []
        sells = []
        error = False
        errmsg = ''

        if apikey in [None, ""]:
            pass
        else:
            txns  = True
            try:
                buys  = self.fetch_buys(apikey)
                # sells = self.fetch_sells(apikey)
            except Exception, e:
                errmsg = str(e)
                logging.error(errmsg)
                error = True

        template = JENV.get_template('transactions.html')
        self.response.write(template.render({
            'txns'  : txns,
            'buys'  : buys,
            'sells' : sells,
            'cgmod' : cg,
            'error' : error,
            'errmsg' : errmsg
            }))

class CGActualHandler(CSHandler):
    def get (self):
        apikey    = self.request.get('apikey', None)
        date_from = self.request.get('from', None)
        date_to   = self.request.get('to', None)
        debug     = self.request.get('debug', False)
        ltg_threshold = self.request.get('stg_threshold', False)

        error  = False
        errmsg = ""
        buys   = []
        sells  = []

        if not (apikey or date_from or date_to):
            template = JENV.get_template('cg-actual.html')
            self.response.write(template.render({
                'cgs' : None,
                'error' : False
                }))
            return

        if not (apikey and date_from and date_to):
            template = JENV.get_template('cg-actual.html')
            self.response.write(template.render({
                'cgs' : None,
                'error' : True,
                'errmsg' : "All form fields are mandatory"
                }))
            return

        try:
            buys  = self.fetch_buys(apikey)
            sells = self.fetch_sells(apikey)
            error = False
        except Exception, e:
            error = True
            logging.error(str(e))
            errmsg = str(e)

        p = Portfolio(buys, sells, ltg_threshold=ltg_threshold)

        dt = datetime.strptime(date_from, "%Y-%m-%d")
        from_ts = ts_ms_from_dt(dt)
        dt = datetime.strptime(date_to, "%Y-%m-%d")
        to_ts = ts_ms_from_dt(dt) + ONEDAY

        cgs = p.cg(from_ts, to_ts)
        result = {
            'cgs' : cgs,
            'cgmod' : cg,
            'error' : error,
            'errmsg' : errmsg
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
                               ('/transactions', TradesHandler),
                               ('/cgActual', CGActualHandler),
                               ])

