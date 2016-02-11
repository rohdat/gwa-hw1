
rot13_form="""
<form method="post">
	<br>
	<textarea rows="4" cols="50" name="text" >%(encrypted)s</textarea>
	<br>
	<input type="submit">
	<br>
</form>
"""


class Rot13Handler(webapp2.RequestHandler):

    def write_form(self, encrypted=""):
        self.response.write(rot13_form % {"encrypted":cgi.escape(encrypted, quote=True)})

    def get(self):
        self.write_form()

    def post(self):
    	intext = self.request.get('text')
    	outtext = rot13(intext)
    	self.write_form(cgi.escape(outtext, quote=True))
