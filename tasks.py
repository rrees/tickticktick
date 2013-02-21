import webapp2
import jinja2
import os
import json
import logging
import datetime
from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.api import memcache

import headers

def reading_seconds(words):
	return (words / 250) * 60


def read_todays_content(page = 1, results =  None):
	url = "http://content.guardianapis.com/search"

	payload = {"page" : str(page),
		"page-size" : "50",
		"format" : "json",
		"show-fields" : "wordcount,headline,standfirst,thumbnail",
		"tags" : "tone",
		"date-id" : "date/today",}

	final_url = url + "?" + urlencode(payload)
	logging.info(final_url)

	if not results:
		results = []

	result = urlfetch.fetch(final_url, deadline = 9)

	if not result.status_code == 200:
		logging.warning("Failed to read from the Content Api")
		return

	data = json.loads(result.content)

	api_response = data.get("response", {})

	total_pages = api_response.get("pages", None)

	if not total_pages:
		return

	results.extend(api_response.get("results", []))
	#logging.info(results)

	if int(total_pages) == page:
		return results
	
	return read_todays_content(page + 1, results)


class TodaysContent(webapp2.RequestHandler):
	def get(self):
		
		data = {"status" : "ok"}

		content = read_todays_content()

		if content:
			memcache.set("today", json.dumps(content))
			data['results'] = content

		headers.json(self.response)
		self.response.out.write(json.dumps(data))

app = webapp2.WSGIApplication([('/tasks/today', TodaysContent),
                              ], debug=True)