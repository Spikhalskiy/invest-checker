from flask import Flask
from server_logic import *
from flask import request
from flask import render_template
from settings import Settings

app = Flask("Invest Checker")

@app.route('/accounts_summary')
def get_accounts_summary():
    period = int(request.args.get('period', 7))
    return accounts_summary(period)


@app.route('/index')
def index():
    return render_template('index.html')


settings = Settings("checker.properties")
app.run(host=settings.get_property("ip.to.listen"),
        port=int(settings.get_property("port.to.listen")),
        debug=bool(settings.get_property("debug")))