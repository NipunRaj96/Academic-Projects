import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class Account:
    def __init__(self, account_number, account_holder, initial_balance=0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = initial_balance
        self.transactions = []

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transactions.append({"type": "Deposit", "amount": amount, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            return True
        else:
            return False

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.transactions.append({"type": "Withdrawal", "amount": amount, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            return True
        else:
            return False

    def transfer(self, amount, target_account):
        if 0 < amount <= self.balance:
            self.withdraw(amount)
            target_account.deposit(amount)
            self.transactions.append({"type": "Transfer Out", "amount": amount, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "target": target_account.account_number})
            target_account.transactions.append({"type": "Transfer In", "amount": amount, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "source": self.account_number})
            return True
        else:
            return False

    def get_balance(self):
        return self.balance

    def get_transaction_history(self):
        return self.transactions

    def to_dict(self):
        return {
            'account_number': self.account_number,
            'account_holder': self.account_holder,
            'balance': self.balance,
            'transactions': self.transactions
        }

    @staticmethod
    def from_dict(data):
        account = Account(
            account_number=data['account_number'],
            account_holder=data['account_holder'],
            initial_balance=data['balance']
        )
        account.transactions = data.get('transactions', [])
        return account

    def __str__(self):
        return f"Account[{self.account_number}] - Holder: {self.account_holder}, Balance: ${self.balance:.2f}"

class Bank:
    def __init__(self, db_path='bank_data.json'):
        self.db_path = db_path
        self.accounts = self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                return {acc['account_number']: Account.from_dict(acc) for acc in data}
        else:
            return {}

    def save_accounts(self):
        with open(self.db_path, 'w') as f:
            json.dump([acc.to_dict() for acc in self.accounts.values()], f)

    def create_account(self, account_number, account_holder, initial_balance=0):
        if account_number not in self.accounts:
            account = Account(account_number, account_holder, initial_balance)
            self.accounts[account_number] = account
            self.save_accounts()
            return True
        else:
            return False

    def find_account(self, account_number):
        return self.accounts.get(account_number, None)

    def deposit_to_account(self, account_number, amount):
        account = self.find_account(account_number)
        if account:
            if account.deposit(amount):
                self.save_accounts()
                return True
        return False

    def withdraw_from_account(self, account_number, amount):
        account = self.find_account(account_number)
        if account:
            if account.withdraw(amount):
                self.save_accounts()
                return True
        return False

    def transfer_between_accounts(self, source_account_number, target_account_number, amount):
        source_account = self.find_account(source_account_number)
        target_account = self.find_account(target_account_number)
        if source_account and target_account:
            if source_account.transfer(amount, target_account):
                self.save_accounts()
                return True
        return False

    def get_account_balance(self, account_number):
        account = self.find_account(account_number)
        if account:
            return account.get_balance()
        return None

    def get_account_transactions(self, account_number):
        account = self.find_account(account_number)
        if account:
            return account.get_transaction_history()
        return []

    def display_account_info(self, account_number):
        account = self.find_account(account_number)
        if account:
            return str(account)
        else:
            return f"Account {account_number} not found."

    def display_all_accounts(self):
        return "\n".join(str(account) for account in self.accounts.values())

class BankingApp:
    def __init__(self, root):
        self.bank = Bank()
        self.root = root
        self.root.title("Banking System")
        self.root.geometry("900x700")
        self.root.configure(bg="#e0f7fa")
        self.create_widgets()

    def create_widgets(self):
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=10)
        self.style.configure("TLabel", font=("Helvetica", 12))
        
        header_frame = tk.Frame(self.root, bg="#00796b")
        header_frame.pack(fill=tk.X)

        header = ttk.Label(header_frame, text="Banking System", font=("Helvetica", 24, "bold"), background="#00796b", foreground="white")
        header.pack(pady=20)
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Create Account", command=self.create_account, width=20).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(button_frame, text="Deposit Money", command=self.deposit_money, width=20).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(button_frame, text="Withdraw Money", command=self.withdraw_money, width=20).grid(row=0, column=2, padx=10, pady=10)
        ttk.Button(button_frame, text="Check Balance", command=self.check_balance, width=20).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(button_frame, text="Display Account Info", command=self.display_account_info, width=20).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(button_frame, text="Display All Accounts", command=self.display_all_accounts, width=20).grid(row=1, column=2, padx=10, pady=10)
        ttk.Button(button_frame, text="Transfer Money", command=self.transfer_money, width=20).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(button_frame, text="View Transactions", command=self.view_transactions, width=20).grid(row=2, column=1, padx=10, pady=10)

        self.info_text = tk.Text(self.root, height=15, width=80, state=tk.DISABLED, bg="#e0f7fa", font=("Helvetica", 12))
        self.info_text.pack(pady=20)

    def create_account(self):
        account_number = simpledialog.askstring("Create Account", "Enter account number:")
        account_holder = simpledialog.askstring("Create Account", "Enter account holder name:")
        initial_balance = simpledialog.askfloat("Create Account", "Enter initial balance:")
        if account_number and account_holder and initial_balance is not None:
            if self.bank.create_account(account_number, account_holder, initial_balance):
                messagebox.showinfo("Success", "Account created successfully.")
            else:
                messagebox.showerror("Error", "Account creation failed. Account number already exists.")
        else:
            messagebox.showerror("Error", "Invalid input. Please try again.")

    def deposit_money(self):
        account_number = simpledialog.askstring("Deposit Money", "Enter account number:")
        amount = simpledialog.askfloat("Deposit Money", "Enter amount to deposit:")
        if account_number and amount is not None:
            if self.bank.deposit_to_account(account_number, amount):
                messagebox.showinfo("Success", "Deposit successful.")
            else:
                messagebox.showerror("Error", "Deposit failed. Account not found.")
        else:
            messagebox.showerror("Error", "Invalid input. Please try again.")

    def withdraw_money(self):
        account_number = simpledialog.askstring("Withdraw Money", "Enter account number:")
        amount = simpledialog.askfloat("Withdraw Money", "Enter amount to withdraw:")
        if account_number and amount is not None:
            if self.bank.withdraw_from_account(account_number, amount):
                messagebox.showinfo("Success", "Withdrawal successful.")
            else:
                messagebox.showerror("Error", "Withdrawal failed. Account not found or insufficient balance.")
        else:
            messagebox.showerror("Error", "Invalid input. Please try again.")

    def check_balance(self):
        account_number = simpledialog.askstring("Check Balance", "Enter account number:")
        if account_number:
            balance = self.bank.get_account_balance(account_number)
            if balance is not None:
                messagebox.showinfo("Account Balance", f"Account balance: ${balance:.2f}")
            else:
                messagebox.showerror("Error", "Account not found.")
        else:
            messagebox.showerror("Error", "Invalid input. Please try again.")

    def display_account_info(self):
        account_number = simpledialog.askstring("Display Account Info", "Enter account number:")
        if account_number:
            info = self.bank.display_account_info(account_number)
            self.info_text.configure(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info)
            self.info_text.configure(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", "Invalid input. Please try again.")

    def display_all_accounts(self):
        info = self.bank.display_all_accounts()
        self.info_text.configure(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
        self.info_text.configure(state=tk.DISABLED)

    def transfer_money(self):
        source_account = simpledialog.askstring("Transfer Money", "Enter source account number:")
        target_account = simpledialog.askstring("Transfer Money", "Enter target account number:")
        amount = simpledialog.askfloat("Transfer Money", "Enter amount to transfer:")
        if source_account and target_account and amount is not None:
            if self.bank.transfer_between_accounts(source_account, target_account, amount):
                messagebox.showinfo("Success", "Transfer successful.")
            else:
                messagebox.showerror("Error", "Transfer failed. Check account numbers and balance.")
        else:
            messagebox.showerror("Error", "Invalid input. Please try again.")

    def view_transactions(self):
        account_number = simpledialog.askstring("View Transactions", "Enter account number:")
        if account_number:
            transactions = self.bank.get_account_transactions(account_number)
            if transactions:
                transactions_info = "\n".join([f"{t['date']}: {t['type']} of ${t['amount']:.2f}" for t in transactions])
                self.info_text.configure(state=tk.NORMAL)
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, transactions_info)
                self.info_text.configure(state=tk.DISABLED)
            else:
                messagebox.showinfo("No Transactions", "No transactions found for this account.")
        else:
            messagebox.showerror("Error", "Invalid input. Please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BankingApp(root)
    root.mainloop()
