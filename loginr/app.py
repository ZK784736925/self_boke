from flask import Flask, render_template, flash, request, redirect, url_for, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yzzismine2@127.0.0.1:3306/user_demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ss'
csrf = CSRFProtect(app)

db = SQLAlchemy(app)


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('登录')
    submit2 = SubmitField('注册')


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
    password2 = rform.password2.data
    user = User.query.filter(User.username == username).first()
    if user:
        return '已存在此用户 请重新注册'
    else:
        if password == password2:
            new_user = User(username=username, password=password)

            db.session.add(new_user)
            db.session.commit()

            return '注册成功'
        else:
            return '两次密码不一致 请重新注册'


@app.route('/ss', methods=['GET', 'POST'])
def success():
    return '登录成功'


@app.route('/login', methods=['POST'])
def login():
    lform = UserForm()
    username = lform.username.data
    password = lform.password.data
    user = User.query.filter(User.username == username, User.password == password).first()
    if user:
        session['username'] = username
        session['password'] = password
        return redirect(url_for('lor1'))
    else:
        return '用户名或密码错误'


@app.route('/', methods=['GET', 'POST'])
def lor1():
    lform = UserForm()
    rform = UserForm()
    if g.username:
        return redirect(url_for('success'))
    else:
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
