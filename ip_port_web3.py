#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import xlrd
from pyExcelerator import *
import Queue
import requests
import re
import os
import optparse
import threading
from base64 import b64encode

class ip_port_web:
    def __init__(self, target, threads_num, output):
        self.target = target.strip()#
        self.threads_num = threads_num
        dir=os.path.dirname(os.path.realpath(__file__))
        self.outfile = dir+'/'+os.path.basename(target.strip()) + '_web.xls' if not output else output
        self.w = Workbook()
        self.ws = self.w.add_sheet(u'ip_port_server_web')
        self.ws.write(0,0,u'服务器IP地址:')
        self.ws.write(0,1,u'服务器port号')
        self.ws.write(0,2,u'服务器port类型')
        self.ws.write(0, 3, u'服务器port banner')
        self.ws.write(0,4,u'web-status')
        self.ws.write(0,5,u'web_server信息')
        self.ws.write(0,6,u'web-title信息')
        self.ws.write(0,7,u'web-script信息')
        self.ws.write(0,8,u'web-headers信息')
        self.ws.write(0,9,u'web-content信息')
        self.ws.write(0,10,u'url信息')

    class WyWorker(threading.Thread):
        def __init__(self,queue,queue2):
            threading.Thread.__init__(self)
            self.queue = queue
            self.queue2=queue2

        def run(self):
            while True:
                if self.queue.empty():
                    break
                # 用hack方法，no_timeout读取Queue队列，直接异常退出线程避免阻塞
                n=0
                url=''
                try:
                    tmp_url_n = self.queue.get_nowait()
                    for i in tmp_url_n:
                        n=i
                        #print tmp_url_n
                        url=tmp_url_n[i]
                    #url='http://192.168.109.139/'
                    req=requests.get(url,allow_redirects=True,timeout=10)
                    status_code=req.status_code
                    #print status_code,n,url
                    result_dict={}
                    server='unknown'
                    content='unknown'
                    script="unkonwn"
                    title=''
                    for header in req.headers:
                        if header.upper() =='SERVER':
                            server=req.headers[header]
                        if header.upper()=='X-POWERED-BY':
                            script=req.headers[header]
                    re_title = re.search(r'<Title>(.*)</title>', req.text,flags=re.IGNORECASE)
                    #re_title = re.match(r"<title>(.*)</title>", req.content,re.IGNORECASE)
                    '''
                    if server.find('title') >=0 or server.find('head')>=0:
                        print url,server
                        break
                    '''
                    if re_title !=None:
                        title=re_title.group(0)
                        #print title
                    if len(req.content)< 200:
                        content=req.content
                    else:
                        content=req.content[:200]
                    #print status_code,n,url,title,content,server
                    result_dict['n']=n
                    result_dict['status_code']=status_code
                    result_dict['server']=server
                    result_dict['title']=title
                    result_dict['script']=script
                    result_dict['content']=content
                    result_dict['url']=url
                    #result_dict['headers']=req.headers
                    self.queue2.put(result_dict)
                except Exception, e:
                    # print e # 队列阻塞
                    try:
                        url=url.replace('http','https')
                        req=requests.get(url,allow_redirects=True,timeout=10,verify=False)
                        status_code=req.status_code
                        #print status_code,n,url
                        result_dict={}
                        server='unknown'
                        content='unknown'
                        script="unkonwn"
                        title=''
                        for header in req.headers:
                            if header.upper() =='SERVER':
                                server=req.headers[header]
                            if header.upper()=='X-POWERED-BY':
                                script=req.headers[header]
                        #print 'title'
                        re_title = re.search(r'<Title>(.*)</title>', req.text,flags=re.IGNORECASE)
                        #re_title = re.match(r"<title>(.*)</title>", req.content,re.IGNORECASE)
                        #print 'title'
                        if re_title !=None:
                            title=re_title.group(0)
                            #print title
                        if len(req.content)< 200:
                            content=req.content
                        else:
                            content=req.content[:200]
                        #print status_code,n,url,title,content,server
                        #print status_code,n,url,title,content,server
                        result_dict['n']=n
                        result_dict['status_code']=status_code
                        result_dict['server']=server
                        result_dict['title']=title
                        result_dict['script']=script
                        result_dict['content']=content
                        result_dict['url']=url
                        self.queue2.put(result_dict)
                        '''
                        self.ws.write(n,3,status_code)
                        self.ws.write(n,4,server)
                        self.ws.write(n,5,title)
                        self.ws.write(n,6,script)
                        self.ws.write(n,7,content)
                        '''
                        #print n,url
                    except Exception, e:
                        continue
                except Exception, e:
                        continue
    def check(self):
        web_list=[]
        # 生成任务队列
        queue = Queue.Queue()
        queue2 = Queue.Queue()
        f2=open(self.target)
        lines=f2.readlines()
        f2.close()

        ip_list=[]
        tmp_url_n={}
        n=1
        for line in lines:

            try:
                if line.find('Ports:')>=0:
                    re_ip=re.search(r'(\d*\.\d*\.\d*\.\d*)', line)
                    tmp_ip=re_ip.group(0)
                    if tmp_ip in ip_list:
                        continue
                    else:
                        ip_list.append(tmp_ip)
                    port_list=[]
                    #print tmp_ip,line
                    #print tmp_ip
                    tmp_ip_port=line.split(':')[2].split(',')
                    #print  tmp_ip_port
                    for tmp in tmp_ip_port:
                        #print tmp.split('/')[0],tmp.split('/')[4]
                        #port_list.append(tmp.split('/')[0].strip())
                        #print port_list
                        tmp_port=tmp.split('/')[0].strip()
                        tmp_port_type=tmp.split('/')[4].strip()
                        tmp_port_type_banner = tmp.split('/')[6].strip()
                        #print tmp_port_type
                        #tmp_shuaihu[tmp_ip]=port_list
                        url='http://'+tmp_ip.strip()+':'+tmp_port
                        #print url,tmp_ip_port
                        tmp_url_n={}
                        tmp_url_n[n]=url
                        self.ws.write(n,0,tmp_ip)
                        self.ws.write(n,1,tmp_port)
                        self.ws.write(n,2,tmp_port_type)
                        self.ws.write(n, 3, tmp_port_type_banner)
                        #if tmp_port == '443' or tmp_port=='80':
                        #    link = tmp_port_type+'://'+tmp_ip+':'+tmp_port
                        #    self.ws.write(n,9,link)
                        queue.put(tmp_url_n)
                        #print url
                        n=n+1
            except Exception as e:
                print 'error',e
                continue


        threads = [] # 初始化线程组
        for i in xrange(self.threads_num):
            threads.append(self.WyWorker(queue,queue2))
        for t in threads: # 启动线程
            t.start()
        for t in threads: # 等待线程执行结束后，回到主线程中
            t.join()

        print 'check ok！'
        while True:
            if queue2.empty():
                    break
            try:
                result_dict = queue2.get_nowait()
                n=0
                status_code='test'
                server='test'
                title='test'
                script='test'
                content='test'
                headers='test'
                for key in result_dict:
                    if key=='status_code':
                        status_code=result_dict[key]
                    elif key=='server':
                        server=result_dict[key]
                    elif key=='title':
                        title=result_dict[key]
                    elif key=='script':
                        script=result_dict[key]
                    elif key=='content':
                        content=result_dict[key]
                    elif key=='n':
                        n=result_dict[key]
                    elif key=='headers':
                        headers=result_dict[key]
                    elif key == 'url':
                        url=result_dict[key]
                '''
                if len(server)>=30:
                    print server,n,content
                    '''
                #print("Line: %s, code: %s, server: %s, title:%s, script:%s content:%s"%(n,status_code,server,title, script,content))
                #content=content.replace('!',' ').
                content=b64encode(content)
                self.ws.write(n,4,status_code)
                self.ws.write(n,5,server)
                self.ws.write(n,6,title)
                self.ws.write(n,7,script)
                self.ws.write(n,8,headers)
                self.ws.write(n,10,url)
                #self.ws.write(n,8,content.strip())  
            except Exception as e:
                print 'error',e
        self.w.save(self.outfile)
      



if __name__ == '__main__':
    parser = optparse.OptionParser('usage: %prog [options] nmap_oG.xls')
    parser.add_option('-t', '--threads', dest='threads_num',
              default=10, type='int',
              help='Number of threads. default = 30')
    parser.add_option('-o', '--output', dest='output', default=None,
              type='string', help='Output file name. default is {target}_web.xls')

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(0)

    d = ip_port_web(target=args[0],
                 threads_num=options.threads_num,
                 output=options.output)

    d.check()
'''
    d = ip_port_web(target='all_ip_port.txt',
             threads_num=10,
             output=options.output)
    '''
