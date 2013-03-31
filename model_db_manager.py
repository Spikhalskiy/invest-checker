import sqlite3 as lite
from model import *

def transactional(fn):
    """add transactional semantics to a method."""

    def transact(*args):
        con = lite.connect('checker.db')
        try:
            fn(con, *args)
            con.commit()
        except:
            con.rollback()
            raise
    transact.__name__ = fn.__name__
    return transact


@transactional
def init_db(connection):
    connection.execute("CREATE TABLE Record(Id integer primary key autoincrement, \
                provider_name VARCHAR(64), timestamp TIMESTAMP, account TEXT, pamm TEXT, \
                deposit REAL, balance REAL)")

@transactional
def save(connection, rec):
    connection.execute("INSERT INTO Record(provider_name, timestamp, account, pamm, deposit, balance) \
                        VALUES(?, ?, ?, ?, ?, ?)", rec.get_db_data())


def record_from_database(database_data):
    return Record((database_data[0], database_data[2], database_data[3], database_data[4], database_data[5]),
                  database_data[1])

