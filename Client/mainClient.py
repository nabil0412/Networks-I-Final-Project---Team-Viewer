from PyQt5 import QtWidgets, QtCore  # Add QtCore import
from pyqt5.design import Ui_MainWindow
from clientLogic.Client0 import Client

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Password)
        self.connectButton.clicked.connect(self.on_connect)
        self.hiddingButton.stateChanged.connect(self.on_check)
        
    def on_check(self):
        if self.hiddingButton.isChecked():
            self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Password)

    def on_connect(self):
        ip_address_input = self.ipAddressInput.text()
        password_input = self.passwordInput.text()
        if password_input == "" or ip_address_input == "":
            self.connectionStatus.setText("Data Missing")
            self.connectionStatus.setStyleSheet("color: red")
        else:
            print(f"Connecting to {ip_address_input} with password {password_input}")
            self.start_client(ip_address_input, password_input)

    def start_client(self, ip_address_input, password_input):
        self.client = Client(ip_address_input, 1234)
        self.client.start(password_input)
        if self.client.connection == True:
            self.connectionStatus.setText("Connected")
            self.connectionStatus.setStyleSheet("color: green")
            self.connectButton.setEnabled(False)
            self.connectButton.setStyleSheet("background-color: lightgray")
        else:
            self.connectionStatus.setText("Incorrect Data")
            self.connectionStatus.setStyleSheet("color: red")
            QtCore.QTimer.singleShot(3, self.close) 


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
