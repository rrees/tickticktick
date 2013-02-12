import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.api import memcache

import data_filters
import extract

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		template_values = {}

		data = memcache.get("today")

		if data:
			all_content = json.loads(data)
			valid_filter = lambda x: data_filters.has_wordcount(x) and data_filters.minutes(0, 5)(x) and data_filters.valid_section(x)
			five_minute_content = filter(valid_filter, all_content)

			template_values['content'] = sorted(five_minute_content, key = lambda x: extract.wordcount(x), reverse = True)

		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)