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
            print "Error occurred while processing " + str(provider)
            traceback.print_exc(e)

retrieve_to_db(GammaIC, FXTrend)