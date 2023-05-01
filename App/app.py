from flask import Flask, render_template, request
import requests
from pusher import Pusher
import jinja2
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
import json
import plotly
import plotly.express as px
import os
import datetime
from collections import Counter

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, 'templates')
app = Flask(__name__, template_folder=template_path)


@app.route('/')
def transactions():
    url = "http://192.168.1.183:5000/transactions"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content)
        transactions = []
        for transaction in data['transactions']:
            if '' in transaction:
                del transaction['']
            # print(transaction)
            transactions.append((transaction["trans_date_trans_time"], transaction["amt"]))
        df = pd.DataFrame(transactions, columns=["trans_date_trans_time", "amt"])
        #fig = px.line(df, x="timestamp", y="amount")
        fig = px.line(df, x="trans_date_trans_time", y="amt")
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('dashboard.html', transactionsJSON=graphJSON)
    else:
        print('Error in getting response from the url')
        return render_template('dashboard.html', transactionsJSON=graphJSON)


if __name__ == '__main__':
    #  app.run(debug=True, port=5000, host='0.0.0.0')
    app.run(host='192.168.1.183', port=8000)

# kill $(lsof -t -i:8080) ---------to kill process at 5000
