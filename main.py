import sqlite3
from random import sample


class BankingSystem:
    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        sql_create_card_table = """CREATE TABLE IF NOT EXISTS card (
            id INTEGER, 
            number TEXT,
            pin TEXT, 
            balance INTEGER DEFAULT 0
            );"""
        self.cur.execute(sql_create_card_table)

    def create_card(self, id_, number, pin, balance):
        sql_insert_card = f"""INSERT INTO card VALUES ({id_}, {number}, {pin}, {balance});"""
        self.cur.execute(sql_insert_card)
        self.conn.commit()

    def gen_id(self):
        query = """SELECT id FROM card ORDER BY id DESC LIMIT 1;"""
        self.cur.execute(query)
        records = self.cur.fetchall()
        try:
            return records[0][0] + 1
        except IndexError:
            return 1

    def read_card(self, card, pin):
        query = f"""SELECT number, pin FROM card WHERE number = {card} AND pin = {pin}"""
        rows = self.cur.execute(query).fetchone()
        return rows

    def read_balance(self, card):
        query = f"""SELECT balance FROM card WHERE number = {card}"""
        rows = self.cur.execute(query).fetchone()
        return rows[0]

    def read_num(self, card):
        query = f"""SELECT number FROM card WHERE number = {card}"""
        rows = self.cur.execute(query).fetchone()
        return rows

    def add_income(self, card, income):
        query = f"""UPDATE card SET balance = balance + {income} WHERE number = {card}"""
        self.cur.execute(query)
        self.conn.commit()

    def close_account(self, card):
        query = f"""DELETE FROM card WHERE number = {card}"""
        self.cur.execute(query)
        self.conn.commit()

    def check_card(self, number):
        exists = self.cur.execute(f"SELECT * FROM card WHERE number = {number}").fetchone()
        return exists is None

    def transfer(self, card):
        tr_card = input('Card where to transfer: ')
        if card == tr_card:
            print("You can't transfer money to the same account!")
        elif self.prove_luhn(tr_card) == 1:
            print('Probably you made mistake in the card number. Please try again!')
        elif self.read_num(tr_card):
            money = int(input())
            if money > self.read_balance(card):
                print("Not enough money!")
            else:
                query = f"""UPDATE card SET balance = balance + {money} WHERE number = {tr_card}"""
                self.cur.execute(query)
                query = f"""UPDATE card SET balance = balance - {money} WHERE number = {card}"""
                self.cur.execute(query)
                self.conn.commit()
        else:
            print('Such a card does not exist.')

    def creation_card(self):
        pin = ''.join([str(n) for n in sample(range(10), 4)])
        card = self.luhn_alg()
        print(f'\nYour card number:\n{card}')
        print(f'Your card PIN:\n{pin}\n')
        id_ = self.gen_id()
        self.create_card(id_, card, pin, 0)

    def prove_luhn(self, card):
        num = 0
        mas = 0
        for i in range(len(card)-1):
            if i % 2 == 0:
                num = int(card[i]) * 2
            else:
                num = int(card[i])
            if num > 9:
                num -= 9
            mas += num
        mas += int(card[-1])
        if mas % 10 == 0:
            return 0
        else:
            return 1

    def luhn_alg(self):
        card = '400000' + ''.join([str(n) for n in sample(range(10), 9)])
        num = 0
        mas = 0
        #print(card)
        for i in range(len(card)):
            if i % 2 == 0:
                num = int(card[i]) * 2
            else:
                num = int(card[i])
            if num > 9:
                num -= 9
            mas += num
        card += str((10 - mas % 10) % 10)
        return card

    def login(self):
        card = input('Enter your card number:\n')
        pin = input('Enter your PIN:\n')
        cards = self.read_card(card, pin)
        if cards:
            print('\nYou have successfully logged in!\n')
            self.menu_login(card)
        else:
            print('\nWrong card number or Pin!\n')

    def menu(self):
        while True:
            print('1. Create an account')
            print('2. Log into account')
            print('0. Exit')
            choice = input()
            if choice == '1':
                self.creation_card()
            elif choice == '2':
                self.login()
            elif choice == '0':
                print('Bye!')
                self.cur.close()
                self.conn.close()
                exit()
            else:
                print('Unknown option.\n')

    def menu_login(self, card):
        while True:
            print('1. Balance')
            print('2. Add income')
            print('3. Do transfer')
            print('4. Close account')
            print('5. Log out')
            print('0. Exit')

            choice = input()
            if choice == '1':
                print(self.read_balance(card))
            elif choice == '2':
                self.add_income(card, int(input('Income: ')))
            elif choice == '3':
                self.transfer(card)
            elif choice == '4':
                self.close_account(card)
            elif choice == '5':
                print('You have successfully logged out!\n')
                return
            elif choice == '0':
                print('Bye!')
                self.cur.close()
                self.conn.close()
                exit()
            else:
                print('Unknown option.\n')


BankingSystem().menu()
