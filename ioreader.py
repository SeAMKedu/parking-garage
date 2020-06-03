import pyads
from PyQt5 import QtCore

import config


class OutputReader(QtCore.QThread):
    """
    Read the values of the PLC output variables and send a signal
    to the main app when a variable changes its state.
    """
    signal = QtCore.pyqtSignal(dict)

    def __init__(self, connection: object):
        QtCore.QThread.__init__(self)
        self.conn = connection
    

    def run(self):
        """Will be executed when the thread is started."""
        @self.conn.notification(pyads.PLCTYPE_BOOL)
        def callback(handle: int, name: str, timestamp: str, value: bool):
            """
            Called everytime when the PLC variable changes its state.

            :param int handle: An unique ID that the PLC associates to an address.
            :param str name: The name of the PLC variable, "MAIN.myVariable".
            :param datetime timestamp: YYYY-mm-dd HH:MM:SS.ssssss.
            :param bool value: The value of the PLC variable.
            """
            data = {"name": name, "value": value}
            self.signal.emit(data)
        
        attr = pyads.NotificationAttrib(1)
        try:
            self.conn.add_device_notification(config.Outputs.QH0.value, attr, callback)
            self.conn.add_device_notification(config.Outputs.QM1LOWER.value, attr, callback)
            self.conn.add_device_notification(config.Outputs.QM1RAISE.value, attr, callback)
            self.conn.add_device_notification(config.Outputs.QM2LOWER.value, attr, callback)
            self.conn.add_device_notification(config.Outputs.QM2RAISE.value, attr, callback)
        except pyads.pyads_ex.ADSError as err:  # e.g. wrong variable name
            print(err)
            self.signal.emit({"name": "error", "value": err})
