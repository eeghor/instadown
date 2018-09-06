from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import json
import re

from collections import defaultdict

class Instadown:

	def __init__(self):

		# options = webdriver.ChromeOptions()
		# options.add_argument('headless')

		# self.driver = webdriver.Chrome('webdriver/chromedriver', chrome_options=options)

		self.driver = webdriver.Chrome('webdriver/chromedriver')

		self.login_url ='https://www.instagram.com/accounts/login/'

		self.login_creds = json.load(open('credentials/instagram.json'))


	def login(self):

		self.driver.get(self.login_url)

		self.driver.find_element_by_name("username").send_keys(self.login_creds['user'])
		self.driver.find_element_by_name("password").send_keys(self.login_creds['password'])


		login_button = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Log in"]')))
		login_button.click()

		time.sleep(2)

		for c in ['chBAG', 'ckWGn']:

			try:
				close_button = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, f'//button[@class="{c}"]')))
				close_button.click()
				break
			except:
				print(f'couldn\'t find and click button with class {c}')
				pass

	def search(self, tag):

		search_field = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Search"]')))
		search_field.send_keys(tag)

		# search_field.send_keys(Keys.RETURN)

		time.sleep(6)

		for a in self.driver.find_elements_by_tag_name('a'):
			at = a.get_attribute('href')
			if f'/explore/tags/{tag.strip("#")}/' in at:
				print('clicking...')
				a.click()
				break

		time.sleep(4)

		last_height = self.driver.execute_script("return document.body.scrollHeight")
		print('starting last height=', last_height)

		# search_field.send_keys(Keys.RETURN)
		# time.sleep(3)

		for h2 in self.driver.find_elements_by_tag_name('h2'):
			if re.search(r'\d+', h2.text):
				print(h2.text)
				break

		d = defaultdict(lambda: defaultdict())
		c = 0

		for a in self.driver.find_elements_by_tag_name('a'):

			print(f'c={c}')

			if c == 100:
				break 

			# if (c > 0) and (c%6 == 0):

			# 	print('scrolling..')
			# 	self.driver.execute_script(f"window.scrollTo(0, {last_height + 1000});")
			# 	time.sleep(6)

			# 	new_height = self.driver.execute_script("return document.body.scrollHeight")

			# 	print('now height=', new_height)

			# 	if new_height == last_height:
			# 		break
			# 	else:
			# 		last_height = new_height

			
			ff =  f'tagged={tag.strip("#")}'

			href = None

			try:
				href = a.get_attribute('href')
			except:
				continue

			if ff in href:

				im = None

				try:
					im = a.find_element_by_xpath('.//div[1]/div[1]/img')
				except:
					pass

				if im:

					c += 1

					source = im.get_attribute('src')

					d[href]['source'] = source

				else:

					pass

				actions = ActionChains(self.driver)
				actions.move_to_element(a)
				actions.perform()

				time.sleep(3)

				for div in a.find_elements_by_xpath('.//div'):

					tx_ = div.text.lower().strip()
					
					if tx_:

						tx_ = tx_.replace(',','').replace('\n', ' ')

						print('text=', tx_)

						if 'video' in tx_:
							d[href]['type'] = 'video'
						else:

							try:
								print('looking for likes..')
								m1, m2 = tx_.split()
								print('m1=',m1)
								print('m2=',m2)
								d[href]['views' if d[href].get('type', None) else 'likes'] = m1
								d[href]['comments'] = m2
							except:
								pass
				a.click()
				time.sleep(2)

				vid = self.driver.find_element_by_xpath('//video').get_attribute('src')

				print(vid)

				self.driver.find_element_by_class_name('ckWGn').click()



		# 		if overs:

		# 			print(overs.text)

		# 			if not re.match(r'\d+', overs.text):

		# 				try:
		# 					overs = a.find_element_by_xpath('.//div[2]')
		# 				except:
		# 					print('still no overs')
		# 		else:

		# 			try:
		# 				overs = a.find_element_by_xpath('.//div[2]')
		# 			except:
		# 				print('still no overs')

		# 		if overs:
		# 			# print(overs.get_property('attributes')[0])
		# 			print('image metrics text: ', overs.text)

		# 			d[href]['metrics'] = overs.text

		# print(f'total urls: {len(d)}')

		json.dump(d, open('sample.json','w'))
		# self.driver.close()


if __name__ == '__main__':

	ins = Instadown()

	ins.login()
	ins.search('#timtamslam')
