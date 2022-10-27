my_file = open('/home/fang/.sqlmap/output/results-05192016_1144pm.csv')
import re
def get_title(ip):
    import requests
    """给定网址返回title值"""
    try:
        req = requests.get(f'{ip}', timeout=3)
        req.encoding = req.apparent_encoding
        pattern = re.compile('<title>(.*?)</title>')
        if i := re.findall(pattern, req.text):
            return i[0]
    except Exception as e:
        print(e)
for i in my_file.readlines():
    print(i.split(',')[0],)#'页面标题:',get_title(i.split(',')[0]),'注入参数:',i.split(',')[2])