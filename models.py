from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from peewee import *

import datetime


DATABASE = SqliteDatabase('learningjournal.db')


class User(UserMixin, Model):
    
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=20)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)
    
    class Meta:
        
        database = DATABASE
        
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(username = username, email = email, password = generate_password_hash(password), is_admin = admin)
        except IntegrityError:
            raise ValueError('That user already exists')


class Entries(Model):
    username = ForeignKeyField(User, backref='entries')
    title = CharField(max_length=255)
    date = DateField()
    timeSpent = IntegerField()
    whatILearned = TextField()
    ResourcesToRemember = TextField()
    
    class Meta:
        database = DATABASE
        
    @classmethod
    def create_entry(cls, username, title, date, timeSpent, whatILearned, ResourcesToRemember):
        with DATABASE.transaction():
            cls.create(username=username, title=title, date=date, timeSpent=timeSpent, whatILearned=whatILearned, ResourcesToRemember=ResourcesToRemember)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Entries, User], safe=True)
    DATABASE.close()