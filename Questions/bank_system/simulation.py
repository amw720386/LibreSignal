"""
All your implementation code for the bank system simulation goes here.
"""

class Simulation:

    def __init__(self):
        self.accounts = {}
        self.payments = 0

    def create_account(self, timestamp: int, account_id: str) -> bool | None:
        if account_id in self.accounts:
            return False

        self.accounts[account_id] = {"creation":timestamp, "transactions": [], "balance": 0}

        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        if account_id not in self.accounts:
            return None

        self.accounts[account_id]["transactions"].append({"time":timestamp, "transaction_type": "deposit", "amount": amount})
        self.accounts[account_id]["balance"] += amount

        return self.accounts[account_id]["balance"]

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        self.update_cash_backs(timestamp)
        if source_account_id == target_account_id:
            return None

        if source_account_id not in self.accounts or target_account_id not in self.accounts:
            return None
        
        if self.accounts[source_account_id]["balance"] < amount:
            return None
        
        self.accounts[source_account_id]["transactions"].append({"time": timestamp, "transaction_type": "send_transfer", "amount": amount, "target": target_account_id})
        self.accounts[source_account_id]["transactions"].append({"time": timestamp, "transaction_type": "recieve_transfer", "amount": amount, "source": source_account_id})

        self.accounts[source_account_id]["balance"] -= amount
        self.accounts[target_account_id]["balance"] += amount

        return self.accounts[source_account_id]["balance"]

    def top_spenders(self, timestamp: int, n: int) -> list[str] | None:
        self.update_cash_backs(timestamp)
        totals = []

        for account, details in self.accounts.items():
            total = 0
            for transaction in details["transactions"]:
                if transaction["transaction_type"] in ["send_transfer", "pay"]:
                    total += transaction["amount"]

            totals.append([account, total])
        
        totals.sort(key=lambda total: (-total[1], total[0]))

        out = []

        for i in range(min(n, len(totals))):
            out.append(f"{totals[i][0]}({totals[i][1]})")
        
        return out

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        if account_id not in self.accounts:
            return None
        
        if self.accounts[account_id]["balance"] < amount:
            return None
        
        self.payments += 1

        out = f"payment{self.payments}"

        self.accounts[account_id]["transactions"].append({"time": timestamp, "transaction_type": "pay", "amount": amount, "id": out})
        self.accounts[account_id]["transactions"].append({"time": timestamp, "transaction_type": "pending_cash_back", "amount": int(amount * 0.02), "id": out})

        self.accounts[account_id]["balance"] -= amount
        
        return out

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        self.update_cash_backs(timestamp)

        if account_id not in self.accounts:
            return None
        
        for transaction in self.accounts[account_id]["transactions"]:
            if transaction["transaction_type"] == "pending_cash_back":
                if transaction["id"] == payment:
                    return "IN_PROGRESS"
                
            if transaction["transaction_type"] == "cash_back":
                if transaction["id"] == payment:
                    return "CASHBACK_RECEIVED"


        return None

    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool | None:
        self.update_cash_backs(timestamp)

        if account_id_1 == account_id_2:
            return False
        if account_id_1 not in self.accounts or account_id_2 not in self.accounts:
            return False
        
        self.accounts[account_id_1]["transactions"] += self.accounts[account_id_2]["transactions"]
        self.accounts[account_id_1]["balance"] += self.accounts[account_id_2]["balance"]

        del self.accounts[account_id_2]

        pass

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        self.update_cash_backs(timestamp)

        if account_id not in self.accounts:
            return None
        
        if self.accounts[account_id]["creation"] > time_at:
            return None
        
        out = 0

        for transaction in self.accounts[account_id]["transactions"]:
            if transaction["time"] <= time_at:
                if transaction["transaction_type"] == "deposit":
                    out += transaction["amount"]
                if transaction["transaction_type"] == "send_transfer":
                    out -= transaction["amount"]
                if transaction["transaction_type"] == "recieve_transfer":
                    out += transaction["amount"]
                if transaction["transaction_type"] == "pay":
                    out -= transaction["amount"]
                if transaction["transaction_type"] == "cash_back" and transaction["time"] +  (1 * 24 * 60 * 60 * 1000) <= time_at:
                    out += transaction["amount"]
        
        return out

    def update_cash_backs(self, timestamp: int) -> None:
        for account_id in self.accounts.keys():
            for transaction in self.accounts[account_id]["transactions"]:
                if transaction["transaction_type"] == "pending_cash_back" and (transaction["time"] + (1 * 24 * 60 * 60 * 1000)) <= timestamp:
                    transaction["transaction_type"] = "cash_back"
                    self.accounts[account_id]["balance"] += transaction["amount"]

