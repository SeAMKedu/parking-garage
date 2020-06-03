from PyQt5 import QtCore


class PropertyAnimations(QtCore.QThread):
    """Show an animation on the UI."""
    def __init__(self):
        QtCore.QThread.__init__(self)


    @QtCore.pyqtSlot()
    def move_car(self, car: object, start: int, end: int):
        """
        Move the position of the car.

        :param object car: The car to be moved.
        :param int start: The start point of the animation.
        :param int end: The end point of the animation.
        """
        self.car_anim = QtCore.QPropertyAnimation(car, b"pos")
        self.car_anim.setStartValue(QtCore.QPoint(start, 185))
        self.car_anim.setEndValue(QtCore.QPoint(end, 185))
        self.car_anim.setDuration(3000)  # 3 seconds
        self.car_anim.start()


    @QtCore.pyqtSlot()
    def ctrl_barrier(self, barrier: object, xpos: int, action: str):
        """
        Raise or lower the barrier of the parking garage.

        :param object barrier: The barrier to be controlled.
        :param int xpos: The X position of the barrier.
        :param str action: The action to be performed, raise/lower.
        """
        self.bar_anim = QtCore.QPropertyAnimation(barrier, b"geometry")
        if action == "raise":
            self.height1 = 99
            self.height2 = 10
        elif action == "lower":
            self.height1 = 10
            self.height2 = 99
        # QRect(xpos, ypos, width, height)
        self.bar_anim.setStartValue(QtCore.QRect(xpos, 160, 9, self.height1))
        self.bar_anim.setEndValue(QtCore.QRect(xpos, 160, 9, self.height2))
        self.bar_anim.setDuration(4000)
        self.bar_anim.start()