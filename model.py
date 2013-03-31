from datetime import datetime


class Record:
    @property
    def profit(self):
        return self.balance - self.deposit

    @property
    def percent(self):
        return self.profit / self.deposit

    def __init__(self, data, timestamp=datetime.now()):
        self.provider = data[0]
        self.timestamp = timestamp
        self.account = data[1]
        self.pamm = data[2]
        self.deposit = float(data[3])
        self.balance = float(data[4])

    def get_db_data(self):
        return self.provider, self.timestamp, self.account, self.pamm, self.deposit, self.balance

    def __str__(self):
        return u', '.join(map(unicode, (self.provider, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.account,
                                        self.pamm, self.deposit, self.balance, self.profit, self.percent))).encode('utf-8')
