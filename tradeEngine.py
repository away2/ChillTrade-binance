from gwBinance import *
from strategies.strategy_btc_1h import *

from PyQt5.QtCore import QObject, pyqtSignal

import logging
import copy
import time

class TradeEngine():
    def __init__(self, settings):
        self.settings = settings

        bn_key = settings.value('key')
        bn_secret = settings.value('secret')

        self.bn = GWBinance(bn_key, bn_secret)

    def start_instrument(self, instrument):
        if not hasattr(self, 'bn'):
            logging.error('Gate binance is none')
            return
        self.bn.new_candle.connect(self.onBnCandle)
        self.candel_storage = {}
        self.candel_storage['BTCUSDT'] = self.bn.get_candles('BTCUSDT')
        #print(self.candel_storage)
        logging.info('start_instrument: BTCUSDT\n' + str(self.candel_storage['BTCUSDT'].tail(1)))
        self.bn.start()

        self.last_size = {}

        self.strBTC = StrategyBTCml()
        self.last_size['BTCUSDT'] = self.strBTC.last_size
        self.strBTC.signalSize.connect(self.slot_newSize)

        local_time1 = int(time.time() * 1000)
        server_time = self.bn.client.get_server_time()
        diff = server_time['serverTime'] - local_time1
        if diff > 1000:
            logging.error(f'Time diff {diff}')
        else:
            logging.info(f'Time diff {diff}')

    def stop(self):
        if hasattr(self, 'bn'):
            self.bn.stop()

    def onBnCandle(self, symbol, candle):
        #logging.info('onCandle: ' + str(candle))
        self.candel_storage[symbol].loc[len(self.candel_storage[symbol])]=candle
        if type(self.candel_storage[symbol]['date'][0]) == np.float64:
            self.candel_storage[symbol]['time'] = self.candel_storage[symbol]['time'].astype(int)
            self.candel_storage[symbol]['date'] = self.candel_storage[symbol]['date'].astype(int)
        #logging.info('onCandle: ' + str(candle))
        #print(self.candel_storage[symbol])

        data = copy.deepcopy(self.candel_storage[symbol])
        data['time'] = data['time'].astype(int)
        data['date'] = data['date'].astype(int)

        if symbol == 'BTCUSDT':
            self.strBTC.on_candle_thread(data)
        else:
            logging.info('onCandle: unknown symbol')

    def slot_newSize(self, instrument, size):
        #logging.info(f'onBTC1h_newSize: size {size}' )
        if self.last_size[instrument] != size:
            dif = round(size - self.last_size[instrument], 3)
            logging.info(f'trade {instrument}: {dif} last size {self.last_size[instrument]} new size {size}' )
            if instrument == 'BTCUSDT':
                r = self.bn.market_trade_fut(self.strBTC.instrument, dif)
                if r == 'OK':
                    self.strBTC.set_size(size)
            else:
                logging.warning('slot_newSize: unknown symbol')
                r = 0

            if r == 'OK':
                self.last_size[instrument] = size

    def __del__(self):
        self.stop()
        
