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
    del dates[0]    # first date and corresponding records used only as helpers in calculation

    providers = list(set(map(lambda x: x.provider, records)))

    data_set = map(lambda name: sorted(filter(lambda rec: rec.account == name, records),
                                       cmp=lambda x, y: cmp(parse(x.timestamp), parse(y.timestamp))),
                   account_names)

    #process records, add some info for rendering
    for raw in data_set:
        prev = None
        for rec in raw:
            #add date for easy process on client
            timestamp = parse(rec.timestamp)
            rec.date = datetime(timestamp.year, timestamp.month, timestamp.day).strftime("%Y-%m-%d")

            #add profit in perc in relation to previous date
            if prev is not None:
                rec.profit_in_perc = ((rec.balance - prev.balance) - (rec.deposit - prev.deposit)) / rec.deposit
            prev = rec
        del raw[0]  # we use first element only for calculating, they are helpers and should be deleted

    result = {
        "dates": dates,
        "accounts": account_names,
        "providers": providers,
        "dataset": map(lambda x: map(props, x), data_set)
    }

    return json.dumps(result)

