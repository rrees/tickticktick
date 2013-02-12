import utils
import extract

def invalid_section(unwanted = ["Crosswords", ""]):
	return lambda x : x.get("sectionName", "") in unwanted

def valid_section(item):
	return not invalid_section()(item)

def minutes(min, max):
	return lambda x : min <= int(extract.wordcount(x)) / 250 <= max

def has_wordcount(item):
	return 'wordcount' in item.get('fields', {}).keys()