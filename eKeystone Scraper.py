from selenium import webdriver
from bs4 import BeautifulSoup
from requests import get
from selenium.webdriver.common.keys import Keys
import urllib.request as ur
from urllib.request import urlopen
import re
import csv
import sys
import requests
import time
import os
import urllib

index = 0

print("######################### eKeystone Crawler #########################")
print("Delete previous ___.csv and images folder if re-running program.")
print("Note: Categories are not finished & tags are only partially finished.")
print("#####################################################################")
print("")

print("###################### Date | Supplier | Brand ######################")
date = input('Enter Date (YYYY/MM): ')
supplier = input('Enter Supplier (Ex. A12): ')
brand1 = input('Enter Brand: ')
print("#####################################################################")
print("")

print("########################### File Location ###########################")
file_location = input('Enter location of SKU txt file: ')
store2 = input('Enter location to store images: ')
print("#####################################################################")

file_location1 = file_location.replace('\\','/')
store = store2.replace('\\','/')

csvfile = store + "/" + supplier + ".csv"

chromedriver = '' #LOCATION OF CHROMEDRIVER
browser = webdriver.Chrome(chromedriver)

print(" Opening browser")

browser.get('https://wwwsc.ekeystone.com/login?Logout=true&RedirectURL=/')

print(" Logging into eKeystone")

username = browser.find_element_by_name('webcontent_0$txtUserName')
username.send_keys('') #USERNAME

password = browser.find_element_by_name('webcontent_0$txtPassword')
password.send_keys('') #PASSWORD

browser.find_element_by_xpath("""//*[@id="webcontent_0_submit"]""").click()

time.sleep(3)

num_lines = sum(1 for line in open(file_location1))

with open(csvfile, 'w', newline='') as csv_file:
	writer = csv.writer(csv_file)
	writer.writerow(["SKU", "Name", "Published", "Is featured?", "Visibility in catalog", "Short description", "Description", "Tax status", "In stock?", "Stock", "Backorders allowed?", "Sold individually?", "Allow customer reviews?", "Regular Price", "Categories", "Tags", "Images", "Position", "Attribute 1 name", "Attribute 1 value(s)", "Attribute 1 visible", "Attribute 1 global"])
	with open(file_location1) as f:
		for line in f:

			sku_input = browser.find_element_by_name('siteheadercontent_0$smartSearch$txtSmartSearch')
			input2 = line.replace("\r","")
			input2 = line.replace("\n","")
			sku_input.send_keys(input2)

			index += 1
			
			print("     Searching SKU: " + input2 + " (" + str(index) + " out of " + str(num_lines) + ")")

			time.sleep(5)
			
			sku_input.send_keys(Keys.DOWN)
			sku_input.send_keys(Keys.ENTER)
			print("     Loading page...")
			time.sleep(5)
			
			data = browser.page_source
			soup = BeautifulSoup(data, 'lxml')


			#NAME
			name_box = soup.find('span', attrs={'id': 'webcontent_0_row2_0_productDetailHeader_lblTitle'})
			if name_box is None:
				print("!! ERROR LOADING PRODUCT PAGE !!")
			else:
				name = name_box.text.strip()
			

			print("        Extracting data")
			sku1 = line
			sku = line.replace("\r","")
			sku = line.replace("\n","")
			print("             Name: " + name)

			#SHORT DESC
						shortdesc_box = soup.find('div', attrs={'id': 'webcontent_0_row2_0_productDetailTabs_upAdditionalInfoTab'})
						shortdesc_remove_box = soup.find('div', attrs={'id': 'webcontent_0_row2_0_productDetailTabs_requiredProducts'})
						if shortdesc_box is None: 
							shortdesc = "No description"
						
						elif shortdesc_remove_box is not None:

							shortdesc_remove = shortdesc_remove_box.text.strip()
							shortdesc_original = shortdesc_box.text.strip()

							shortdesc1 = shortdesc_original.replace(shortdesc_remove, '')
							shortdesc2 = shortdesc1.replace("                                        ", "")
							shortdesc3 = shortdesc2.replace("â€™", "'")
							#print(shortdesc)
							shortdesc4= shortdesc3.split("Recommended Items")
							shortdesc5 = shortdesc4[0]

							shortdesc6 = shortdesc5.split("Replacement Items")
							shortdesc7 = shortdesc6[0]
							
							shortdesc = shortdesc7.replace(":\r",": ")
							shortdesc = shortdesc.replace(":\n",": ")
							shortdesc = shortdesc.replace(": \r",": ")
							shortdesc = shortdesc.replace(": \n",": ")
							shortdesc = shortdesc.replace("®", "")
							shortdesc = shortdesc.replace("‘", "'")
							shortdesc = shortdesc.replace("™","")
							shortdesc = shortdesc.replace("’", "'")
						print("             Short Description: ...")
						
						#LONG DESC
						longdesc_box = soup.find('span', attrs={'id': 'webcontent_0_row2_0_productDetailHeader_lblDescription'})
						if longdesc_box is None:
							longdesc = "No longdesc"
						else:
							longdesc = longdesc_box.text.strip()
						print("             Long Description: ...")
						#print(longdesc)
			
			#LONG DESC
			longdesc_box = soup.find('span', attrs={'id': 'webcontent_0_row2_0_productDetailHeader_lblDescription'})
			if longdesc_box is None:
				longdesc = "No longdesc"
			else:
				longdesc = longdesc_box.text.strip()
			print("             Long Description: ...")
			#print(longdesc)

			#STOCK
			stock_box = soup.find('td', attrs={'id': 'webcontent_0_row2_0_productDetailBasicInfo_tdInventory'})
			if stock_box is None:
				stock2 = "No stock"
			else:
				stock = stock_box.text.strip()
				stockfirst = stock[0:3]
				stock1 = stockfirst.replace("Sp","0")
				stock3 = stock1.replace(" i", '')
				stock2 = stock3.replace("0e", '0')
				#print(stock1)
			print("             Stock: " + stock2)

			#TAGS
			tags1 = sku + ", " + name + ", " + longdesc
			tags2 = tags1.replace(';',',')
			tags = tags2.replace("No longdesc","")

			#PRICE
			price_box = soup.find('span', attrs={'id': 'webcontent_0_row2_0_productDetailBasicInfo_lblRetailPrice'})
			if price_box is None:
				price1 = "No price found"
			else:
				price = price_box.text.strip()
				price1 = "".join(_ for _ in price if _ in ".1234567890")
				#print(price1)
			print("             Price: $" + price1)

			#IMAGE LINKS
			image2 = '' + date + "/" + sku + ".jpg" #WORDPRESS ADDRESS
			store1 = store + "/" + "images" + "/" + sku + "/"
			os.makedirs(store1)

			#DOWNLOAD IMAGES
			link = soup.find('img',attrs={'id': 'webcontent_0_row2_0_imgLarge'})
			image = link.get("src")
			r2 = requests.get(image)
			with open(store1 + sku + ".jpg", "wb") as f:
				f.write(r2.content)
			print("        Downloading image")
			print("------------------------------------------------")
			
			#WRITE CSV
			writer = csv.writer(csv_file)
			writer.writerow([sku, name, "1", "0", "visible", shortdesc, longdesc, "taxable", "1", stock2, "0", "0", "1", price1, "", tags, image2, "0", "Brand", brand1, "1", "1"])

	print("Done!")
	sys.exit()