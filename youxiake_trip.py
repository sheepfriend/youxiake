import cookielib,urllib,urllib2,getpass
from bs4 import BeautifulSoup
import bs4
import json
import re
import time
import sys
import socket

socket.setdefaulttimeout(5)
cj=cookielib.CookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
header=[('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')]
opener.addheaders=header

#things to download
#user profile => place clustering?
#user friends => network
#user page comments (another html request)
#posts and comments (relationship btw the comments)
#trips (pid & bid & update_place!) => friends goes together?

#partial influence of traveling girls in weighted network (shorted path & MCMC)
#'pagerank' used to compute the spread speed of influence of traveling gilrs
#periodic pattern of users to go for a trip, place pattern


#basic functions
def soup_load(url):
	return BeautifulSoup(opener.open(url).read().replace("\n"," ").replace("\r"," ").replace("\t"," "))

def json_load(url,info):
	return json.loads(
		opener.open(url+"?"+urllib.urlencode(info))
			.read()
			.replace("\n"," ").replace("\r"," ").replace("\t"," "))

def file_write(name,content):
	f=open(name,'a')
	f.write(content.encode('utf-8'))
	f.write('\n')
	f.close()
	

#file info
file_trip="youxiake/trip.csv"


class Trip:
	def __init__(self,pid):
		self.pid=str(pid)
		self.loaded=True
		self.users=[]
		self.page=soup_load('http://www.youxiake.com/lines-allorders.html?pid='+self.pid)
		
	def load_bid(self):
		self.batches=[]
		li=self.page.select('ul[id="J-lot-nav"]')[0].contents
		li=[x for x in li if type(x)==bs4.element.Tag]
		for i in li:
			bid=i.contents[0]['href'].split('&bid=')[1]
			date=i.contents[0].contents[0].split('(')[0].strip()
			self.batches.append([bid,date])
	
	def load_one_batch(self,bid,date):
		page=soup_load('http://www.youxiake.com/lines-allorders.html?pid='+self.pid+'&bid='+bid)
		table=page.select('table[class="orderTable"]')[0].contents[3]
		users=table.contents
		users=[x for x in users if type(x)==bs4.element.Tag]
		for x in users:
			uid=x.contents[1].contents[0]['href'].split('uid=')[1]
			sex=x.contents[5].contents[0]
			place=x.contents[7].contents[0]
			man=x.contents[9].contents[0]
			woman=x.contents[11].contents[0]
			child=x.contents[13].contents[0]
			add_date=x.contents[17].contents[0]
			status=x.contents[19].contents[0]['class'][0]
			self.users.append([str(self.pid),str(bid),date,uid,sex,place,man,woman,child,add_date,status])
	def load_batches(self):
		for i in self.batches:
			print i
			try:
				self.load_one_batch(i[0],i[1])
			except:
				pass
	
	def write_all(self):
		for i in self.users:
			file_write(file_trip,"\t".join(i))

			
try:
	trip_group=int(sys.argv[1])
except:
	trip_group=1
	
for i in range((trip_group-1)*20000,trip_group*20000):
	print i
	try:
		a=Trip(i)
		a.load_bid()
		a.load_batches()
		a.write_all()
	except:
		pass