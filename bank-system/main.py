from core.bank import BankSystem
from admin.admin import Admin

# =========================
# MENU USER
# =========================
def user_menu(bank):
    while True:
        print("\n=== MENU USER ===")
        print("1. Cek Saldo")
        print("2. Deposit")
        print("3. Tarik Tunai")
        print("4. Transfer")
        print("5. Riwayat Transaksi")
        print("6. Logout")

        choice = input("Pilih menu: ")

        if choice == "1":
            bank.transactions.check_balance()

        elif choice == "2":
            bank.transactions.deposit()

        elif choice == "3":
            bank.transactions.withdraw()

        elif choice == "4":
            bank.transactions.transfer()

        elif choice == "5":
            bank.transactions.history()

        elif choice == "6":
            bank.auth.logout()
            break

        else:
            print("❌ Pilihan tidak valid")


# =========================
# MENU ADMIN
# =========================
def admin_menu(admin):
    while admin.is_logged_in:
        print("\n=== MENU ADMIN ===")
        print("1. Lihat semua user")
        print("2. Lihat semua transaksi")
        print("3. Hapus user")
        print("4. Logout admin")

        choice = input("Pilih menu: ")

        if choice == "1":
            admin.view_all_users()

        elif choice == "2":
            admin.view_all_transactions()

        elif choice == "3":
            admin.delete_user()

        elif choice == "4":
            admin.logout()

        else:
            print("❌ Pilihan tidak valid")


# =========================
# PROGRAM UTAMA
# =========================
def main():
    bank = BankSystem()
    admin = Admin()

    while True:
        print("\n=== SISTEM BANK ===")
        print("1. Register User")
        print("2. Login User")
        print("3. Keluar")
        print("4. Login Admin")

        choice = input("Pilih menu: ")

        if choice == "1":
            bank.auth.register()

        elif choice == "2":
            if bank.auth.login():
                user_menu(bank)

        elif choice == "3":
            print("👋 Terima kasih telah menggunakan sistem bank")
            break

        elif choice == "4":
            account = input("Account admin: ")
            pin = input("PIN admin: ")
            admin.login(account, pin)

            if admin.is_logged_in:
                admin_menu(admin)

        else:
            print("❌ Pilihan tidak valid")


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
