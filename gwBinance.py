from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *

import logging
import pandas as pd
from datetime import datetime, timedelta

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

class GWBinance(QObject):
    #signals
    new_candle = pyqtSignal(str, object)

    def __init__(self, api_key, api_secret, parent=None):
        super().__init__(parent=parent)
        self.client = Client(api_key, api_secret)
        status = self.client.get_system_status()
        logging.info('GWBinance: ' + str(status))

    def get_candles(self, instrument):
        klines = self.client.get_historical_klines(instrument, Client.KLINE_INTERVAL_1HOUR, "60 day ago UTC")
        #klines = self.client.get_historical_klines(instrument, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
        df = pd.DataFrame(klines)
        df.columns = ["date", "open", "high", "low", "close", "basevol", "cdate", "vol", "trnum", "tbbvol", "tbqvol", "ign"]
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df['date'] = df['date'] + timedelta(hours = 3) #UTC+3
        df['time'] = df['date'].dt.time
        df['time'] = df['time'].astype(str).str.replace(':', '').astype(int)
        df['date'] = df['date'].dt.date
        df['date'] = df['date'].astype(str).str.replace('-', '').astype(int)

        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["vol"] = df["vol"].astype(float)

        df.drop(df.tail(1).index,inplace=True) #drop last unfinished candle
        return df[["date", "time", "open", "high", "low", "close", "vol"]]

    def start(self):
        self.bm = BinanceSocketManager(self.client)
        #conn_key = self.bm.start_trade_socket(self.instrument, self.process_message)
        #conn_key = self.bm.start_kline_socket(self.instrument, self.process_message, \
        #                                 interval=KLINE_INTERVAL_1MINUTE)
        #conn_key = self.bm.start_kline_socket(self.instrument, self.process_message, \
        #                                 interval=KLINE_INTERVAL_1HOUR)
        tf='1h' #1h 1m
        conn_key = self.bm.start_multiplex_socket([f'btcusdt@kline_{tf}', f'ethusdt@kline_{tf}', f'adausdt@kline_{tf}',
                                                                        f'bnbusdt@kline_{tf}', f'vetusdt@kline_{tf}', f'trxusdt@kline_{tf}',
                                                                        f'xlmusdt@kline_{tf}', f'xrpusdt@kline_{tf}'], \
                                         self.process_message)
        self.bm.start()

    def stop(self):
        if hasattr(self, 'bm'):
            self.bm.close()
            print('stopped')

    def market_trade_fut(self, instrument, size):
        if size > 0:
            side = Client.SIDE_BUY
        elif size < 0:
            side = Client.SIDE_SELL
        else:
            return 0

        #for disable trading
        #return 'OK'

        try:
            order = self.client.futures_create_order(
                    symbol=instrument,
                    side=side,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=abs(size) )
        except Exception as err: #BinanceAPIException
            print(err.args)
            print(err)
            logging.error('ERROR')
            logging.error(str(err.args), str(err))
            return 0
        else:
            print(order)
            return 'OK'

    def process_message(self, msg):
        #print("message type: {}".format(msg['e']))
        if 'data' not in msg:
            if msg['e'] == 'error':
                print('ws error no data' + str(msg))
                logging.error('ws error no data' + str(msg))
                self.stop()
                self.start()
            else:
                print('data not in msg', msg)
                logging.error('data not in msg', msg)
        elif msg['data']['e'] == 'kline' and msg['data']['k']['x'] == True:
            payload = msg['data']
            o_date = datetime.fromtimestamp(payload['k']['t'] / 1e3)
            o_time = o_date.time()
            o_time = int( str(o_time).replace(':', '') )
            o_date = o_date.date()
            o_date = int( str(o_date).replace('-', '') )
            open = float(payload['k']['o'])
            high = float(payload['k']['h'])
            low = float(payload['k']['l'])
            close = float(payload['k']['c'])
            vol = float(payload['k']['v'])
            #logging.info(o_time + ' ' + str(close))

            symbol = payload['s']
            self.new_candle.emit(symbol, [o_date, o_time, open, high, low, close, vol]) # <---- emit signal here
        elif msg['data']['e'] == 'kline':
            pass
        elif msg['data']['e'] == 'error':
            print('ws error ' + str(msg))
            self.stop()
            self.start()
        else:
            print("new message type: {}".format(msg['e']))
            print(msg)

    def __del__(self):
        self.stop()
        
