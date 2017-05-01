import queue
import WebDown
from bs4 import BeautifulSoup
import bs4
import codecs


if __name__ == '__main__':
    q = queue.Queue()
    a = ('http://www.proxynova.com/proxy-server-list/', 'proxylist.html')
    q.put(a)
#    purl = WebDown.process_one_url(q, 0)
 #   purl.start()
  #  purl.join()

    fobj = codecs.open('proxylist.html', 'r')
    s1 = fobj.read()
    fobj.close()

    soup = BeautifulSoup(s1, 'lxml')
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
