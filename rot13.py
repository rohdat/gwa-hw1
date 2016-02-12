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

rot13_form="""
<form method="post">
	<br>
	<textarea rows="4" cols="50" name="text" >%(encrypted)s</textarea>
	<br>
	<input type="submit">
	<br>
</form>
"""


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

class Rot13Handler(webapp2.RequestHandler):

    def write_form(self, encrypted=""):
        self.response.write(rot13_form % {"encrypted":cgi.escape(encrypted, quote=True)})

    def get(self):
        self.write_form()

    def post(self):
    	intext = self.request.get('text')
    	outtext = rot13(intext)
    	self.write_form(cgi.escape(outtext, quote=True))
