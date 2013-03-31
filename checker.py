import operator
import traceback
from providers import *
from model_db_manager import save


def process(provider):
        p = provider()
        p.login()
        return p.parse()


def retrieve_to_db(*args):
    for provider in args:
        try:
            for elem in process(provider):
                save(elem)
        except BaseException as e:
            print "Error occured while processing " + str(provider)
            traceback.print_exc(e)


def total(provider):
        data = process(provider)
        print map(str, data)

        profit = reduce(operator.add, map(lambda x: x.profit, data))
        depo = reduce(operator.add, map(lambda x: x.deposit, data))
        print profit, depo, profit / depo


# def report(*args):
#         for provider in args:
#                 try:
#                         for elem in process(provider):
#                                 print >>out, str(elem)
#                 except BaseException as e:
#                         print "Error occured while processing " + str(provider)
#                         traceback.print_exc(e)
#
#
# out = sys.argv[-1] if len(sys.argv) > 1 else None
# out = open(out, 'a') if out else sys.stdout

retrieve_to_db(GammaIC, FXTrend)