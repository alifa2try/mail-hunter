#!/usr/bin/env python3

# This program crawls websites

try:
	# import modules
	import requests
	import re
	import urllib.parse
	import argparse
	from colorama import Fore, init, Style
	import xlsxwriter
	import MailboxValidator
except KeyboardInterrupt:
    print('[!] Detected CTRL + C ...Now exiting!')
    raise SystemExit
except:
    print('[!] Missing requirements. Try running python3 -m pip install -r requirements.txt')
    raise SystemExit

init()

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Yellow = Fore.LIGHTYELLOW_EX
Reset = Fore.RESET
Red = Fore.RED
Green = Fore.LIGHTGREEN_EX
Blue = Fore.BLUE
White = Fore.LIGHTWHITE_EX
Style = Style.BRIGHT

def display_banner():
	
	banner_text = '''

8""8""8 8""""8 8  8          8   8 8   8 8"""8 ""8"" 8"""" 8"""8     
8  8  8 8    8 8  8          8   8 8   8 8   8   8   8     8   8     
8e 8  8 8eeee8 8e 8e         8eee8 8e  8 8e  8   8e  8eeee 8eee8e    
88 8  8 88   8 88 88    eeee 88  8 88  8 88  8   88  88    88   8    
88 8  8 88   8 88 88         88  8 88  8 88  8   88  88    88   8    
88 8  8 88   8 88 88eee      88  8 88ee8 88  8   88  88eee 88   8                                                                        
		v2.0.0
Collects E-mails and Performs OSINT on the E-mails
By Faisal Gama

Contact: info@faisalgama.com
Github: github.com/alifa2try/mail-hunter
Website: faisalgama.com 

	'''
	print(f"{Yellow}{Style}{banner_text}{White}")


def get_argument():
	parser = argparse.ArgumentParser(description=display_banner())
	parser.add_argument("-d", "--domain", dest='domain', help="Domain to search phone numbers from")
	parser.add_argument("-sm", "--single-mail", dest='mail', help="Single number to perform OSINT")
	parser.add_argument("-iL", "--input-list", dest='list', help="Input numbers from a list")
	parser.add_argument("-vs", "--verification-service", dest= "verification_service", 
						help="Verification service to use: " 
		                "mailbox(https://www.mailboxvalidator.com/)|"
		                "no-verification")
	option = parser.parse_args()

	if not option.domain:
		if not option.mail:
			if not option.list:
				parser.error(f"{Red}[-] You need to specify a domain, input an email or input emails from a list{Reset}")
				raise SystemExit
	
	if not option.verification_service:
		parser.error(f"{Red}[-] You need to specify a verification service")
		raise SystemExit	
	return option	


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
	except UnicodeDecodeError: #r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com" r'[\w\.-]+@[\w\.-]+\.\w+'
		pass


def crawl_and_verify_with_mailbox(url):
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

						check_if_temp = check_if_mail_is_temp(mail)
						verify_is_mail = single_mail_validator(mail)
						check_if_free = check_if_mail_is_free(mail) 

						if check_if_temp != None:
							if check_if_temp == 'True':
								pass

						elif verify_is_mail != None:

							if check_if_free == 'True':
								print(f"[+]{Green} This is a free e-mail{Reset}")

							if mail not in mail_list and verify_is_mail == 'True': 
								mail_list.append(mail)
								print(f"{Green}[+] Found an e-mail: {mail} on page >> {link}{Reset}")	
								print(f"{White}[+] Next searching Google for >> {mail}\n\n")
								serp_stack(mail)
								global mails_counter
								mails_counter += 1
					crawl_and_verify_with_mailbox(link)	
	except TypeError:
		pass 

	generate_csv_report(mail_list)	


def crawl_with_no_verification(url):

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
							print(f"{Green}[+] Found an e-mail: {mail} on page >> {link}{Reset}")	
							print(f"{White}[+] Next searching Google for >> {mail}\n\n")
							serp_stack(mail)
							global mails_counter
							mails_counter += 1
					crawl_with_no_verification(link)	
	except TypeError:
		pass 

	generate_csv_report(mail_list)

			

# https://serpstack.com/quickstart
def serp_stack(mail):
	global SERPSTACK_key

	params = {
	  'access_key': SERPSTACK_key,
	  'query': mail
	}

	print(f"[+]{Green} Searching for {mail} on Google >>{Reset}")

	api_result = requests.get('http://api.serpstack.com/search', params)

	api_response = api_result.json()

	
	print("Total results: ", api_response['search_information']['total_results'])

	for number, result in enumerate(api_response['organic_results'], start=1):
	    print("%s. Found on Page Titled >> %s" % (number, result['title']))
	    print("Page URL >> %s\n\n" % (result['url']))


# https://www.mailboxvalidator.com/python
def single_mail_validator(mail):
	global MAILBOX_key

	mbv = MailboxValidator.SingleValidation(MAILBOX_key)
	results = mbv.ValidateEmail(mail)

	if results is None:
		print("Error connecting to MailboxValidator.\n")
		return None
		
	elif results['error_code'] == '':
		return results['status']
		
	else:
		print('error_code = ' + results['error_code'] + "\n")
		print('error_message = ' + results['error_message'] + "\n")
		return None


# check if temporary email
def check_if_mail_is_temp(mail):
	global MAILBOX_key

	mbv = MailboxValidator.SingleValidation(MAILBOX_key)
	results = mbv.DisposableEmail(mail)

	if results is None:
		print("Error connecting to MailboxValidator.\n")
		return None
		
	elif results['error_code'] == '':
		return results['is_disposable']
		
	else:
		print('error_code = ' + results['error_code'] + "\n")
		print('error_message = ' + results['error_message'] + "\n")
		return None


# check if mail is free like gmail or yahoo
def check_if_mail_is_free(mail):
	global MAILBOX_key

	mbv = MailboxValidator.SingleValidation(MAILBOX_key)
	results = mbv.FreeEmail(mail)

	if results is None:
		print("Error connecting to MailboxValidator.\n")
		return None
		
	elif results['error_code'] == '':
		return results['is_free']
		
	else:
		print('error_code = ' + results['error_code'] + "\n")
		print('error_message = ' + results['error_message'] + "\n")
		return None


def generate_csv_report(mails):
	global xlsx_file_name
	global export_mail_list
	global domain
	global workbook
	global report_worksheet

	#csv_sheet_header = "REPORT FOR NUMBERS FOUND ON " + domain.upper()
	
	for mail in mails:
		if mail not in export_mail_list:
			export_mail_list.append(mail)


	# Start from the first cell. Rows and columns are zero indexed.
	row = 1
	col = 0
	i = 0
	try:
		if len(export_mail_list) != 0:
			
			row += 1
			# Iterate over the data and write it out row by row.
			for mail in export_mail_list:
					col = 0
					report_worksheet.write(row, col, mail)
					row += 1
					i += 1

			#Close the excel
			workbook.close()

	except Exception as e:
		print(f"{Red}[-]Error in export_results {e}{Reset}")

try:
	target_links = []
	mail_list = []
	export_mail_list = []
	mails_counter = 0
	
	option = get_argument()
	verification = option.verification_service

	api_keys_file = open('key.txt', 'r')
	lines = api_keys_file.readlines()
	api_keys_file.close()

	SERPSTACK_key = lines[0].split(':')[1].split()
	MAILBOX_key = lines[1].split(':')[1].split()

	SERPSTACK_key = ''.join(SERPSTACK_key) # convert to a string
	MAILBOX_key = ''.join(MAILBOX_key) # convert to a string

	
	if option.domain:
		domain = option.domain
		xlsx_file_name = domain + ".xlsx"
		target_url = "https://" + domain
		
		csv_sheet_header = "REPORT FOR E-MAILS FOUND ON " + domain.upper()


		workbook = xlsxwriter.Workbook(xlsx_file_name)
		report_worksheet = workbook.add_worksheet('report')
		header_border = workbook.add_format({"bottom":6, "bottom_color":"#ff0000", "top":1, "top_color":"#ff0000" })
			
		
		report_worksheet.write(0, 5, csv_sheet_header)

		second_header_list = ['E-MAIL', 'URL PAGE FOUND ON', 'E-MAIL VERIFICATION RESULT', 'GOOGLE SEARCH RESULT']

		start_row = 1
		start_column = 0
		end_column = start_column + len(second_header_list)

		for column_index in range(start_column, end_column):
			report_worksheet.write(start_row, column_index, second_header_list[column_index - start_column], header_border)

		if option.verification_service == 'no-verification':
			crawl_with_no_verification(target_url)
		elif option.verification_service == 'mailbox':
			crawl_and_verify_with_mailbox(target_url)	
		print(f"\n{Green}[+] Finished hunting down e-mails and now exiting ...{Reset}")
		print(f"\n{Green}[+] A total of {mails_counter} numbers were hunted down.{Reset}")
	elif option.mail:
		if option.verification_service == 'no-verification':
			serp_stack(option.mail)
		elif option.verification_service == 'mailbox':
			serp_stack(option.mail)	
	elif option.list:
		path = option.list
		file = open(path, 'r') 
		
		while True:

			line = file.readline()
			if not line:
				break
			mail = line.strip()

			if option.verification_service == 'no-verification':
				serp_stack(mail)
				print("\n\n")
			elif option.verification_service == 'mailbox':
				serp_stack(mail)
				print("\n\n")
					
		file.close()	

except KeyboardInterrupt:
	print(f"\n{Blue}[+] Detected CTRL + C .... Now halting the program{Reset}")
	print(f"\n{Green}[+] A total of {mails_counter} numbers were hunted down.{Reset}")				
