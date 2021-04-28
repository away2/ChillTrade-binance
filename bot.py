import logging
from logger import *
from tradeEngine import *

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QCheckBox, QGridLayout, QLabel, QSpacerItem, \
    QSizePolicy, qApp, QAction
from PyQt5.QtCore import QSize, QCoreApplication, QSettings

from twisted.internet import reactor

CONFIG_PATH = 'settings.ini'

class MainWindow(QMainWindow):
    settings_file = QSettings(CONFIG_PATH, QSettings.IniFormat)

    check_box = None

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(960, 640))
        self.setWindowTitle("ChillTrade-binance")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
 
        grid_layout = QGridLayout(self)
        central_widget.setLayout(grid_layout)
 
        title = QLabel("ChillTrade-binance", self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(title, 0, 0) 

        self.check_box = QCheckBox('CheckBox')
        grid_layout.addWidget(self.check_box, 1, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)
 
        self.check_box.clicked.connect(self.save_check_box_settings)

        #logging
        handler = LogHandler(self)
        log_text_box = QtWidgets.QPlainTextEdit(self)
        grid_layout.addWidget(log_text_box, 2, 0)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG)
        handler.new_record.connect(log_text_box.appendPlainText)

        self._button = QtWidgets.QPushButton(self)
        self._button.setText('Start')
        grid_layout.addWidget(self._button, 3, 0)
        self._button.clicked.connect(self.start_btn)

        self._buttonStop = QtWidgets.QPushButton(self)
        self._buttonStop.setText('Stop')
        grid_layout.addWidget(self._buttonStop, 4, 0)
        self._buttonStop.clicked.connect(self.stop_btn)
        
 
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)
        file_menu = self.menuBar()
        file_menu.addAction(exit_action)

    def save_check_box_settings(self):
        pass

    def start_btn(self):
        logging.debug('sample bug')
        logging.info('some info')
        logging.warning('warning')
        logging.error('error')

        self.te = TradeEngine(self.settings_file)
        self.te.start_instrument('BTCUSDT')

    def stop_btn(self):
        if hasattr(self, 'te'):
            self.te.stop()

    def closeEvent(self, event):
        if hasattr(self, 'te'):
            self.te.stop()
            reactor.stop()
 


if __name__ == "__main__":
    import sys

    QCoreApplication.setApplicationName("ChillTrade-binance")
    QCoreApplication.setOrganizationDomain("ChillTrade-binance")

    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()

    sys.exit(app.exec())