from flask import Flask, render_template, request

from graph_api import settings
from graph_api.spider import spider

app = Flask(__name__)

@app.route("/", methods=['GET'])
def main_page():
    return render_template('index.html')

@app.route('/page_name', methods=['POST'])
def page_name():
    assert request.method == 'POST'
    name = request.form['name']
    if not name:
        facebook_spider = spider(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET, name)
        baseinfo = facebook_spider.get_base_info()




