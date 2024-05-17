from . import db
import base64
from sqlalchemy import LargeBinary

class AdminData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class EmpData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    empid = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer)
    category = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(LargeBinary, nullable=True)

    def get_profile_image_base64(self):
        if self.profile_image:
            return base64.b64encode(self.profile_image).decode('utf-8')
        return None

class Leaves(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    empid = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    numberOfDays = db.Column(db.Integer, nullable=False)
    fromDate = db.Column(db.DateTime, nullable=False)
    toDate = db.Column(db.DateTime, nullable=False)

class ProjectList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projectName = db.Column(db.String(255))
    task = db.Column(db.String(255))  
    tags = db.Column(db.String(255))
    timeElapsed = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'projectName': self.projectName,
            'tags': self.tags,
            'timeElapsed': self.timeElapsed
        }

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'allDay': self.all_day
        }
class TagList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100), nullable=False)
