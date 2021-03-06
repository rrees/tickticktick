import webapp2
import os
import json
import logging
from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.api import memcache

import data_filters
import extract
import headers

import math

def calculate_reading_time(content):
	wordcount = int(extract.wordcount(content))
	readingMinutes = wordcount / 250.0
	minutes = math.floor(readingMinutes)
	seconds = math.floor(60 * (readingMinutes % 1))

	content['readingTime'] = "%02d:%02d" % (minutes, seconds)

	return content

class RangedContent(webapp2.RequestHandler):
	def get(self, minimum, maximum):

		result = {}

		data = memcache.get("today")


		if data:
			all_content = json.loads(data)
			valid_filter = lambda x: data_filters.has_wordcount(x) and data_filters.minutes(int(minimum), int(maximum))(x) and data_filters.valid_section(x)
			appropriate_content = [calculate_reading_time(i) for i in all_content if valid_filter(i)]

			sorted_content = sorted(appropriate_content, key = lambda x: int(extract.wordcount(x)), reverse = True)

			result['content'] = sorted_content

		headers.json(self.response)
		self.response.out.write(json.dumps(result))

class MinimumContent(webapp2.RequestHandler):
	def get(self, minimum):

		result = {}

		data = memcache.get("today")


		if data:
			all_content = json.loads(data)

			at_least = lambda x: int(extract.wordcount(x)) >= int(minimum) * 250
			valid_filter = lambda x: data_filters.has_wordcount(x) and at_least(x) and data_filters.valid_section(x)
			appropriate_content = [calculate_reading_time(i) for i in all_content if valid_filter(i)]

			sorted_content = sorted(appropriate_content, key = lambda x: int(extract.wordcount(x)), reverse = True)

			result['content'] = sorted_content

		headers.json(self.response)
		self.response.out.write(json.dumps(result))


app = webapp2.WSGIApplication([('/api/content/from/(\d+)/to/(\d+)', RangedContent),
	('/api/content/from/(\d+)', MinimumContent),],
                              debug=True)