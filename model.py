from datetime import datetime


class Record:
    provider = ""
    timestamp = None
    account = ""
    pamm = ""
    deposit = None
    balance = None
    declared_profit = None

    def __init__(self, data, timestamp=datetime.now()):
        self.provider = data[0]
        self.timestamp = timestamp
        self.account = data[1]
        self.pamm = data[2]
        self.deposit = float(data[3])
        self.balance = float(data[4])
        if data[5]:
            self.declared_profit = float(data[5])

    def get_db_data(self):
        return self.provider, self.timestamp, self.account, self.pamm, self.deposit, self.balance, self.declared_profit

    def __str__(self):
        return u', '.join(map(unicode, (self.provider, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.account,
                                        self.pamm, self.deposit, self.balance, self.declared_profit))).encode('utf-8')
