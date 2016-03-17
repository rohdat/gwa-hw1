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
import urllib2
from xml.dom import minidom
import logging
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import memcache

MAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"
MY_COORDS = "44,-68"

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

class Art(ndb.Model):
	title = ndb.StringProperty(required=True)
	art = ndb.TextProperty(required=True)
	location = ndb.GeoPtProperty()
	created = ndb.DateTimeProperty(auto_now_add=True)

IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip=MAPS_URL):
	url = IP_URL + ip
	content = None
	return ndb.GeoPt(MY_COORDS)
	try:
		content = urllib2.urlopen(url).read()
	except URLError:
		return

def get_arts(update = False):
	key = 'top'
	arts = memcache.get(key)
	if arts is None or update:
		arts = Art.query().order(-Art.created)
		logging.error("NDB QUERY")
		arts = list(arts)
		memcache.set(key, arts)
	return arts	

def gmaps_img(points):
	markers = '&'.join('markers=%s,%s'%(p.lat,p.lon) for p in points)
	return MAPS_URL + markers


class AsciiChanHandler(Handler):

	def render_front(self, title="", art="", error=""):
		arts = get_arts()
		points = []
		img_url = ""
		for a in arts:
			if a.location:
				points.append(a.location)

		points = filter(None, (a.location for a in arts))
		if points:
			img_url = gmaps_img(points)

		self.write(repr(img_url))
		self.render("asciichan.html", title=title, art=art, error=error, arts=arts, img_url=img_url)

	def get(self):
		self.render_front()
		#self.clear_db()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		if title and art:
			a = Art(title=title, art=art)
			coords = get_coords()
			if coords:
				a.location = coords
			a.put()
			time.sleep(1)
			get_arts(True)
			# have to wait for the db to be updatd 
			# else we don't see blog post updates after clicking Submit
			self.redirect("/asciichan")
		else:
			error = "we need title and art"
			self.render_front(error=error, title=title, art=art)

	def clear_db(self):
		arts = db.GqlQuery("SELECT * from Art")
		for art in arts:
			art.delete()