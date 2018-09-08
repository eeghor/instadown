from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import json
import re
import os

import urllib.request

from collections import defaultdict

class Instadown:

	def __init__(self, headless=False):

		self.WAIT_SECS = 20

		options = webdriver.ChromeOptions()
		options.add_argument('disable-notifications')

		if headless:
			options.add_argument('headless')

		self.driver = webdriver.Chrome('webdriver/chromedriver', chrome_options=options)

		self.login_url ='https://www.instagram.com/accounts/login/'

		self.login_creds = json.load(open('credentials/instagram.json'))

		self.posts = defaultdict(lambda: defaultdict())

		self.video_dir = 'videos'

		if not os.path.exists(self.video_dir):
			os.mkdir(self.video_dir)

		self.picture_dir = 'pictures'

		if not os.path.exists(self.picture_dir):
			os.mkdir(self.picture_dir)


	def login(self):

		print('logging in...')

		self.driver.get(self.login_url)

		self.driver.find_element_by_name("username").send_keys(self.login_creds['user'])
		self.driver.find_element_by_name("password").send_keys(self.login_creds['password'])

		login_button = WebDriverWait(self.driver, self.WAIT_SECS) \
							.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Log in"]'))).click()
		time.sleep(2)

		# there's usually an annoying dialog popping up once you logged in; we'll try to close it

		for c in ['chBAG', 'ckWGn']:

			try:
				close_button = WebDriverWait(self.driver, self.WAIT_SECS) \
						.until(EC.element_to_be_clickable((By.XPATH, f'//button[@class="{c}"]'))).click()
				break
			except:
				pass

	def _get_number_posts_found(self, tg):

		"""
		returns the number of posts found for the hashtag tg
		 - return type is int
		"""
		# scenario 1:
		# when you see a large hashtag tg (which is when the browser window size is large enough)

		try:
			posts_found_txt = [_ for _ in self.driver.find_elements_by_partial_link_text(f"{tg}") if _.tag_name == 'a'] \
									.pop() \
									.find_element_by_xpath('../following-sibling::div') \
									.text
		except:
			# scenario 2: 
			# no large hashtag and the total found posts is on the same panel as the "Top posts" text
			try:	
				posts_found_txt = self.driver.find_element_by_xpath('//div[contains(text(), "Top posts")]') \
									.text
			except:
				print(f'can\'t find the total number of posts for {tg}!')
				return None

		return int(re.search(r'(\d+,?\d*)', posts_found_txt).group(0).replace(',',''))


	def _get_post_urls(self):

		avail_urls = self.driver.find_elements_by_xpath('//a[contains(@href, "tagged=")]')
		print(f'get posts called. {len(avail_urls)} available on the page')

		for i, a in enumerate(avail_urls, 1):

			url_p_ = a.get_attribute('href')
			id_ = url_p_.split('/?')[0].split('/')[-1]

			if id_ not in self.posts:
				self.posts[id_]['post_url'] = url_p_

		return self

	def scroll_and_collect(self, sleep_secs=10):
		"""
		assume you're looking at the page with the search results; now you'd like to
		collect all or some of the post URLs corresponding to the pictures you see;
		because this is an infinite page, we'll need to scroll until we've collected
		everything we wanted; 
		 - it seems like only up to 50 pictures can be 'active' on the page, so we can't 
		 	first scroll until all pictures are visible and then collect the URLs - we have to
		 	collect as we go 
		"""

		hight_ = self.driver.execute_script("return document.body.scrollHeight")

		self._get_post_urls()

		while len(self.posts) < 6:

			print('scroll..')

			self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight);")

			time.sleep(sleep_secs)

			self._get_post_urls()

			print(f'collected urls so far: {len(self.posts)}')

			new_height = self.driver.execute_script("return document.body.scrollHeight")

			if new_height > hight_:
				hight_ = new_height
			else:
				print('reached the bottom of the page')
				break

		return self

	def get_post(self, post_url):

		"""
		collects various information for the post at post_url
		"""

		self.driver.get(post_url)

		likes = comments = when_posted = post_type = content_url = None

		try:
			likes = int(re.search(r'(\d+,?\d*)', 
						[_ for _ in self.driver.find_elements_by_xpath('//a[@href]') 
									if 'liked_by' in _.get_attribute('href')] \
						.pop() \
						.text) \
						.group(0) \
						.replace(',',''))
		except:
			# another scenario
			try:
				likes = int(re.search(r'(\d+,?\d*)', 
							[_ for _ in self.driver.find_elements_by_xpath('//span[@role="button"]') 
										if 'views' in _.text.lower()] \
							.pop() \
							.text) \
							.group(0) \
							.replace(',',''))
			except:
				pass

		try:
			when_posted = self.driver.find_element_by_xpath('//time[@datetime]').get_attribute('datetime')
		except:
			pass

		try:
			comments = len(self.driver.find_element_by_tag_name('ul').find_elements_by_tag_name('li'))
		except:
			pass

		# check if this is a video
		try:
			vid = self.driver.find_element_by_xpath('//video[@src]')
			post_type = vid.get_attribute('type')
			content_url = vid.get_attribute('src')
		except:
			# check if it's a picture
			try:
				content_url = self.driver.find_element_by_xpath('//img[@srcset]').get_attribute('srcset') \
									.split(',')[-1].strip().split()[0]
				post_type = 'picture'
			except:
				pass


		return {'type': post_type, 'posted': when_posted, 'likes': likes, 'comments': comments, 'content_url': content_url}

	def search(self, tag):

		search_field = WebDriverWait(self.driver, self.WAIT_SECS) \
							.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Search"]'))) \
								.send_keys(tag)

		time.sleep(5)

		for a in self.driver.find_elements_by_tag_name('a'):
			at = a.get_attribute('href')
			if f'/explore/tags/{tag.strip("#")}/' in at:
				a.click()
				break

		time.sleep(4)

		print(f'found posts: {self._get_number_posts_found(tag)}')

		# self._get_post_urls()
		self.scroll_and_collect()

		for p in self.posts:
			self.posts[p].update(self.get_post(self.posts[p]['post_url']))

		json.dump(self.posts, open('posts.json','w'))

	def get_content(self, id, url):

		"""
		download whatever the url points to
		"""
		ext_ = url.split('.')[-1]

		if ext_ == 'mp4':
			local_filename, headers = urllib.request.urlretrieve(url, os.path.join(self.video_dir, f'video_{id}.{ext_}'))
		else:
			local_filename, headers = urllib.request.urlretrieve(url, os.path.join(self.picture_dir, f'picture_{id}.{ext_}'))

		return self




if __name__ == '__main__':

	ins = Instadown()

	ins.login()
	ins.search('#timtamslam')

	for i, k in enumerate(ins.posts, 1):
		if i == 10:
			break
		ins.get_content(k, ins.posts[k]['content_url'])
