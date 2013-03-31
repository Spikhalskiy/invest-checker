from flask import Flask
from server_logic import *
from flask import request

app = Flask("Invest Checker")


@app.route('/accounts_summary')
def get_accounts_summary():
    period = int(request.args.get('period', 7))
    return accounts_summary(period)


app.run(host='localhost', port=8080, debug=True)