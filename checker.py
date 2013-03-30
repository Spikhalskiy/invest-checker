from mechanize import Browser
from lxml.cssselect import CSSSelector
from lxml.html import document_fromstring, fragment_fromstring
from lxml.etree import tostring
import sys, operator, re
from json import loads
from datetime import datetime
import lxml
import traceback
from settings import Settings

BUF = len(sys.argv) > 1 and sys.argv[1] == 'buf'
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
out = sys.argv[-1] if len(sys.argv) > 1 and not BUF else None
out = open(out, 'a') if out else sys.stdout

def read_buf():
        with open('buffer.html', 'r') as buf:
                return '\n'.join(buf.readlines())

class Record:
        def __init__(self, data, timestamp=TIMESTAMP):
                self.timestamp = timestamp
                self.account = data[0]
                self.pamm = data[1]
                self.deposit = float(data[2])
                self.balance = float(data[3])
                self.profit = self.balance - self.deposit
                self.percent = self.profit / self.deposit

        def __str__(self):
                return u', '.join(map(unicode, (self.timestamp, self.account, self.pamm, self.deposit, self.balance, self.profit, self.percent))).encode('utf-8')


class Provider:

        def __init__(self):
                self.browser = Browser()
                self.browser.addheaders = [
('User-agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'),
                        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                         ('Accept-Language', 'en-US,en;q=0.8'),
                         ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
                ]
                self.browser.set_handle_robots(False)

        def login(self):
                if BUF: return
                b = self.browser
                b.open(self.get_login_url())
                b.select_form(self.get_login_form())
                for k, v in self.get_credentials().items():
                        b[k] = v
                b.submit()

        def _get_html(self):
                return read_buf() if BUF else self._read_url(self.get_data_url())

        def _read_url(self, url): return self.browser.open(url).get_data()

        def _get_doc(self):
                return document_fromstring(self._get_html())

        def parse(self):
                return map(Record, self.extract(self._get_doc()))


class FXTrend(Provider):
        def get_login_url(self):        return "https://fx-trend.com/login"

        def get_credentials(self):
            settings = Settings("checker.properties")
            return {'login': settings.get_property("fx.username"), 'pass': settings.get_property("fx.password")}

        def get_login_form(self):       return 'login_form'

        def get_data_url(self):         return "https://fx-trend.com/my/pamm_investor/accounts/"

        def extract(self, h):
                return map(
                        lambda x: (x[1][0].text, x[2].text_content(), x[6].text.strip(), x[7].text.strip()),#, x[8].text.strip()),
                        filter(
                                lambda x: len(list(x)) > 1,
                                h.cssselect('div#investors_block table tr.dt_actual')
                        )
                )


class Alpari(Provider):
        def get_login_url(self):    return "https://www.alpari.ru/ru/login/"

        def get_credentials(self):  return {'login': '$$$', 'password': '%%%'}

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
                        lambda x: (x[0], x[1], data[x[0]][0], x[3].replace(',','')),
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
            settings = Settings("checker.properties")
            return {'USER_LOGIN': settings.get_property("gamma.username"),
                    'USER_PASSWORD': settings.get_property("gamma.password")}

        def get_login_form(self):   return "enter"

        def get_data_url(self):         return "https://gamma-ic.com/investor/"

        def extract(self, h):
                return [[
                        'GammaIC',
                        'GammaIC',
                        float(h.cssselect('div.yy > ul > li')[0].text_content().strip().split(' ')[0]),
                        float(h.cssselect('div.block_left div.yi > ul > li')[0].text_content().strip().split(' ')[0])
                        ]]


def process(provider):
        p = provider()
        p.login()
        return p.parse()


def total(provider):
        data = process(provider)
        print map(str, data)

        profit = reduce(operator.add, map(lambda x: x.profit, data))
        depo = reduce(operator.add, map(lambda x: x.deposit, data))
        print profit, depo, profit/depo


def report(*args):
        for provider in args:
                try:
                        for elem in process(provider):
                                print >>out, str(elem)
                except BaseException as e:
                        print "Error occured while processing " + str(provider)
                        traceback.print_exc(e)

total(GammaIC)
# total(Alpari)
total(FXTrend)

# report(GammaIC, FXTrend, Alpari)
#report(Alpari)
