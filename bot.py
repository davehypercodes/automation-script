import re
import time
import random
from comments import comments
from selenium import webdriver
from urllib.parse import urlparse
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC

WHATSAPP_LINK = "https://web.whatsapp.com"
PROFILE_PATH = "/home/dave/.mozilla/firefox/idltvjev.default-release-1712832970540" #Edit as needed
TWITTER_USERNAME = "adesanyadavidj" #Edit as needed
SESSION_LINK_COUNT = 21 #Edit as needed
SLEEP_TIME = 10
SHORT_SLEEP_TIME = 5
TIMEOUT = 30

class WhatsTweetBot:
    def __init__(self):
        self.driver = None
        self.twitter_links = []
        self.messages = []
        self.count = 0
        with open("interacted_tweets.txt", "a") as file:
            pass
        
    def open_browser(self):
        options = Options()
        options.profile = PROFILE_PATH
        self.driver = webdriver.Firefox(options=options)

    def open_whatsapp(self):
        self.driver.get(WHATSAPP_LINK)
        input("Press Enter after chats are fully synced: ")
        group_chat = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, f"//span[@title='$💰💰💰💰💰Farming 🧑‍🌾']")))
        group_chat.click()

    def get_messages(self):
        self.messages = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".x3psx0u")))

    def extract_links(self):
        print("Getting links...")
        for message in self.messages:
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
            self.twitter_links = [link for link in urls if "twitter.com" in link or "x.com" in link]
            self.twitter_links = list(dict.fromkeys(self.twitter_links))
            self.twitter_links = self.twitter_links[-SESSION_LINK_COUNT:]
    
    def get_tweet_id_from_url(self, link):
        return link.split("/")[-1]
    
    def has_been_interacted_with(self, tweet_id):
        with open('interacted_tweets.txt', 'r') as file:
            interacted_tweets = file.read().splitlines()
        return tweet_id in interacted_tweets
    
    def mark_as_interacted_with(self, tweet_id):
        with open('interacted_tweets.txt', 'a') as file:
            file.write(tweet_id + '\n')

    def extract_username(self, link):
        path = urlparse(link).path
        parts = path.split('/')
        if len(parts) > 1:
            return parts[1]
        return None


    def like_tweet(self):
        like_buttons = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='like']")))
        like_buttons[0].click()

    def retweet(self):
        retweet_buttons = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='retweet']")))
        retweet_buttons[0].click()
        retweet_confirm_button = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='retweetConfirm']")))
        retweet_confirm_button.click()

    def comment(self):
        comment_box = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
        comment_box.click()
        comment_box.send_keys(random.choice(comments))
        post_button = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetButtonInline']")))
        post_button.click()

    def engage_tweets(self):
        print("Engaging tweets...")
        for link in self.twitter_links:
            self.count += 1
            try:
                tweet_id = self.get_tweet_id_from_url(link)
                if self.has_been_interacted_with(tweet_id) or self.extract_username(link) == TWITTER_USERNAME:
                    print(f"{self.count}: Tweet {link} has already been interacted with or it is a personal tweet. Skipping...")
                    print("===============================================")
                    continue

                # # Find the specific tweet and interact with it
                # tweets = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_all_elements_located((By.XPATH, "//article[@data-testid='tweet']")))
                # for tweet in tweets:
                #     tweet_text = tweet.text
                #     # Check if the username is in the tweet text
                #     if target_username in tweet_text:
                #         index = tweets.index(tweet)
                #         break

                commands = [self.like_tweet, self.retweet, self.comment]
                self.driver.get(link)
                time.sleep(SLEEP_TIME)
                for _ in range(3):
                    command = random.choice(commands)
                    command()
                    commands.remove(command)
                    time.sleep(SHORT_SLEEP_TIME)
                self.mark_as_interacted_with(tweet_id)
            except:
                print(f"{self.count}: Error engaging {link}. Skipping...")
                print("===============================================")
