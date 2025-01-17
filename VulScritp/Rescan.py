#coding=utf-8
#author=Cond0r@CodeScan
import socket
import threading
from concurrent import futures
from  Queue import Queue 
from sys import argv
import ipaddr
import sys
socket.setdefaulttimeout(3)
data='''
Lib:
	https://github.com/google/ipaddr-py
	https://pypi.python.org/pypi/futures
	pip install futures
Usage:
	python rescan.py -f  inputfile.txt 
	inputfile.txt:
		10.14.40.194:6379
	python rescan.py -i  192.168.1.1/24 -p 6379
'''
target_list=[]
def stdout( name):
	scanow = f'[*] Scan {name}.. '
	sys.stdout.write(str(scanow)+" "*20+"\b\b\r")
	sys.stdout.flush()
def extract_target(inputfile):
	global target_list
	inputdata=open(inputfile).read().replace("\r",'').split("\n")
	for host in inputdata:
		host=host.split(":")
		if len(host)==2:
			target_list.append(f"{host[0]}:{host[1]}")
		elif len(host)==1:
			target_list.append(f"{host[0]}:6379")
	return target_list	
def send_dbsize(conn):
	try:
		conn.send("dbsize\n")
		recv=conn.recv(5) 
		conn.close()	
		recv=recv.replace("\n",''),
		return recv
	except:
		return False
	
def conn_redis(args):
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	args=args.split(":")
	host=args[0]
	port=int(args[1])
	try:
		client.connect((host, port))
		return client
	except:
		return False
def run_task(target):
	stdout(target)
	if conn := conn_redis(target):
		size=send_dbsize(conn)
		size=str(size)
		if 'NOAUTH' not in size and ':' in size:
			return f"[!] Find {target} Unauthorized  "		
def main():
	if len(argv) <= 2:
		return
	if argv[1]=='-f':
		return extract_target(argv[2])
	if argv[1]=='-i':
		port = int(argv[4]) if len(argv)==5 else 6379
		targets = ipaddr.IPv4Network(argv[2])
		return ["%s:%d"%(tar,port) for tar in targets]
				
			
		
if len(argv)<3:
	print data
	exit()

target_list=main()

thread_pool = futures.ThreadPoolExecutor(max_workers=10)
for i in  thread_pool.map(run_task, target_list):
	if i!=None:
		print i
