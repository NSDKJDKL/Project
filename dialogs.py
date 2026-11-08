import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QDoubleSpinBox, QFileDialog,
QFormLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit,QMessageBox, QProgressBar, 
QPushButton, QSlider, QSpinBox,QVBoxLayout,)

from database import DatabaseManager


class AuthWindow(QDialog):
    def __init__(self, db_manager=None):
        super().__init__()
        self.db = db_manager or DatabaseManager()
        self.profile_id = None
        self.avatar_path = ""
        self.promo_bonus = 0.0

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

        btn_promo = QPushButton("Ввести промокод")
        btn_promo.clicked.connect(self.use_promo)
        layout.addWidget(btn_promo)

        # кнопка входа
        btn_login = QPushButton("Начать майнить")
        btn_login.clicked.connect(self.login_or_create)
        layout.addWidget(btn_login)
        self.setLayout(layout)

    def load_profiles(self):
        self.combo_profiles.clear()
        for p in self.db.get_profiles():
            self.combo_profiles.addItem(
                f"{p['username']} (ID: {p['id']})", p['id'])

    # этот кусок помогла сделай иишка
    def choose_avatar(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать фото", "", "Картинки (*.png *.jpg *.jpeg)")
        if path:
            self.avatar_path = path
            pixmap = QPixmap(path).scaled(
                100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            self.avatar_label.setPixmap(pixmap)

    def use_promo(self):
        code, ok = QInputDialog.getText(
            self, "Промокод", "Введи стартовый промокод:")
        if ok and code.strip().upper() in ("YANDEX", "START", "2026"):
            self.promo_bonus = 100.0
            QMessageBox.information(
                self, "Успех", "Промокод активирован! +$100 игроку.")
        elif ok:
            QMessageBox.warning(self, "Ошибка", "Неверный промокод!")

    def login_or_create(self):
        name = self.input_name.text().strip()
        if name:
            new_id = self.db.create_profile(name)
            if self.avatar_path:
                self.db.update_avatar(new_id, self.avatar_path)
            if self.promo_bonus > 0:
                self.db.add_fiat(new_id, self.promo_bonus, "Промокод")
            self.profile_id = new_id
            self.accept()
        elif self.combo_profiles.count() > 0:
            self.profile_id = self.combo_profiles.currentData()
            self.accept()
        else:
            QMessageBox.warning(
                self, "Ошибка", "Введи имя или выбери профиль!")


class OverclockDialog(QDialog):
    def __init__(self, item_data, db_manager, profile_id):
        super().__init__()
        self.db = db_manager
        self.profile_id = profile_id
        self.inv_id = item_data['inv_id']
        self.is_gpu = (item_data['category'] == 'GPU')

        self.setWindowTitle(f"Стенд: {item_data['name']}")
        self.setFixedWidth(400)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            f"<h3>{item_data['name']} ({item_data['category']})</h3>"))

        layout.addWidget(QLabel("⚙️ Разгон (Мощность):"))
        self.slider_oc = QSlider(Qt.Orientation.Horizontal)
        self.slider_oc.setMinimum(50)
        self.slider_oc.setMaximum(150)
        self.slider_oc.setValue(item_data['overclock'])

        self.lbl_oc_value = QLabel(f"{item_data['overclock']}%")
        self.slider_oc.valueChanged.connect(
            lambda val: self.lbl_oc_value.setText(f"{val}%"))
        if not self.is_gpu:
            self.slider_oc.setEnabled(False)
            self.lbl_oc_value.setText(
                f"{item_data['overclock']}% (только для GPU)")

        layout.addWidget(self.slider_oc)
        layout.addWidget(self.lbl_oc_value)

        layout.addWidget(QLabel("🔋 Техническое состояние:"))
        self.bar_condition = QProgressBar()
        self.bar_condition.setRange(0, 100)
        self.bar_condition.setValue(int(item_data['condition']))
        layout.addWidget(self.bar_condition)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Сохранить")
        btn_save.clicked.connect(self.save_overclock)
        btn_repair = QPushButton("🔧 Починить")
        btn_repair.clicked.connect(self.repair)
        btn_remove = QPushButton("📦 На склад")
        btn_remove.clicked.connect(self.remove_to_inventory)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_repair)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save_overclock(self):
        self.db.update_overclock(self.inv_id, self.slider_oc.value())
        self.accept()

    def repair(self):
        if self.bar_condition.value() >= 100:
            QMessageBox.information(
                self, "Информация", "Устройство и так целое (100%)!")
            return
        ok, cost = self.db.repair_item(self.inv_id, self.profile_id)
        if ok:
            self.bar_condition.setValue(100)
            QMessageBox.information(
                self, "Успех", f"Отремонтировано за ${cost:.2f}!")
        else:
            QMessageBox.critical(
                self, "Ошибка",
                f"Не хватает денег (нужно ${cost:.2f})!")

    def remove_to_inventory(self):
        self.db.update_slot(self.inv_id, -1)
        self.accept()


# админку и форму QFormLayout полностью набросала иишка
class AdminEditorWindow(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setWindowTitle("Админ-панель: новый товар")
        self.setFixedWidth(360)
        layout = QVBoxLayout()
        form = QFormLayout()

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("RTX 5090")

        self.combo_cat = QComboBox()
        self.combo_cat.addItems(["GPU", "Cooler", "PSU"])

        self.spin_hash = QDoubleSpinBox()
        self.spin_hash.setRange(0, 1000)
        self.spin_hash.setSuffix(" MH/s")

        self.spin_watts = QSpinBox()
        self.spin_watts.setRange(-2000, 2000)
        self.spin_watts.setSuffix(" W")

        self.spin_heat = QDoubleSpinBox()
        self.spin_heat.setRange(-50, 50)
        self.spin_heat.setSuffix(" °C")

        self.spin_price = QDoubleSpinBox()
        self.spin_price.setRange(1, 100000)
        self.spin_price.setSuffix(" $")
        self.spin_price.setValue(500)

        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Описание")

        form.addRow("Название:", self.input_name)
        form.addRow("Категория:", self.combo_cat)
        form.addRow("Хешрейт:", self.spin_hash)
        form.addRow("Ватты:", self.spin_watts)
        form.addRow("Нагрев:", self.spin_heat)
        form.addRow("Цена:", self.spin_price)
        form.addRow("Описание:", self.input_desc)
        layout.addLayout(form)

        btn_save = QPushButton("💾 Добавить в магазин")
        btn_save.clicked.connect(self.save_item)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def save_item(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введи название!")
            return
        self.db.add_to_catalog(
            name, self.combo_cat.currentText(), self.spin_hash.value(),
            self.spin_watts.value(), self.spin_heat.value(),
            self.spin_price.value(), self.input_desc.text().strip())
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
