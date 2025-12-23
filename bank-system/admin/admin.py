import hashlib
from database.database import Database


class Admin:
    def __init__(self):
        self.db = Database()
        self.is_logged_in = False

        # Kredensial admin
        self.ADMIN_ACCOUNT = "admin"
        self.ADMIN_PIN_HASH = self._hash_pin("1234")

    def _hash_pin(self, pin):
        return hashlib.sha256(pin.encode()).hexdigest()

    def login(self, account, pin):
        if account == self.ADMIN_ACCOUNT and self._hash_pin(pin) == self.ADMIN_PIN_HASH:
            self.is_logged_in = True
            print("✅ Login admin berhasil")
        else:
            print("❌ Login admin gagal")

    def logout(self):
        self.is_logged_in = False
        print("👋 Admin logout")

    # =========================
    # FITUR ADMIN
    # =========================

    def view_all_users(self):
        if not self.is_logged_in:
            print("❌ Admin belum login")
            return

        with self.db.connect() as conn:
            users = conn.execute(
                "SELECT account_number, full_name FROM users"
            ).fetchall()

        print("\n=== DAFTAR USER ===")
        if not users:
            print("Tidak ada user")
            return

        for u in users:
            print(f"Rek: {u[0]} | Nama: {u[1]}")

    def view_all_transactions(self):
        if not self.is_logged_in:
            print("❌ Admin belum login")
            return

        with self.db.connect() as conn:
            txs = conn.execute(
                """
                SELECT account_number, type, amount, timestamp
                FROM transactions
                ORDER BY timestamp DESC
                """
            ).fetchall()

        print("\n=== SEMUA TRANSAKSI ===")
        if not txs:
            print("Belum ada transaksi")
            return

        for t in txs:
            print(f"{t[3]} | Rek: {t[0]} | {t[1]} | {t[2]}")

    def delete_user(self):
        if not self.is_logged_in:
            print("❌ Admin belum login")
            return

        account = input("Masukkan nomor rekening user yang akan dihapus: ")

        with self.db.connect() as conn:
            user = conn.execute(
                "SELECT full_name FROM users WHERE account_number = ?",
                (account,)
            ).fetchone()

            if not user:
                print("❌ User tidak ditemukan")
                return

            conn.execute(
                "DELETE FROM transactions WHERE account_number = ?",
                (account,)
            )
            conn.execute(
                "DELETE FROM users WHERE account_number = ?",
                (account,)
            )

        print(f"✅ User {user[0]} berhasil dihapus")
