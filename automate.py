from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from comments import comments
import time
import re
import random
from urllib.parse import urlparse

def extract_username(url):
    path = urlparse(url).path
    parts = path.split('/')
    if len(parts) > 1:
        return parts[1]
    return None


# Function to like a tweet
def like(index):
    like_buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='like']")))
    time.sleep(2)  # Allow some time for the tweet to fully load
    like_buttons[index].click()

# Function to quote a tweet
def quote(index):
    try:
        retweet_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='unretweet']")))
        time.sleep(2)  # Allow some time for the tweet to fully load
        retweet_button.click()
    except:
        retweet_buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='retweet']")))
        time.sleep(2)  # Allow some time for the tweet to fully load
        retweet_buttons[index].click()
    quote_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/compose/post']")))
    quote_button.click()
    send_tweet = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
    send_tweet.send_keys(random.choice(comments))
    post = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetButton']")))
    post.click()

# Function to comment on a tweet
def comment(index):
    comment_buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='reply']")))
    time.sleep(2)  # Allow some time for the tweet to fully load
    comment_buttons[index].click()
    input_comment = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
    input_comment.send_keys(random.choice(comments))
    post_comment = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetButton']")))
    post_comment.click()

# Function to repost a tweet
def repost(index):
    retweet_buttons = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='retweet']")))
    time.sleep(2)  # Allow some time for the tweet to fully load
    retweet_buttons[index].click()
    retweet_confirm_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='retweetConfirm']")))
    retweet_confirm_button.click()

def get_tweet_id_from_url(url):
    return url.split('/')[-1]

def has_been_interacted_with(tweet_id):
    # Open the file and read the IDs
    with open('interacted_tweets.txt', 'r') as file:
        interacted_tweets = file.read().splitlines()

    # Check if the tweet ID is in the file
    return tweet_id in interacted_tweets

def mark_as_interacted_with(tweet_id):
    # Append the tweet ID to the file
    with open('interacted_tweets.txt', 'a') as file:
        file.write(tweet_id + '\n')


#Open file for interacted tweet
with open('interacted_tweets.txt', 'a') as file:
    pass

options = Options()
options.profile = "/home/dave/.mozilla/firefox/68pj9xf2.default-release"  # Replace with your actual profile path
driver = webdriver.Firefox(options=options)

# Go to the WhatsApp web client
driver.get("https://web.whatsapp.com/")
input("Press enter after scanning QR code.....")

# Open the group chat (replace 'Group Chat Name' with the name of your group chat)
group_chat = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, f"//span[@title='$BLOCK Farming 🧑‍🌾']")))
group_chat.click()

# Wait for the chat to load
time.sleep(30)

# Get all the messages in the chat
messages = WebDriverWait(driver, 40).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".x3psx0u")))

# Extract links from the messages
links = []
count = 0
for message in messages:
    text = message.text
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    links.extend(urls)
    links = list(dict.fromkeys(links))

# Get links from last session
needed_links = links[-52:]
links = needed_links

for link in links:
    try:
        tweet_id = get_tweet_id_from_url(link)
        if has_been_interacted_with(tweet_id):
            # Skip this tweet
            continue
        target_username = extract_username(link)
        if target_username == "adesanyadavidj":
            continue
        count += 1
        print(f"{link} : {count}")
        driver.get(link)
        time .sleep(20)
        
        # Find the specific tweet and interact with it
        tweets = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//article[@data-testid='tweet']")))
        for tweet in tweets:
            tweet_text = tweet.text
            # Check if the username is in the tweet text
            if target_username in tweet_text:
                index = tweets.index(tweet)
                break
        
        # Interact with the tweet
        command_options = [like, quote, comment, repost]
        for _ in range(4):
            random_command = random.choice(command_options)
            command_options.remove(random_command)
            random_command(index)
            time.sleep(5)
        mark_as_interacted_with(tweet_id)
    except:
        print(f"Error occured with {link}")
        print("Continuing....")
    

# Close the browser
driver.quit()

# Path: automate.py