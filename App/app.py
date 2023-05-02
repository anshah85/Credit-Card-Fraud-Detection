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
import plotly.graph_objs as go
import os
import datetime
from collections import Counter

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, 'templates')
app = Flask(__name__, template_folder=template_path)


@app.route('/')
def transactions():
    url = "http://192.168.1.183:5000/transactions"
    urlCount = "http://192.168.1.183:5000/transactions/metrics"
    urlCategory = "http://192.168.1.183:5000/transactions/category/metrics"
    response = requests.get(url)
    responseCount = requests.get(urlCount)
    responseCategory = requests.get(urlCategory)
    if response.status_code == 200:
        data = json.loads(response.content)
        
        transactions = []
        for transaction in data['transactions']:
            if '' in transaction:
                del transaction['']
            # print(transaction)
            transactions.append((transaction["category"], transaction["zip"]))
        df = pd.DataFrame(transactions, columns=["category", "zip"])
        fig = px.line(df, x="category", y="zip")
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        #Graph2: Fraud and non Fraud records
    fraud_count = 0
    not_fraud_count = 0
    total_transactions = 0
    if response.status_code == 200:
        dataCount = json.loads(responseCount.content)
        print(dataCount)
        fraud_count = dataCount['fraud']
        not_fraud_count = dataCount['notFraud']
        total_transactions = dataCount['totalTransactions']

        # Create the donut chart
        labels = ['Fraud', 'Not Fraud']
        values = [fraud_count, not_fraud_count]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
        fig.update_layout(
        title_text=f"Fraud Transactions: {fraud_count}/{total_transactions} ({fraud_count/total_transactions*100:.2f}%)",
        annotations=[dict(text='Fraud', x=0.5, y=0.5, font_size=20, showarrow=False)]
)
        #Graph3:Histogram of top categories and fraud count
        categories = []
        totals = []
        for result in responseCategory["results"]:
            categories.append(result["_id"])
            totals.append(result["total"])

        graphCount = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('dashboard.html', transactionsJSON=graphJSON, count=graphCount)
    else:
        print('Error in getting response from the url')
        return render_template('dashboard.html')


if __name__ == '__main__':
    #  app.run(debug=True, port=5000, host='0.0.0.0')
    app.run(host='192.168.1.183', port=8000, debug=True)

# kill $(lsof -t -i:8080) ---------to kill process at 5000
