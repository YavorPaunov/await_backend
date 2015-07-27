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

    return jsonify(data)

@app.route('/')
def index():
    data = {
        'message':"Welcome!"
    }
    return jsonify(data)


@app.route('/counter', methods=['POST', 'GET'])
@app.route('/counter/<int:id>', 
    methods=['GET', 'DELETE', 'UPDATE'])
def counter(id=None):
    if request.method == 'POST':
        response = {
            'status': 'OK'
        }

        data = request.get_json()
        print 'data', data

        text_after = data['text_after']
        text_before = data['text_before']

        # The time in UTC
        time = dateutil.parser.parse(data['time'])
        print 'time', time
        print 'now', datetime.utcnow().replace(tzinfo=pytz.utc)

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

        response['data'] = counter.to_dict(True)
        return jsonify(response)

    if request.method == 'GET':
        if id:
            # Show existing counter
            counter = Counter.query.get_or_404(id)
            response = {
                'status': 'OK',
                'data': counter.to_dict()
            }

            return jsonify(response)
        else:
            # Filter out counters
            response = {
                'status':"Not implemented"
            }
            return jsonify(response)

    if request.method == 'UPDATE' and id is not None:
        response = {
            'status':"Not implemented"
        }
        return jsonify(response)

    if request.method == 'DELETE' and id is not None:
        response = {
            'status':"Not implemented"
        }
        return jsonify(response)

        # Implement some sort of simple authentication
        counter = Counter.query.filter(Counter.url
                ==url).first_or_404()

        if counter:
            db.session.delete(counter)
            db.session.commit()
        else:
            abort(404)

        response = {
            'status': "OK"
        }
        return jsonify(response)

    return 404


@app.route('/convert')
def convert():
    millis = int(request.args.get('millis'))
    return relative_time_to_text(seconds=(millis / 1000))


if __name__ == '__main__':
    app.run()
