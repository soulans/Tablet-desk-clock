# For Python 2 and 3

import bottle, json, sys, time, xml.etree.ElementTree
if sys.version_info.major == 2:
    python_version = 2
    import urllib2
else:
	python_version = 3
	import urllib.request


@bottle.route("/")
def index():
	bottle.redirect("clock.html", 301)


@bottle.route("/<path:path>")
def static_file(path):
	if path in AUTHORIZED_STATIC_FILES:
		mime = "auto"
		for ext in MIME_TYPES:
			if path.endswith("." + ext):
				mime = MIME_TYPES[ext]
				break
		return bottle.static_file(path, root=".", mimetype=mime)
	else:
		bottle.abort(404)

AUTHORIZED_STATIC_FILES = ["clock.css", "clock.html", "clock.js", "swiss-721-bt-bold.woff", "swiss-721-bt-light.woff", "swiss-721-bt-medium.woff", "swiss-721-bt-normal.woff", "swiss-721-bt-thin.woff"]
MIME_TYPES = {"html":"application/xhtml+xml", "woff":"application/x-font-woff"}


@bottle.route("/weather.json")
def weather():
	global weather_cache
	if weather_cache is None or time.time() > weather_cache[1]:
		# Data provided by Environment Canada. Documentation:
		# - http://dd.meteo.gc.ca/about_dd_apropos.txt
		# - http://dd.weather.gc.ca/citypage_weather/docs/README_citypage_weather.txt
		url = "http://dd.weatheroffice.ec.gc.ca/citypage_weather/xml/ON/s0000458_e.xml"  # Toronto, Ontario
		expiration = 20 * 60  # In seconds
		xmlstr = (urllib.request if python_version == 3 else urllib2).urlopen(url=url, timeout=60).read()
		root = xml.etree.ElementTree.fromstring(xmlstr)
		sunrise = "?"
		sunset = "?"
		for elem in root.findall("./riseSet/dateTime"):
			if elem.get("zone") != "UTC":
				s = elem.findtext("./hour") + ":" + elem.findtext("./minute")
				if elem.get("name") == "sunrise":
					sunrise = s
				elif elem.get("name") == "sunset":
					sunset = s
		result = {
			"condition"  : root.findtext("./currentConditions/condition"),
			"temperature": root.findtext("./currentConditions/temperature"),
			"sunrise": sunrise,
			"sunset" : sunset,
		}
		weather_cache = (json.dumps(result), time.time() + expiration)
	bottle.response.content_type = "application/json"
	return weather_cache[0]

weather_cache = None  # Either None or a tuple of (JSON string, expiration time)


if __name__ == "__main__":
	bottle.run(host="localhost", port=51367, reloader=True)