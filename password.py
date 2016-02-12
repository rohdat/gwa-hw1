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

	#<p style="color:red" value="%(invalid_pwd)s)></p>

password_form = """
<form method="post">

	<head>Signup</head>

	<br>
	<br>
	<div class="container">
	<label>Username
		<input type="text" name="username" value="%(username)s">%(invalid_uname)s
	</label>
	<p style="color:red")></p>
	<br>
	
	<label>Password
		<input type="password" name="password">
	</label>
	<p style="color:red">%(invalid_pwd)s</p>
	<br>

	<label>Verify Password
		<input type="password" name="verify">
	</label>
	<p style="color:red">%(pwd_no_match)s</p>
	<br>

	<label>Email(optional)
		<input type="text" name="email" value="%(email)s">
	</label>
	<p style="color:red">%(invalid_email)s</p>
	<br>
	<div>
	
	<input type="submit">


</form>

"""

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
					  "invalid_email":""}

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]{2,3}$")

def valid_in_regex(s, r):
	return r.match(s)

class PasswordHandler(webapp2.RequestHandler):

	form_dict = {}
	form_dict = password_form_dict

	def write_form(self, respond_dict=form_dict):
		self.response.write(password_form % respond_dict)
	
	def get(self):
		self.form_dict = {}
		self.form_dict = password_form_dict
		self.write_form()
		#self.response.write("Hello welcome to signup")

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

		self.form_dict["username"] = cgi.escape(username,quote=True)
		self.form_dict["email"] = cgi.escape(email,quote=True)

		error = 0

		if not (password1 == password2):
			self.form_dict["pwd_no_match"] = "Your passwords didn't match."
			error = 1
		else:
			self.form_dict["pwd_no_match"] = ""


		if not valid_in_regex(username, USER_RE):
			self.form_dict["invalid_uname"] = "Invalid username."
			error = 1
		else:
			self.form_dict["invalid_uname"] = ""

		if not valid_in_regex(password1, PASS_RE):
			self.form_dict["invalid_pwd"] = "That wasn't a valid password."
			error = 1
		else:
			self.form_dict["invalid_pwd"] = ""

		if not valid_in_regex(email, EMAIL_RE):
			self.form_dict["invalid_email"] = "That's not a valid email."
			error = 1
		else:
			self.form_dict["invalid_email"] = ""

		if error == 1:
			#self.response.write(password_form_dict)
			self.write_form()
		else:
			global welcome_form
			welcome_form = welcome_form % {'username' :cgi.escape(username , quote=True)}
			self.redirect('/welcome')


class WelcomeHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write(welcome_form)
