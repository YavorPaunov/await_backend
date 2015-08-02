import os
from flask import Flask, current_app, send_file, url_for, request, g, abort
from flask import jsonify, json
from flask.ext.cors import CORS
from werkzeug.exceptions import NotFound
from models import Counter, TripTheme, db, get_or_create
from sqlalchemy.exc import IntegrityError
from time2words import relative_time_to_text
from datetime import datetime
from util import date_format, random_str
import dateutil.parser
from dateutil.tz import tzutc
import pytz

app = Flask(__name__)

app.secret_key = 'super secret'
app.config['SERVER_NAME'] = "awaitify.com"

app.config['SQLALCHEMY_DATABASE_URI'] = \
    "postgresql://await_user:await_password@localhost/await"

cors = CORS(app)
db.app = app
db.init_app(app)


def create_app():
    with app.app_context():
        db.create_all()


@app.errorhandler(404)
def not_found(error=None):
    data = {
        'status': 404,
        'message': 'Not found'
    }
    return jsonify(**data), 404


@app.route('/', subdomain="www")
def static_root():
    return app.send_static_file('index.html')


@app.route('/<path:path>', subdomain="www")
def static_path(path):
    return app.send_static_file(path)


@app.route('/', subdomain="api")
def index():
    data = {
        'message': "Welcome!"
    }
    return jsonify(**data)


@app.route('/counter', methods=['POST', 'GET'], subdomain="api")
@app.route('/counter/<int:counter_id>', methods=['GET'], subdomain="api")
def counter(counter_id=None):
    response = {
        'status': 'OK'
    }
    if request.method == 'POST':
        data = request.get_json()

        text_after = data['text_after']
        text_before = data['text_before']

        # The time in UTC
        time = dateutil.parser.parse(data['time'])

        theme = data['theme']
        counter = None
        with db.session.no_autoflush:
            # The unlikely event of violationg the unique constraint for url
            # is not handled in any way.
            counter = Counter(url=random_str(), theme=theme, secret=random_str(),
                              text_before=text_before, text_after=text_after, time=time)

            if theme == 'trip':
                origin = data['city_origin']
                destination = data['city_destination']
                trip_theme = TripTheme(counter=counter,
                                       origin=origin,
                                       destination=destination)
                db.session.add(trip_theme)

            db.session.add(counter)

        db.session.commit()
    elif request.method== 'GET':
        if counter_id is not None:
            print 'counter_id', counter_id
            counter = Counter.query.get_or_404(counter_id)
            response['data'] = counter.to_dict()
        else:            
             # Filter out counters
            url = request.args.get('url', None)
            
            if url is None:
                abort(404)

            counters = Counter.query.filter_by(url=url).all()
            response['data'] = map(lambda x: x.to_dict(), counters)

    return jsonify(**response)


@app.route('/counter/<int:id>',
           methods=['GET'], subdomain="api")
def counterz(id=None):
    print 'get counter'
    if request.method == 'GET':
        if id:
            # Show existing counter
            counter = Counter.query.get_or_404(id)
            response = {
                'status': 'OK',
                'data': counter.to_dict()
            }
            return jsonify(**response)
        else:
           
  
            counters = Counter.query.filter(url==url).all()
  
            response = {
                'status': 'OK',
                'data': counters
            }
            return jsonify(**response)

    return 404


@app.route('/convert', subdomain="api")
def convert():
    millis = int(request.args.get('millis'))
    return relative_time_to_text(seconds=(millis / 1000))


if __name__ == '__main__':
    app.run()
