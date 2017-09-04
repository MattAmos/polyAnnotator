#! python3
#! PY_PYTHON=3

import sys
from PyQt5.QtWidgets import QApplication
from mainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())