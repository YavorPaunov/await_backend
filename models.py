from flask.ext.sqlalchemy import SQLAlchemy
from util import hex_to_rgb, rgb_to_hex
from time2words import relative_time_to_text
from datetime import datetime
from dateutil.tz import tzutc
import pytz

db = SQLAlchemy()

def created_on_default():
    return datetime.utcnow()

class Counter(db.Model):
    __tablename__ = 'counters'

    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=created_on_default)
    updated_on = db.Column(
        db.DateTime, default=created_on_default, onupdate=created_on_default)
    time = db.Column(db.DateTime)
    text_after = db.Column(db.String())
    text_before = db.Column(db.String())

    theme = db.Column(
        db.Enum('simple', 'trip', name='themes'), default='simple')

    url = db.Column(db.String, unique=True)
    secret = db.Column(db.String)

    # Foreign keys
    trip_theme = db.relationship(
        'TripTheme', backref='counter', lazy='joined', uselist=False)

    def __repr__(self):
        return '<Counter (id: {0}, time:{1})>'.format(self.id, self.time)

    def time_left_in_text(self):
        time_in_seconds = int((self.time.replace(tzinfo=pytz.utc) 
            - datetime.utcnow().replace(tzinfo=pytz.utc)).total_seconds())
        return relative_time_to_text(seconds=abs(time_in_seconds))

    def has_passed(self):
        return self.time.replace(tzinfo=pytz.utc) < datetime.utcnow().replace(tzinfo=pytz.utc)

    def full_text(self):
        full_text_list = []
        if self.has_passed():
            full_text_list = [self.time_left_in_text(), "ago"]
        else:
            if len(self.text_before) > 0:
                full_text_list.append(self.text_before)
            full_text_list.append(self.time_left_in_text())
            if len(self.text_after) > 0:
                full_text_list.append(self.text_after)

        full_text = " ".join(full_text_list)
        full_text = full_text[0].upper() + full_text[1:]

        return full_text

    def to_dict(self, just_created=False):
        data = {
            'id': self.id,
            'created_on': self.created_on,
            'updated_on': self.updated_on,
            'time': self.time,
            'text_after': self.text_after,
            'text_before': self.text_before,
            'full_text': self.full_text(),
            'url': self.url,
            'theme': self.theme
        }

        if self.theme == 'trip':
            data['city_origin'] = self.trip_theme.origin
            data['city_destination'] = self.trip_theme.destination

        if just_created:
            data['secret'] = self.secret

        return data

    def to_json(self):
        return jsonify(self.to_dict())


class TripTheme(db.Model):
    __tablename__ = 'trip_themes'

    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=created_on_default)
    updated_on = db.Column(
        db.DateTime, default=created_on_default, onupdate=created_on_default)
    origin = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)

    # Relationships
    counter_id = db.Column(
        db.Integer, db.ForeignKey('counters.id'), nullable=False)

    def to_dict(self):
        data = {
            'origin': self.origin,
            'destination': self.destination
        }
        return data


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
