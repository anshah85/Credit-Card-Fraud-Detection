from flask import Flask, render_template, request
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




# Connection to MongoDB
def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)
    return conn[db]

def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))

    return df



@app.route('/twitterPage')
def twitter_page():
	return render_template('twitter.html')

@app.route('/tumblrPage')
def tumblr_page():
	return render_template('Tumblr.html')

@app.route('/redditPage')
def reddit_page():
	return render_template('reddit.html')



@app.route('/tumblr', methods=['POST'])
def domain_graphtumblr():
	data = request.form
	return createTopHastags(data['noOfRecords'])

@app.route('/reddit', methods=['POST'])
def domain_graph():
	data = request.form
	print(data['days'])
	return create_domain_graph(data['days'])
	# return "Graph"

@app.route('/twitter', methods=['POST'])
def twitter_graph():
	data = request.form
	print(data['submitStates'])
	return create_twitter_graph(data['submitStates'])

# @app.route('/twitter_all_data')
# def twitter_all_graph():
# 	return create_twitter_all_graph()
# Method calls

# def createTopUsers(days):
# 	print(days)
# 	db = "FantasticFive"
# 	collection = "tumblr"
# 	df_tumblr = read_mongo(db,collection)

# 	df = read_mongo(db,collection)
# 	df['date'] = pd.to_datetime(df['date'])
# 	df['Date_new'] = df['date'].dt.date
# 	df['blog_name'].describe()
# 	grouped = df.groupby('blog_name')['_id'].agg({'count'})
# 	grouped = grouped.reset_index()
# 	grouped
# 	grouped_top_10 = grouped.nlargest(int(days),'count')
# 	grouped_top_10 = grouped_top_10.reset_index()
# 	grouped_top_10
# 	fig = px.bar(grouped_top_10, x = "blog_name",y = "count", barmode='group')
# 	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# 	return render_template('Tumblr1.html', graphJSON=graphJSON)
	
def createTopHastags(noOfRecords):
	# print(days)
	db = "FantasticFive"
	collection = "tumblr"
	#df_tumblr = read_mongo(db,collection)
	df = read_mongo(db,collection)

	df['date'] = pd.to_datetime(df['date'])
	df['Date_new'] = df['date'].dt.date
	hashtag_extract = df['tags'].sum()
	counts = Counter(hashtag_extract)
	cnt = Counter()
	for text in hashtag_extract:
		cnt[text.lower()] += 1
	plotvariable= cnt.most_common(int(noOfRecords))
	print(plotvariable)
	for i in plotvariable:
		word_freq = pd.DataFrame(plotvariable,
								columns=['hashtag_extract', 'count'])
	word_freq.head()
	word_freq = pd.DataFrame(cnt.most_common(int(noOfRecords)),
                             columns=['hashtag_extract', 'count'])
	word_freq.head()
	fig = px.bar(word_freq, x = "hashtag_extract",y = "count", barmode='group')
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	return render_template('Tumblr.html', tumblrJSON=graphJSON)

def create_domain_graph(days):
	print(days)
	db = "FantasticFive"
	collection = "redditAbortion"
	df_abortion = read_mongo(db,collection)

	grouped_domain = df_abortion.groupby('domain')['_id'].agg({'count'})
	grouped_domain = grouped_domain.reset_index()
	df_abortion['domain'].describe()


	grouped_top_10_domain = grouped_domain.nlargest(int(days),'count')
	grouped_top_10_domain = grouped_top_10_domain.reset_index()
	print(grouped_top_10_domain)
	print(type(grouped_top_10_domain))

	#fig = grouped_top_10_domain.plot.barh(x = "domain",y = "count")
	#graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	fig = px.bar(grouped_top_10_domain, x = "domain",y = "count", barmode='group')
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

     
    # Use render_template to pass graphJSON to html
	print("hello" + days)

	return render_template('reddit.html', redditJSON=graphJSON)

#method for twitter graph
def create_twitter_graph(states):
	db = "FantasticFive"
	collection = "tweets"
	db = _connect_mongo(host='localhost', port=27017, username=None, password=None, db=db)
	data_list = []
	states_list = states.split(",")
	print(states_list)
	for state in states_list:
		print(state)
		data_obj = {}
		count = db[collection].count_documents({ "location": { "$regex": state, "$options": "i" } })
		data_obj['count'] = count
		data_obj['state'] = state
		data_list.append(data_obj)
	print(data_list)
	df =  pd.DataFrame(data_list)
	df.head()
	fig = px.bar(df, x = "state",y = "count", barmode='group')
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return render_template('twitter.html', graphTwitterJSON=graphJSON)


#method for twitter all data graph
@app.route('/dashboard')
def create_twitter_all_graph():
	# db = "FantasticFive"
	# #twitter graph
	# collection = "tweets"
	# # db = _connect_mongo(host='localhost', port=27017, username=None, password=None, db=db)
	# data_list = []
	# states_list = ["AL","KY","OH","AK","LA","OK","AZ","ME","OR","AR","MD","PA","AS","MA","PR","CA","MI","RI","CO","MN","SC","CT","MS","SD","DE","MO","TN","DC","MT","TX","FL","NE","TT","GA","NV","UT","GU","NH","VT","HI","NJ","VA","ID","NM","VI","IL","NY","WA","IN","NC","WV","IA","ND","WI","KS","MP","WY"]
	# for state in states_list:
	# 	data_obj = {}
	# 	# count = db[collection].count_documents({ "location": { "$regex": state, "$options": "i" } })
	# 	data_obj['count'] = count
	# 	data_obj['state'] = state
	# 	data_list.append(data_obj)
	# df =  pd.DataFrame(data_list)
	# df.head()
	# fig = px.bar(df, x = "state",y = "count", barmode='group')
	# graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	# tumblr graph
	# df1 = read_mongo("FantasticFive","tumblr")
	# hashtag_extract = df1['tags'].sum()
	# counts = Counter(hashtag_extract)
	# cnt = Counter()
	# for text in hashtag_extract:
	# 	cnt[text.lower()] += 1
	# plotvariable= cnt.most_common(int(10))
	# print(plotvariable)
	# for i in plotvariable:
	# 	word_freq = pd.DataFrame(plotvariable,
	# 							columns=['hashtag_extract', 'count'])
	# word_freq.head()
	# word_freq = pd.DataFrame(cnt.most_common(int(10)),
    #                          columns=['hashtag_extract', 'count'])
	# word_freq.head()
	# fig1 = px.bar(word_freq, x = "hashtag_extract",y = "count", barmode='group')
	# graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

	# #RedditGraph
	# df_abortion = read_mongo("FantasticFive","redditAbortion")

	# grouped_domain = df_abortion.groupby('domain')['_id'].agg({'count'})
	# grouped_domain = grouped_domain.reset_index()
	# # df_abortion['domain'].describe()
	# grouped_top_10_domain = grouped_domain.nlargest(10,'count')
	# grouped_top_10_domain = grouped_top_10_domain.reset_index()
	# fig2 = px.bar(grouped_top_10_domain, x = "domain",y = "count", barmode='group')
	# graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
	
	
	# #all counts
	# tw_count = db[collection].count_documents({ })
	# rd_count = db["redditAbortion"].count_documents({ })
	# tm_count = db["tumblr"].count_documents({ })
	# total_count = tw_count + rd_count + tm_count
	total_count=1;
	return render_template('dashboard.html',  total_count=str(total_count))
#method for twitter all data graph
@app.route('/')
def create_twitter_all_graphRoot():
	db = "FantasticFive"
	#twitter graph
	collection = "tweets"
	db = _connect_mongo(host='localhost', port=27017, username=None, password=None, db=db)
	data_list = []
	states_list = ["AL","KY","OH","AK","LA","OK","AZ","ME","OR","AR","MD","PA","AS","MA","PR","CA","MI","RI","CO","MN","SC","CT","MS","SD","DE","MO","TN","DC","MT","TX","FL","NE","TT","GA","NV","UT","GU","NH","VT","HI","NJ","VA","ID","NM","VI","IL","NY","WA","IN","NC","WV","IA","ND","WI","KS","MP","WY"]
	for state in states_list:
		data_obj = {}
		count = db[collection].count_documents({ "location": { "$regex": state, "$options": "i" } })
		data_obj['count'] = count
		data_obj['state'] = state
		data_list.append(data_obj)
	df =  pd.DataFrame(data_list)
	df.head()
	fig = px.bar(df, x = "state",y = "count", barmode='group')
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	# tumblr graph
	df1 = read_mongo("FantasticFive","tumblr")
	hashtag_extract = df1['tags'].sum()
	counts = Counter(hashtag_extract)
	cnt = Counter()
	for text in hashtag_extract:
		cnt[text.lower()] += 1
	plotvariable= cnt.most_common(int(10))
	print(plotvariable)
	for i in plotvariable:
		word_freq = pd.DataFrame(plotvariable,
								columns=['hashtag_extract', 'count'])
	word_freq.head()
	word_freq = pd.DataFrame(cnt.most_common(int(10)),
                             columns=['hashtag_extract', 'count'])
	word_freq.head()
	fig1 = px.bar(word_freq, x = "hashtag_extract",y = "count", barmode='group')
	graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

	#RedditGraph
	df_abortion = read_mongo("FantasticFive","redditAbortion")

	grouped_domain = df_abortion.groupby('domain')['_id'].agg({'count'})
	grouped_domain = grouped_domain.reset_index()
	# df_abortion['domain'].describe()
	grouped_top_10_domain = grouped_domain.nlargest(10,'count')
	grouped_top_10_domain = grouped_top_10_domain.reset_index()
	fig2 = px.bar(grouped_top_10_domain, x = "domain",y = "count", barmode='group')
	graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
	
	
	#all counts
	tw_count = db[collection].count_documents({ })
	rd_count = db["redditAbortion"].count_documents({ })
	tm_count = db["tumblr"].count_documents({ })
	total_count = tw_count + rd_count + tm_count
	return render_template('dashboard.html', plot_url=graphJSON,plot_tumblr=graphJSON1, plot_reddit=graphJSON2, tw_count=str(tw_count), rd_count=str(rd_count), tm_count=str(tm_count), total_count=str(total_count))

if __name__ == '__main__':
	#  app.run(debug=True, port=5000, host='0.0.0.0')
    app.run(debug=True)

#kill $(lsof -t -i:8080) ---------to kill process at 5000