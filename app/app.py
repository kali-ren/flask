from flask import Flask,flash,render_template, url_for, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_required, login_user,logout_user,UserMixin, current_user
import md5

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir,'teste.db')
app.config['SECRET_KEY'] = 'randomkey'
app.config['SQLALCHEMY_BINDS'] = {'users':'sqlite:///'+os.path.join(base_dir,'user.db')}

db = SQLAlchemy(app)
login_manager = LoginManager(app)

class Users(UserMixin,db.Model):
	__bind_key__ = 'users'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50))
	password = db.Column(db.String(50))

class Blogpost(UserMixin,db.Model):
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(50))
	subtitle = db.Column(db.String(50))
	author = db.Column(db.String(20))
	date_posted = db.Column(db.DateTime)
	content = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

class MyModelView(ModelView):
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('index'))



class MyAdminIndexView(AdminIndexView):
	@expose('/')                                                                   
	def index(self):
		if not current_user.is_authenticated:
			return redirect(url_for('.login'))
		return super(MyAdminIndexView, self).index()
		
	@expose('/login',methods=('GET','POST'))#change to only post 
	def login(self):
		error = None

		if request.method == 'POST':
			try:
				user = Users.query.filter_by(name=request.form['username']).first()
				if user.password == md5.new(request.form['password']).hexdigest():
					login_user(user)
					return redirect(url_for('.index'))#zig
				else:
					error = 'login invalido'
			except Exception, e:
				#error = e#'login invalid'
				error = 'login invalido'
		return render_template('admin/login.html',error=error)
	
	#def is_accessible(self):
	#	return current_user.is_authenticated

	#def inaccessible_callback(self, name, **kwargs):
	#	return redirect(url_for('.index'))

admin = Admin(app,index_view=MyAdminIndexView(url='/secretadminpainel')) 
admin.add_view(MyModelView(Blogpost,db.session))

@app.route('/')
def index():
	posts = Blogpost.query.order_by(Blogpost.date_posted.desc() ).all()
	
	return render_template("index.html",posts=posts)

@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/post/<post_title>')
def post(post_title):
	try:
		post = Blogpost.query.filter_by(subtitle=post_title).one()
	except:
		return "page_not_found"
	return render_template("post.html",post=post)

@app.route('/contact')
def contact():
	return render_template("contact.html")


#SSTI example with jinja template: begin
#@app.errorhandler(404)
#def page_not_found(e):
	#template = """
	
	#<div class="center-content error">
	#<h1>Oops! That page doesn't exist.</h1>
	#<h3>%s</h3>
	#</div>
	#""" % (request.url)
	#return render_template_string(template), 404
	#@app.route('')
#SSTI example with jinja template: end


@login_manager.unauthorized_handler
def unauthorized():
	return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():	
	logout_user()
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)
