from selenium import webdriver
import urllib
import time
import threading
import queue
import random
# from bs4 import BeautifulSoup
import socket

# import bs4
# import codecs

# target_url="http://www.google.com/"  # visit this website while verify the proxy
# target_string='Google Search'		# the returned html text should contain this string
target_url = "http://www.baidu.com/"  # visit this website while verify the proxy
target_string = '030173'		# the returned html text should contain this string
target_timeout = 30                   # the response time should be less than target_timeout seconds
                                    # then we consider this is a valid proxy


q = queue.Queue()
qout = queue.Queue()


class ThreadSocksChecker(threading.Thread):
    def __init__(self, queue, timeout, idx):
        self.timeout = timeout
        self.q = queue
        self.index = idx
        threading.Thread.__init__(self)

    def isSocks4(self, host, port, soc):
        ipaddr = socket.inet_aton(host)
        packet4 = "\x04\x01" + pack(">H",port) + ipaddr + "\x00"
        soc.sendall(packet4)
        data = soc.recv(8)
        if(len(data)<2):
            # Null response
            return False
        if data[0] != "\x00":
            # Bad data
            return False
        if data[1] != "\x5A":
            # Server returned an error
            return False
        return True

    def isSocks5(self, host, port, soc):
        soc.sendall("\x05\x01\x00")
        data = soc.recv(2)
        if(len(data)<2):
            # Null response
            return False
        if data[0] != "\x05":
            # Not socks5
            return False
        if data[1] != "\x00":
            # Requires authentication
            return False
        return True

    def getSocksVersion(self, host, port):
        try:
            proxy = host+':'+str(port)
            if port < 0 or port > 65536:
                print("Invalid: " + proxy)
                return 0
        except:
            print("Invalid: " + proxy)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            s.connect((host, port))
            if(self.isSocks4(host, port, s)):
                s.close()
                return 5
            elif(self.isSocks5(host, port, s)):
                s.close()
                return 4
            else:
                print("Not a SOCKS: " + host +':'+ str(port))
                s.close()
                return 0
        except socket.timeout:
            print(self.index, ": Timeout")
            s.close()
            return 0
        except socket.error:
            print(self.index, "Connection refused: " + host + ':'+str(port))
            s.close()
            return 0
    def run(self):
        while True:
            try:
                proxy = self.q.get(False)
                version = self.getSocksVersion(proxy[0], proxy[1])
                if version == 5 or version == 4:
                    print("Working: " + proxy)
                    socksProxies.put(proxy)
            except queue.Empty:
                print(self.index,': quit')
                break


class thread_check_one_proxy(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.index = index
        proxydata = ()
        return

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
            url=url+'?rnd='+str(random.random())
        else:
            url=url+'&rnd='+str(random.random())

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
        return

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
        return


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
    return


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
                elif idx == 2:
                    if td.text == 'SOCKS5':
                        a = (ip, port)
                        q.put(a)
                else:
                    break
    driver.quit()
    return


def generateProxyListFromFree_proxy_lists():
    driver = webdriver.Chrome()
    driver.get('http://free-proxy-list.net/')
    next = driver.find_element_by_id('proxylisttable_next')

    while True:
        t = driver.find_element_by_id('proxylisttable')
        if not t:
            driver.quit()
            return
        tb = t.find_element_by_tag_name('tbody')
        trs = tb.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            ip = ''
            port = 0
            if len(tds)==8:
                for idx, td in enumerate(tds):
                    if idx == 0:
                        if td.text == 'IP地址':
                            break
                        ip = td.text
                    elif idx == 1:
                        port = int(td.text)
                    elif idx == 6:
                        if td.text == 'yes':
                            a = (ip, port)
                            q.put(a)
        next.click()
        next = driver.find_element_by_id('proxylisttable_next')
        next_class = next.get_attribute('class')
        if 'disabled' in next_class:
            break
    driver.quit()
    return


def generateProxyListFromNordVpn():
    driver = webdriver.Chrome()
    driver.get('https://nordvpn.com/free-proxy-list/')
    time.sleep(1)
    dlg = driver.find_element_by_class_name('modal-dialog')
    if dlg:
        close = dlg.find_element_by_class_name('close')
        if close:
            close.click()
            time.sleep(1)
    for i in range(1):
        loadmores = driver.find_elements_by_class_name('btn-brand-yellow')
        for loadmore in loadmores:
            if loadmore.text == 'Load more':
                break
        loadmore.click()
        time.sleep(1)
    time.sleep(2)
    t = driver.find_element_by_class_name('proxy-list-table')
    tb = t.find_element_by_tag_name('tbody')
    trs = tb.find_elements_by_tag_name('tr')
    for itr, tr in enumerate(trs):
        tds = tr.find_elements_by_tag_name('td')
        ip = ''
        port = 0
        for itd, td in enumerate(tds):
            print(itr,itd)
            if itd==0:
                pass
            if itd==1:
                ip = td.text
            if itd==2:
                port = int(td.text)
            if itd==3:
                if td.text == 'SOCKS5':
                    a = (ip, port)
                    q.put(a)
    driver.quit()

if __name__ == '__main__':
    generateProxyListFromNordVpn()
    print('total ', q.qsize(), 'items in queue')
    threadNum = 1
    t = []
    for i in range(threadNum):
        t.append(ThreadSocksChecker(q, 10, i))
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
