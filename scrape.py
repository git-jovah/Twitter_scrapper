from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import datetime as dt
import streamlit as st
import os,dotenv
import mongo
import pandas as pd

MAIN_TWEETS = []

def driver_setup():
    global wait
    # Setup Chrome (auto installs driver)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver,5)
    return driver

def print_text(username,tweet_text,like,retweet,reply,date):
    st.write(username, "   --   ",tweet_text)
    if (like == 0) and ( retweet == 0) and (reply == 0):
        like = retweet = reply = "--"
        st.write(f"likes - {like} | retweets - {retweet} | replys - {reply}")
        st.write(f"Date - {date}")
    elif (like == 0) and ( retweet == 0) :
        like = retweet = "--"
        st.write(f"likes - {like} | retweets - {retweet} | replys - {reply}")
        st.write(f"Date - {date}")
    elif ( retweet == 0) and (reply == 0):
        retweet = reply = "--"
        st.write(f"likes - {like} | retweets - {retweet} | replys - {reply}")
        st.write(f"Date - {date}")
    elif (reply == 0):
        reply = "--"
        st.write(f"likes - {like} | retweets - {retweet} | replys - {reply}")
        st.write(f"Date - {date}")
    elif (like == 0):
        like = "--"
        st.write(f"likes - {like} | retweets - {retweet} | replys - {reply}")
        st.write(f"Date - {date}")
    elif (retweet == 0):
        retweet = "--"
        st.write(f"likes - {like} | retweets - {retweet} | replys - {reply}")
        st.write(f"Date - {date}")

    else:
        st.write(f"likes - {like.text} | retweets - {retweet.text} | replys - {reply.text}")
        st.write(f"Date - {date}")
    st.write("-"*20)
    
def begin_upload():
    if MAIN_TWEETS:
        mongo.mongo_upload(data=MAIN_TWEETS,db_name="twitter_db",coll_name="tweets")
    else:
        st.markdown("no main tweets...")

def data_prep(csv=True):
    if MAIN_TWEETS:
        dt = [i.values() for i in MAIN_TWEETS]
        twt_data = pd.DataFrame(data=dt,columns=list(MAIN_TWEETS[0].keys()))
        print(twt_data)
        if twt_data.any().any():
            if csv:
                return twt_data.to_csv(index=False)
            else:
                return twt_data.to_json(index=False,indent=5)
    else:
        st.write("NO TWEETS FOUND!s")
        return 0

def login_set(driver,url):
    try:
        st.write("Login started...")
        dotenv.load_dotenv()
        user_name = os.getenv("TWITTER_USERNAME")
        user_pass = os.getenv("TWITTER_PASSKEY")
        mail = os.getenv("MAIL")

        driver.get(url)

        user_name_input = wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@name='text']")))
        user_name_input.send_keys(user_name)
        user_name_input.send_keys("\n")
        try:
            verify = driver.find_element(By.XPATH,"//input[@name='text']")
            if verify:
                st.markdown("asking verification")
                verify.send_keys(mail)
                ver_next_button = wait.until(EC.visibility_of_element_located((By.XPATH,"//button[@data-testid='ocfEnterTextNextButton']")))
                ver_next_button.click()
                user_password = wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@name='password']")))
                user_password.send_keys(user_pass)
                driver.find_element(By.XPATH,"//button[@data-testid='LoginForm_Login_Button']").click()
                return "login success"
        except:
            user_password = wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@name='password']")))
            user_password.send_keys(user_pass)
            driver.find_element(By.XPATH,"//button[@data-testid='LoginForm_Login_Button']").click()
            return "login success"
    except Exception as e:
        st.write("something went wrong!")
        print("LOGIN ATTEMPT FAILED ERROR :",e)


def user_data_getter(driver,url):
    st.markdown(":green[setting connection...]")
    driver.get(url)
    
    st.markdown(":green[connection found...]")
    try:
        user_name = wait.until(EC.visibility_of_element_located((By.XPATH,("//div[@data-testid='UserName']"))))
        user_name = user_name.text
        yield user_name
    except Exception as e:
        yield 0
        st.markdown("USER NAME NOT FOUND...")
        st.markdown("scrapping process stopped...")
        print("Error finding user name:", e)
        return False

    try:
        join_date = wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@data-testid='UserProfileHeader_Items']")))
        join_date = join_date.find_element(By.XPATH, ".//span[@data-testid='UserJoinDate']")
        join_date = join_date.text
        yield join_date
    except Exception as e:
        yield 0
        print("Error finding join date:", e)
    
    try:
        tweet_count = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/div")))
        tweet_count = tweet_count.text
        yield tweet_count
    except Exception as e:
        yield 0
        print("Error finding tweet count:", e)
    
    try:
        followers_link = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a[href$='/verified_followers']")))
        yield followers_link.text
    except Exception as e:
        yield 0
        print("Error finding followers count:", e)
    
    try:
        following_count = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"div[class='css-175oi2r r-1rtiivn']")))
        yield following_count.text
    except Exception as e:
        yield 0
        print("Error finding following count:", e)

def temp_det(count,tweets):
    for i in range(1,count+1):
            MAIN_TWEETS.append(tweets[i])
            st.write(i)
            print_text(
                username=tweets[i]["username"],
                tweet_text = tweets[i]["tweets_text"],
                like = tweets[i]["like"],
                retweet = tweets[i]["retweet"],
                reply= tweets[i]["reply"],
                date = tweets[i]["date"]
                )
    return MAIN_TWEETS

def hash_tag_getter(driver,url,count):
    driver.get(url)
    try:
        tweets = {}
        st.write("scrapping started now for getting tweets")
        for _ in range(0,int(count/3)):
            cont = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,"[data-testid='cellInnerDiv']")))
            for x,ele in enumerate(cont,start=1):
                handle = ele.find_element(By.CSS_SELECTOR,"[data-testid='User-Name']")
                if handle:
                    tweets_T = ele.find_element(By.CSS_SELECTOR,"[data-testid='tweetText']")
                    if tweets_T:
                        like = driver.find_element(By.CSS_SELECTOR,"[data-testid='like']")
                        retweet = ele.find_element(By.CSS_SELECTOR,"[data-testid='retweet']")
                        reply = ele.find_element(By.CSS_SELECTOR,"[data-testid='reply']")
                        time_ele = ele.find_element(By.TAG_NAME,"time")
                        att_date = time_ele.get_attribute("datetime")
                        tweet_date = dt.datetime.strptime(att_date,"%Y-%m-%dT%H:%M:%S.%fZ") #"2025-08-22T17:34:41.000Z"
                        tweet_date = tweet_date.strftime("%d/%m/20%y")
                        while x in list(tweets.keys()):
                            x+=1
                        else:
                            tweets[x] = {
                                "username":re.findall(r"\w+",handle.text)[0],
                                "id" : re.findall(r"@\w+",handle.text)[0],
                                "tweets_text":tweets_T.text,
                                "like":0 if like.text== "" else like.text,
                                "retweet":0 if retweet.text=="" else retweet.text,
                                "reply":0 if reply.text=="" else reply.text,
                                "date":tweet_date,
                                }
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(5)
        m_n = temp_det(count=count,tweets=tweets)
        return m_n
    except Exception as e:
        st.markdown("HASH TAG NOT FOUND...")
        st.markdown("scrapping process stopped...")
        print("Error finding hash tag:", e)
        return False

def check_type(n):
    if n.startswith("#"): return False
    elif n.startswith('@'): return True
    else: return True
    
def scrape_it(test,since=dt.datetime.today().date(),until=dt.datetime.today().date(),tweet_range = 10):
    if len(test) <= 5:
        if test[0]=="#":
            Est_time = (len(test)+(len(test)+tweet_range))*3.54
            st.markdown(f"Estimated time : {Est_time:.2f} *seconds*")
        else:
            Est_time = (len(test)+(5-len(test)))*4.54
            st.markdown(f"Estimated time : {Est_time:.2f} *seconds*")
    else:
        if test[0]=="#":
            Est_time = (len(test)+(len(test)+tweet_range))*3.54
            st.markdown(f"Estimated time : {Est_time:.2f} *seconds*")
        else:
            Est_time = ((len(test)/2)+1)*3.54
            st.markdown(f"Estimated time : {Est_time:.2f} *seconds*")
    st.markdown(":green[setting up driver...]")

    driver = driver_setup()

    if check_type(test):

        try:
            st.markdown(":green[opening twitter link..]")
            data = user_data_getter(driver, f"https://x.com/{test}")
            time.sleep(3)
            st.markdown("\n")
            st.markdown(f"*:gray[User Name      ]* **:** {next(data)}")
            st.markdown(f"*:gray[join date      ]* **:** {next(data)}")
            st.markdown(f"*:gray[tweet count    ]* **:** {next(data)}")
            st.markdown(f"*:gray[follower count ]* **:** {next(data)}")
            st.markdown(f"*:gray[following count]* **:** {next(data)}")
            st.markdown(f"*:gray[scrapping date ]* **:** {dt.date.today()}")
            driver.quit()
            return Est_time

        except Exception as e:
            print("An error occurred:", e)
    
    else:
        login_set(driver,r"https://x.com/i/flow/login")
        time.sleep(4)
        mn = hash_tag_getter(driver, f"https://x.com/search?q=(%23{test[1:]})%20until%3A{until}%20since%3A{since}&src=typed_query&f=live",count=tweet_range)
        # https://x.com/search?f=top&q=(%23HeavyRains)%20until%3A2020-06-15%20since%3A2020-06-10&src=typed_query


# it stopping if i give the tweet count more than 10
# it stopping if i give the tweet count more than 10
# it stopping if i give the tweet count more than 10
        driver.quit()
        return mn,Est_time
    if driver.session_id:
        driver.quit()


if __name__ == "__main__":
    scrape_it()
