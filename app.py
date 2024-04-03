from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import math
from datetime import datetime
import os
import json

local_server = True
with open('config.json') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'gand-me-danda-le-teri-gand-me-danda-le'
app.config['UPLOAD_FOLDER'] = params['upload_location']
base_dir = os.path.abspath(os.path.dirname(__file__))
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri'] + os.path.join(base_dir, 'instance', 'database.db')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri'] + os.path.join(base_dir, 'instance', 'database.db')
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_passwd'],
    MAIL_DEFAULT_SENDER=params['gmail_user']
)
mail = Mail(app)

db = SQLAlchemy(app)



class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.date)
    
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.date)
    
class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.date)


@app.route('/')
def home():
    return render_template('home.html')


@app.route("/proj/<string:proj_slug>", methods=['GET'])
def project_route(proj_slug):
    project = Projects.query.filter_by(slug=proj_slug).first()
    return render_template('project1.html', params=params, project=project)


  
@app.route('/projects')
def proj_sec():
    projects = Projects.query.filter_by().all()
    last = math.ceil(len(projects) / int(params['num_side_proj']))
    page = request.args.get('page', 1, type=int)
    page = int(page)
    offset = (page - 1) * int(params['num_side_proj'])
    projects = projects[offset:offset + int(params['num_side_proj'])]
    prev = page - 1 if page > 1 else '#'
    after = page + 1 if page < last else '#'
    return render_template('projects.html', params=params, projects=projects, prev=prev, after=after)

  
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        table_type = request.form.get('table_type', 'projects')
        if request.method == 'POST':
            table_type = request.form.get('table_type', 'projects')
            if table_type == 'projects':
                data = Projects.query.all()
            elif table_type == 'posts':
                data = Posts.query.all()
            else:
                data = []
            return render_template('dashboard.html', params=params, data=data, table_type=table_type)
        data = Projects.query.all()
        return render_template('dashboard.html', params=params, data=data, table_type=table_type)
    elif request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('pass')
        if username == params['admin_user'] and password == params['admin_password']:
            session['user'] = username
            table_type = request.form.get('table_type', 'projects')
            if table_type == 'projects':
                data = Projects.query.all()
            elif table_type == 'posts':
                data = Posts.query.all()
            else:
                data = []
            return render_template('dashboard.html', params=params, data=data, table_type=table_type)
    return render_template('Login.html', params=params)


@app.route("/edit/<string:table_type>/<string:id>", methods=['GET', 'POST'])
def editing_sec(id, table_type):
    if 'user' in session and session['user'] == params['admin_user']:
        if table_type == 'projects':
            post = Projects.query.filter_by(id=id).first() if id != 'new' else None
        elif table_type == 'posts':
            post = Posts.query.filter_by(id=id).first() if id != 'new' else None
        else:
            post = None
        if request.method == 'POST':
            title = request.form.get('title')
            slug = request.form.get('slug')
            image = request.form.get('image')
            date = request.form.get('date')
            content = request.form.get('content')
            content = content.replace('\n', '<br>')
            if not id or id == 'new':
                if table_type == 'projects':
                    post = Projects(id=None, title=title, slug=slug, image=image, date=date, content=content)
                elif table_type == 'posts':
                    post = Posts(id=None, title=title, slug=slug, image=image, date=date, content=content)
                db.session.add(post)
                db.session.commit()
                return redirect('/edit/' + table_type + '/' + id)
            else:
                if table_type == 'projects':
                    post = Projects.query.filter_by(id=id).first()
                elif table_type == 'posts':
                    post = Posts.query.filter_by(id=id).first()

                if post:
                    post.title = title
                    post.slug = slug
                    post.image = image
                    post.date = date
                    post.content = content

                    db.session.commit()
                    return redirect('/edit/' + table_type + '/' + id)
            return render_template('editing.html', params=params, id=id, table_type=table_type)
        if table_type == 'projects':
            post = Projects.query.filter_by(id=id).first()
        elif table_type == 'posts':
            post = Posts.query.filter_by(id=id).first()
        return render_template('editing.html', params=params, id=id, table_type=table_type, post=post)
    else:
        return render_template('404.html')


@app.route('/blog')
def blog_sec():
    posts = Posts.query.all()
    last = math.ceil(len(posts) / int(params['num_side_post']))
    page = request.args.get('page', 1, type=int)
    page = int(page)
    offset = (page - 1) * int(params['num_side_post'])
    posts = posts[offset:offset + int(params['num_side_post'])]
    prev = page - 1 if page > 1 else '#'
    after = page + 1 if page < last else '#'
    return render_template('blog.html', params=params, posts=posts, prev=prev, after=after)

  
@app.route("/blog/<string:blog_slug>")
def blogs(blog_slug):
    post = Posts.query.filter_by(slug=blog_slug).first()
    return render_template('blog1.html', params=params, post=post)  

  
@app.route('/contact', methods=['GET', 'POST'])
def cont_sec():
  if request.method == 'POST':
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    entry = Contacts(name=name, email=email, message=message)
    db.session.add(entry)
    db.session.commit()
    subject = 'New Message From Your Website'
    recipient_email = params['gmail_user']

    msg = Message(subject, recipients=[recipient_email])
    msg.body = f"Name: {name}\n\nEmail: {email}\n\nMessage Content: {message}"

    mail.send_message('New Feedback Form Your Website',
                      sender=email,
                      recipients=[params['gmail_user']],
                      body=str(msg)
                      )
    print("Message submitted successfully!")
  return render_template('contact.html', params=params)


@app.route('/about')
def abt_sec():
    return render_template('about.html')
  
  
if __name__ == '__main__':
    with app.app_context():
      db.create_all()
    app.run(host='0.0.0.0', port=3000, debug=True)
