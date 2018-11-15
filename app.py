from functools import wraps

from flask import Flask, session, request, url_for, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/first_flask"
app.config['SQLCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'iii'
db = SQLAlchemy(app)


# 定义ORM
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<User %r>' % self.username


# 创建表格，插入数据
@app.before_first_request
def create_db():
    db.drop_all()
    db.create_all()
    admin = User(username='admin', password='123456', email='admin@qq.com')
    db.session.add(admin)
    db.session.commit()
    guestes = User(username='guest1', password='12345', email='123@qq.com'),
    db.session.add_all(guestes)
    db.session.commit()


# 登录检验（用户名，密码验证)
def valid_login(username, password):
    user = User.query.filter(and_(User.username == username, User.password == password)).first()
    if user:
        return True
    else:
        return False


# 用户名邮箱验证
def valid_regist(username, email):
    user = User.query.filter(or_(User.username == username, User.email == email)).first()
    if user:
        return False
    else:
        return True


# 登录
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('username'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('loginpage.html', next=request.url))

    return wrapper


# 1.主页

@app.route('/home')
def home():
    return render_template('homepage.html', username=session.get('username'))


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            flash('登录成功！')
            session['username'] = request.form.get('username')
            return redirect(url_for('home'))
        else:
            error = '错误的用户名或者密码!'
    return render_template('loginpage.html', error=error)


# 注销
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


# 注册
@app.route('/regist', methods=['GET', 'POST'])
def regist():
    error = None
    if request.method == 'POST':
        if request.form['password1'] != request.form['password2']:
            error = '两次密码不相同'
        elif valid_regist(request.form['username'], request.form['email']):
            user = User(username=request.form['username'], password=request.form['password1'], email=request.form['email'])
            db.session.add(user)
            db.session.commit()
            flash('成功注册！')
            return redirect(url_for('login'))
        else:
            error = '该用户名已经被注册'
    return render_template('registerpage.html', error=error)


# 删除
@app.route('/delete_user/<id>')
def delete_user(id):
    user = User.query.get(id)
    password = User.query.get(id)
    email = User.query.get(id)
    if user:
        User.query.filter_by(id=id).delete()
        db.session.delete(user)
        db.session.delete(password)
        db.session.delete(email)
        db.session.commit()
    else:
        print('删除作者出错')
        db.session.rollback
    return redirect(url_for('login'))


# 个人中心
@app.route('/person')
@login_required
def panel():
    username = session.get('username')
    user = User.query.filter(User.username == username).first()
    return render_template('personpage.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def hello_world():
    return render_template('welcome.html')



if __name__ == '__main__':
    app.run()
