import hashlib
import random
from database.database import Database


class Auth:
    def __init__(self):
        self.db = Database()
        self.current_user = None

    def _hash_pin(self, pin):
        return hashlib.sha256(pin.encode()).hexdigest()

    def _generate_account(self):
        return str(random.randint(10000000, 99999999))

    def register(self):
        name = input("Nama lengkap: ")
        pin = input("PIN: ")

        account = self._generate_account()
        pin_hash = self._hash_pin(pin)

        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO users VALUES (?, ?, ?, 0)",
                (account, name, pin_hash)
            )

        print(f"✅ Registrasi berhasil. Nomor rekening Anda: {account}")

    def login(self):
        account = input("Nomor rekening: ")
        pin = input("PIN: ")

        with self.db.connect() as conn:
            user = conn.execute(
                "SELECT account_number, pin_hash FROM users WHERE account_number = ?",
                (account,)
            ).fetchone()

        if user and self._hash_pin(pin) == user[1]:
            self.current_user = account
            print("✅ Login berhasil")
            return True

        print("❌ Login gagal")
        return False

    def logout(self):
        self.current_user = None
        print("👋 Logout berhasil")
