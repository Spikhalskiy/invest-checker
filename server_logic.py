from __future__ import division
from datetime import datetime
import simplejson as json
from model_db_manager import get_last_results_for_period
from utils import props
from dateutil.parser import parse


def accounts_summary(period):
    records = get_last_results_for_period(period + 1) # one more, earlier date for calculation
    account_names = list(set(map(lambda x: x.account, records)))

    dates = map(lambda round_tmstmp: round_tmstmp.strftime("%Y-%m-%d"),
                sorted(list(set(
                    map(lambda tmstmp: datetime(tmstmp.year, tmstmp.month, tmstmp.day),
                        map(lambda rec: parse(rec.timestamp), records)))))
                )

    providers = list(set(map(lambda x: x.provider, records)))

    # form a list of sorted by date lists of records
    data_set = map(lambda name: sorted(filter(lambda rec: rec.account == name, records),
                                       cmp=lambda x, y: cmp(parse(x.timestamp), parse(y.timestamp))),
                   account_names)

    #prepare summary arrays
    summary_profit_for_date = {}
    summary_prev_balance_for_date = {}
    for date in dates:
        summary_profit_for_date[date] = 0
        summary_prev_balance_for_date[date] = 0

    #process records, add some info for rendering
    for row in data_set:
        prev = None
        for rec in row:
            #add date for easy process on client
            timestamp = parse(rec.timestamp)
            rec.date = datetime(timestamp.year, timestamp.month, timestamp.day).strftime("%Y-%m-%d")

            #add profit in perc in relation to previous date
            if prev is not None:
                profit = (rec.balance - prev.balance) - (rec.deposit - prev.deposit)
                prev_balance = prev.balance
                rec.profit_in_perc = profit / prev_balance
                #use later for summary series
                summary_profit_for_date[rec.date] += profit
                summary_prev_balance_for_date[rec.date] += prev_balance
            prev = rec

    # remove helpers - elements for first additional date
    del dates[0]    # first date and corresponding records used only as helpers in calculation
    for row in data_set:
        del row[0]  # we use first element only for calculating, they are helpers and should be deleted
    data_set = filter(lambda row: row, data_set) # remove empty rows (this rows contained only one helper element)

    #process summary
    sumary_perc_profit = map(lambda date: summary_profit_for_date[date] / summary_prev_balance_for_date[date], dates)

    # serialize in json
    result = {
        "dates": dates,
        "providers": providers,
        "dataset": map(lambda x: map(props, x), data_set),
        "summary_profit": sumary_perc_profit
    }

    return json.dumps(result)

