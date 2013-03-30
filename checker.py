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
from providers import *

out = sys.argv[-1] if len(sys.argv) > 1 else None
out = open(out, 'a') if out else sys.stdout

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
