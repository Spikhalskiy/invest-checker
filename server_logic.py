from datetime import datetime
import simplejson as json
from model_db_manager import get_last_results_for_period
from utils import props
from dateutil.parser import parse


def accounts_summary(period):
    records = get_last_results_for_period(period)
    account_names = list(set(map(lambda x: x.account, records)))

    dates = map(lambda round_tmstmp: round_tmstmp.strftime("%Y-%m-%d"), list(set(
                map(lambda tmstmp: datetime(tmstmp.year, tmstmp.month, tmstmp.day),
                    map(lambda rec: parse(rec.timestamp), records)))))

    providers = list(set(map(lambda x: x.provider, records)))

    data_set = map(lambda name: sorted(filter(lambda rec: rec.account == name, records),
                                       cmp=lambda x, y: cmp(parse(x.timestamp), parse(y.timestamp))),
                   account_names)

    result = {
        "dates": dates,
        "accounts": account_names,
        "providers": providers,
        "dataset": map(lambda x: map(props, x), data_set)
    }

    return json.dumps(result)

