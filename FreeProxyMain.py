import queue
from selenium import webdriver
import urllib
import time
import threading
import queue
#import random
from bs4 import BeautifulSoup

#import bs4
#import codecs

#target_url="http://www.google.com/"  # visit this website while verify the proxy
#target_string='Google Search'		# the returned html text should contain this string
target_url = "http://www.baidu.com/"  # visit this website while verify the proxy
target_string = '030173'		# the returned html text should contain this string
target_timeout = 30                   # the response time should be less than target_timeout seconds
									# then we consider this is a valid proxy


q = queue.Queue()
qout = queue.Queue()

class thread_check_one_proxy(threading.Thread):
	def __init__(self, index):
		threading.Thread.__init__(self)
		self.index = index
		proxydata = ()
	def check_one_proxy(self, ip,port):
		global target_url,target_string,target_timeout

		print('thread '+str(self.index)+': processing '+str(ip)+':'+str(port))
		url=target_url
		checkstr=target_string
		timeout=target_timeout
		ip=ip.strip()
		proxy=ip+':'+str(port)
		proxies = {'http':'http://'+proxy+'/'}
		opener = urllib.request.FancyURLopener(proxies)
		opener.addheaders = [
			('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)')
			]
		t1=time.time()

		if (url.find("?")==-1):
			pass
	#		url=url+'?rnd='+str(random.random())
		else:
			pass
	#		url=url+'&rnd='+str(random.random())

		try:
			f = opener.open(url)
			s= str(f.read())
			pos=s.find(checkstr)
		except Exception as ee:
			print('thread ', self.index,':', ee)
			pos=-1
			pass
		t2=time.time()
		timeused=t2-t1
		if (timeused<timeout and pos>0):
			active=1
		else:
			active=0
		qout.put([active,ip,port,timeused])
		print('thread ',(self.index),' ',qout.qsize(),' active:: ',active," ",ip,':',port,'--',int(timeused))
	def run(self):
		while True:
			try:
				proxydata = q.get(False)
				self.check_one_proxy(proxydata[0], proxydata[1])
			except queue.Empty:
				print(self.index,': quit')
				break
			except Exception as ee:
				print(self.index,': Exception ',ee)
				break


def generateProxyListFromProxynova():
	driver = webdriver.Chrome()
	driver.get('http://www.proxynova.com/proxy-server-list/')

	fobj = open('proxylist.txt', 'w')
	trs = driver.find_elements_by_tag_name('tr')
	for tr in trs:
		tds = tr.find_elements_by_tag_name('td')
		ip = ''
		port = 0
		for idx, td in enumerate(tds):
			if idx == 0:
				if (len(td.text) > 0):
					fobj.write(td.text + ':')
					ip = td.text
				else:
					break
			elif idx == 1:
				fobj.write(td.text + '\n')
				port = int(td.text)
				a = (ip, port)
				q.put(a)
			else:
				break
	fobj.close()
	driver.quit()

def generateProxyListFromFreeproxylists():
	driver = webdriver.Chrome()
	driver.get('http://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0')
	t = driver.find_element_by_class_name('DataGrid')

	trs = t.find_elements_by_tag_name('tr')
	for tr in trs:
		tds = tr.find_elements_by_tag_name('td')
		ip = ''
		port = 0
		if len(tds)==10:
			for idx, td in enumerate(tds):
				if idx == 0:
					lk = td.find_element_by_tag_name('a')
					if lk.text == 'IP地址':
						break
					ip = lk.text
				elif idx == 1:
					port = int(td.text)
					a = (ip, port)
					q.put(a)
				else:
					break
	driver.quit()

if __name__ == '__main__':
	generateProxyListFromFreeproxylists()
	threadNum = 50
	t = []
	for i in range(threadNum):
		t.append(thread_check_one_proxy(i))
		t[i].start()
	for i in range(threadNum):
		t[i].join(30)
	fobj = open('proxylist.txt', 'w')
	while True:
		try:
			a = qout.get(False)
			print(a)
			if(a[0]==1):
				s = str(a) + '\n'
				fobj.write(s)
		except queue.Empty:
			break
	fobj.close()
	print('process closed')
	quit(0)
'''
	tables = soup('table')
	s1 = ''
	for t in tables:
		if t['id'] == 'tbl_proxy_list':
			for ch in t('tbody'):
				print('tr count:', len(ch('tr')))
				for idx, ch1 in enumerate(ch('tr')):  # ch1 is tr
					print('tr <',idx+1, '>')
					for idx, ch2 in enumerate(ch1('td')):  # ch2 is td
						if idx == 1:
							if type(ch2.string) == bs4.element.NavigableString:
								print(ch2.string.strip())
							else:
								a = ch2('a')
								if len(a)>0:
									print(a[0].string)
				break
	print(s1)
'''
