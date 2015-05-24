#!/usr/bin/python

import SocketServer
import datetime
import os.path
import socket

CONF_DIR = "/etc/fake-whois/"
LOG_FILE = "/var/log/fake-whois.log"

def do_domain_lookup(query):
	if query.startswith("="):
		# Registry WHOIS -- need to check for "d " or "domain "
		query = strip_equals(query)
		if query.startswith("d "):
			resp = get_response_from_file("=" + query[2:])
		elif query.startswith("domain "):
			resp = get_response_from_file("=" + query[7:])
		else:
			resp = get_response_from_file("=" + query)
	elif query.startswith("d ") or query.startswith("domain ") or ' ' not in query:	
		resp = get_response_from_file(query)
	else:
		resp = "Invalid query"

	return resp

def do_network_lookup(query):
	resp = "Invalid query '" + query + "'"

	query = query.replace("n + ", "")
	for i in range(1, len(query)):
		path = CONF_DIR + "networks/" + query[:i]
		if os.path.isfile(path):
			try:
				resp = open(path, 'r').read()
			except:
				pass

	return resp

def get_response_from_file(filename):
	path = CONF_DIR + "domains/" + filename.lower()
	if os.path.isfile(path):
		try:
			text = open(path, 'r').read()
		except IOError:
			# Fall back to invalid query
			text = "Invalid query\n\n"
	elif filename.startswith("="):
		# Handle the case where we're doing a registry WHOIS. These are
		# easy to generate a "no match" message for (at least for .com/.net).
		name = strip_equals(filename).upper()
		path = CONF_DIR + "domains/nomatch.txt"
		try:
			text = open(path, 'r').read().replace("%domain%", name)
		except IOError:
			# Fall back to invalid query
			text = "Invalid query\n\n"
	else:
		# Each registrar has their own "no match" message.
		# It's easier to just return invalid query
		text = "Invalid query " + filename + "\n\n"

	return text

def process_query(query):
	if '..' in query:
		# Some sneaky bastard is trying a file path traversal
		# The legit whois client should return "No whois server is known for this kind of object."
		# But just in case they're trying whois over telent, dont tell them we are looking for it.
		# Just give a generic error.
		resp = "Invalid query\n\n"

	if query.startswith("as ") or query.startswith("a "):
		# AS query
		resp = "WHOIS AS query not supported\n"
	elif query.startswith("n + "):
		# network WHOIS
		resp = do_network_lookup(query)
	else:
		# try a domain lookup
		resp = do_domain_lookup(query)
	return resp

def strip_equals(request):
	if request.startswith("="):
		return request[1:]
	else:
		return request

def timestamp():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class WhoisRequestHandler(SocketServer.BaseRequestHandler):

	def handle(self):
		self.data = self.request.recv(1024).strip()
		self.data = self.data.lower()
		reply = process_query(self.data)
		self.request.send(reply)
		return

	def finish(self):
		# This logs the request so that we can evaluate if a request was made and from where.
		# The output looks like this:
		#     2012-01-04 07:04:23, 127.0.0.1, Requested wetestyou.com
		#     2012-01-04 07:04:53, 192.168.169.140, Requested yahoo.com
		#     2012-01-04 07:04:23, 192.168.169.142, Requested www.crazychinchilla.com
		
		# This line doesnt work on python 2.4...
		#with open("whoislog.log", "a") as myfile:

		myfile = open(LOG_FILE, "a")
		try:
			myfile.write(timestamp() + ", " + self.client_address[0] + ", Requested " + self.data + "\n")
		finally:
			myfile.close()

class IPv6Server(SocketServer.ThreadingTCPServer):

	address_family = socket.AF_INET6

#server = SocketServer.ThreadingTCPServer(("::", 43), WhoisRequestHandler)
server = IPv6Server(("::", 43), WhoisRequestHandler)
try:
	server.serve_forever()
except KeyboardInterrupt:
	# die gracefully on [ctrl+c]
	pass

