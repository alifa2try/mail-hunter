#!/usr/bin/env python3

# This program crawls websites


# import modules
import requests
import re
import urllib.parse
import argparse
from colorama import Fore, init
import xlsxwriter

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
	global target_links
	global mail_list

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
							global mails_counter
							mails_counter += 1
					crawl(link)	
	except TypeError:
		pass 

	export_results(mail_list)					


def export_results(emails):
	global xlsx_file_name
	global export_mails_list
	global domain

	csv_sheet_header = "Mails found on " + domain
	
	for mail in emails:
		if mail not in export_mails_list:
			export_mails_list.append(mail)


	# Start from the first cell. Rows and columns are zero indexed.
	row = 0
	col = 0
	i = 0
	try:
		if len(export_mails_list) != 0:
			workbook = xlsxwriter.Workbook(xlsx_file_name)
			worksheet = workbook.add_worksheet()
			worksheet.write(row, col, csv_sheet_header)
			row += 1
			# Iterate over the data and write it out row by row.
			for email in export_mails_list:
					col = 0
					worksheet.write(row, col, email)
					row += 1
					i += 1

			#Close the excel
			workbook.close()

	except Exception as e:
		print(f"{Red}[-]Error in export_results {e}{Reset}")


try:
	target_links = []
	mail_list = []
	export_mails_list = []
	mails_counter = 0

	domain = get_argument()
	xlsx_file_name = domain + ".xlsx"
	target_url = "https://" + domain
	crawl(target_url)
	print(f"{Green}\n[+] Finished hunting down e-mails and now exiting ...")
	print(f"[+] A total of {mails_counter} mails were hunted down.{Reset}")
except KeyboardInterrupt:
	print(f"\n{Red}[+] Detected CTRL + C .... Now halting the program{Reset}")
	print(f"[+] A total of {mails_counter} mails were hunted down.{Reset}")				
