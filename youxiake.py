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
	try:
		f=open(name,'a')
	except:
		f=open(name,'w+')
	f.write(content.encode('utf-8'))
	f.write('\n')
	f.close()
	

#file info
file_user_profile='user_profile.csv'
file_user_friends='user_friends.csv'
file_user_comments='user_comments.csv'
file_user_quotation='user_quotation.csv'


class User:
	def __init__(self,uid):
		self.uid=str(uid)
		self.loaded=True
		
	def load_user_profile(self):
		user_profile=soup_load('http://www.youxiake.com/space-uid-'+self.uid+'-profile.html')
		
		#get profile panel
		statistics=user_profile.select("h3")[0].parent
		statistics=[x for x in statistics.contents if x !=" "]
		
		#read data from panel
		photo=statistics[1].contents[0].split(":")[1].strip()
		visit=statistics[2].contents[0].split(":")[1].strip()
		reg=statistics[3].contents[0].split(":")[1].strip()
		
		name=user_profile.select('h1[class="userInfoName"]')[0].contents[0]
		
		self.user_profile=[self.uid,name,photo,visit,reg]
		
	def load_user_friend(self):
		user_friend=soup_load('http://bbs.youxiake.com/home.php?mod=space&uid='+self.uid+'&do=friend&from=space&page=1')
		
		#get number of pages of friends
		page=user_friend.select('input')[0].parent.contents[1].contents[0]
		page_max=int("".join([str(page[x]) for x in range(0,len(page)) if page[x].isdigit()]))
		
		#get friends info
		friends=user_friend.select('h4')
		friends=[[self.uid,x.contents[1]['href'].split('uid-')[1].split('.html')[0]] for x in friends]
		
		self.friends=friends
		page=1
		
		while page<=page_max:
			page+=1
			user_friend=soup_load('http://bbs.youxiake.com/home.php?mod=space&uid='+self.uid+'&do=friend&from=space&page='+str(page))
			friends=user_friend.select('h4')
			friends=[[self.uid,x.contents[1]['href'].split('uid-')[1].split('.html')[0]] for x in friends]
			self.friends.append(friends)
	
	def load_user_comments(self):
		comments=json_load('http://www.youxiake.com/newzone-liuyan-getLiuyan_ajax.html',{
			'page':1,
			'uid':self.uid
		})
		page=1
		comment_num=0
		self.comments=[]
		while comments['result']==1:
			feeds=BeautifulSoup(comments['message'].replace("\n"," ").replace("\t"," ").replace("\r"," ")).contents[0].contents
			feeds=[x for x in feeds if x!=" " and type(x)==bs4.element.Tag]
			for feed_num in range(0,len(feeds)):
				comment_num+=1
				feed_uid=feeds[feed_num].contents[3].contents[1].contents[1]['src'].split('uid=')[1]
				feed_time=feeds[feed_num].contents[9].contents[13].contents[3].contents[2].strip()
				feed_comments=int(feeds[feed_num].contents[9].contents[13].contents[1].contents[1].contents[0].split('(')[1].split(')')[0])
				self.comments.append([str(self.uid),str(comment_num),str(feed_uid),feed_time,str(feed_comments)])
				if comment_num%100==0:
					print comment_num
			comments=json_load('http://www.youxiake.com/newzone-liuyan-getLiuyan_ajax.html',{
						'page':page+1,
						'uid':self.uid
					})
			page+=1
			
	def load_user_quotation(self):
		comments=json_load('http://www.youxiake.com/newzone-quotation-getQuoteByUid_ajax.html',{
			'page':1,
			'uid':self.uid
		})
		page=1
		comment_num=0
		self.quotation=[]
		while comments['result']==1:
			feeds=BeautifulSoup(comments['message'].replace("\n"," ").replace("\t"," ").replace("\r"," ")).contents
			feeds=[x for x in feeds if x!=" " and type(x)==bs4.element.Tag]
			try:
				for feed_num in range(0,len(feeds)):
					comment_num+=1
					feed_time=feeds[feed_num].contents[3].contents[7].contents[3].contents[2].strip()
					feed_comments=int(feeds[feed_num].contents[3].contents[7].contents[1].contents[1].contents[0].split('(')[1].split(')')[0])
					self.quotation.append([str(self.uid),str(comment_num),feed_time,str(feed_comments)])
					if comment_num%100==0:
						print comment_num
				comments=json_load('http://www.youxiake.com/newzone-liuyan-getLiuyan_ajax.html',{
							'page':page+1,
							'uid':self.uid
						})
			except:
				feeds=feeds[0].contents
				feeds=[x for x in feeds if x!=" " and type(x)==bs4.element.Tag]
				for feed_num in range(0,len(feeds)):
					comment_num+=1
					feed_time=feeds[feed_num].contents[9].contents[13].contents[3].contents[2].strip()
					feed_comments=int(feeds[feed_num].contents[9].contents[13].contents[1].contents[1].contents[0].split('(')[1].split(')')[0])
					self.quotation.append([str(self.uid),str(comment_num),feed_time,str(feed_comments)])
					if comment_num%100==0:
						print comment_num
				comments=json_load('http://www.youxiake.com/newzone-liuyan-getLiuyan_ajax.html',{
							'page':page+1,
							'uid':self.uid
						})
			page+=1		
	
	def load_all(self):
		try:
			print 'Loading user '+self.uid
			self.load_user_profile()
			try:
				print '\tLoading user friends'
				self.load_user_friend()
			except:
				'\tuser '+self.uid+' has no friend, or fail to load friends'
			try:
				print '\tLoading user comments'
				self.load_user_comments()
			except:
				print '\tFail to load user commnets'
			try:
				print '\tLoading user quotations'
				self.load_user_quotation()
			except:
				print '\tFail to load user quotations'
		except:
			self.loaded=False
			print '\tFail to load user '+self.uid
	
	def write_all(self):
		self.uid=str(self.uid)
		if self.loaded:
			print 'Writing info for user '+self.uid
			try:
				print '\tWriting user info...'
				file_write(file_user_profile,"\t".join(self.user_profile))
			except:
				print '\tFail to write user info'
			try:
				print '\tWriting user friends...'
				for i in self.friends:
					try:
						file_write(file_user_friends,"\t".join(i))
					except:
						for j in i:
							try:
								file_write(file_user_friends,"\t".join(j))
							except:
								pass
							
			except:
				print '\tFail to write friends info'
			try:
				print '\tWriting comments...'
				for i in self.comments:
					try:
						file_write(file_user_comments,"\t".join(i))
					except:
						pass
			except:
				print '\tFail to write comments'
			try:
				print '\tWriting quotations...'
				for i in self.quotation:
					try:
						file_write(file_user_quotation,"\t".join(i))
					except:
						pass
			except:
				print '\tFail to write quotations'
				
			
try:
	user_group=int(sys.argv[1])
except:
	user_group=1

#for i in range((user_group-1)*10000,user_group*10000):
for i in range((user_group-1)*10000,user_group*10000):
	a=User(i)
	a.load_all()
	a.write_all()