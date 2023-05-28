from typing import Union

from PySide6.QtCore import Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QComboBox, QPushButton, QLineEdit, \
    QLabel, QInputDialog, QGridLayout, QGroupBox, QFormLayout

from .controllers import PTZCameras, ServerHandler
from .widgets import ColorCircleStatus, InputDialog, LabelStatusWidget, IpList, IpCreateWidget, SettingsButton


class MainWindow(QMainWindow):
    def __init__(self, ptz: PTZCameras):
        super().__init__()
        self.index = None
        self.ptz = ptz
        self.__current_scene = None
        self.server_handler = ServerHandler(self.ptz)
        self.server_handler.start()
        self.window_select_scene()

    def set_window(self, frame: Union[QWidget, QFrame]):
        self.setCentralWidget(frame)

    @property
    def current_scene(self):
        return self.__current_scene

    @current_scene.setter
    def current_scene(self, widget):
        self.setCentralWidget(widget)
        self.__current_scene = widget

    def window_select_scene(self):
        self.current_scene = SelectSceneWindow()
        self.current_scene.set_scenes_combo(self.ptz.get_scenes())
        if self.index is not None:
            self.current_scene.combo_scenes.setCurrentIndex(self.index)
        self.current_scene.create_signal.connect(self.ptz.add_new_scene)
        self.current_scene.create_signal.connect(self.set_scene)
        self.current_scene.edit_btn.clicked.connect(self.edit_scene_select)

    def window_edit_scene(self):
        self.index = self.current_scene.combo_scenes.currentIndex()
        self.current_scene = EditSceneWindow(self.ptz)
        self.current_scene.exit_btn.clicked.connect(self.window_select_scene)
        self.current_scene.settings_btn.clicked.connect(self.set_settings_window)
        self.server_handler.unreal_status_signal.connect(self.current_scene.scene_status.status.set_status)

    def set_settings_window(self):
        settings_w = SettingsWindow(self.ptz)
        settings_w.btn_close.clicked.connect(self.window_edit_scene)
        self.setCentralWidget(settings_w)

    def edit_scene_select(self):
        self.set_scene(self.current_scene.combo_scenes.currentText())

    def set_scene(self, scene_name=None):
        if scene_name is not None:
            self.ptz.load_scene(scene_name)

        self.window_edit_scene()


class SelectSceneWindow(QWidget):
    create_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.btn_layout = QHBoxLayout()

        self.title = QLabel('PTZ Cameras')
        self.title.setObjectName('TitleLabel')

        self.combo_scenes = QComboBox()
        # self.scene_name = QLineEdit()
        # self.combo_scenes.setLineEdit(self.scene_name)
        self.combo_scenes.setFixedSize(300, 40)

        # self.open_btn = QPushButton('Open')
        # self.open_btn.setFixedSize(300, 40)

        self.add_btn = QPushButton('Add New Scene')
        self.add_btn.setFixedSize(150, 40)
        self.add_btn.clicked.connect(self.show_dialog_scene)

        self.edit_btn = QPushButton('Select Scene')
        self.edit_btn.setFixedSize(100, 40)

        self.ui()

    def ui(self):
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addSpacing(100)
        self.main_layout.addWidget(self.combo_scenes, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addSpacing(10)
        # self.main_layout.addWidget(self.open_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addSpacing(45)
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addStretch()

        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addStretch()
        self.main_layout.addStretch()

        self.setLayout(self.main_layout)

    def show_dialog_scene(self):
        d = InputDialog(self)
        d.setWindowTitle('Create new scene')
        d.btn_ok.setText('Create')
        d.btn_ok.clicked.connect(lambda: self.create_scene(d.lineedit))
        d.exec()

    def create_scene(self, lineedit: QLineEdit):
        self.create_signal.emit(lineedit.text())

    def set_scenes_combo(self, data: list):
        self.combo_scenes.clear()
        self.combo_scenes.addItems(data)


class EditSceneWindow(QWidget):
    is_server_start = False
    btn_start_texts = ('START', 'STOP')

    def __init__(self, ptz: PTZCameras):
        super().__init__()
        self.ptz = ptz

        self.add_camera = IpCreateWidget(ptz)

        self.initialize_cameras_btn = QPushButton('INITIALIZE CAMERAS')
        self.initialize_cameras_btn.clicked.connect(self.save_data)

        self.ip_list = IpList(self.ptz)
        self.add_camera.create.connect(lambda d: self.ip_list.add_widget(*d))

        self.scene_status = LabelStatusWidget(self.ptz.current_scene)
        self.work_status = LabelStatusWidget('Work Status')

        self.start_btn = QPushButton(self.btn_start_texts[self.is_server_start])
        self.start_btn.clicked.connect(self.server_start_stop)

        self.exit_btn = QPushButton('Edit Scene')

        self.settings_btn = SettingsButton()

        self.main_layout = QHBoxLayout()
        self.l_layout = QVBoxLayout()
        self.r_layout = QVBoxLayout()
        self.top_l_layout = QHBoxLayout()
        self.bottom_r_layout = QHBoxLayout()
        self.ui()

    def ui(self):
        self.work_status.scene_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.scene_status.scene_name.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.start_btn.setFixedWidth(100)
        self.exit_btn.setFixedWidth(175)
        self.settings_btn.setFixedSize(60, 60)

        self.scene_status.scene_name.setFixedWidth(280)
        self.work_status.scene_name.setFixedWidth(280)

        self.top_l_layout.addWidget(self.add_camera)
        self.top_l_layout.addWidget(self.initialize_cameras_btn)
        self.l_layout.addLayout(self.top_l_layout)
        self.l_layout.addWidget(self.ip_list)
        # self.l_layout.addStretch()

        self.r_layout.setContentsMargins(10, 0, 10, 0)

        self.r_layout.addWidget(self.scene_status, alignment=Qt.AlignmentFlag.AlignCenter)
        self.r_layout.addWidget(self.work_status, alignment=Qt.AlignmentFlag.AlignCenter)

        self.bottom_r_layout.addSpacing(25)
        self.bottom_r_layout.addStretch()
        self.bottom_r_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.bottom_r_layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.bottom_r_layout.addStretch()
        self.r_layout.addLayout(self.bottom_r_layout)
        self.r_layout.addStretch()
        self.r_layout.addWidget(self.settings_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.r_layout.addSpacing(10)

        # self.main_layout.addWidget(self.scene_status)
        # self.main_layout.addWidget(self.ip_list)
        #
        # self.main_layout.addWidget(self.work_status)
        #
        # self.main_layout.addWidget(self.start_btn)
        # self.main_layout.addWidget(self.exit_btn)

        self.main_layout.addLayout(self.l_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.r_layout)
        self.setLayout(self.main_layout)

    def save_data(self):
        if self.is_server_start:
            self.start_btn.clicked.emit()
        self.ptz.cameras_save()

    def server_start_stop(self):
        self.is_server_start = not self.is_server_start
        self.start_btn.setText(self.btn_start_texts[self.is_server_start])
        if self.is_server_start:
            self.ptz.start_scene()
        else:
            self.ptz.stop_scene()


class SettingsWindow(QWidget):
    def __init__(self, ptz: PTZCameras):
        super().__init__()
        self.ptz = ptz
        self.main_layout = QVBoxLayout()
        self.btn_layout = QHBoxLayout()

        self.btn_save = QPushButton('save')
        self.btn_close = QPushButton('close')

        layout = QFormLayout()
        layout.addRow(QLabel("x:"), QLineEdit())
        layout.addRow(QLabel("y:"), QLineEdit())
        layout.addRow(QLabel("z:"), QLineEdit())

        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_close)
        self.btn_layout.addWidget(self.btn_save)

        self.main_layout.addLayout(layout)
        self.main_layout.addLayout(self.btn_layout)
        self.setLayout(self.main_layout)
