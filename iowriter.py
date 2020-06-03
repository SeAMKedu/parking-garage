import time

from PyQt5 import QtCore


class InputWriter(QtCore.QThread):
    """
    Send a signal to the main app where the signal is connected to
    the method that writes the values of the PLC input variables.
    """
    signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
    

    def run(self):
        """Will be executed when the thread is started."""
        while True:
            self.signal.emit()
            time.sleep(0.1)  # 100 ms
