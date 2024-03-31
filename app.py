from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
  
@app.route('/contact')
def cont_sec():
    return render_template('contact.html')
  
@app.route('/blog')
def blog_sec():
    return render_template('blog.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
