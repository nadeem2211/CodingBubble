from flask import Flask, render_template, request, url_for, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import json
from datetime import datetime
from flask_mail import Mail


with open('E:\Bhai\\vs code\python\\flask\\templates\config.json','r') as c:
    params = json.load(c)['params']

app = Flask(__name__)

# configuration of mail 
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_username'],
    MAIL_PASSWORD = params['gmail_pass']
    )
mail = Mail(app) # instantiate the mail class

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/CodingBubble'
app.config['SECRET_KEY'] = 'super secret'
db = SQLAlchemy(app)


class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    phone_num = db.Column(db.String(12), unique=True, nullable=False)
    msg = db.Column(db.Text, unique=False, nullable=False)
    created_on = db.Column(db.DateTime)

    # def __init__(self,id,name,):

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, unique=True, nullable=False)
    img_url = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime)

@app.route('/')
def home():
    post = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', post= post,params = params)

@app.route('/dashboard',methods= ['GET','POST'])
def dasboard():
    if 'user' in session and session['user'] == params['ADMIN_USER']:
        post2 = Posts.query.filter_by().all()
        return render_template('dashboard.html', post=post2,params = params)
    else:
        #return redirect(url_for('login'))
        return redirect('/login')

@app.route('/login',methods= ['GET','POST'])
def login():
    if 'user' in session and session['user'] == params['ADMIN_USER']:
        return render_template('dashboard.html', params = params)
    
    if request.method == 'POST':
        uname = request.form['username']
        upass = request.form['userpass']
        if uname==params['ADMIN_USER'] and upass==params['ADMIN_PASS']:
            session['user']=uname
            return render_template('dashboard.html', params = params)
        else:
            flash('wrong user name password')
    
    return render_template('login.html', params = params)


@app.route('/about')
def about():
    return render_template('about.html',params = params)

@app.route('/contact', methods = ['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone =request.form['phone']
        message = request.form['message']
        if not name or not email or not phone or not message:
            flash('please enter details and then submit')
        else:
            entry= Contacts(name=name,email=email,phone_num=phone,msg=message, created_on = datetime.now())
            db.session.add(entry)
            db.session.commit()
            mail.send_message('New Message from '+name, sender =email,recipients =[params['admin_mail']],body=message+"\n"+phone)

    return render_template('contact.html',params = params)

@app.route('/post/<string:post_slug>')
def post_route(post_slug):
    post1 = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',post=post1,params = params)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    if 'user' in session and session['user']==params['ADMIN_USER']:
        if request.method=='POST':
            
            updated_slug = request.form['slug']
            updated_title = request.form['title']
            updated_content = request.form['content']
            updated_imgurl = request.form['imgurl']
            if not updated_slug or not updated_title or not updated_content or not updated_imgurl:
                return redirect('/newpost')
            else:
                postnew = Posts(slug=updated_slug,title=updated_title,content=updated_content,img_url=updated_imgurl,date=datetime.now())
                db.session.add(postnew)
                db.session.commit()
                newrow = Posts.query.filter_by().all()
                #newrow = db.session.query(Posts).filter(Posts.id == max_postid).all()
                #return redirect('/edit/'+str(max_postid) )
                return render_template('dashboard.html',post= newrow,params = params)
        else:
            return render_template('newpost.html',params = params)
    else:
        return redirect('/login')


@app.route('/edit/<string:post_id>', methods=['GET','POST'])
def edit(post_id):
    if 'user' in session and session['user']==params['ADMIN_USER']:
        if request.method=='POST':
            
            updated_slug = request.form['slug']
            updated_title = request.form['title']
            updated_content = request.form['content']
            updated_imgurl = request.form['imgurl']

            if not updated_slug or not updated_title or not updated_content or not updated_imgurl:
                return redirect('/edit/'+post_id)
            else:                
                postedit = Posts.query.filter_by(id=post_id).first()
                postedit.title = updated_title
                postedit.slug = updated_slug
                postedit.img_url = updated_imgurl
                postedit.content=updated_content
                db.session.commit()
                #edited_post = Posts.query.filter_by(id=post_id).first()
                #return render_template('dashboard.html',post =edited_post, params = params)
                return redirect('/dashboard')
        else:
            query_post = Posts.query.filter_by(id=post_id).first()
            return render_template('edit.html',post=query_post,params = params)
    else:
        return render_template('login.html',params = params)

if __name__ == "__main__":
    app.run(debug=True)
