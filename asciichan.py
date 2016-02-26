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
import os
import webapp2
import cgi
import jinja2 
import time

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler (webapp2.RequestHandler):
    def write (self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Art(db.Model):
	title = db.StringProperty(required=True)
	art = db.TextProperty(required=True)

	created = db.DateTimeProperty(auto_now_add=True)



class AsciiChanHandler(Handler):

	def render_front(self, title="", art="", error=""):
		arts = db.GqlQuery("SELECT * FROM Art "
						   "ORDER BY created DESC ")

		self.render("asciichan.html", title=title, art=art, error=error, arts=arts)

	def get(self):
		self.render_front()
		#self.clear_db()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		if title and art:
			a = Art(title=title, art=art)
			a.put()
			# have to wait for the db to be updatd 
			# else we don't see blog post updates after clicking Submit
			time.sleep(1)
			self.redirect("/asciichan")
		else:
			error = "we need title and art"
			self.render_front(error=error, title=title, art=art)

	def clear_db(self):
		arts = db.GqlQuery("SELECT * from Art")
		for art in arts:
			art.delete()