import cookielib,urllib,urllib2,getpass
from bs4 import BeautifulSoup
import bs4
import json
import re
import time
import sys
import socket

socket.setdefaulttimeout(900)
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
file_trip="thread.csv"


class Forum:
	def __init__(self,pid):
		self.pid=str(pid)
		self.loaded=True
		self.page=soup_load('http://bbs.youxiake.com/forum-'+self.pid+'-1.html')
		total_page=self.page.select('input[name="custompage"]')[0].parent.contents[1].contents[0]
		self.total_page=int("".join([total_page[x] for x in range(0,len(total_page)) if total_page[x].isdigit()]))
		self.contents=[]
	
	def load_one_row(self,soup):
		thread_id=soup['id'].split('normalthread_')[1]
		try:
			place=soup.select('th[class="common"]')[0].select('em')[0].contents[1].contents[0]
		except:
			place=''
		title=soup.select('a[class*="xst"]')[0].contents[0]
		try:
			uid=soup.select('td[class="by"]')[0].contents[1].contents[1]['href'].split('space-uid-')[1].split('.html')[0]
		except:
			uid='0'
		try:
			time_=soup.select('td[class="by"]')[0].contents[3].contents[0].contents[0]['title']
		except:
			time_=soup.select('td[class="by"]')[0].contents[3].contents[0].contents[0]
		reply=soup.select('td[class="num"]')[0].contents[0].contents[0]
		read=soup.select('td[class="num"]')[0].contents[1].contents[0]
		self.contents.append([thread_id,place,title,uid,time_,reply,read])
		
	def load_one_page(self,page):
		soup=soup_load('http://bbs.youxiake.com/forum-'+self.pid+'-'+str(page)+'.html')
		tables=soup.select('tbody[id*="normalthread"]')
		for i in tables:
			try:
				self.load_one_row(i)
			except:
				print 'fail to load '+str(page)
			
	def load_all_pages(self):
		for i in range(480,self.total_page+1):
			print 'reading page '+str(i)
			self.contents=[]
			self.load_one_page(i)
			for i in self.contents:
				file_write(str(self.pid)+'_'+file_trip,"\t".join(i))


class Post:
	def __init__(self,pid,uid):
		self.pid=str(pid)
		self.loaded=True
		self.uid=str(uid)
		self.page=soup_load('http://bbs.youxiake.com/thread-'+self.pid+'-1-1.html')
		try:
			total_page=self.page.select('input[name="custompage"]')[0].parent.contents[1].contents[0]
			self.total_page=int("".join([total_page[x] for x in range(0,len(total_page)) if total_page[x].isdigit()]))
		except:
			self.total_page=1
		self.contents={}
	def load_one_page(self,page):
		soup=soup_load('http://bbs.youxiake.com/thread-'+self.pid+'-'+str(page)+'-1.html')
		users=soup.select('a[class="avtm"]')
		users=[x['href'].split('uid-')[1].split('.html')[0] for x in users]
		for i in users:
			try:
				self.contents[i]+=1
			except:
				self.contents[i]=1
	def load_all_pages(self):
		for i in range(1,self.total_page+1):
			self.load_one_page(i)
		for j in self.contents.keys():
			file_write(file_trip,"\t".join([self.pid,self.uid,j,str(self.contents[j])]).encode('utf-8'))

file=open('36_forum.csv').read().split('\n')
posts=[]
for x in file:
	m=x.split('\t')
	try:
		posts.append([m[0],m[3]])
	except:
		pass

print 'finish loading post id'

for m in posts:
	print m
	a=Post(m[0],m[1])
	a.load_all_pages()