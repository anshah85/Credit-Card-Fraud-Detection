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

def get_transactions():
    url = "http://149.125.108.55:5000/transactions"
    response = requests.get(url)

    if response.status_code == 200:
        data = json.loads(response.content)
        
        transactions = []
        for transaction in data['transactions']:
            if '' in transaction:
                del transaction['']
            transactions.append((transaction["category"], transaction["zip"]))
        df = pd.DataFrame(transactions, columns=["category", "zip"])
        fig = px.line(df, x="category", y="zip")
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
    else:
        print('Error in getting response from the url')
        return None

def get_fraud_chart():
    urlCount = "http://149.125.108.55:5000/transactions/metrics"
    responseCount = requests.get(urlCount)

    fraud_count = 0
    not_fraud_count = 0
    total_transactions = 0
    if responseCount.status_code == 200:
        dataCount = json.loads(responseCount.content)
        print(dataCount)
        fraud_count = dataCount['fraudCount']
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
        graphCount = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphCount
    else:
        print('Error in getting response from the url')
        return None

def get_category_chart():
    urlCategory = "http://149.125.108.55:5000/transactions/category/metrics"
    responseCategory = requests.get(urlCategory)

    categories = []
    fraud_counts = []
    non_fraud_counts = []
    if responseCategory.status_code == 200:
        dataCat = json.loads(responseCategory.content)
        print(dataCat)
        for result in dataCat["results"]:
            categories.append(result["_id"])
            fraud_counts.append(result["fraudCount"])
            non_fraud_counts.append(result["total"])
        # Create a trace for the fraud counts histogram
        fraud_trace = go.Bar(
            x=categories,
            y=fraud_counts,
            name='Fraud',
            marker_color='red',
            orientation='v'
        )

        # Create a trace for the non-fraud counts histogram
        non_fraud_trace = go.Bar(
            x=categories,
            y=non_fraud_counts,
            name='Non-Fraud',
            marker_color='green',
            orientation='v'
        )

        # Create the layout for the histogram
        layout = go.Layout(
            barmode='stack',
            title='Fraud and Non-Fraud Counts by Category',
            xaxis=dict(title='Category'),
            yaxis=dict(title='Count'),
        )
        # Combine the traces and layout into a figure
        fig = go.Figure(data=[fraud_trace, non_fraud_trace], layout=layout)
        graphCat = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphCat

@app.route('/')
def route():
    graphJSON=get_transactions()
    graphCount = get_fraud_chart()
    graphCat = get_category_chart()
    return render_template('dashboard.html',
                            transactionsJSON=graphJSON, 
                            count=graphCount, cat=graphCat)

if __name__ == '__main__':
     app.run(debug=True, port=8000, host='149.125.108.55')
  #  app.run(host='192.168.1.183', port=8000, debug=True)

# kill $(lsof -t -i:8080) ---------to kill process at 5000
