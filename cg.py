##
## Created : Fri Jul 10 19:10:06 IST 2015
##
## Copyright (C) 2015 Sriram Karra.
## All Rights Reserved
##
## Licenced under Affero GPL (AGPL) version 3
##

import demjson, sys

_BUY  = 0
_SELL = 1

class TxnType(object):
    def __init__ (self, typ):
        self.typ = typ

    def __str__ (self):
        return " BUY" if self.typ == _BUY else "SELL"

BUY = TxnType(_BUY)
SELL = TxnType(_SELL)

class Txn(object):
    def __init__ (self, typ, **kwargs):
        self.buy_or_sell = typ

        self.time      = kwargs.get(u'time')
        self.vol       = kwargs.get('vol', 0.0)
        self.rate      = kwargs.get('rate', 0.0)
        self.rate_spec = kwargs.get('rateSpecified', 0.0)
        self.order_id  = kwargs.get('orderID')
        self.trade_id  = kwargs.get('tradeID')
        self.fiat      = kwargs.get('fiat', 0)

    def __repr__ (self):
        ret = '\n'
        ret += 'Trade Type : %s ; ' % self.buy_or_sell
        ret += 'Trade ID : %s ; ' % (self.trade_id)
        ret += 'Timestamp : %s ; ' % (self.time)
        ret += 'BTC : %f ; ' % (self.vol / 100000000.0)
        ret += 'Amt (INR) : %.2f ; ' % (self.fiat / 100.0)
        ret += 'Txn Rate : %s ; ' % (self.rate)
        ret += 'Order ID : %s ; ' % (self.order_id)
        ret += 'Order Rate : %s ; ' % (self.rate_spec)

        return ret

def main ():
    buys_fn = sys.argv[1]
    sells_fn = sys.argv[2]

    with open(buys_fn, "r") as f:
        buys_json = demjson.decode(f.read())

    # FIXME: We will need to ensure it is sorted in chronological order
    buys = []
    for txn in buys_json['result']:
        buys.append(Txn(BUY, **txn))

    with open(sells_fn, "r") as f:
        sells_json = demjson.decode(f.read())

    sells = []
    for txn in sells_json['result']:
        sells.append(Txn(SELL, **txn))

    print "Buys: ", buys
    print "Sells: ", sells

if __name__ == "__main__":
    main()
