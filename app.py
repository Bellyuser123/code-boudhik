from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join('.data', 'contacts.db')
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@app.route('/')
def home():
    return render_template('home.html')
  
@app.route('/contact', methods=['GET', 'POST'])
def cont_sec():
  if request.method == 'POST':
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    entry = Contacts(name=name, email=email, message=message)
    db.session.add(entry)
    db.session.commit()
    print("Message submitted successfully!")
    return render_template('contact.html')
  
@app.route('/blog')
def blog_sec():
    return render_template('blog.html')

  
if __name__ == '__main__':
    with app.app_context():
      db.create_all()
    app.run(host='0.0.0.0', port=3000, debug=True)
