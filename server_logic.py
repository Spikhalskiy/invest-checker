from __future__ import division
from datetime import datetime
import simplejson as json
from model_db_manager import get_last_results_for_period
from utils import props
from dateutil.parser import parse
from const import PYTHON_DATE_FORMAT
from providers import ALPARI_PROVIDER_NAME, FX_TREND_PROVIDER_NAME, GAMMA_IC_PROVIDER_NAME


def calculate_profit(curr_rec, prev_rec):
    if curr_rec.provider == FX_TREND_PROVIDER_NAME:
        # fx-trend profit calculation strategy
        if curr_rec.declared_profit and prev_rec.declared_profit:
            # divide by 100 because declared_profit in FX-Trend is percents
            return (curr_rec.declared_profit - prev_rec.declared_profit) / 100 * prev_rec.balance

    #if it is not fx-trend or there is no information about declared profit - try to calculate
    add_deposit_for = curr_rec.deposit - prev_rec.deposit

    # if add deposit > 0 - we simply add money to account and we should correct it from balance profit
    if add_deposit_for < 0:
        add_deposit_for = 0

    return curr_rec.balance - prev_rec.balance - add_deposit_for


def accounts_summary(period):
    records = get_last_results_for_period(period + 1) # one more, earlier date for calculation
    account_names = list(set(map(lambda x: x.account, records)))

    dates = map(lambda round_tmstmp: round_tmstmp.strftime(PYTHON_DATE_FORMAT),
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
            rec.date = datetime(timestamp.year, timestamp.month, timestamp.day).strftime(PYTHON_DATE_FORMAT)

            #add profit in perc in relation to previous date
            if prev is not None:
                profit = calculate_profit(rec, prev)
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

