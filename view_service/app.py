from flask import Flask, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse
app = Flask(__name__)

def get_database():

    # Configure MongoDB connection
    u=urllib.parse.quote_plus("raghuvararora")

    p=urllib.parse.quote_plus("QKpTBzfqCPyYa6X2")
    uri = "mongodb+srv://%s:%s@cluster0.udtc1lx.mongodb.net/?retryWrites=true&w=majority"%(u, p)
    uri = "mongodb+srv://u_ra:0LRHAlo8e01DMJGr@cluster0.udtc1lx.mongodb.net/?retryWrites=true&w=majority"
    # print(uri)
    # app.config["MONGO_URI"] = uri
    # mongo = PyMongo(app)

    # Create a new client and connect to the server
    client = MongoClient(uri,server_api=ServerApi('1'))
    return client["transactions"]
# Send a ping to confirm a successful connection


# Route to retrieve users data
db=get_database()
@app.route("/transactions", methods=["GET"])
def get_transactions():
    # print(db.list_collections())
    collection_transactions=db["transactions"]
    # collection_transactions
    transactions=collection_transactions.find({},{'_id': 0})

    return jsonify(transactions=[user for user in transactions])

@app.route("/transactions/metrics", methods=["GET"])
def get_transaction_metrics():
    # print(db.list_collections())
    collection_transactions=db["transactions"]
    notFraud=collection_transactions.count_documents({"is_fraud":"0"})
    totalTransactions=collection_transactions.count_documents({})
    fraud=collection_transactions.count_documents({"is_fraud":"1"})

    # transactions=collection_transactions.find({},{'_id': 0})

    return jsonify(notFraud=notFraud, totalTransactions=totalTransactions,fraud=fraud)


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
    collection_transactions=db["transactions"]
    agg_result=collection_transactions.aggregate(pipeline)

    # print(agg_result)
    return jsonify(results=[result for result in agg_result])


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
    collection_transactions=db["transactions"]
    agg_result=collection_transactions.aggregate(pipeline)

    # print(agg_result)
    return jsonify(results=[result for result in agg_result])


if __name__ == "__main__":
    app.run(debug=True)
