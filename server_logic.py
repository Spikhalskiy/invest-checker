import simplejson as json
from model_db_manager import get_last_results_for_period
from utils import props


def accounts_summary(period):
    records = get_last_results_for_period(period)
    return json.dumps(map(props, records))
