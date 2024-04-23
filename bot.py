import re
import time
import torch
import random
from comments import comments
from selenium import webdriver
from urllib.parse import urlparse
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from transformers import AutoModelForCausalLM, AutoTokenizer


WHATSAPP_LINK = "https://web.whatsapp.com"
PROFILE_PATH = "/home/dave/.mozilla/firefox/idltvjev.default-release-1712832970540"
TWITTER_USERNAME = "adesanyadavidj"
SESSION_LINK_COUNT = 21
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
        group_chat = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, f"//span[@title='$BLOCK FARMING']")))
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

    def like_tweet(self, index):
        like_buttons = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='like']")))
        like_buttons[index].click()

    def retweet(self, index):
        retweet_buttons = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='retweet']")))
        retweet_buttons[index].click()
        retweet_confirm_button = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='retweetConfirm']")))
        retweet_confirm_button.click()

    def generate_reply(self, user_input, temperature=1.0):
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium", padding_side="left")
        model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

        inputs = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
        reply_length = 30

        with torch.no_grad():
            reply = model.generate(inputs, max_length=inputs.shape[-1] + reply_length, pad_token_id=tokenizer.eos_token_id, temperature=temperature, do_sample=True)

        return tokenizer.decode(reply[:, inputs.shape[-1]:][0], skip_special_tokens=True)
    
    def remove_lines(self, tweet_text):
        lines = tweet_text.split('\n')
        lines = lines[2:-7]
        return '\n'.join(lines)

    def comment(self, tweet_text):
        comment_box = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
        comment_box.click()
        temperature = random.uniform(0.7, 1.3)  # generate a random temperature value between 0.7 and 1.3
        reply = self.generate_reply(tweet_text, temperature)
        comment_box.send_keys(reply)
        post_button = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetButtonInline']")))
        post_button.click()

    def get_tweet_text(self, username):
        tweets = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_all_elements_located((By.XPATH, "//article[@data-testid='tweet']")))
        for tweet in tweets:
            if username in tweet.text:
                tweet_text = tweet.text
                index = tweets.index(tweet)
                return self.remove_lines(tweet_text), index
                        
    def engage_tweets(self):
        print("Engaging tweets...")
        print("===============================================")
        for link in self.twitter_links:
            self.count += 1
            try:
                target_username = self.extract_username(link)
                tweet_id = self.get_tweet_id_from_url(link)

                if self.has_been_interacted_with(tweet_id):
                    print(f"{self.count}: Tweet {link} has already been engaged!!")
                    print("===============================================")
                    continue
                elif target_username == TWITTER_USERNAME:
                    print(f"{self.count}: Tweet {link} belongs to the bot!!")
                    print("===============================================")
                    continue

                print(f"{self.count}: Engaging {link}...")
                print("===============================================")
                self.driver.get(link)
                time.sleep(SLEEP_TIME)
                tweet_text, index = self.get_tweet_text(target_username)

                commands = [self.like_tweet, self.retweet, self.comment]
                random.shuffle(commands)

                for command in commands:
                    if command == self.comment:
                        command(tweet_text)
                    else:
                        command(index)
                    time.sleep(SHORT_SLEEP_TIME)

                self.mark_as_interacted_with(tweet_id)
            except Exception as e:
                print(e)
                print(f"{self.count}: Error engaging {link}. Skipping...")
                print("===============================================")
