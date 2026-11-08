import csv
import datetime
import random
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QColorDialog, QComboBox, QDialog,
    QFileDialog, QGridLayout, QHBoxLayout, QHeaderView, QInputDialog,
    QLabel, QLCDNumber, QLineEdit, QMainWindow, QMessageBox,
    QProgressBar, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QTextBrowser, QVBoxLayout, QWidget,
)

from database import DatabaseManager
from dialogs import AdminEditorWindow, OverclockDialog


class MainWindow(QMainWindow):
    def __init__(self, profile_id, db_manager):
        super().__init__()
        self.profile_id = profile_id
        self.db = db_manager
        self.theme_color = "#00e676"

        self.setWindowTitle("Майнинг Ферма")
        self.resize(740, 600)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        status_layout = QHBoxLayout()
        status_layout.setSpacing(14)

        self.lbl_balance = QLabel("💰 $0.00")
        self.lbl_balance.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.lbl_balance.setStyleSheet("padding-right: 10px;")

        lbl_btc_icon = QLabel("🪙")
        lbl_btc_icon.setFont(QFont("Segoe UI", 11))

        self.lcd_crypto = QLCDNumber()
        self.lcd_crypto.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.lcd_crypto.setDigitCount(7)
        self.lcd_crypto.setFixedSize(85, 24)
        self.lcd_crypto.setStyleSheet(
            "border: 1px solid #444; background: #181818; color: #00e676;")

        self.bar_temp = QProgressBar()
        self.bar_temp.setRange(20, 100)
        self.bar_temp.setValue(24)
        self.bar_temp.setFixedSize(110, 20)
        self.bar_temp.setFormat("🌡️ %v°C")

        self.lbl_power = QLabel("⚡ 0 / 400 W")
        self.lbl_power.setFont(QFont("Segoe UI", 10))

        status_layout.addWidget(self.lbl_balance)
        status_layout.addWidget(lbl_btc_icon)
        status_layout.addWidget(self.lcd_crypto)
        status_layout.addWidget(self.bar_temp)
        status_layout.addWidget(self.lbl_power)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tabs)

        # Ферма
        self.tab_farm = QWidget()
        farm_layout = QVBoxLayout(self.tab_farm)
        self.grid_layout = QGridLayout()
        self.slot_buttons = []
        for i in range(16):
            btn = QPushButton(f"Слот {i + 1}\nПусто")
            btn.setFixedHeight(72)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda ch, idx=i: self.on_slot_clicked(idx))
            self.grid_layout.addWidget(btn, i // 4, i % 4)
            self.slot_buttons.append(btn)
        farm_layout.addLayout(self.grid_layout)

        click_layout = QHBoxLayout()
        btn_mine = QPushButton("⚡ Клик (+BTC)")
        btn_mine.setFixedHeight(28)
        btn_mine.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_mine.clicked.connect(self.manual_click_mine)
        click_layout.addWidget(btn_mine)
        click_layout.addWidget(QLabel(
            "Хоткеи: [Пробел] продувка | [1/2/3] режим | [F5] продать"))
        click_layout.addStretch()
        farm_layout.addLayout(click_layout)

        self.log_browser = QTextBrowser()
        self.log_browser.setFixedHeight(50)
        self.log_browser.setStyleSheet(
            "background: #181818; color: #aaa; border: 1px solid #333; "
            "border-radius: 4px; font-size: 11px;")
        farm_layout.addWidget(self.log_browser)
        self.tabs.addTab(self.tab_farm, "⛏️ Ферма")

        # Магазин
        self.tab_shop = QWidget()
        shop_layout = QVBoxLayout(self.tab_shop)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["Все", "GPU", "Cooler", "PSU"])
        self.combo_filter.currentTextChanged.connect(self.refresh_shop)
        filter_layout.addWidget(self.combo_filter)
        filter_layout.addStretch()
        shop_layout.addLayout(filter_layout)

        self.table_shop = QTableWidget()
        self.table_shop.setColumnCount(4)
        self.table_shop.setHorizontalHeaderLabels(
            ["Модель", "Хешрейт", "Нагрев", "Цена"])
        self.table_shop.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table_shop.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_shop.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        shop_layout.addWidget(self.table_shop)

        btn_buy = QPushButton("💰 Купить выбранное")
        btn_buy.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_buy.clicked.connect(self.buy_selected)
        shop_layout.addWidget(btn_buy)
        self.tabs.addTab(self.tab_shop, "🛒 Магазин")

        # Склад
        self.tab_inv = QWidget()
        inv_layout = QVBoxLayout(self.tab_inv)
        self.table_inv = QTableWidget()
        self.table_inv.setColumnCount(4)
        self.table_inv.setHorizontalHeaderLabels(
            ["Модель", "Категория", "Состояние", "Статус"])
        self.table_inv.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table_inv.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_inv.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_inv.itemDoubleClicked.connect(
            self.install_from_warehouse_table)
        inv_layout.addWidget(self.table_inv)

        inv_btns = QHBoxLayout()
        btn_sell_item = QPushButton("Продать выбранное со склада (70% цены)")
        btn_sell_item.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_sell_item.clicked.connect(self.sell_warehouse_item)
        inv_btns.addWidget(btn_sell_item)
        inv_btns.addWidget(
            QLabel("(Двойной клик по детали ставит её в свободный слот)"))
        inv_layout.addLayout(inv_btns)
        self.tabs.addTab(self.tab_inv, "📦 Склад")

        # Биржа
        self.tab_exchange = QWidget()
        ex_layout = QVBoxLayout(self.tab_exchange)
        self.lbl_rate = QLabel("Курс BTC: $60 000")
        self.lbl_rate.setFont(QFont("Arial", 14))
        ex_layout.addWidget(self.lbl_rate)

        btn_sell = QPushButton("💵 Продать всю крипту")
        btn_sell.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_sell.clicked.connect(self.sell_crypto)
        ex_layout.addWidget(btn_sell)

        self.table_history = QTableWidget()
        self.table_history.setColumnCount(4)
        self.table_history.setHorizontalHeaderLabels(
            ["Время", "Тип", "Сумма", "Детали"])
        self.table_history.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table_history.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_history.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        ex_layout.addWidget(self.table_history)
        self.tabs.addTab(self.tab_exchange, "💱 Биржа")

        file_menu = self.menuBar().addMenu("Файл")
        file_menu.addAction("Экспорт истории (.csv)", self.export_csv)
        file_menu.addAction("Техпаспорт фермы (.txt)", self.export_txt)

        settings_menu = self.menuBar().addMenu("Настройки")
        settings_menu.addAction("🎨 Цвет темы", self.change_theme)
        settings_menu.addAction("🛠 Админ-панель", self.open_admin)

        self.btc_rate = 60000.0
        self.power_mode = 1.0
        self.cool_boost = 0.0
        self.tick_counter = 0

        self.rate_timer = QTimer()
        self.rate_timer.timeout.connect(self.update_rate)
        self.rate_timer.start(3000)

        profile = self.db.get_profile(self.profile_id)
        if profile and profile['theme']:
            self.theme_color = profile['theme']

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_tick)
        self.timer.start(1000)

        self.update_stats()
        self.refresh_shop()
        self.refresh_inventory()
        self.refresh_history()
        self.log_event("Ферма готова к работе.", "#38bdf8")

    # тут html разметку для логов помогла сделать иишка
    def log_event(self, text, color="white"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_browser.append(
            f"<span style='color:#666;'>[{now}]</span> "
            f"<span style='color:{color};'>{text}</span>")

    def on_tab_changed(self, index):
        if index == 1:
            self.refresh_shop()
        elif index == 2:
            self.refresh_inventory()
        elif index == 3:
            self.refresh_history()

    # эту функцию подсчета ватт подсказала иишка
    def get_power_info(self, inventory):
        used_w = sum(
            max(0, i['watts']) for i in inventory
            if 0 <= i['slot_index'] < 16 and i['category'] != 'PSU')
        base_w = 400
        for i in inventory:
            if 0 <= i['slot_index'] < 16 and i['category'] == 'PSU':
                base_w += 850 if "850W" in i['name'] else 500
        return used_w, base_w

    def update_stats(self):
        profile = self.db.get_profile(self.profile_id)
        if profile:
            self.lbl_balance.setText(f"💰 ${profile['balance']:,.2f}")
            self.lcd_crypto.display(f"{profile['crypto_balance']:.5f}")

        inventory = self.db.get_inventory(self.profile_id)
        for btn in self.slot_buttons:
            btn.setText("Пусто")
            btn.setStyleSheet(
                "background-color: #1a1a1a; color: #555; "
                "border: 1px dashed #333; border-radius: 4px;")

        for item in inventory:
            slot = item['slot_index']
            if 0 <= slot < 16:
                self.slot_buttons[slot].setText(
                    f"{item['name']}\n{item['hashrate']} MH/s\n"
                    f"⚙️ {item['condition']:.0f}%")
                self.slot_buttons[slot].setStyleSheet(
                    f"background-color: #242424; color: white; "
                    f"border: 2px solid {self.theme_color}; "
                    f"border-radius: 4px;")

        used_w, limit_w = self.get_power_info(inventory)
        if used_w > limit_w:
            self.lbl_power.setText(f"⚡ {used_w} / {limit_w} W (ПЕРЕГРУЗКА!)")
            self.lbl_power.setStyleSheet("color: #ef4444; font-weight: bold;")
        else:
            self.lbl_power.setText(f"⚡ {used_w} / {limit_w} W")
            self.lbl_power.setStyleSheet("color: white;")

    def refresh_shop(self):
        cat_filter = self.combo_filter.currentText()
        self.table_shop.setRowCount(0)
        for item in self.db.get_catalog():
            if cat_filter != "Все" and item['category'] != cat_filter:
                continue
            row = self.table_shop.rowCount()
            self.table_shop.insertRow(row)
            heat_val = item['heat']
            heat_text = f"+{heat_val}°C" if heat_val > 0 else f"{heat_val}°C"
            self.table_shop.setItem(row, 0, QTableWidgetItem(item['name']))
            self.table_shop.setItem(
                row, 1, QTableWidgetItem(f"{item['hashrate']} MH/s"))
            self.table_shop.setItem(row, 2, QTableWidgetItem(heat_text))
            self.table_shop.setItem(
                row, 3, QTableWidgetItem(f"${item['price']:,.0f}"))
            self.table_shop.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, item['id'])

    def refresh_inventory(self):
        self.table_inv.setRowCount(0)
        for item in self.db.get_inventory(self.profile_id):
            if item['slot_index'] == -1:
                row = self.table_inv.rowCount()
                self.table_inv.insertRow(row)
                self.table_inv.setItem(row, 0, QTableWidgetItem(item['name']))
                self.table_inv.setItem(
                    row, 1, QTableWidgetItem(item['category']))
                self.table_inv.setItem(
                    row, 2, QTableWidgetItem(f"{item['condition']:.0f}%"))
                self.table_inv.setItem(row, 3, QTableWidgetItem("На складе"))
                self.table_inv.item(row, 0).setData(
                    Qt.ItemDataRole.UserRole, item['inv_id'])

    def install_from_warehouse_table(self, table_item):
        row = table_item.row()
        inv_id = self.table_inv.item(row, 0).data(Qt.ItemDataRole.UserRole)
        inventory = self.db.get_inventory(self.profile_id)

        target = next((i for i in inventory if i['inv_id'] == inv_id), None)
        if not target:
            return

        if target['category'] != 'PSU':
            used_w, limit_w = self.get_power_info(inventory)
            if used_w + target['watts'] > limit_w:
                QMessageBox.warning(
                    self, "Перегрузка БП",
                    "Не хватает мощности БП! Установите блок питания "
                    "в стойку.")
                return

        occupied = {i['slot_index'] for i in inventory if i['slot_index'] >= 0}
        free_slot = next((s for s in range(16) if s not in occupied), None)
        if free_slot is None:
            QMessageBox.warning(self, "Ошибка", "Все слоты заняты!")
            return
        if self.db.install_to_slot(inv_id, free_slot):
            self.update_stats()
            self.refresh_inventory()
            self.log_event(f"Установлен {target['name']}", "#10b981")

    def sell_warehouse_item(self):
        row = self.table_inv.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выбери деталь на складе!")
            return
        inv_id = self.table_inv.item(row, 0).data(Qt.ItemDataRole.UserRole)
        ok, price = self.db.sell_hardware(inv_id, self.profile_id)
        if ok:
            self.update_stats()
            self.refresh_inventory()
            self.refresh_history()
            self.log_event(f"Продано со склада за ${price}", "#f59e0b")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось продать деталь!")

    def manual_click_mine(self):
        self.db.manual_mine(self.profile_id, 0.000001)
        self.cool_boost = max(-10.0, self.cool_boost - 0.5)
        self.update_stats()

    # рандомайзер курса помогла набросать нейронка
    def update_rate(self):
        self.btc_rate = max(
            40000.0, min(90000.0, self.btc_rate + random.uniform(-800, 800)))
        self.lbl_rate.setText(f"Курс BTC: ${self.btc_rate:,.0f}")

    def sell_crypto(self):
        ok, earned = self.db.sell_crypto(self.profile_id, self.btc_rate)
        if ok:
            self.update_stats()
            self.refresh_history()
            self.log_event(f"Продано крипты на ${earned:.2f}", "#10b981")
            QMessageBox.information(
                self, "Успех", f"Продано крипты на ${earned:.2f}!")
        else:
            QMessageBox.warning(
                self, "Ошибка", "Нечего продавать, крипта на нуле!")

    def change_theme(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.theme_color = color.name()
            self.db.update_theme(self.profile_id, color.name())
            self.update_stats()

    def open_admin(self):
        password, ok = QInputDialog.getText(
            self, "Вход", "Пароль администратора:",
            echo=QLineEdit.EchoMode.Password)
        if ok and password == "admin":
            win = AdminEditorWindow(self.db)
            if win.exec() == QDialog.DialogCode.Accepted:
                self.refresh_shop()
        elif ok:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль!")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.cool_boost = min(self.cool_boost + 8.0, 30.0)
            self.log_event("Продувка охлаждения!", "#38bdf8")
        elif event.key() == Qt.Key.Key_F5:
            self.sell_crypto()
        elif event.key() in (Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3):
            self.power_mode = {
                Qt.Key.Key_1: 0.8,
                Qt.Key.Key_2: 1.0,
                Qt.Key.Key_3: 1.3,
            }[event.key()]
            self.log_event(f"Режим мощности: {self.power_mode}x", "#f59e0b")
        else:
            super().keyPressEvent(event)

    def game_tick(self):
        inventory = self.db.get_inventory(self.profile_id)
        used_w, limit_w = self.get_power_info(inventory)

        if used_w > limit_w:
            if self.tick_counter % 5 == 0:
                self.log_event(
                    "ОБЕСТОЧЕНО! Перегрузка БП, майнинг остановлен.",
                    "#ef4444")
            self.tick_counter += 1
            self.update_stats()
            return

        self.cool_boost = max(0.0, self.cool_boost - 1.0)
        self.tick_counter += 1

        heat = sum(i['heat'] for i in inventory if 0 <= i['slot_index'] < 16)
        temp = max(20.0, 24.0 + heat * self.power_mode - self.cool_boost)
        self.bar_temp.setValue(int(temp))

        if temp >= 90:
            self.bar_temp.setStyleSheet("QProgressBar::chunk { background-color: #ef4444; }")
        elif temp >= 75:
            self.bar_temp.setStyleSheet("QProgressBar::chunk { background-color: #f59e0b; }")
        else:
            self.bar_temp.setStyleSheet("QProgressBar::chunk { background-color: #10b981; }")

        is_throttling = (temp >= 90.0)
        if temp >= 100.0:
            self.log_event("ПЕРЕГРЕВ! Аварийная продувка фермы", "#ef4444")
            self.cool_boost += 25.0

        self.db.process_tick(self.profile_id, self.power_mode, is_throttling)

        # списание за электроэнергию
        if self.tick_counter % 10 == 0 and used_w > 0:
            cost = round(used_w * 0.006, 2)
            self.db.deduct_electricity(self.profile_id, cost)
            self.log_event(f"Списание за свет: -${cost}", "#94a3b8")

        self.update_stats()

    def refresh_history(self):
        self.table_history.setRowCount(0)
        for t in self.db.get_transactions(self.profile_id):
            row = self.table_history.rowCount()
            self.table_history.insertRow(row)
            amt = float(t['amount'])
            amt_str = f"+${amt:.2f}" if amt >= 0 else f"-${abs(amt):.2f}"
            self.table_history.setItem(
                row, 0, QTableWidgetItem(str(t['time'])))
            self.table_history.setItem(
                row, 1, QTableWidgetItem(str(t['type'])))
            self.table_history.setItem(row, 2, QTableWidgetItem(amt_str))
            self.table_history.setItem(
                row, 3, QTableWidgetItem(str(t['details'])))

    # тут написала иишка экспорт в csv с кодировкой
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить CSV", "transactions.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(
                    ["Время", "Тип", "Сумма ($)", "Курс BTC", "Детали"])
                for t in self.db.get_transactions(self.profile_id):
                    writer.writerow(
                        [t['time'], t['type'], t['amount'],
                         t['btc_rate'], t['details']])
            QMessageBox.information(
                self, "Готово", f"История сохранена:\n{path}")
        except Exception:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить файл!")

    # форматирование техпаспорта в txt написала нейронка
    def export_txt(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить TXT", "farm_passport.txt", "Text (*.txt)")
        if not path:
            return
        try:
            profile = self.db.get_profile(self.profile_id)
            inventory = self.db.get_inventory(self.profile_id)
            if not profile:
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    "=" * 42 + "\n   ТЕХПАСПОРТ МАЙНИНГ-ФЕРМЫ\n"
                    + "=" * 42 + "\n")
                f.write(f"Владелец: {profile['username']}\n")
                f.write(
                    f"Баланс: ${profile['balance']:,.2f} | "
                    f"Крипта: {profile['crypto_balance']:.5f} BTC\n\n"
                    "Оборудование:\n")
                for item in inventory:
                    slot = (item['slot_index'] if item['slot_index'] >= 0
                            else "склад")
                    f.write(
                        f"- {item['name']} | слот: {slot} | "
                        f"состояние: {item['condition']:.0f}%\n")
            QMessageBox.information(
                self, "Готово", f"Техпаспорт сохранён:\n{path}")
        except Exception:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить файл!")

    def buy_selected(self):
        row = self.table_shop.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выбери товар в магазине!")
            return
        catalog_id = self.table_shop.item(row, 0).data(
            Qt.ItemDataRole.UserRole)
        if self.db.buy_hardware(self.profile_id, catalog_id):
            self.update_stats()
            self.refresh_inventory()
            self.refresh_history()
            self.log_event("Куплено оборудование", "#10b981")
        else:
            QMessageBox.critical(self, "Ошибка", "Недостаточно средств!")

    def on_slot_clicked(self, slot_index):
        inventory = self.db.get_inventory(self.profile_id)
        item_in_slot = next(
            (item for item in inventory if item['slot_index'] == slot_index),
            None)

        if item_in_slot:
            dialog = OverclockDialog(item_in_slot, self.db, self.profile_id)
            dialog.exec()
            self.update_stats()
            self.refresh_inventory()
            self.refresh_history()
        else:
            on_warehouse = [
                item for item in inventory if item['slot_index'] == -1]
            if not on_warehouse:
                return

            if len(on_warehouse) == 1:
                chosen = on_warehouse[0]
            else:
                items_text = [
                    f"{item['name']} ({item['category']}, "
                    f"{item['condition']:.0f}%)"
                    for item in on_warehouse]
                chosen_text, ok = QInputDialog.getItem(
                    self, "Установка", "Выбери деталь:", items_text, 0, False)
                if not ok or not chosen_text:
                    return
                chosen = on_warehouse[items_text.index(chosen_text)]

            if chosen['category'] != 'PSU':
                used_w, limit_w = self.get_power_info(inventory)
                if used_w + chosen['watts'] > limit_w:
                    QMessageBox.warning(
                        self, "Перегрузка БП",
                        "Не хватает мощности БП! Установите блок питания "
                        "в стойку.")
                    return

            if self.db.install_to_slot(chosen['inv_id'], slot_index):
                self.update_stats()
                self.refresh_inventory()
                self.log_event(f"Установлен {chosen['name']}", "#10b981")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = DatabaseManager()
    profiles = db.get_profiles()
    test_id = profiles[0]['id'] if profiles else db.create_profile("Player")
    window = MainWindow(test_id, db)
    window.show()
    sys.exit(app.exec())
