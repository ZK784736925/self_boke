from flask import Flask, render_template, redirect, url_for, flash, request, g, jsonify, Response, session
from flask_wtf import FlaskForm
from wtforms.validators import required
from sqlalchemy import extract
import datetime
from wtforms.fields import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import uuid
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yzzismine2@127.0.0.1:3306/self_blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "12345678"
app.secret_key = 'ss'

csrf = CSRFProtect(app)

db = SQLAlchemy(app)


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('登录')
    submit2 = SubmitField('注册')


class Article(db.Model):

    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    author_id = db.Column(db.Integer, unique=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128), unique=False)


@app.route('/editor')
def editor():
    return render_template('ckeditor5.html')


@app.route('/editorup/<blog_id>')
def editup(blog_id):
    session['upblog_id']=blog_id
    return render_template('updateck.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_key = request.form.get('search')
    article = Article.query.all()
    if search_key:
        return render_template('searchjm.html', search_key=search_key, article=article)

    else:
        return redirect(url_for('lor1'))


@app.route('/editupd', methods=['POST'])
def ck_editorup():
    blog_id = session.get('upblog_id')
    print(blog_id)
    article = Article.query.get(blog_id)
    content = request.form.get('content')
    title = request.form.get('title')

    if content and title:
        article.title = title
        article.content = content
        db.session.commit()
        return redirect(url_for('lor1'))

    else:
        return '标题或内容为空'


@csrf.exempt
@app.route('/img', methods=['POST'])
def img_load():
    file = request.files['upload']
    suffix = file.filename.rsplit('.', 1)[1]
    name = uuid.uuid4().hex + '.' + suffix
    while os.path.exists(os.path.join(os.getcwd(), 'static/imgs', name)):
        name = uuid.uuid4().hex + '.' + suffix
    file.save(os.path.join(os.getcwd(), 'static/imgs', name))
    response = {
                'uploaded': True,
                'url': '/imgs/' + name
                }
    return jsonify(response)


@app.route('/imgs/<img_name>')
def load(img_name):
    image = os.path.join(os.getcwd(), 'static/imgs', img_name)
    if not os.path.exists(image):
        return '', 404
    suffix = {
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif'
    }
    mine = suffix[str(image.rsplit('.', 1)[1])]
    with open(image, 'rb') as file:
        img = file.read()
    return Response(img, mimetype=mine)


@app.route('/edit', methods=['POST'])
def ck_editor():
    content = request.form.get('content')
    title = request.form.get('title')

    if content and title:
        new_article = Article(title=title, content=content, author_id=g.id)
        db.session.add(new_article)
        db.session.commit()
        return redirect(url_for('lor1'))

    else:
        return '标题或内容为空'


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
        article = Article.query.all()

        return render_template('userjm.html', article=article)

    else:

        return render_template('lor.html', lform=lform, rform=rform)


@app.route('/blog/<blog_id>', methods=['GET', 'POST'])
def blogll(blog_id):
    article = Article.query.get(blog_id)

    return render_template('blog.html', article=article)


@app.route('/delete_blog/<blog_id>', methods=['GET', 'POST'])
def delete_blog(blog_id):
    article = Article.query.get(blog_id)
    db.session.delete(article)
    db.session.commit()

    return redirect(url_for('lor1'))



@app.before_request
def jc():
    g.username = None
    username = session.get('username')
    password = session.get('password')
    if username:
        user = User.query.filter(User.username == username, User.password == password).first()
        if user:
            g.username = username
            g.id = user.id


@app.context_processor
def name():
    username = session.get('username')
    return {'username': username}


db.drop_all()
db.create_all()

if __name__ == '__main__':
    app.run()
