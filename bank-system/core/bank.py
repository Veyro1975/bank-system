from auth.auth import Auth
from trancsactions import Transactions

class BankSystem:
    def __init__(self):
        self.auth = Auth()
        self.transactions = Transactions(self.auth)
