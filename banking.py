import random
import sqlite3

random.seed()


def account_menu():
    print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")


def exit():
    print("Buy!")


def login_form():
    print("Enter your card number:")
    number_input = input()
    print("Enter your PIN:")
    pin_input = input()
    return number_input, pin_input


def luhn_func(string_):
    string_list = list(string_)
    int_list = [int(x) for x in string_list]
    for i_ in range(0, 15, 2):
        int_list[i_] = int_list[i_] * 2
    int_list = [x - 9 if x > 9 else x for x in int_list]

    sum_ = 0
    for i_ in range(len(int_list)):
        sum_ += int_list[i_]
    checksum = 10 - (sum_ % 10)
    if checksum < 10:
        return str(checksum)
    else:
        return str(0)


def db_connector(db_name):
    conn = sqlite3.connect(db_name)
    return conn.cursor()


class Account:

    def __init__(self):
        self.id = 0
        self.number = ""
        self.pin = ""
        self.balance = 0

    def menu(self):
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        user_input = input()
        print()
        if user_input == "1":
            self.create_account()
            self.menu()
        elif user_input == "2":
            self.log_account()
        elif user_input == "0":
            exit()

    def create_account(self):
        self.gen_number()
        self.gen_pin()
        self.gen_id()
        self.to_sql()
        print(f"""Your card has been created
Your card number:
{self.number}
Your card PIN:
{self.pin}
""")

    def log_account(self):
        number_input, pin_input = login_form()
        print()
        match = self.match_account_number(number_input)

        if match:
            conn = sqlite3.connect('card.s3db')
            cur = conn.cursor()
            pin_query = 'SELECT pin FROM card WHERE number = {}'.format(number_input)
            cur.execute(pin_query)
            pin_result = cur.fetchone()
            if pin_input == pin_result[0]:
                print("You have successfully logged in!")
                print()
                self.logged_in(number_input)
            else:
                print("Wrong card number or PIN!")
                print()
                self.menu()
        else:
            print("Wrong card number!")
            self.menu()

    def logged_in(self, number_input):
        account_menu()
        user_input = input()
        print()
        if user_input == "1":
            balance = self.get_balance(number_input)
            print(f"Balance: {balance}")
            print()
            self.logged_in(number_input)
        elif user_input == "2":
            self.add_income(number_input)
            print("Income was added!")
            print()
            self.logged_in(number_input)
        elif user_input == "3":
            response = self.transfer(number_input)
            print(response)
            self.logged_in(number_input)
        elif user_input == "4":
            self.close_account(number_input)
            print("The account has been closed!")
            self.menu()
        elif user_input == "5":
            print("You have successfully logged out!")
            print()
            self.menu()
        elif user_input == "0":
            exit()

    def gen_pin(self):
        pin_list = []
        for _ in range(4):
            digit = random.randint(0, 9)
            pin_list.append(str(digit))
        self.pin = "".join(pin_list)

    def gen_number(self):
        random_number = str(random.randint(100000000, 999999999))
        number = "400000" + random_number
        check_sum = luhn_func(number)
        self.number = number + check_sum

    def gen_id(self):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        query = 'SELECT * FROM card'
        cur.execute(query)
        self.id = len(cur.fetchall()) + 1

    def get_balance(self, number):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute('SELECT balance FROM card WHERE number = {}'.format(number))
        balance = cur.fetchone()
        return balance[0]

    def add_income(self, number):
        print("Enter income:")
        income_input = int(input())
        balance = self.get_balance(number)
        new_balance = balance + income_input

        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        update_query = f'UPDATE card SET balance = {new_balance} WHERE number = {number}'
        cur.execute(update_query)
        conn.commit()

    def transfer(self, number):
        print("Transfer")
        print("Enter card number:")
        card_input = input()
        temp_list = list(card_input)
        last_digit = temp_list.pop()
        temp_card = "".join(temp_list)
        check_sum = luhn_func(temp_card)
        match = self.match_account_number(card_input)
        if last_digit != check_sum:
            return "Probably you made a mistake in the card number. \nPlease try again!"
        elif not match:
            return "Such a card does not exist."
        elif card_input == number:
            return "You can't transfer money to the same account!"
        else:
            print("Enter how much money you want to transfer:")
            transfer_input = int(input())
            balance = self.get_balance(number)
            if balance < transfer_input:
                return "Not enough money!"
            else:
                conn = sqlite3.connect('card.s3db')
                cur = conn.cursor()
                new_balance = balance - transfer_input
                withdraw_query = f'UPDATE card SET balance = {new_balance} WHERE number = {number}'
                cur.execute(withdraw_query)
                conn.commit()
                reciever_balance = self.get_balance(card_input)
                new_reciever_balance = reciever_balance + transfer_input
                deposit_query = f'UPDATE card SET balance = {new_reciever_balance} WHERE number = {card_input}'
                cur.execute(deposit_query)
                conn.commit()
                return "Success!"

    def match_account_number(self, number):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        query = 'SELECT number FROM card'
        cur.execute(query)
        numbers = cur.fetchall()
        match_list = []
        for i in numbers:
            match = any([x == number for x in i])
            match_list.append(match)

        return any(match_list)

    def close_account(self, number):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        query = 'DELETE FROM card WHERE number = {}'.format(number)
        cur.execute(query)
        conn.commit()

    def to_sql(self):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        insert_query = 'INSERT INTO card VALUES({}, {}, {}, {});'.format(self.id, self.number, self.pin, self.balance)
        cur.execute(insert_query)
        conn.commit()

    def __str__(self):
        return f"Your card number: {self.number}, Your card PIN: {self.pin}"


account = Account()
account.menu()
