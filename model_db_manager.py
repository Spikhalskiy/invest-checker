import sqlite3 as lite
from model import *
from datetime import timedelta
import dateutil.parser

RECORD_SQL_COLUMN_NAMES = "provider, timestamp, account, pamm, deposit, balance"

def transactional(fn):
    """add transactional semantics to a method."""

    def transact(*args):
        con = lite.connect('checker.db')
        try:
            result = fn(con, *args)
            con.commit()
            return result
        except:
            con.rollback()
            raise
    transact.__name__ = fn.__name__
    return transact


@transactional
def init_db(connection):
    connection.execute("CREATE TABLE Record(Id integer primary key autoincrement, \
                provider VARCHAR(64), timestamp TIMESTAMP, account TEXT, pamm TEXT, \
                deposit REAL, balance REAL)")

@transactional
def save(connection, rec):
    connection.execute("INSERT INTO Record(%s) \
                        VALUES(?, ?, ?, ?, ?, ?)" % RECORD_SQL_COLUMN_NAMES, rec.get_db_data())

@transactional
def get_last_results_for_period(connection, number_of_days):
    start_datetime = datetime.now() - timedelta(days=number_of_days)
    rounded_start_datetime = datetime(
        start_datetime.year, start_datetime.month, start_datetime.day, 0, 0, 0)

    query = ("SELECT %s FROM Record" % RECORD_SQL_COLUMN_NAMES) + " JOIN \
                        (SELECT MAX(timestamp) as tmstmp, provider as prov_name, account as acc \
                            FROM Record WHERE timestamp > :from_time \
                            GROUP BY provider, account, \
                            strftime(" + r"'%Y%m%d'" + ", timestamp)) \
                        ON provider = prov_name AND account = acc AND timestamp = tmstmp"

    cur = connection.cursor()

    cur.execute(query, {"from_time": rounded_start_datetime})
    data = cur.fetchall()
    records = map(record_from_database, data)
    return records


def record_from_database(database_data):
    return Record((database_data[0], database_data[2], database_data[3], database_data[4], database_data[5]),
                  database_data[1])

