from PyQt5 import QtWidgets
from pyqt5.design import Ui_myServer
from serverLogic.Server0 import Server

class MainWindow(QtWidgets.QMainWindow, Ui_myServer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.startServerButton.clicked.connect(self.on_connect)

    def on_connect(self):
        server_password_input = self.serverPasswordInput.text()
        if server_password_input == "" :
            self.statusLabel.setText("Data Missing")
            self.statusLabel.setStyleSheet("color: red")
        else:
            server_password = self.serverPasswordInput.text()
            self.start_server(server_password)

    def start_server(self, password):
        self.server = Server(None, 1234, password)
        self.server.start()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
