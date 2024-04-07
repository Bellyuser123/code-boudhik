from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import requests
from io import BytesIO
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
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri'] + os.path.join(base_dir, 'data', 'database.db')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri'] + os.path.join(base_dir, 'data', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    date = db.Column(db.DateTime, nullable=False)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)


class Signups(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=False)


@app.route('/')
def welcome():
    return render_template('front.html')


@app.route('/home')
def home():
    posts = Posts.query.filter_by().all()[0:params['num_index']]
    projects = Projects.query.filter_by().all()[0:params['num_index']]
    return render_template('home.html', params=params, projects=projects, posts=posts)


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
                print("projects")
            elif table_type == 'posts':
                data = Posts.query.all()
                print("posts")
            elif table_type == 'contacts':
                data = Contacts.query.all()
                print("contacts")
            elif table_type == 'signups':
                data = Signups.query.all()
                print("signups")
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
                print("projects")
            elif table_type == 'posts':
                data = Posts.query.all()
                print("posts")
            elif table_type == 'contacts':
                data = Contacts.query.all()
                print("contacts")
            elif table_type == 'signups':
                data = Signups.query.all()
                print("signups")
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
            date_str = request.form.get('date')
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                date = datetime.now()
            content = request.form.get('content')
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


@app.route("/delete/<string:table_type>/<string:id>")
def delete(id, table_type):
    if 'user' in session and session['user'] == params['admin_user']:
        if table_type == 'projects':
            post = Projects.query.filter_by(id=id).first() if id != 'new' else None
        elif table_type == 'posts':
            post = Posts.query.filter_by(id=id).first() if id != 'new' else None
        elif table_type == 'contacts':
            post = Contacts.query.filter_by(id=id).first() if id != 'new' else None
        else:
            post = None
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')
    else:
        return render_template('404.html')


@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return """
                    <script>
                    setTimeout(function() {
                        window.location.href = "/dashboard";
                    }, 3000);
                    </script>
                    <div>Uploaded successfully</div>
                    """
    else:
        return render_template('404.html')


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/signup", methods=['GET', 'POST'])
def sign_sec():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        entry = Signups(name=name, email=email)
        db.session.add(entry)
        db.session.commit()
        return redirect('/success')
    return render_template('signup.html', params=params)


@app.route("/success", methods=['GET', 'POST'])
def download():
    image_url = 'https://cdn.glitch.global/23ec6fd6-4c08-4fcf-8e26-4de29dd1642e/Thank_you_greet.jpg?v=1712299334493'
    response = requests.get(image_url)
    if response.status_code == 200:  
      image_bytes = BytesIO(response.content)
      headers = {
        'Content-Type': 'image/jpeg',  
        'Content-Disposition': 'attachment; filename="Thanks.jpg"'
      }
      return app.response_class(image_bytes, headers=headers)
    else:
      return """
        <script>
        setTimeout(function() {
            window.location.href = "/";
        }, 3000);
        </script>
        <div>Signed up successfully</div>
        <div>Thanks For Signing Up</div>
        <div>Error downloading the image.</div>
        """
    return render_template("lol.html")


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
        date = datetime.now()
        entry = Contacts(name=name, email=email, message=message, date=date)
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
        flash('Thank you for your feedback!')
        print("Message submitted successfully!")
    return render_template('contact.html', params=params)


@app.route('/about')
def abt_sec():
    return render_template('about.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=3000, debug=True)
