import sqlite3
import datetime

class DatabaseManager:
    def __init__(self):
        self.db_name = 'mining_farm.db'
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.seed_catalog()
        
    def create_tables(self):
        cur = self.conn.cursor()
        
        # 1 таблица - профиль игрока
        cur.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                balance REAL DEFAULT 600.0,
                crypto_balance REAL DEFAULT 0.0,
                avatar TEXT DEFAULT '',
                theme TEXT DEFAULT '#00e676'
            )
        """)
        
        # 2 таблица - профиль карточек с видеокартами таам охлаждением и тд
        cur.execute("""
            CREATE TABLE IF NOT EXISTS catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                hashrate REAL DEFAULT 0.0,
                watts INTEGER DEFAULT 0,
                heat REAL DEFAULT 0.0,
                price REAL DEFAULT 100.0,
                image TEXT DEFAULT '',
                description TEXT DEFAULT ''
            )   
        """)
        
        # 3 таблица - склад, инвентарь купленных товаров
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                hardware_id INTEGER NOT NULL,
                slot_index INTEGER DEFAULT -1,
                overclock INTEGER DEFAULT 100,
                condition REAL DEFAULT 100.0,
                FOREIGN KEY (profile_id) REFERENCES profiles (id),
                FOREIGN KEY (hardware_id) REFERENCES catalog (id)
            )
        """)
        
        # 4 таблица - история финансов, все транзакции
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                time TEXT NOT NULL,
                type TEXT NOT NULL,
                amount TEXT NOT NULL,
                btc_rate TEXT NOT NULL,
                details TEXT NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES profiles (id)
            )
        """)
        self.conn.commit()
        
    def get_profiles(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM profiles")
        return cur.fetchall()
    
    def create_profile(self, name):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO profiles (username) VALUES (?)", (name,))
        self.conn.commit()
        return cur.lastrowid
        
    def get_profile(self, id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT * FROM profiles
            WHERE id = ?            
        """, (id,))
        return cur.fetchone()
        
    def get_catalog(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM catalog")
        return cur.fetchall()
    
    def update_avatar(self, profile_id, avatar_path):
        cur = self.conn.cursor()
        cur.execute("UPDATE profiles SET avatar = ? WHERE id = ?", (avatar_path, profile_id))
        self.conn.commit()
        
    def process_tick(self, profile_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT inv.id, cat.hashrate, cat.heat 
            FROM inventory inv 
            JOIN catalog cat ON inv.hardware_id = cat.id 
            WHERE inv.profile_id = ? AND inv.slot_index >= 0
        """, (profile_id,))
        items = cur.fetchall()
        
        total_hashrate = sum(item["hashrate"] for item in items)
        
        if total_hashrate > 0:
            earned = total_hashrate * 0.00001
            cur.execute("UPDATE profiles SET crypto_balance = crypto_balance + ? WHERE id = ?", (earned, profile_id))
            for item in items:
                cur.execute("UPDATE inventory SET condition = condition - 0.5 WHERE id = ?", (item["id"],))
                
        self.conn.commit()
    
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
        cur.execute("""
            SELECT inv.id as inv_id, inv.slot_index, inv.overclock, inv.condition,
            cat.name, cat.category, cat.hashrate, cat.watts, cat.heat
            FROM inventory inv
            JOIN catalog cat ON inv.hardware_id = cat.id
            WHERE inv.profile_id = ?
        """, (profile_id,))
        return cur.fetchall()
    
    def seed_catalog(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM catalog")
        if cur.fetchone()[0] == 0:
            items = [
                ("GTX 1050 Ti", "GPU", 15.0, 75, 2.0, 140.0, "", "Базовая карта"),
                ("RTX 3060", "GPU", 45.0, 170, 4.5, 420.0, "", "Народный выбор"),
                ("RTX 4090", "GPU", 135.0, 450, 12.0, 1800.0, "", "Зверь"),
                ("Deepcool AK620", "Cooler", 0.0, 5, -4.0, 70.0, "", "Башня"),
                ("Liquid Freezer 360", "Cooler", 0.0, 25, -12.0, 150.0, "", "Водянка"),
                ("Chieftec 600W", "PSU", 0.0, 0, 2.0, 80.0, "", "Блок питания"),
            ]
            cur.executemany("""
                INSERT INTO catalog (name, category, hashrate, watts, heat, price, image, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)              
            """, items)
            self.conn.commit()
            
    def buy_hardware(self, profile_id, catalog_id):
        cur = self.conn.cursor()
        
        cur.execute("SELECT balance FROM profiles WHERE id = ?", (profile_id,))
        balance = cur.fetchone()["balance"]
        
        cur.execute("SELECT price FROM catalog WHERE id = ?", (catalog_id,))
        price = cur.fetchone()["price"]
        
        if balance < price:
            return False
        
        try:
            cur.execute("UPDATE profiles SET balance = balance - ? WHERE id = ?", (price, profile_id))
            cur.execute("INSERT INTO inventory (profile_id, hardware_id, slot_index) VALUES (?, ?, -1)", (profile_id, catalog_id))
            cur.execute("""
                INSERT INTO transactions (profile_id, time, type, amount, btc_rate, details)
                VALUES (?, ?, "BUY", ?, 0, ?)
            """, (profile_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), -price, f"Куплен {catalog_id}"))
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