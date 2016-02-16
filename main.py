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
from rot13 import *
from bday import *
from password import *
from templates import *
import jinja2 

choice_form="""
<form method="post">
	<input type="radio" name="choice" value="one"> Enter Birthday<br>
	<input type="radio" name="choice" value="two"> Encrypt Message<br>
	<input type="radio" name="choice" value="three"> User Signup Message<br>
	<input type="submit">
</form>

"""

class MainHandler(webapp2.RequestHandler):
    
    def write_form(self):
	    self.response.write(choice_form)

    def get(self):
        self.write_form()

    def post(self):
    	choice = self.request.get('choice')
    	if choice == 'two':
    		self.redirect("/rot13")
    	elif choice == 'one':
    		self.redirect("/bday")
    	elif choice == 'three':
    		self.redirect("/signup")
        elif choice == "four":
            self.redirect("/templates")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bday', BdayHandler),
    ('/thanks', ThanksHandler),
    ('/rot13', Rot13Handler),
    ('/signup', PasswordHandler),
    ('/templates', TemplateHandler),
    ('/welcome', WelcomeHandler)
], debug=True)

