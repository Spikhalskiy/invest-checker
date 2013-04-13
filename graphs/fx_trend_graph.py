import traceback
from providers import FXTrend
from model_db_manager import save
from settings import Settings
from dateutil.parser import parse
from mechanize import Browser
from lxml.html import document_fromstring
from graph import GraphPoint

def build_weekly_graph(url, tag=None, start_date=None, provider=None):
    if not provider:
        provider = FXTrend()
    if not start_date:
        start_date = parse('2012-01-01')
    if not tag:
        tag = url.split('/')[-2]

    provider.login()
    html = document_fromstring(provider._read_url(url))
    rate_tr = filter(lambda x: len(x) > 1 and 'Remuneration' in x[0].text_content(), html.cssselect('table tr'))
    rate = float(rate_tr[0][1].text_content().split(' ')[0])/100
    for row in filter(
            lambda x: len(list(x)) == 3 and len(x[0].text_content().split(' - ')) == 2,
            html.cssselect('table.my_accounts_table tr')[1:]):
        date = parse(row[0].text_content().split(' - ')[0])
        if date >= start_date:
            yield GraphPoint(
                date=date,
                category="Weekly_PAMM_Stats",
                name=tag,
                value=float(row[2].text_content()[:-1]) * rate
            )

