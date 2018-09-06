from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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

if __name__ == '__main__':

	ins = Instadown()

	ins.login()

