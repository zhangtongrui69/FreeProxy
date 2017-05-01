import queue
from selenium import webdriver
import urllib
import time
import random
from bs4 import BeautifulSoup

import bs4
import codecs

target_url="http://www.google.com/"   # 验证代理的时候通过代理访问这个地址
target_string=b'Google Search'               # 如果返回的html中包含这个字符串，
target_timeout=30                    # 并且响应时间小于 target_timeout 秒
									 #那么我们就认为这个代理是有效的

check_in_one_call=1  # 本次程序运行时 最多检查的代理个数

update_array=[]         # 这个数组保存将要更新的代理的数据


def check_one_proxy(ip,port):
	global update_array
	global check_in_one_call
	global target_url,target_string,target_timeout

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
		s= f.read()
		pos=s.find(checkstr)
	except Exception as ee:
		print(ee)
		pos=-1
		pass
	t2=time.time()
	timeused=t2-t1
	if (timeused<timeout and pos>0):
		active=1
	else:
		active=0
	update_array.append([ip,port,active,timeused])
	print(len(update_array),' status: ',active," ",ip,':',port,'--',int(timeused))



if __name__ == '__main__':
	driver = webdriver.Chrome()
	driver.get('http://www.proxynova.com/proxy-server-list/')

	fobj = open('proxylist.txt', 'w')
	trs = driver.find_elements_by_tag_name('tr')
	for tr in trs:
		tds = tr.find_elements_by_tag_name('td')
		ip = ''
		port = 0
		for idx, td in enumerate(tds):
			if idx==0:
				if(len(td.text)>0):
					fobj.write(td.text+':')
					ip = td.text
				else:
					break
			elif idx==1:
				fobj.write(td.text+'\n')
				port = int(td.text)
				check_one_proxy(ip, port)
			else:
				break
	fobj.close()
	driver.quit()
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
