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

# What is the directory where the templates (aka HTML) is stored?
# that's template_dir. the RHS joins the /templates to the current working directory returned by path_dirname

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# tell the jinja environment where this template directory is when instantiating it
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler (webapp2.RequestHandler):
	def write (self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class TemplateHandler(Handler):
	def get(self):
		n = self.request.get("n")
		if n:
			n = int(n)
		self.render("shopping_list.html", n=n)
