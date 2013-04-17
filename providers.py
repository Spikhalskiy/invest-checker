import re
from json import loads

from mechanize import Browser
from lxml.html import document_fromstring, fragment_fromstring

from settings import Settings
from model import *

ALPARI_PROVIDER_NAME = "Alpari"
FX_TREND_PROVIDER_NAME = "FX-Trend"
GAMMA_IC_PROVIDER_NAME = "GammaIC"

class Provider:

    def __init__(self):
        self.browser = Browser()
        self.settings = Settings("checker.properties")
        self.browser.addheaders = [
            ('User-agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.8'),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
        ]
        self.browser.set_handle_robots(False)

    def login(self):
        b = self.browser
        b.open(self.get_login_url())
        b.select_form(self.get_login_form())
        for k, v in self.get_credentials().items():
            b[k] = v
        b.submit()

    def _get_html(self):
        return self._read_url(self.get_data_url())

    def _read_url(self, url):
        return self.browser.open(url).get_data()

    def _get_doc(self):
        return document_fromstring(self._get_html())

    def parse(self):
        return map(Record, self.extract(self._get_doc()))


class FXTrend(Provider):
    def get_login_url(self):        return "https://fx-trend.com/login"

    def get_credentials(self):
        return {'login': self.settings.get_property("fx.username"), 'pass': self.settings.get_property("fx.password")}

    def get_login_form(self):       return 'login_form'

    def get_data_url(self):         return "https://fx-trend.com/my/pamm_investor/accounts/"

    def get_deposit(self, inv_account):
        doc = document_fromstring(
            self._read_url('https://fx-trend.com/my/pamm_investor/details/' + inv_account[3:])
        )
        transfers = map(
            lambda x: float(x[1].text_content().split(' ')[0]),
            filter(
                lambda x: len(x) == 2 and len(x[0]) == 1 and
                             ('Depositing' in x[0][0].text_content() or 'Withdrawal' in x[0][0].text_content()),
                doc.cssselect('div#mb_center table tr')
            )
        )
        return transfers[0] + transfers[1]

    def extract(self, h):
        return map(
            lambda x: (FX_TREND_PROVIDER_NAME,
                       x[1][0].text, x[2].text_content(), x[6].text.strip(), x[7].text.strip(), x[8].text.strip()),
            filter(
                lambda x: len(list(x)) > 1 and x[5].get('class') == 'acc_status_1',
                h.cssselect('div#investors_block table tr.dt_actual')
            )
        )


class Alpari(Provider):
    def get_login_url(self):    return "https://www.alpari.ru/ru/login/"

    def get_credentials(self):  return {'login': self.settings.get_property("alpari.username"),
                                        'password': self.settings.get_property("alpari.password")}

    def get_data_url(self):     return "https://my.alpari.ru/ru/"

    def get_login_form(self):       return "login"

    def extract(self, h):
        table = fragment_fromstring(loads(
            self._read_url("https://my.alpari.ru/ru/my_pamm/my/essence/share/action/managed_accounts/id_paging_show/1/")
        )['content'])
        data = dict(map(
            lambda x: (x[0].text_content(), (x[3].text_content(),)),
            table[1]
        ))
        return map(
            lambda x: (ALPARI_PROVIDER_NAME, x[0], x[1], data[x[0]][0], x[3].replace(',',''), None),
            map(
                lambda x: (re.split('\W+', x[0][0].text)[0], x[0][0].get('title'), 1, x[1].text, 1),
                filter(
                    lambda x: x[0][0].get('title'),
                    h.cssselect('div#acc_list_purses ul.my-panel > li')
                )
            )
        )


class GammaIC(Provider):
    def get_login_url(self):        return "https://gamma-ic.com/"

    def get_credentials(self):
        return {'USER_LOGIN': self.settings.get_property("gamma.username"),
                'USER_PASSWORD': self.settings.get_property("gamma.password")}

    def get_login_form(self):   return "enter"

    def get_data_url(self):         return "https://gamma-ic.com/investor/"

    def extract(self, h):
        return [[
                    GAMMA_IC_PROVIDER_NAME,
                    'GammaIC',
                    'GammaIC',
                    float(h.cssselect('div.yy > ul > li')[0].text_content().strip().split(' ')[0]),
                    float(h.cssselect('div.block_left div.yi > ul > li')[0].text_content().strip().split(' ')[0]),
                    None
                ]]