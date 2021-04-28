import logging
from PyQt5.QtCore import QSettings, QObject, QMutex, QThread, QRunnable, QThreadPool, pyqtSignal, pyqtSlot

symbol = 'BTC'

class StrategyBTCml(QObject):
    signalSize = pyqtSignal(str, float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.instrument = 'BTCUSDT'
        self.settings_file = QSettings('./strategies/settings_{0}.ini'.format(symbol.lower()), QSettings.IniFormat)
        self.last_pos = float(self.settings_file.value('pos'))
        self.last_size = float(self.settings_file.value('size'))
        self.usd_risk = float(self.settings_file.value('risk'))

        self.threadpool = QThreadPool()

    def on_candle_thread(self, data):
        worker = CandleWorker(self.on_candle, data)
        self.threadpool.start(worker)

    def on_candle(self, data):
        close = data['close'].iloc[-1] 

        #insert trade logic here
        
        logging.info('StrategyBTC: pos ' + str(pos) + ' cndl close=' + str(close))

        if self.last_pos != pos:
            self.last_pos = pos
            self.settings_file.setValue('pos', pos)
            self.settings_file.sync()
            
            #calculate new size here
            size = 0
            
            self.signalSize.emit(self.instrument, size)
            return

        self.signalSize.emit(self.instrument, self.last_size)
        return

    def set_size(self, size):
        self.last_size = size
        self.settings_file.setValue('size', str(size))
        self.settings_file.sync()

class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class CandleWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(CandleWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)
        #self.signals.finished.emit(0)