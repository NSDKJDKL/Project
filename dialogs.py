from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QComboBox, QLineEdit, 
QPushButton, QLabel, QFileDialog, QMessageBox, QApplication)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from database import DatabaseManager
import sys


class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.profile_id = None
        self.avatar_path = ""
        
        self.setWindowTitle("Вход в Ферму")
        self.setFixedWidth(350)
        
        layout = QVBoxLayout()
        
        # список профилей
        self.combo_profiles = QComboBox()
        self.load_profiles()
        layout.addWidget(QLabel("Выбери майнера:"))
        layout.addWidget(self.combo_profiles)
        
        # поле для нового имени
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Или введи новое имя...")
        layout.addWidget(self.input_name)
        
        # аватарка
        self.avatar_label = QLabel("Аватар не выбран")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_avatar = QPushButton("Выбрать аватарку")
        btn_avatar.clicked.connect(self.choose_avatar)
        layout.addWidget(self.avatar_label)
        layout.addWidget(btn_avatar)
        
        # кнопка входа
        btn_login = QPushButton("Начать майнить")
        btn_login.clicked.connect(self.login_or_create)
        layout.addWidget(btn_login)
        
        self.setLayout(layout)
    
    def load_profiles(self):
        self.combo_profiles.clear()
        profiles = self.db.get_profiles()
        for p in profiles:
            self.combo_profiles.addItem(f"{p['username']} (ID: {p['id']})", p['id'])

    def choose_avatar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать фото", "", "Картинки (*.png *.jpg)")
        if path:
            self.avatar_path = path
            pixmap = QPixmap(path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            self.avatar_label.setPixmap(pixmap)

    def login_or_create(self):
        name = self.input_name.text().strip()
        
        if name:
            new_id = self.db.create_profile(name)
            if self.avatar_path:
                self.db.update_avatar(new_id, self.avatar_path)
            self.profile_id = new_id
            self.accept()
        else:
            if self.combo_profiles.count() > 0:
                self.profile_id = self.combo_profiles.currentData()
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Введи имя или выбери профиль!")
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
    