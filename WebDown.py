import threading
import codecs
import requests
import queue

class process_one_url(threading.Thread):
    def __init__(self, q, tid):
        threading.Thread.__init__(self)
        self.q = q
        self.tid = tid

    def run(self):
        while True:
            try:
                pair = self.q.get(False)
                if pair == None:
                    print(str(self.tid) + ': quit')
                    break
                if len(pair) != 2:
                    print(str(self.tid) + ': error in queue data, len()!=2')
                url = pair[0]
                fname = pair[1]
                print(str(self.tid) + ':' + url)
                while True:
                    try:
                        html = requests.get(url)
                        break
                    except requests.ConnectionError:
                        print(str(self.tid) + ': ConnectionError')
                    except requests.exceptions.ChunkedEncodingError:
                        print(str(self.tid) + ': ChunkedEncodingError')
                    except Exception as ex:
                        print('{0}: request.get() exception ({1}) occurred.'.format(self.tid, type(ex).__name__))
                fw = codecs.open(fname, 'w', 'utf-8')
                fw.write(html.text)
                fw.close()
            except queue.Empty:
                print(str(self.tid) + ': quit')
                break
            except Exception as ex:
                print('{0}: An exception ({1}) occurred.'.format(self.tid, type(ex).__name__))
