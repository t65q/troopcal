from flask import Flask, jsonify, request, make_response, render_template
from urllib.parse import urlparse, parse_qs, urlunparse
from ics import Calendar
from ics.timeline import Timeline
from urllib.request import urlopen
import arrow

app = Flask(__name__)
# configure this url to be the endpoint for your ical server
url = "https://www.scoutbook.com/ics/62638.E7F02.ics"

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "This should contain info on how to use the oEmbed server..."})

@app.route('/oembed', methods=['GET'])
def oembed():
    status404 = jsonify({"result":"Unable to find the requested resource."}), 404
    status501 = jsonify({"result":"Not implemented."}), 501
    # let's check the request for a url
    params = request.args
    if 'format' in params:
        if params['format'] != 'json':
            return status501
    width = 400
    height = 600
    max_width = params.get('maxwidth',width)
    max_height = params.get('maxheight',height)

    if max_width < width:
        width = max_width
    if max_height < height:
        height = max_height

    if 'url' in params:
        # from this url we get some json formatted data that
        url = params['url']

        response_data = {
            "version": "1.0",
            "type": "rich",
            "width": width,
            "height": height,
            "html": "<iframe src=\"%s\" width=\"400\" height=\"600\" scrolling=\"yes\" frameborder=\"0\" allowfullscreen><\/iframe>" % url
        }
        return jsonify(response_data)


@app.route('/upcoming', methods=['GET'])
def upcoming():
    status404 = jsonify({"result":"Unable to find the requested resource."}), 404
    status501 = jsonify({"result":"Not implemented."}), 501
    # we need to parse the contents of the .ics file
    calendar = Calendar(urlopen(url).read().decode('iso-8859-1'))
    timeline = Timeline(calendar).start_after(arrow.utcnow())
    # then we need to format them for display
    events = []
    #'YYYY-MM-DD HH:mm:ss ZZ'
    for event in timeline:
        event_data = {
            "name":event.name, 
            "begin_human":event.begin.humanize(),
            "description":event.description, 
            "location":event.location, 
            "begin":event.begin.format('dddd, MMM D, YYYY h:mm A'), 
            "end":event.end.format('dddd, MMM D, YYYY h:mm A'),
            "url":event.url
        }
        events.append(event_data)
    return render_template('upcoming.html',context={"events":events})