#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import re
import os
import jinja2 
import hashlib
import hmac
import string
import time
import random
from google.appengine.ext import db

# What is the directory where the templates (aka HTML) is stored?
# that's template_dir. the RHS joins the /templates to the current working directory returned by path_dirname

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# tell the jinja environment where this template directory is when instantiating it
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


welcome_form = """
<form method="get">
<br>

<b><head>Welcome %(username)s</head></b>
</form>

"""
password_form_dict = {"username":"",
					  "invalid_uname":"",
					  "invalid_pwd":"",
					  "pwd_no_match":"",
					  "email":"",
					  "invalid_email":"",
					  "user_exists":False}

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]{1,5}$")

def valid_in_regex(s, r):
	return r.match(s)

class Handler (webapp2.RequestHandler):
    def write (self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))



class UserProfile(db.Model):
	user = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email = db.StringProperty(required=False)

	def verify_password(self,pwd_in):
		if pwd_in == "":
			return False
		myhash, mysalt = self.password.split('|')
		return self.password == self.encrypt(pwd_in, salt=mysalt)

	@classmethod
	def encrypt(self, pwd_in, **salt):
		if not salt:
			salt['salt'] = self.make_salt()
		return self.hashme(pwd_in, salt.get('salt')) + "|" + salt.get('salt')

	@classmethod
	def make_salt(self):
		return ''.join(random.choice(string.ascii_letters) for x in xrange(5))

	@classmethod
	def hashme(self, string1, string2):
		return hashlib.sha256(string1+string2).hexdigest()
	
class PasswordHandler(Handler):

	form_dict = {}
	form_dict = password_form_dict

	def write_form(self, respond_dict=form_dict):
		self.render("signup.html" , **respond_dict)
	
	def get(self):
		self.form_dict = {}
		self.form_dict = password_form_dict

		self.write_form()
		#self.response.write("Hello welcome to signup")

	@classmethod
	def check_if_exists(self,username):
		for user in WelcomeHandler.getusers():
			if user.user == username:
				return True

	def post(self):
		self.form_dict = {}
		self.form_dict = password_form_dict
		username = self.request.get('username')
		username = username.encode('ascii')
		password1 = self.request.get('password')
		password1 = password1.encode('ascii')
		password2 = self.request.get('verify')
		password2 = password2.encode('ascii')
		email = self.request.get('email')
		email = email.encode('ascii')

		self.form_dict["user_exists"] = self.check_if_exists(username)
		error = self.check_if_exists(username)

		self.form_dict["username"] = cgi.escape(username,quote=True)
		self.form_dict["email"] = cgi.escape(email,quote=True)

		#get cookie
		user_cookie = self.request.cookies.get("username")
		if not user_cookie == username:
			self.response.headers.add_header('Set-Cookie', 'username=%s;Path=/'%username)

		if not (password1 == password2):
			self.form_dict["pwd_no_match"] = "Your passwords didn't match."
			error = True
		else:
			self.form_dict["pwd_no_match"] = ""

		if not valid_in_regex(username, USER_RE):
			self.form_dict["invalid_uname"] = "Invalid username."
			error = True
		else:
			self.form_dict["invalid_uname"] = ""

		if not valid_in_regex(password1, PASS_RE):
			self.form_dict["invalid_pwd"] = "That wasn't a valid password."
			error = True
		else:
			self.form_dict["invalid_pwd"] = ""

		if not valid_in_regex(email, EMAIL_RE) and not email == "":
			self.form_dict["invalid_email"] = "That's not a valid email."
			error = True
		else:
			self.form_dict["invalid_email"] = ""

		if error:
			#self.response.write(password_form_dict)
			self.write_form()
		else:
			user = UserProfile(user = username, password=UserProfile.encrypt(password1), email=email)
			user.put()
			is_pwd = user.verify_password(password1)
			time.sleep(1)
			self.redirect('/welcome')


class WelcomeHandler(Handler):
	def get(self):
		allusers = bool(self.request.get('render_all')) | True

		# Get the cookie from the request
		username = self.request.cookies.get('username')
		users = self.getusers()
		self.render("welcome_user.html", **{"username": username, "users" : users, "render_all" : allusers})

	@classmethod
	def getusers(self):
		return db.GqlQuery("SELECT * from UserProfile "
							"ORDER BY user DESC ")


class LoginHandler (Handler):

	def get(self):
		self.render("login.html")

	def post(self):
		user = db.GqlQuery("SELECT * from UserProfile "
						   "WHERE user = '%s'"%self.request.get('username'))
		user_validated = False
		for u in user:
			if u:
				username = u.user
				if u.verify_password(self.request.get('password')) :
					user_validated = True

		if user_validated:
			self.response.headers.add_header('Set-Cookie', 'username=%s;Path=/'%str(username))
			self.redirect('/welcome?user=%s&?is_pwd=%s&?render_all=False'%(username,user_validated))
		else:
			self.render("login.html", **{"username": username, "invalid_user": not user_validated})

class LogoutHandler(Handler):
	def get(self):
		#redirect to signup and delete cookie
		self.response.headers.add_header('Set-Cookie', 'username=;Path=/')
		self.redirect("/signup")
