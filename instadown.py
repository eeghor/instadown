from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import json

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
			print(at)
			if f'/explore/tags/{tag.strip("#")}/' in at:
				print('clicking...')
				a.click()
				break

		time.sleep(4)

		# search_field.send_keys(Keys.RETURN)
		# time.sleep(3)

		total_posts = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, 'h2')))
		print(total_posts.text)

		for a in self.driver.find_elements_by_tag_name('a'):

			
			ff =  f'tagged={tag.strip("#")}'

			try:
				
				if ff in a.get_attribute('href'):
					print('got this:')
					print(a.get_attribute('href'))
					im = a.find_element_by_xpath('.//div[1]/div[1]/img')
					print(im.get_attribute('src'))

					actions = ActionChains(self.driver)
					actions.move_to_element(a)
					actions.perform()

					time.sleep(2)

					overs = a.find_element_by_xpath('.//div[3]')

					print('got hidden one!')

					print(overs.text)



			except:
				continue


		

if __name__ == '__main__':

	ins = Instadown()

	ins.login()

	ins.search('#timtamslam')

