from flask import Flask, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import redis
import urllib.parse
import logging

logging.basicConfig(filename="logs.txt")
app = Flask(__name__)
TTL=600
def get_database():

    # Configure MongoDB connection
    u=urllib.parse.quote_plus("raghuvararora@gmail.com")

    p=urllib.parse.quote_plus("qwert_asdfg")
    uri = "mongodb+srv://%s:%s@cluster0.udtc1lx.mongodb.net/?retryWrites=true&w=majority"%(u, p)
    uri = "mongodb+srv://u_ra:0LRHAlo8e01DMJGr@cluster0.udtc1lx.mongodb.net/?retryWrites=true&w=majority"
    # print(uri)
    # app.config["MONGO_URI"] = uri
    # mongo = PyMongo(app)

    # Create a new client and connect to the server
    client = MongoClient(uri,server_api=ServerApi('1'))
    return client["transactions"]
# Send a ping to confirm a successful connection


def get_redis():

    r = redis.Redis(
    host='redis-16311.c57.us-east-1-4.ec2.cloud.redislabs.com',
    port=16311,
    password='biSw53IihqlNggEqqsUK6BMlFuMd9SGZ')
    r.set("key","value")
    return r

redis_client=get_redis()
# Route to retrieve users data
db=get_database()
@app.route("/transactions", methods=["GET"])
def get_transactions():
    try:
        # print(db.list_collections())
        collection_transactions=db["transactions"]
        # collection_transactions
        transactions=collection_transactions.find({},{'_id': 0})

        return jsonify(transactions=[user for user in transactions])
    except Exception as e:
        return "server error "+str(e), 500

@app.route("/transactions/metrics", methods=["GET"])
def get_transaction_metrics():
    # print(db.list_collections())
    try:
        reqstring="/transactions/metrics"
        if not redis_client.exists(reqstring):
            collection_transactions=db["transactions"]
            notFraud=collection_transactions.count_documents({"is_fraud":"0"})
            totalTransactions=collection_transactions.count_documents({})
            fraud=collection_transactions.count_documents({"is_fraud":"1"})

            # transactions=collection_transactions.find({},{'_id': 0})
            res=jsonify(notFraud=notFraud, totalTransactions=totalTransactions,fraud=fraud)
            redis_client.set(reqstring, res.get_data() )
            redis_client.expire(reqstring, TTL)
            return res.get_data()
        else:
            return redis_client.get(reqstring)
    except Exception as e:
        return "server error "+str(e), 500


@app.route("/transactions/category", methods=["GET"])
def get_transaction_category():
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "count": {
                    "$sum": "$is_fraud"
                }
            }
        }
    ]
    reqstring="/transactions/category"
    try:
        if not redis_client.exists(reqstring):
            collection_transactions=db["transactions"]
            agg_result=collection_transactions.aggregate(pipeline)

            # print(agg_result)
            res=jsonify(results=[result for result in agg_result])
            redis_client.set(reqstring, res.get_data() )
            redis_client.expire(reqstring, TTL)
            return res.get_data()
        else:
            return redis_client.get(reqstring)
    except Exception as e:
        return "server error "+str(e), 500


@app.route("/transactions/category/metrics", methods=["GET"])
def get_transaction_category_metrics():
    pipeline = [
        {
            "$group": {
            "_id": "$category",
            "total": {
                "$sum": 1
            },
            "is_fraud": {
                "$sum": {
                "$cond": [
                    {
                    "$eq": [
                        "$is_fraud",
                        True
                    ]
                    },
                    1,
                    0
                ]
                }
            }
            }
        }
    ]

    reqstring="/transactions/category/metrics"
    try:
        if not redis_client.exists(reqstring):
            collection_transactions=db["transactions"]
            agg_result=collection_transactions.aggregate(pipeline)

            # print(agg_result)

            res=jsonify(results=[result for result in agg_result])
            redis_client.set(reqstring, res.get_data() )
            redis_client.expire(reqstring, TTL)
            return res.get_data()
        else:
            return redis_client.get(reqstring)
    except Exception as e:
        return "server error "+str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
