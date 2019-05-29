from flask import Flask, render_template, flash, request, redirect, url_for, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yzzismine2@127.0.0.1:3306/user_demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ss'

db = SQLAlchemy(app)


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128), unique=False)


@app.route('/register', methods=['POST'])
def register():
    rform = UserForm()
    username = rform.username.data
    password = rform.password.data

    user = User.query.filter(User.username == username, User.password == password).first()
    if user:
        return '已存在此用户'
    else :

@app.route('/ss', methods=['POST'])
def success():
    return 'success'


@app.route('/lor', methods=['GET', 'POST'])
def lor1():
    lform = UserForm()
    rform = UserForm()

    return render_template('login.html', lform=lform, rform=rform)


@app.before_request
def jc():
    g.username = None
    username = session.get('username')
    password = session.get('password')
    if username:
        user = User.query.filter(User.username == username, User.password == password).first()
        if user:
            g.username = username


db.drop_all()
db.create_all()

if __name__ == '__main__':
    app.run()
