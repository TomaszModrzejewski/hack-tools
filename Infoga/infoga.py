#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Infoga: Email Information Gathering
#
# @url: https://github.com/m4ll0k/Infoga
# @author: Momo Outaadi (M4ll0k)
#
# Infoga is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License.
#
# Infoga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Infoga; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import json 
import os 
import sys 
import getopt 
import socket
import re 
import requests
import urlparse
from core.lib import http
from core.lib import parser 
from core.lib import colors 
from core.lib import printer
from core.recon import google
from core.recon import bing
from core.recon import pgp
from core.recon import yahoo
from core.recon import netcraft

class Infoga(object):
	color = colors.colors()
	printf = printer.printer()
	allemail = []
	def banner(self):
		print self.color.red(1)+"   __        ___                         "+self.color.reset()
		print self.color.red(1)+"  |__.-----.'  _.-----.-----.---.-.      "+self.color.reset()
		print self.color.red(1)+"  |  |     |   _|  _  |  _  |  _  |      "+self.color.reset()
		print self.color.red(1)+"  |__|__|__|__| |_____|___  |___._|      "+self.color.reset()
		print self.color.red(1)+"                      |_____|            "+self.color.reset()
		print self.color.white(0)+"                                       "+self.color.reset()
		print self.color.white(0)+"|| Infoga - Email Information Gathering"+self.color.reset()
		print self.color.white(0)+"|| Infoga v4.1 - \"Mr.Robot\"          "+self.color.reset()
		print self.color.white(0)+"|| Momo Outaadi (M4ll0k)               "+self.color.reset()
		print self.color.white(0)+"|| https://github.com/m4ll0k/infoga    "+self.color.reset()
		print self.color.white(0)+"                                       "+self.color.reset()

	def usage(self):
		name = os.path.basename(sys.argv[0]).split(".")[0]
		self.banner()
		print "Usage: %s -t [target] -s [source]\n"%(name)
		print "\t-t --target\tDomain to search"
		print "\t-s --source\tData source: [all,google,bing,yahoo,pgp]"
		print "\t-i --info\tGet email informatios"
		print "\t-h --help\tShow this help and exit\n"
		print "Examples:"
		print "\t %s --target site.com --source all"%(name)
		print "\t %s --target site.com --source [google,bing,...]"%(name)
		print "\t %s --info test123@site.com"%(name)
		print ""
		sys.exit()

	def info(self):
		if self.allemail == []:
			self.printf.error("Not found email :(")
			sys.exit(0)
		allemail = []
		for x in self.allemail:
			if x not in allemail:
				allemail.append(x)
		try:
			for item in allemail:
				self.printf.plus(f"Email: {item}")
				data = {'lang': 'en', 'email': item}
				req = requests.packages.urllib3.disable_warnings()
				req = requests.post("http://mailtester.com/testmail.php",data=data,verify=False)
				regex = re.compile("[0-9]+(?:\.[0-9]+){3}")
				ip = regex.findall(req.content)
				new = []
				for e in ip:
					if e not in new:
						new.append(e)
				for item_ in new:
					req = requests.packages.urllib3.disable_warnings()
					req = requests.get(
						f"https://api.shodan.io/shodan/host/{item_}?key=UNmOjxeFS2mPA3kmzm1sZwC0XjaTTksy",
						verify=False,
					)

					jso = json.loads(req.content,"utf-8")
					try:
						self.sock = socket.gethostbyaddr(item_)[0]
					except  socket.herror as err:
						try:
							self.sock = jso["hostnames"][0]
						except KeyError as err:
							pass
					if "country_name" in jso:
						self.printf.ip(f"IP: {item_} ({self.sock})")
						self.printf.info(f'Country: {jso["country_code"]} ({jso["country_name"]})')
						self.printf.info(f'City: {jso["city"]} ({jso["region_code"]})')
						self.printf.info(f'ASN: {jso["asn"]}')
						self.printf.info(f'ISP: {jso["isp"]}')
						self.printf.info(
							f'Geolocation: https://www.google.com/maps/@{jso["latitude"]},{jso["longitude"]},9z'
						)

						self.printf.info(f'Hostname: {jso["hostnames"][0]}')
						self.printf.info(f'Organization: {jso["org"]}')
						self.printf.info(f'Ports: {jso["ports"]}')
						if "vulns" in jso:
							self.printf.info(f'Vulns: {jso["vulns"][0]}')
					else:
						self.printf.ip(f"IP: {item_} ({self.sock})")
						self.printf.info("No information available for that ip :(",color="r")
					self.printf.ip("IP: %s (%s)"%(new[s],self.sock))
		except Exception as error:
			pass
		sys.exit()

	def checkurl(self,url):
		scheme = urlparse.urlsplit(url).scheme
		netloc = urlparse.urlsplit(url).netloc
		path = urlparse.urlsplit(url).path
		if netloc == "":
			return path.split("www.")[1] if path.startswith("www.") else path
		return netloc.split("www.")[1] if netloc.startswith("www.") else netloc

	def checkemail(self,email):
		if '@' not in email:
			self.banner()
			sys.exit(self.printf.error("Invalid email! Check your email"))
		return email

	def getinfo(self,email):
		self.printf.test("Checking email info...")
		try:
			data = {'lang': 'en', 'email': email}
			req = requests.packages.urllib3.disable_warnings()
			req = requests.post("http://mailtester.com/testmail.php",data=data,verify=False)
			regex = re.compile("[0-9]+(?:\.[0-9]+){3}")
			ip = regex.findall(req.content)
			new = []
			for e in ip:
				if e not in new:
					new.append(e)
			self.printf.plus(f"Email: {email}")
			for item in new:
				req = requests.packages.urllib3.disable_warnings()
				req = requests.get(
					f"https://api.shodan.io/shodan/host/{item}?key=UNmOjxeFS2mPA3kmzm1sZwC0XjaTTksy",
					verify=False,
				)

				jso = json.loads(req.content)
				try:
					self.sock = socket.gethostbyaddr(item)[0]
				except socket.herror as err:
					try:
						self.sock = jso["hostnames"][0]
					except KeyError as err:
						pass
				if "country_name" in jso:
					self.printf.ip(f"IP: {item} ({self.sock})")
					self.printf.info(f'Country: {jso["country_code"]} ({jso["country_name"]})')
					self.printf.info(f'City: {jso["city"]} ({jso["region_code"]})')
					self.printf.info(f'ASN: {jso["asn"]}')
					self.printf.info(f'ISP: {jso["isp"]}')
					self.printf.info(
						f'Geolocation: https://www.google.com/maps/@{jso["latitude"]},{jso["longitude"]},9z'
					)

					self.printf.info(f'Hostname: {jso["hostnames"][0]}')
					self.printf.info(f'Organization: {jso["org"]}')
					self.printf.info(f'Ports: {jso["ports"]}')
					if 'vulns' in jso:
						self.printf.info(f'Vulns: {jso["vulns"][0]}')
				else:
					self.printf.ip(f"IP: {item} ({self.sock})")
					self.printf.info("No information available for that ip :(",color="r")
				self.printf.ip("IP: %s (%s)"%(new[s],self.sock))
		except Exception as error:
			pass
		sys.exit()

	def main(self,kwargs):
		if len(sys.argv) <= 1:
			self.usage()
		try:
			opts,args = getopt.getopt(kwargs,"t:s:i:h:",["target=","source=","info=","help"])
		except Exception as error:
			self.usage()
		for opt,arg in opts:
			if opt in ("-t","--target"):
				self.target = self.checkurl(arg) 
			if opt in ("-s","--source"):
				source = arg
				if source not in ("all","google","bing","yahoo","pgp"):
					self.banner()
					sys.exit(self.printf.error("Invalid search engine! Try with: all, google, bing, yahoo or pgp"))
				self.banner()
				netcraft.netcraft(self.target).search()
				if source == "google":
					self.google()
					self.info()
				elif source == "bing":
					self.bing()
					self.info()
				elif source == "yahoo":
					self.yahoo()
					self.info()
				elif source == "pgp":
					self.pgp()
					self.info()
				elif source == "all":
					self.all()
					self.info()
			if opt in ("-i","--info"):
				email = self.checkemail(arg)
				self.banner()
				self.getinfo(email)
			if opt in ("-h","--help"):
				self.usage()

	def google(self):
		self.printf.test("Searching \"%s\" in Google..."%(self.target))
		search = google.google(self.target)
		search.process()
		emails = search.getemail()
		self.allemail.extend(emails)

	def bing(self):
		self.printf.test("Searching \"%s\" in Bing..."%(self.target))
		search = bing.bing(self.target)
		search.process()
		emails = search.getemail()
		self.allemail.extend(emails)

	def yahoo(self):
		self.printf.test("Searching \"%s\" in Yahoo..."%(self.target))
		search = yahoo.yahoo(self.target)
		search.process()
		emails = search.getemail()
		self.allemail.extend(emails)

	def pgp(self):
		self.printf.test("Searching \"%s\" in Pgp..."%(self.target))
		search = pgp.pgp(self.target)
		search.process()
		emails = search.getemail()
		self.allemail.extend(emails)

	def all(self):
		self.google()
		self.bing()
		self.yahoo()
		self.pgp()

if __name__ == "__main__":
	try:
		Infoga().main(sys.argv[1:])
	except KeyboardInterrupt:
		sys.exit("CTRL+C.... :(")
