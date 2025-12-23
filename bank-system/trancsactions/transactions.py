from database.database import Database

class Transactions:
    def __init__(self, auth):
        self.db = Database()
        self.auth = auth

    def _check_login(self):
        if not self.auth.current_user:
            print("❌ Silakan login terlebih dahulu")
            return False
        return True

    def check_balance(self):
        if not self._check_login():
            return

        with self.db.connect() as conn:
            balance = conn.execute(
                "SELECT balance FROM users WHERE account_number = ?",
                (self.auth.current_user,)
            ).fetchone()[0]

        print(f"💰 Saldo Anda: {balance}")

    def deposit(self):
        if not self._check_login():
            return

        amount = int(input("Jumlah deposit: "))

        with self.db.connect() as conn:
            conn.execute(
                "UPDATE users SET balance = balance + ? WHERE account_number = ?",
                (amount, self.auth.current_user)
            )
            conn.execute(
                "INSERT INTO transactions (account_number, type, amount) VALUES (?, ?, ?)",
                (self.auth.current_user, "DEPOSIT", amount)
            )

        print("✅ Deposit berhasil")

    def withdraw(self):
        if not self._check_login():
            return

        amount = int(input("Jumlah tarik tunai: "))

        with self.db.connect() as conn:
            balance = conn.execute(
                "SELECT balance FROM users WHERE account_number = ?",
                (self.auth.current_user,)
            ).fetchone()[0]

            if amount > balance:
                print("❌ Saldo tidak cukup")
                return

            conn.execute(
                "UPDATE users SET balance = balance - ? WHERE account_number = ?",
                (amount, self.auth.current_user)
            )
            conn.execute(
                "INSERT INTO transactions VALUES (NULL, ?, ?, ?, CURRENT_TIMESTAMP)",
                (self.auth.current_user, "WITHDRAW", amount)
            )

        print("✅ Tarik tunai berhasil")

    def transfer(self):
        if not self._check_login():
            return

        target = input("Rekening tujuan: ")
        amount = int(input("Jumlah transfer: "))

        with self.db.connect() as conn:
            sender_balance = conn.execute(
                "SELECT balance FROM users WHERE account_number = ?",
                (self.auth.current_user,)
            ).fetchone()[0]

            receiver = conn.execute(
                "SELECT account_number FROM users WHERE account_number = ?",
                (target,)
            ).fetchone()

            if not receiver:
                print("❌ Rekening tujuan tidak ditemukan")
                return

            if amount > sender_balance:
                print("❌ Saldo tidak cukup")
                return

            conn.execute(
                "UPDATE users SET balance = balance - ? WHERE account_number = ?",
                (amount, self.auth.current_user)
            )
            conn.execute(
                "UPDATE users SET balance = balance + ? WHERE account_number = ?",
                (amount, target)
            )

            conn.execute(
                "INSERT INTO transactions VALUES (NULL, ?, ?, ?, CURRENT_TIMESTAMP)",
                (self.auth.current_user, "TRANSFER", amount)
            )

        print("✅ Transfer berhasil")

    def history(self):
        if not self._check_login():
            return

        with self.db.connect() as conn:
            txs = conn.execute(
                "SELECT type, amount, timestamp FROM transactions WHERE account_number = ?",
                (self.auth.current_user,)
            ).fetchall()

        print("\n=== RIWAYAT TRANSAKSI ===")
        for t in txs:
            print(f"{t[2]} | {t[0]} | {t[1]}")
