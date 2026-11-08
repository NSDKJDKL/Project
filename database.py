import sqlite3
import datetime


class DatabaseManager:
    def __init__(self, db_name="mining_farm.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.seed_catalog()

    def create_tables(self):
        cur = self.conn.cursor()

        # 1 таблица - профиль игрока
        cur.execute("""CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            balance REAL DEFAULT 200.0,
            crypto_balance REAL DEFAULT 0.0,
            avatar TEXT DEFAULT '',
            theme TEXT DEFAULT '#00e676'
        )""")

        # 2 таблица - профиль карточек с видеокартами таам охлаждением и тд
        cur.execute("""CREATE TABLE IF NOT EXISTS catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            hashrate REAL DEFAULT 0.0,
            watts INTEGER DEFAULT 0,
            heat REAL DEFAULT 0.0,
            price REAL DEFAULT 100.0,
            image TEXT DEFAULT '',
            description TEXT DEFAULT ''
        )""")

        # 3 таблица - склад, инвентарь купленных товаров
        cur.execute("""CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            hardware_id INTEGER NOT NULL,
            slot_index INTEGER DEFAULT -1,
            overclock INTEGER DEFAULT 100,
            condition REAL DEFAULT 100.0,
            FOREIGN KEY (profile_id) REFERENCES profiles (id),
            FOREIGN KEY (hardware_id) REFERENCES catalog (id)
        )""")

        # 4 таблица - история финансов, все транзакции
        cur.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            time TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            btc_rate REAL NOT NULL,
            details TEXT NOT NULL,
            FOREIGN KEY (profile_id) REFERENCES profiles (id)
        )""")
        self.conn.commit()

    def get_profiles(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM profiles")
        return cur.fetchall()

    def create_profile(self, name):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO profiles (username, balance) VALUES (?, 200.0)", (name,))
        self.conn.commit()
        return cur.lastrowid

    def get_profile(self, profile_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        return cur.fetchone()

    def get_catalog(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM catalog")
        return cur.fetchall()

    def update_avatar(self, profile_id, avatar_path):
        cur = self.conn.cursor()
        cur.execute("UPDATE profiles SET avatar = ? WHERE id = ?", (avatar_path, profile_id))
        self.conn.commit()

    def install_to_slot(self, inv_id, slot_index):
        cur = self.conn.cursor()
        cur.execute("""SELECT id FROM inventory
                       WHERE profile_id = (SELECT profile_id FROM inventory WHERE id = ?)
                       AND slot_index = ?""", (inv_id, slot_index))
        if cur.fetchone():
            return False
        cur.execute("UPDATE inventory SET slot_index = ? WHERE id = ?", (slot_index, inv_id))
        self.conn.commit()
        return True

    def update_overclock(self, inv_id, overclock):
        cur = self.conn.cursor()
        cur.execute("UPDATE inventory SET overclock = ? WHERE id = ?", (overclock, inv_id))
        self.conn.commit()

    # эту функцию мне помогла написать нейронка (расчет ремонта) ну потому
    # что я тут хз как и что не допер
    def repair_item(self, inv_id, profile_id):
        cur = self.conn.cursor()
        cur.execute("""SELECT inv.condition, cat.price, cat.name
                    FROM inventory inv
                    JOIN catalog cat ON inv.hardware_id = cat.id
                    WHERE inv.id = ? AND inv.profile_id = ?""",
                    (inv_id, profile_id))
        item = cur.fetchone()
        if not item or item["condition"] >= 100.0:
            return False, 0.0

        wear = 100.0 - item["condition"]
        cost = max(5.0, round(wear * (item["price"] / 100.0) * 0.35, 2))

        cur.execute("SELECT balance FROM profiles WHERE id = ?", (profile_id,))
        prof = cur.fetchone()
        if not prof or prof["balance"] < cost:
            return False, cost

        try:
            cur.execute("""UPDATE inventory
                        SET condition = 100.0 WHERE id = ?""", (inv_id,))
            cur.execute("""UPDATE profiles SET balance = balance - ?
                           WHERE id = ?""", (cost, profile_id))
            self.add_transaction(profile_id, "REPAIR", -cost, 0, f"Ремонт {item['name']}")
            self.conn.commit()
            return True, cost
        except Exception:
            self.conn.rollback()
            return False, cost

    def sell_crypto(self, profile_id, btc_rate):
        cur = self.conn.cursor()
        cur.execute("SELECT crypto_balance FROM profiles WHERE id = ?",
                    (profile_id,))
        row = cur.fetchone()
        if row is None or row["crypto_balance"] <= 0:
            return False, 0.0

        crypto = row["crypto_balance"]
        earned = crypto * btc_rate
        try:
            cur.execute("""UPDATE profiles SET balance = balance + ?,
                           crypto_balance = 0.0 WHERE id = ?""", (earned, profile_id))
            self.add_transaction(profile_id, "SELL", earned, btc_rate, f"Продано {crypto:.5f} BTC")
            self.conn.commit()
            return True, earned
        except Exception:
            self.conn.rollback()
            return False, 0.0

    def add_to_catalog(self, name, category, hashrate, watts, heat, price, description):
        cur = self.conn.cursor()
        cur.execute("""INSERT INTO catalog (name, category, hashrate,
                    watts, heat, price, image,
                    description)
                    VALUES (?, ?, ?, ?, ?, ?, '', ?)""",
                    (name, category, hashrate, watts, heat, price, description))
        self.conn.commit()

    # тут подсмотрел у иишки для базы транзакций
    def add_transaction(self, profile_id, op_type, amount, btc_rate, details):
        cur = self.conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cur.execute("""INSERT INTO transactions (profile_id, time, type, amount, btc_rate, details)
                    VALUES (?, ?, ?, ?, ?, ?)""", (profile_id, now_str, op_type, amount, btc_rate,details))
        self.conn.commit()

    def update_theme(self, profile_id, color):
        cur = self.conn.cursor()
        cur.execute("UPDATE profiles SET theme = ? WHERE id = ?", (color, profile_id))
        self.conn.commit()

    def process_tick(self, profile_id, power_mode=1.0, is_throttling=False):
        cur = self.conn.cursor()
        cur.execute("""SELECT inv.id, inv.overclock, inv.condition,
                        cat.hashrate, cat.category
                        FROM inventory inv
                        JOIN catalog cat ON inv.hardware_id = cat.id
                        WHERE inv.profile_id = ? AND inv.slot_index >= 0""",
                    (profile_id,))
        items = cur.fetchall()

        total_hashrate = 0.0
        for it in items:
            if it["category"] == "GPU" and it["condition"] > 0:
                total_hashrate += it["hashrate"] * (it["overclock"] / 100.0)
        total_hashrate *= power_mode
        if is_throttling:
            total_hashrate *= 0.5

        if total_hashrate > 0:
            earned = total_hashrate * 0.0000001
            cur.execute("""UPDATE profiles SET
                           crypto_balance = crypto_balance + ?
                           WHERE id = ?""", (earned, profile_id))
            wear = 0.15 * power_mode * (1.8 if is_throttling else 1.0)
            for it in items:
                if it["category"] == "GPU":
                    cur.execute("""UPDATE inventory SET condition = MAX(0, condition - ?)
                                   WHERE id = ?""", (wear, it["id"]))
        self.conn.commit()

    def deduct_electricity(self, profile_id, cost):
        cur = self.conn.cursor()
        cur.execute("UPDATE profiles SET balance = balance - ? WHERE id = ?", (cost, profile_id))
        self.add_transaction(profile_id, "POWER", -cost, 0, "Электроэнергия")
        self.conn.commit()

    def manual_mine(self, profile_id, amount=0.000001):
        cur = self.conn.cursor()
        cur.execute("""UPDATE profiles
                       SET crypto_balance = crypto_balance + ?
                       WHERE id = ?""", (amount, profile_id))
        self.conn.commit()

    def add_fiat(self, profile_id, amount, reason="Бонус"):
        cur = self.conn.cursor()
        cur.execute("UPDATE profiles SET balance = balance + ? WHERE id = ?", (amount, profile_id))
        self.add_transaction(profile_id, "BONUS", amount, 0, reason)
        self.conn.commit()

    def sell_hardware(self, inv_id, profile_id):
        cur = self.conn.cursor()
        cur.execute("""SELECT inv.id, cat.price, cat.name
                       FROM inventory inv
                       JOIN catalog cat ON inv.hardware_id = cat.id
                       WHERE inv.id = ? AND inv.profile_id = ?""",
                    (inv_id, profile_id))
        item = cur.fetchone()
        if not item:
            return False, 0.0

        sell_price = round(item["price"] * 0.7, 2)
        try:
            cur.execute("DELETE FROM inventory WHERE id = ?", (inv_id,))
            cur.execute("""UPDATE profiles SET balance = balance + ?
                           WHERE id = ?""", (sell_price, profile_id))
            self.add_transaction(profile_id, "SELL_ITEM", sell_price, 0, f"Продан {item['name']}")
            self.conn.commit()
            return True, sell_price
        except Exception:
            self.conn.rollback()
            return False, 0.0

    def update_slot(self, inv_id, slot_index):
        cur = self.conn.cursor()
        cur.execute("UPDATE inventory SET slot_index = ? WHERE id = ?", (slot_index, inv_id))
        self.conn.commit()

    def get_transactions(self, profile_id):
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM transactions
                       WHERE profile_id = ? ORDER BY id DESC""", (profile_id,))
        return cur.fetchall()

    def del_profile(self, profile_id):
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM transactions WHERE profile_id = ?", (profile_id,))
            cur.execute("DELETE FROM inventory WHERE profile_id = ?", (profile_id,))
            cur.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False

    def get_inventory(self, profile_id):
        cur = self.conn.cursor()
        cur.execute("""SELECT inv.id as inv_id, inv.slot_index,
                        inv.overclock, inv.condition, cat.name,
                        cat.category, cat.hashrate, cat.watts, cat.heat
                        FROM inventory inv
                        JOIN catalog cat ON inv.hardware_id = cat.id
                        WHERE inv.profile_id = ?""", (profile_id,))
        return cur.fetchall()

    # тут написала иишка, нагенерила датасет железа со статами,
    # мне было тяжело составлять баланс, она тут как то криво список сделала
    def seed_catalog(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM catalog")
        if cur.fetchone()[0] <= 6:
            items = [
                ("GTX 1050 Ti", "GPU", 12.0, 65, 1.5, 120.0,
                 "", "Бюджетный старт"),
                ("GTX 1660 Super", "GPU", 30.0, 125, 3.0, 250.0,
                 "", "Рабочая лошадка"),
                ("RTX 3060", "GPU", 50.0, 170, 5.0, 450.0,
                 "", "Оптимальный выбор"),
                ("RTX 4070", "GPU", 90.0, 220, 8.0, 800.0, "", "Предтоп"),
                ("RTX 4090", "GPU", 160.0, 450, 14.0, 1800.0, "", "Флагман"),
                ("Вентилятор 120мм", "Cooler", 0.0, 5, -3.0, 30.0,
                 "", "Базовый обдув"),
                ("Башня AK620", "Cooler", 0.0, 10, -7.0, 80.0,
                 "", "Башенный кулер"),
                ("Водянка 360мм", "Cooler", 0.0, 25, -16.0, 180.0,
                 "", "СВО охлаждение"),
                ("БП 500W", "PSU", 0.0, 0, 1.0, 60.0,
                 "", "Блок питания +500W"),
                ("БП 850W Gold", "PSU", 0.0, 0, 2.0, 140.0,
                 "", "Блок питания +850W"),
            ]
            cur.execute("DELETE FROM catalog")
            cur.executemany("""INSERT INTO catalog (name, category,
                                                    hashrate, watts, heat,
                                                    price, image, description)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            items)
            self.conn.commit()

    def buy_hardware(self, profile_id, catalog_id):
        cur = self.conn.cursor()
        cur.execute("SELECT balance FROM profiles WHERE id = ?", (profile_id,))
        prof = cur.fetchone()
        if not prof:
            return False

        cur.execute("SELECT price, name FROM catalog WHERE id = ?",
                    (catalog_id,))
        item = cur.fetchone()
        if not item or prof["balance"] < item["price"]:
            return False

        try:
            cur.execute("""UPDATE profiles SET balance = balance - ?
                           WHERE id = ?""",
                        (item["price"], profile_id))
            cur.execute("""INSERT INTO inventory
                           (profile_id, hardware_id, slot_index)
                           VALUES (?, ?, -1)""", (profile_id, catalog_id))
            self.add_transaction(profile_id, "BUY", -item["price"], 0, f"Куплен {item['name']}")
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False


if __name__ == "__main__":
    # я тут потестил кароче вроде как бы оно должно работать -_-
    db = DatabaseManager()
    success = db.buy_hardware(1, 1)
    print(f"Покупка успешна: {success}")
    print("Склад:", db.get_inventory(1))
