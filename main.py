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

choice_form="""
<form method="post">
	<input type="radio" name="choice" value="one">Enter bday<br>
	<input type="radio" name="choice" value="two">encrypt message<br>
	<input type="submit">
</form>

"""

rot13_form="""
<form method="post">
	<br>
	<textarea rows="4" cols="50" name="text" >%(encrypted)s</textarea>
	<br>
	<input type="submit">
	<br>
</form>
"""

bday_form="""
<form method="post">
	What is your birthday?
	<br>
	<label>Month
		<input type="text" name="month" value="%(month)s">
	</label>
	<label>Day
		<input type="text" name="day" value="%(day)s">
	</label>
	<label>Year
		<input type="text" name="year" value="%(year)s">
	</label>
	<br>
	<div style="color: red">%(error)s</div>
	<br>
	<div> Valid? Year: %(val_year)s Month: %(val_month)s Day: %(val_day)s</div>
	<br>
	<input type="submit">
</form>
"""

months = ["January",
		  "February",
		  "March",
		  "April",
		  "May",
		  "June",
		  "July",
		  "August",
		  "September"
		  "October",
		  "November",
		  "December"]

month_abbr = dict((m[:3].lower(), m) for m in months)



def valid_month(month):
	m = month[:3].lower()
	return month_abbr.get(m)


def valid_in_range(val, r0, r1):
	if val and r0 and r1 and val.isdigit() and r0.isdigit() and r1.isdigit():
		val = int(val)
		r0 = int(r0)
		r1 = int(r1)
		if val >= r0 and val <= r1:
			return val


def valid_day(day):
	return valid_in_range(day,'1','31')

def valid_year(year):
	return valid_in_range(year,'1900','2020')

def escape_html(s):
	for (i,o) in (("&", "&amp;"),
				   ("<", "&lt;"),
				   (">", "&gt;"),
				   ('"',"&quot;")):
		s = s.replace(i,o)
	return s
def rot13(s):
	rot_out = ""
	for ch in s:
		if ch.isalpha():
			rot_out = rot_out + wrap(ch)
		else:
			rot_out = rot_out + ch
	return rot_out

def wrap(char):
	if char and char.isalpha():
		if char.isupper(): 
			offset = 64
		else:
			offset = 96
		modulo = ((int(ord(char)) -offset) + 13) %26
		if modulo == 0:
			modulo = 26
		return chr (modulo + offset)

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


class Rot13Handler(webapp2.RequestHandler):

    def write_form(self, encrypted=""):
        self.response.write(rot13_form % {"encrypted":cgi.escape(encrypted, quote=True)})

    def get(self):
        self.write_form()

    def post(self):
    	intext = self.request.get('text')
    	outtext = rot13(intext)
    	self.write_form(cgi.escape(outtext, quote=True))

class BdayHandler(webapp2.RequestHandler):
    def writeForm(self, error="",
     					 month="",
     					 day="",
     					 year="",
     					 val_year="",
     					 val_day="",
     					 val_month=""):
	    self.response.write(bday_form %{"error":escape_html(error),
     							   "month":escape_html(month),
     							   "day":escape_html(day),
     							   "year":cgi.escape(year, quote=True),
     							   "val_day":val_day,
     							   "val_year":val_year,
     							   "val_month":val_month})

    def get(self):
        self.writeForm()

    def post(self):

	    user_year = self.request.get('year')
	    user_day = self.request.get('day')
	    user_month = self.request.get('month')

	    year = valid_year(user_year)
	    day = valid_day(user_day)
	    month = valid_month(user_month)

	    if not(year and month and day) :
	    	self.writeForm("Try again", user_month, user_day, user_year, year, day, month)
	    else:
	    	self.redirect("/thanks")

		    
class ThanksHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write("That is a good day!")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bday', BdayHandler),
    ('/thanks', ThanksHandler),
    ('/rot13', Rot13Handler)
], debug=True)

