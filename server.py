from flask import Flask
from server_logic import *
from flask import request
from flask import render_template

app = Flask("Invest Checker")


@app.route('/accounts_summary')
def get_accounts_summary():
    period = int(request.args.get('period', 7))
    return accounts_summary(period)


@app.route('/index')
def index():
    return render_template('index.html')

app.run(host='localhost', port=8080, debug=True)