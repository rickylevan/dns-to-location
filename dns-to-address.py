from geoip import geolite2
import socket
import requests
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


google_map_magic = 'http://maps.googleapis.com/maps/api/geocode/json?latlng='


def host_to_addr(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        match = geolite2.lookup(ip)
        if match is None:
            return "No match found for: " + ip
        lat = str(match.location[0])
        lng = str(match.location[1])
        rsp = requests.get(google_map_magic + lat + "," + lng)
        if rsp.status_code != 200:
            return "Weird, El Goog gave us a " + str(rsp.status_code)
        structured_data = json.loads(rsp.text)
        res = structured_data['results']
        if len(res) is 0:
            return "Hmm, we got a 200 but no data back"
        # winning
        return res[0]['formatted_address']

    except Exception as e:
        return str(e)


PORT_NUMBER = 80

class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        # possibly trim leading '/' in path
        path = self.path
        if path[0] is '/':
            path = path[1:]
        self.wfile.write(host_to_addr(path))
        return

try:
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shut it down!'
    server.socket.close()
