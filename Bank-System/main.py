import sqlite3
import random
from abc import ABC, abstractmethod
from datetime import datetime


# ==========================
# DATABASE CLASS
# ==========================

class Database:
    def __init__(self, db_name="bank.db"):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.connect() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pin TEXT NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                balance REAL DEFAULT 0
            )
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT,
                type TEXT,
                amount REAL,
                description TEXT,
                date TEXT
            )
            """)

    def insert_account(self, name, pin, account_number):
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO accounts (name, pin, account_number, balance) VALUES (?, ?, ?, 0)",
                (name, pin, account_number)
            )

    def get_account(self, account_number, pin=None):
        with self.connect() as conn:
            if pin:
                cur = conn.execute(
                    "SELECT * FROM accounts WHERE account_number=? AND pin=?",
                    (account_number, pin)
                )
            else:
                cur = conn.execute(
                    "SELECT * FROM accounts WHERE account_number=?",
                    (account_number,)
                )
            return cur.fetchone()

    def get_balance(self, account_number):
        with self.connect() as conn:
            cur = conn.execute(
                "SELECT balance FROM accounts WHERE account_number=?",
                (account_number,)
            )
            row = cur.fetchone()
            return row[0] if row else None

    def update_balance(self, account_number, balance):
        with self.connect() as conn:
            conn.execute(
                "UPDATE accounts SET balance=? WHERE account_number=?",
                (balance, account_number)
            )

    def insert_transaction(self, account_number, t_type, amount, description):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO transactions
                (account_number, type, amount, description, date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    account_number,
                    t_type,
                    amount,
                    description,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )

    def get_transactions(self, account_number):
        with self.connect() as conn:
            cur = conn.execute(
                """
                SELECT type, amount, description, date
                FROM transactions
                WHERE account_number=?
                ORDER BY date DESC
                """,
                (account_number,)
            )
            return cur.fetchall()


# ==========================
# ABSTRACT ACCOUNT
# ==========================

class BaseAccount(ABC):

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass


# ==========================
# ACCOUNT CLASS
# ==========================

class Account(BaseAccount):

    def __init__(self, name, pin, account_number, balance, db: Database):
        self.__name = name
        self.__pin = pin
        self.__account_number = account_number
        self.__balance = balance
        self.db = db

    @staticmethod
    def generate_account_number():
        return str(random.randint(1000000000, 9999999999))

    def deposit(self, amount):
        self.__balance += amount
        self.db.update_balance(self.__account_number, self.__balance)

        self.db.insert_transaction(
            self.__account_number,
            "DEPOSIT",
            amount,
            "Setor tunai"
        )

        print(f"✅ Deposit berhasil. Saldo: {self.__balance}")

    def withdraw(self, amount):
        if amount > self.__balance:
            print("❌ Saldo tidak cukup")
            return

        self.__balance -= amount
        self.db.update_balance(self.__account_number, self.__balance)

        self.db.insert_transaction(
            self.__account_number,
            "WITHDRAW",
            amount,
            "Tarik tunai"
        )

        print(f"✅ Penarikan berhasil. Saldo: {self.__balance}")

    def transfer(self, target_account_number, amount):
        if amount > self.__balance:
            print("❌ Saldo tidak cukup untuk transfer")
            return

        target_balance = self.db.get_balance(target_account_number)
        if target_balance is None:
            print("❌ Rekening tujuan tidak ditemukan")
            return

        # pengirim
        self.__balance -= amount
        self.db.update_balance(self.__account_number, self.__balance)

        self.db.insert_transaction(
            self.__account_number,
            "TRANSFER_OUT",
            amount,
            f"Transfer ke {target_account_number}"
        )

        # penerima
        self.db.update_balance(
            target_account_number,
            target_balance + amount
        )

        self.db.insert_transaction(
            target_account_number,
            "TRANSFER_IN",
            amount,
            f"Transfer dari {self.__account_number}"
        )

        print("✅ Transfer berhasil")

    def get_balance(self):
        return self.__balance

    def get_number(self):
        return self.__account_number

    def get_name(self):
        return self.__name


# ==========================
# BANK SYSTEM
# ==========================

class BankSystem:

    def __init__(self):
        self.db = Database()

    def register(self):
        print("\n=== REGISTER AKUN ===")
        name = input("Nama Lengkap : ")
        pin = input("PIN (4 digit): ")

        if not pin.isdigit() or len(pin) != 4:
            print("❌ PIN harus 4 digit")
            return

        account_number = Account.generate_account_number()
        self.db.insert_account(name, pin, account_number)

        print("\n🎉 Akun berhasil dibuat!")
        print("Nomor Rekening:", account_number)

    def login(self):
        print("\n=== LOGIN ===")
        acc = input("Nomor Rekening : ")
        pin = input("PIN            : ")

        data = self.db.get_account(acc, pin)

        if data:
            print(f"\n✅ Login berhasil. Selamat datang {data[1]}")
            return Account(
                name=data[1],
                pin=data[2],
                account_number=data[3],
                balance=data[4],
                db=self.db
            )
        else:
            print("❌ Login gagal")
            return None

    def user_menu(self, user: Account):
        while True:
            print("\n=== MENU USER ===")
            print("1. Cek Saldo")
            print("2. Deposit")
            print("3. Tarik Tunai")
            print("4. Transfer")
            print("5. Mutasi Transaksi")
            print("6. Logout")

            choice = input("Pilih menu: ")

            if choice == "1":
                print("💳 Saldo:", user.get_balance())

            elif choice == "2":
                amount = float(input("Jumlah deposit: "))
                user.deposit(amount)

            elif choice == "3":
                amount = float(input("Jumlah tarik: "))
                user.withdraw(amount)

            elif choice == "4":
                tujuan = input("Rekening tujuan: ")
                amount = float(input("Jumlah transfer: "))
                user.transfer(tujuan, amount)

            elif choice == "5":
                print("\n=== MUTASI TRANSAKSI ===")
                transaksi = user.db.get_transactions(user.get_number())
                if not transaksi:
                    print("Belum ada transaksi")
                for t in transaksi:
                    print(f"{t[3]} | {t[0]} | {t[1]} | {t[2]}")

            elif choice == "6":
                print("Logout berhasil")
                break

            else:
                print("❌ Menu tidak valid")

    def menu(self):
        while True:
            print("\n=== SISTEM PERBANKAN ===")
            print("1. Register")
            print("2. Login")
            print("3. Keluar")

            choice = input("Pilih menu: ")

            if choice == "1":
                self.register()

            elif choice == "2":
                user = self.login()
                if user:
                    self.user_menu(user)

            elif choice == "3":
                print("Terima kasih")
                break

            else:
                print("❌ Menu tidak valid")


# ==========================
# RUN PROGRAM
# ==========================

if __name__ == "__main__":
    BankSystem().menu()