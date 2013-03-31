from datetime import datetime


class Record:
    def init_calculable_field(self):
        self.profit = self.balance - self.deposit
        self.percent = self.profit / self.deposit

    def __init__(self, data, timestamp=datetime.now()):
        self.provider_name = data[0]
        self.timestamp = timestamp
        self.account = data[1]
        self.pamm = data[2]
        self.deposit = float(data[3])
        self.balance = float(data[4])
        self.init_calculable_field()

    def get_db_data(self):
        return self.provider_name, self.timestamp, self.account, self.pamm, self.deposit, self.balance

    def __str__(self):
        return u', '.join(map(unicode, (self.provider_name, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.account,
                                        self.pamm, self.deposit, self.balance, self.profit, self.percent))).encode('utf-8')
