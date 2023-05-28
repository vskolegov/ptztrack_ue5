from PySide6 import QtGui
from PySide6.QtCore import QRegularExpression, Signal
from PySide6.QtGui import QColor, QPainter, Qt, QBrush, QPen, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QDialog, QGridLayout, QHBoxLayout, QLabel, \
    QScrollArea

from frontend.controllers import PTZCameras


class ColorCircleStatus(QWidget):
    color_ok = QColor('#27AE60')
    color_error = QColor('#E74C3C')

    colors = (color_error, color_ok)
    status = False

    def __init__(self, size):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(size, size)

    def set_status(self, status: bool):
        self.status = status
        self.repaint()

    def color(self):
        return self.colors[self.status]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.color(), 0, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(self.color(), Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(0, 0, self.width() - 1, self.width() - 1)
        painter.end()


class LabelStatusWidget(QWidget):
    def __init__(self, name):
        super().__init__()
        self.main_layout = QHBoxLayout()
        self.status = ColorCircleStatus(14)
        self.scene_name = QLabel(name)
        self.scene_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scene_name.setObjectName('LabelStatusLabel')
        self.setObjectName('LabelStatus')

        self.ui()

    def ui(self):
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addSpacing(5)
        self.main_layout.addWidget(self.scene_name, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)


class IpCreateWidget(QWidget):
    create = Signal(tuple)

    def __init__(self, ptz: PTZCameras):
        super().__init__()
        self.ptz = ptz
        self.main_layout = QHBoxLayout()

        ip_re = QRegularExpression(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        validator_ip = QRegularExpressionValidator(ip_re)

        port_re = QRegularExpression("[0-9]*")
        validator_port = QRegularExpressionValidator(port_re)

        self.ip = QLineEdit()
        self.ip.setValidator(validator_ip)
        self.ip.setPlaceholderText('ip')

        self.port = QLineEdit()
        self.port.setValidator(validator_port)
        self.port.setFixedWidth(60)
        self.port.setPlaceholderText('port')

        self.name = QLineEdit()
        self.name.setPlaceholderText('unreal name')

        self.btn_add = QPushButton('ADD')
        self.btn_add.clicked.connect(self.create_add)

        self.ui()

    def ui(self):
        self.main_layout.addWidget(self.ip)
        self.main_layout.addWidget(self.port)
        self.main_layout.addWidget(self.name)

        self.main_layout.addWidget(self.btn_add)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

    def create_add(self):
        d = (self.ip.text(), self.port.text(), self.name.text())
        if '' in d or len(d[0].split('.'))<4:
            return

        self.ip.clear()
        self.port.clear()
        self.name.clear()

        self.ptz.store(*d)
        self.create.emit(d)


class IpViewWidget(QWidget):
    def __init__(self, ptz: PTZCameras, socket: str, name: str):
        super().__init__()
        self.ptz = ptz
        self.current_ip = socket
        self.name = name

        self.main_layout = QHBoxLayout()
        self.status_camera = ColorCircleStatus(14)
        self.ip_line = QLineEdit(self.current_ip)
        self.ip_line.setFixedWidth(200)

        self.name = QLineEdit(name)
        self.name.setPlaceholderText('unreal name')

        self.btn_remove = QPushButton('REMOVE')
        self.btn_remove.clicked.connect(lambda: self.ptz.removeItem(self.current_ip))
        self.btn_remove.clicked.connect(self.hide)
        self.btn_edit = QPushButton('EDIT')
        self.btn_edit.clicked.connect(self.edit_camera)
        self.ui()

    def edit_camera(self):
        self.ptz.edit_camera(self.current_ip, self.ip_line.text(), self.name.text())
        self.current_ip = self.ip_line.text()

        print(self.ptz.get_storage())

    def ui(self):
        self.main_layout.addWidget(self.status_camera)
        self.main_layout.addSpacing(2)
        self.main_layout.addWidget(self.ip_line)
        self.main_layout.addWidget(self.name)
        self.main_layout.addWidget(self.btn_remove)
        self.main_layout.addWidget(self.btn_edit)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)


class IpList(QScrollArea):
    def __init__(self, ptz: PTZCameras):
        super().__init__()
        self.ptz = ptz
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.main_widget.setObjectName('IpList')
        self.setObjectName('IpList')
        self.set_ips()
        self.ui()

    def ui(self):
        self.setWidgetResizable(True)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.main_layout.addStretch()
        self.main_widget.setLayout(self.main_layout)
        self.setWidget(self.main_widget)
        # self.setLayout(self.main_layout)

    def set_ips(self):
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().setParent(None)

        for socket, name in self.ptz.get_cameras().items():
            self.add_widget(*socket, name)

    def add_widget(self, ip, port, name):
        self.main_layout.insertWidget(0, IpViewWidget(self.ptz, ':'.join((ip, port)), name))

    def edit_ip(self, ip):
        pass


class SettingsButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border-image: url(new_frontend/styles/settings.png); "
                           "padding: 0px; "
                           "background-color: none; "
                           "border: none;"
                           )


class InputDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_layout = QVBoxLayout()
        self.lineedit = QLineEdit()
        self.lineedit.setFixedSize(200, 40)
        self.btn_ok = QPushButton()
        self.btn_ok.clicked.connect(self.close)

        self.main_layout.addWidget(self.lineedit, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addSpacing(20)
        self.main_layout.addWidget(self.btn_ok, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.setFixedSize(250, 120)
        self.setLayout(self.main_layout)
        self.setObjectName('InputDialog')
        self.setStyleSheet(open('new_frontend/styles/main.qss').read())
