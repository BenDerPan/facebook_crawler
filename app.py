from flask import Flask, render_template, request
import simplejson as json


app = Flask(__name__)


@app.route('/sentiment/<pagename>')
def show_facebook_sentiment(pagename):
    print 'sentiment : ' + pagename
    return render_template('sentiment.html', pagename=pagename)

@app.route('/buzzgraph/<pagename>')
def show_facebook_buzzgraph(pagename):
    print 'buzzgraph : ' + pagename
    with open('static/buzzgraph.json') as data_file:
        data = json.load(data_file)

    return render_template('buzzgraph.html', data=json.dumps(data))

