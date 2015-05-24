from flask import Flask, request, jsonify, render_template
import os
app = Flask(__name__)

from classifier import Classifier
# from downloader import Downloader
from retrying import retry
import urllib2
from bs4 import BeautifulSoup

DEBUG = os.environ.get('DEBUG') != None
VERSION = 0.1

@retry(stop_max_attempt_number=5)
def fetch_url(url, readable=False):
    '''
    get url with readability
    '''
    html = urllib2.urlopen(url).read()
    if readable: 
        from readability.readability import Document
        readable_article = Document(html).summary()
        readable_title = Document(html).short_title() # unused

        soup = BeautifulSoup(readable_article)

        return soup.get_text()
    else:
        soup = BeautifulSoup(html)
        # extract paragraphs and concatenate them together in one string
        return ' '.join(map((lambda x:x.getText()),soup.find_all('p')))

@app.route("/")
def index():
    """
    When you request the root path, you'll get the index.html template.

    """
    return render_template("index.html")

@app.route("/")
def root():
    return jsonify(dict(message='political affiliation prediction api', version=VERSION))

@app.route("/predict", methods=['POST'])
def predict():
    if request.form.has_key('url'):
        url = request.form['url']
        text = fetch_url(url)
        return jsonify(classifier.predict(text))
    else:
        text = request.form['text']
        return jsonify(classifier.predict(text))

if __name__ == "__main__":
    port = 5000
    classifier = Classifier()
    # Open a web browser pointing at the app.
    # os.system("open http://localhost:{0}".format(port))

    app.run(host='0.0.0.0', port = port, debug = DEBUG)
