import sys

import pyads
from PyQt5 import QtCore, QtGui, QtWidgets

import config
from ioreader import OutputReader
from iowriter import InputWriter
from prop_anim import PropertyAnimations


class SimulatorApp(QtWidgets.QWidget):
    """The parking garage simulator."""

    def __init__(self):
        super().__init__()
        # ADS config.
        self.net_id = config.AdsConnection.AMS_NET_ID.value
        self.net_port = config.AdsConnection.AMS_NET_PORT.value
        self.conn = None
        self.type = pyads.PLCTYPE_BOOL
        # Object for property animations.
        self.animation = PropertyAnimations()
        # X positions of the barriers.
        self.xbar_in = 126
        self.xbar_out = 566
        # X positions of the light sensors.
        self.xls1 = 95
        self.xls2 = 160
        self.xls3 = 535
        self.xls4 = 600
        # Initial position of the car.
        self.xcar = 10
        self.ycar = 185

        self.excess = 10  # excess over the light sensor
        self.car_is_moving = False
        self.drive_in_permit = False
        self.drive_out_permit = False

        self.comm_running = False

        self.parked_cars = []
        self.counter = 0
        
        self.initUi()
    

    def initUi(self):
        """Initialize the user interface."""
        # Window properties.
        self.setGeometry(0, 0, 700, 350)
        self.setWindowTitle("Paikoitustalo")

        # Create image labels.
        self.garage = QtWidgets.QLabel(self)
        self.garage.setPixmap(QtGui.QPixmap("img/garage.png"))
        
        self.barrier_in = QtWidgets.QLabel(self)
        self.barrier_in.setPixmap(QtGui.QPixmap("img/barrier.png"))
        self.barrier_in.move(self.xbar_in, 160)

        self.barrier_out = QtWidgets.QLabel(self)
        self.barrier_out.setPixmap(QtGui.QPixmap("img/barrier.png"))
        self.barrier_out.move(self.xbar_out, 160)

        self.h0_green = QtWidgets.QLabel(self)
        self.h0_green.setPixmap(QtGui.QPixmap("img/h0green.png"))
        self.h0_green.move(118, 275)

        self.h0_red = QtWidgets.QLabel(self)
        self.h0_red.setPixmap(QtGui.QPixmap("img/h0red.png"))
        self.h0_red.move(118, 275)
        self.h0_red.hide()

        self.car = QtWidgets.QLabel(self)
        self.car.setPixmap(QtGui.QPixmap("img/car1.png"))
        self.car.move(self.xcar, self.ycar)

        self.set_parked_cars()

        # Button for opening an instruction popup window.
        #self.btn_help = QtWidgets.QPushButton("Ohje", self)
        #self.btn_help.move(10, 10)
        #self.btn_help.clicked.connect(self.display_help)

        # Button for opening a connection to the TwinCAT message router.
        self.btn_conn_open = QtWidgets.QPushButton("Avaa yhteys", self)
        self.btn_conn_open.move(150, 10)
        self.btn_conn_open.resize(130, 28)
        self.btn_conn_open.clicked.connect(self.conn_open)

        # Button for closing the connection to the TwinCAT message router.
        self.btn_conn_close = QtWidgets.QPushButton("Sulje yhteys", self)
        self.btn_conn_close.move(280, 10)
        self.btn_conn_close.resize(130, 28)
        self.btn_conn_close.clicked.connect(self.conn_close)

        # Text label for displaying the connection status.
        self.textconn = QtWidgets.QLabel(self)
        self.textconn.move(420, 15)
        self.textconn.setText("Yhteys: Kiinni")

        # Button for starting the read/write communication.
        self.btn_comm_start = QtWidgets.QPushButton("Aloita tiedonsiirto", self)
        self.btn_comm_start.move(150, 40)
        self.btn_comm_start.resize(130, 28)
        self.btn_comm_start.clicked.connect(self.comm_start)

        # Button for closing the read/write communication.
        self.btn_comm_stop = QtWidgets.QPushButton("Lopeta tiedonsiirto", self)
        self.btn_comm_stop.move(280, 40)
        self.btn_comm_stop.resize(130, 28)
        self.btn_comm_stop.clicked.connect(self.comm_stop)

        # Text label for displaying the read/write communication status.
        self.textcomm = QtWidgets.QLabel(self)
        self.textcomm.move(420, 45)
        self.textcomm.resize(300, 20)
        self.textcomm.setText("Tiedonsiirto: Keskeytetty")

        # Button for driving the car into the parking garage.
        self.btn_drive_in = QtWidgets.QPushButton("Aja sisään", self)
        self.btn_drive_in.move(10, 90)
        self.btn_drive_in.clicked.connect(self.drive_to_ls1)

        # Button for driving the car out from the parking garage.
        self.btn_drive_out = QtWidgets.QPushButton("Aja ulos", self)
        self.btn_drive_out.move(600, 90)
        self.btn_drive_out.clicked.connect(self.drive_to_ls3)

        # Button for resetting the car counter and hiding the cars.
        self.btn_s1 = QtWidgets.QPushButton("S1", self)
        self.btn_s1.move(10, 275)
        self.btn_s1.clicked.connect(self.reset_garage)

        # Text label for displaying the amount of the parked cars.
        self.textcars = QtWidgets.QLabel(self)
        self.textcars.move(10, 310)
        self.textcars.resize(100, 20)
        self.textcars.setText("Autot: " + str(self.counter))
    

    def set_parked_cars(self):
        """Create the cars that are parked in the parking garage."""
        for i in range(10):
            self.parked_cars.append(QtWidgets.QLabel(self))
        
            if i < 5:
                # The top row.
                xpos = 214 + i*58
                self.parked_cars[i].setPixmap(QtGui.QPixmap("img/car2.png"))
                self.parked_cars[i].move(xpos, 95)
            else:
                # The bottom row.
                xpos = 214 + (i-5)*58
                self.parked_cars[i].setPixmap(QtGui.QPixmap("img/car3.png"))
                self.parked_cars[i].move(xpos, 250)
            
            # Initially, all the parked cars are hidden.
            self.parked_cars[i].hide()


    @QtCore.pyqtSlot()
    def display_help(self):
        """Display the instructions in popup window."""
        pass


    @QtCore.pyqtSlot()
    def conn_open(self):
        """Open a connection with the TwinCAT message router."""
        try:
            self.conn = pyads.Connection(self.net_id, self.net_port)
            self.conn.open()
        except pyads.pyads_ex.ADSError as err:
            print(err)
        else:
            self.textconn.setText("Yhteys: Auki")


    @QtCore.pyqtSlot()
    def conn_close(self):
        """Close the connection with the TwinCAT message router."""
        if self.conn:
            self.conn.close()
            self.textconn.setText("Yhteys: Kiinni")


    @QtCore.pyqtSlot()
    def comm_start(self):
        """Start the read/write communication with the TwinCAT message router."""
        if self.conn:
            # Create and start threads.
            self.reader = OutputReader(self.conn)
            self.reader.signal.connect(self.handle_output)
            self.reader.start()

            self.writer = InputWriter()
            self.writer.signal.connect(self.handle_input)
            self.writer.start()

            self.textcomm.setText("Tiedonsiirto: Käynnissä")
            self.comm_running = True
        

    @QtCore.pyqtSlot()
    def comm_stop(self):
        """Stop the read/write communication with the TwinCAT message router."""
        if self.comm_running:
            self.reader.terminate()
            self.writer.terminate()
        
        self.textcomm.setText("Tiedonsiirto: Keskeytetty")
        self.car.move(self.xcar, self.ycar)
        self.barrier_in.setGeometry(QtCore.QRect(self.xbar_in, 160, 9, 99))
        self.barrier_out.setGeometry(QtCore.QRect(self.xbar_out, 160, 9, 99))


    @QtCore.pyqtSlot()
    def drive_to_ls1(self):
        """Move the car on the top of the light sensor LS1."""
        self.animation.move_car(
            self.car, self.xcar, self.xls1 - self.car.width() + self.excess
        )


    @QtCore.pyqtSlot()
    def drive_to_ls3(self):
        """Move the car out the top of the light sensor LS1."""
        if self.counter > 0:  # check that there are (visible) parked cars
            self.parked_cars[self.counter-1].hide()
            self.animation.move_car(
                self.car,
                self.xls3 - self.car.width() - 40,
                self.xls3 - self.car.width() + self.excess
            )


    @QtCore.pyqtSlot()
    def reset_garage(self):
        """Reset the parker cars in the parking garage."""
        self.counter = 0
        self.textcars.setText("Autot: " + str(self.counter))
        for i in range(10):
            self.parked_cars[i].hide()
        if self.conn:
            self.conn.write_by_name(config.Inputs.IS1.value, True, self.type)


    def handle_input(self):
        """Write the values of the PLC input variables."""
        self.conn.write_by_name(config.Inputs.IS1.value, False, self.type)
        
        # Check if the car is on the top of the light sensor LS1.
        if (self.xls1 - self.car.width()) <= self.car.x() and self.car.x() <= self.xls1:
            self.drive_in_permit = True
            self.conn.write_by_name(config.Inputs.ILS1.value, True, self.type)
        else:
            self.drive_in_permit = False
            self.conn.write_by_name(config.Inputs.ILS1.value, False, self.type)

        # Check the state of the barrier where the cars drive in.
        if self.barrier_in.height() == 10:  # the barrier has been raised
            self.conn.write_by_name(config.Inputs.IM11.value, True, self.type)
            self.conn.write_by_name(config.Inputs.IM12.value, False, self.type)
        elif self.barrier_in.height() == 99:  # the barrier has been lowered
            self.conn.write_by_name(config.Inputs.IM11.value, False, self.type)
            self.conn.write_by_name(config.Inputs.IM12.value, True, self.type)
        else:  # the barrier is moving between its upper and lower positions
            self.conn.write_by_name(config.Inputs.IM11.value, False, self.type)
            self.conn.write_by_name(config.Inputs.IM12.value, False, self.type)
        
        # Drive the car into the parking garage after the barrier has been raised.
        if self.drive_in_permit and self.barrier_in.height() == 10:
            if not self.car_is_moving:
                self.btn_drive_in.setEnabled(False)
                self.car_is_moving = True  # prevent multiple animations
                self.animation.move_car(self.car, self.car.x(), self.xls2 + 10)
        
        # Check if the car is on the top of the light sensor LS2.
        if (self.xls2 - self.car.width()) <= self.car.x() and self.car.x() <= self.xls2:
            self.conn.write_by_name(config.Inputs.ILS2.value, True, self.type)
        # Check if the car has passed the light sensor LS2.
        elif self.car.x() == (self.xls2 + 10) and self.car_is_moving:
            self.conn.write_by_name(config.Inputs.ILS2.value, False, self.type)
            self.car_is_moving = False  # allow the next car to move in
            self.counter += 1
            if self.counter <= 10:
                self.parked_cars[self.counter-1].show()
            else:
                self.counter = 10
            self.textcars.setText("Autot: " + str(self.counter))
            self.car.move(self.xcar, self.ycar)  # move the car back to start
            self.btn_drive_in.setEnabled(True)
        else:
            self.conn.write_by_name(config.Inputs.ILS2.value, False, self.type)
        
        if self.car.x() == (self.xls2 + 10) and not self.car_is_moving:
            self.car.move(self.xcar, self.ycar)
            self.btn_drive_in.setEnabled(True)
    
        # Check if the car is on the top of the light sensor LS3.
        if self.car.x() >= (self.xls3 - self.car.width()) and self.car.x() <= self.xls3:
            self.drive_out_permit = True
            self.conn.write_by_name(config.Inputs.ILS3.value, True, self.type)
        else:
            self.drive_out_permit = False
            self.conn.write_by_name(config.Inputs.ILS3.value, False, self.type)

        # Check the state of the barrier where the cars drive out.
        if self.barrier_out.height() == 10:  # the barrier has been raised
            self.conn.write_by_name(config.Inputs.IM21.value, True, self.type)
            self.conn.write_by_name(config.Inputs.IM22.value, False, self.type)
        elif self.barrier_out.height() == 99:  # the barrier has been lowered
            self.conn.write_by_name(config.Inputs.IM21.value, False, self.type)
            self.conn.write_by_name(config.Inputs.IM22.value, True, self.type)
        else:  # the barrier is moving between its upper and lower positions
            self.conn.write_by_name(config.Inputs.IM21.value, False, self.type)
            self.conn.write_by_name(config.Inputs.IM22.value, False, self.type)

        # Drive the car out from the parking garage after the barrier has been raised.
        if self.drive_out_permit and self.barrier_out.height() == 10:
            if not self.car_is_moving:
                self.car_is_moving = True  # prevent multiple animations
                self.animation.move_car(self.car, self.car.x(), self.xls4 + 10)

        # Check if the car is on the top of the light sensor LS4.
        if self.car.x() >= (self.xls4 - self.car.width()) and self.car.x() <= self.xls4:
            self.conn.write_by_name(config.Inputs.ILS4.value, True, self.type)
        # Check if the car has passed the light sensor LS4.
        elif self.car.x() == (self.xls4 + 10) and self.car_is_moving:
            self.conn.write_by_name(config.Inputs.ILS4.value, False, self.type)
            self.car_is_moving = False  # allow the next car to move out
            self.car.move(self.xcar, self.ycar)  # move the car back to start
            self.counter -= 1
            self.textcars.setText("Autot: " + str(self.counter))
        else:
            self.conn.write_by_name(config.Inputs.ILS4.value, False, self.type)


    def handle_output(self, data: dict):
        """
        Handle the case where the PLC output variable changed its state.

        :param dict data: The data that the signal emitted.
        """
        name = data["name"]
        value = data["value"]

        # Close the communication with the TwinCAT message router if e.g.
        # the output variable does not exists in the PLC program.
        if name == "error":
            self.commstatus = str(value)
            self.comm_stop()
        
        # Raise the barrier where the cars drive into the parking garage.
        if name == config.Outputs.QM1RAISE.value and value is True:
            self.animation.ctrl_barrier(self.barrier_in, self.xbar_in, "raise")
        # Lower the barrier where the cars drive into the parking garage.
        if name == config.Outputs.QM1LOWER.value and value is True:
            self.animation.ctrl_barrier(self.barrier_in, self.xbar_in, "lower")
        # Raise the barrier where the cars drive out from the parking garage.
        if name == config.Outputs.QM2RAISE.value and value is True:
            self.animation.ctrl_barrier(self.barrier_out, self.xbar_out, "raise")
        # Lower the barrier where the cars drive out from the parking garage.
        if name == config.Outputs.QM2LOWER.value and value is True:
            self.animation.ctrl_barrier(self.barrier_out, self.xbar_out, "lower")
        # The parking garage is full, show the red indication light.
        if name == config.Outputs.QH0.value and value is True:
            self.h0_green.hide()
            self.h0_red.show()
        # The parking garage has available parking slot(s).
        if name == config.Outputs.QH0.value and value is False:
            self.h0_green.show()
            self.h0_red.hide()


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    simulator = SimulatorApp()
    simulator.show()
    sys.exit(qapp.exec_())
