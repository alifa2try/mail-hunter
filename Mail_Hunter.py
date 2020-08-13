#!/usr/bin/env python3

# This program crawls websites


# import modules
import requests
import re
import urllib.parse
import argparse
from colorama import Fore, init

init()

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Yellow = Fore.YELLOW
Reset = Fore.RESET
Red = Fore.RED
Green = Fore.GREEN

def display_banner():
	banner_text = '''

8""8""8 8""""8 8  8          8   8 8   8 8"""8 ""8"" 8"""" 8"""8     
8  8  8 8    8 8  8          8   8 8   8 8   8   8   8     8   8     
8e 8  8 8eeee8 8e 8e         8eee8 8e  8 8e  8   8e  8eeee 8eee8e    
88 8  8 88   8 88 88    eeee 88  8 88  8 88  8   88  88    88   8    
88 8  8 88   8 88 88         88  8 88  8 88  8   88  88    88   8    
88 8  8 88   8 88 88eee      88  8 88ee8 88  8   88  88eee 88   8                                                                        
		v1.0
Gathers e-mails from all the pages of a target website
By Faisal Gama

Contact: info@faisalgama.com
Github: github.com/alifa2try/mail-hunter
Website: faisalgama.com 

	'''
	print(f"{Yellow}{banner_text}{Reset}")

def get_argument():
	parser = argparse.ArgumentParser(description=display_banner())
	parser.add_argument("domain", help="Domain to search email from")
	option = parser.parse_args()

	if not option.domain:
		parser.error("[-] You need to specify a domain to search emails from")

	return option.domain	


def extract_links_from_url(url):
	try:
		response = requests.get(url, verify=False)
		return re.findall('(?:href=")(.*?)"', (response.content).decode())
	except UnicodeDecodeError:
		pass	


def extract_mail(url):
	try:	
		response = requests.get(url, verify=False)
		return re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', (response.content).decode())
	except UnicodeDecodeError: #r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com"
		pass

def crawl(url):
	try:
			href_links = extract_links_from_url(url)

			for link in href_links:
				
				link = urllib.parse.urljoin(url, link)

				
				if target_url in link and link not in target_links:
					target_links.append(link)
					
					mails = extract_mail(link)
					
					for mail in mails:

						if mail not in mail_list:
							mail_list.append(mail)
							print(f"{Green}[+] Found an e-mail: {mail}{Reset}")	
					
					crawl(link)	
	except TypeError:
		pass 				

try:
	target_links = []
	mail_list = []

	domain = get_argument()
	target_url = "https://" + domain
	crawl(target_url)
except KeyboardInterrupt:
	print(f"\n{Red}[+] Detected CTRL + C .... Now halting the program{Reset}")				