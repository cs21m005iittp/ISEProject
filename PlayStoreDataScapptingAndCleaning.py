import os

from selenium import webdriver
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup #to parse HTML.
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests, lxml, re, json #requests-to make a request to a website., re-to match parts of the HTML where needed data is located via regular expression.
import pandas as pd


driver =webdriver.Chrome(ChromeDriverManager().install())

driver.maximize_window()
driver.get("https://play.google.com/store/search?q=games&c=apps")


def scrape_google_store_app(url):
    html = requests.get(url).text

    soup = BeautifulSoup(html, "lxml")
    # where all app data will be stored
    app_data = []
    # <script> position is not changing that's why [12] index being selected. Other <script> tags position are changing.
    # [12] index is a basic app information
    # https://regex101.com/r/DrK0ih/1
    basic_app_info = json.loads(re.findall(r"<script nonce=\".*\" type=\"application/ld\+json\">(.*?)</script>",
                                           str(soup.select("script")[12]), re.DOTALL)[0])
    # print("basic app info = ",basic_app_info)
    app_name = basic_app_info["name"]
    app_type = basic_app_info["@type"]
    app_url = basic_app_info["url"]
    app_description = basic_app_info["description"].replace("\n", "")  # replace new line character to nothing
    app_category = basic_app_info["applicationCategory"]
    app_operating_system = basic_app_info["operatingSystem"]
    app_main_thumbnail = basic_app_info["image"]
    app_content_rating = basic_app_info["contentRating"]
    app_rating = round(float(basic_app_info["aggregateRating"]["ratingValue"]), 1)  # 4.287856 -> 4.3
    app_reviews = basic_app_info["aggregateRating"]["ratingCount"]
    app_author = basic_app_info["author"]["name"]
    app_author_url = basic_app_info["author"]["url"]
    # https://regex101.com/r/VX8E7U/1
    app_images_data = re.findall(r",\[\d{3,4},\d{3,4}\],.*?(https.*?)\"", str(soup.select("script")))
    # delete duplicates from app_images_data
    app_images = [item for item in app_images_data if app_images_data.count(item) == 1]
    # User comments
    app_user_comments = []
    # https://regex101.com/r/SrP5DS/1
    app_user_reviews_data = re.findall(r"(\[\"gp.*?);</script>",
                                       str(soup.select("script")), re.DOTALL)
    for review in app_user_reviews_data:
        # https://regex101.com/r/M24tiM/1
        user_name = re.findall(r"\"gp:.*?\",\s?\[\"(.*?)\",", str(review))
        # https://regex101.com/r/TGgR45/1
        user_avatar = [avatar.replace('"', "") for avatar in re.findall(r"\"gp:.*?\"(https.*?\")", str(review))]
        # replace single/double quotes at the start/end of a string
        # https://regex101.com/r/iHPOrI/1
        user_comments = [comment.replace('"', "").replace("'", "") for comment in
                         re.findall(r"gp:.*?https:.*?]]],\s?\d+?,.*?,\s?(.*?),\s?\[\d+,", str(review))]
        # comment utc timestamp
        # use datetime.utcfromtimestamp(int(date)).date() to have only a date
        user_comment_date = [str(datetime.utcfromtimestamp(int(date))) for date in re.findall(r"\[(\d+),", str(review))]
        # https://regex101.com/r/GrbH9A/1
        user_comment_id = [ids.replace('"', "") for ids in re.findall(r"\[\"(gp.*?),", str(review))]
        # https://regex101.com/r/jRaaQg/1
        user_comment_likes = re.findall(r",?\d+\],?(\d+),?", str(review))
        # https://regex101.com/r/Z7vFqa/1
        user_comment_app_rating = re.findall(r"\"gp.*?https.*?\],(.*?)?,", str(review))
        for name, avatar, comment, date, comment_id, likes, user_app_rating in zip(user_name,
                                                                                   user_avatar,
                                                                                   user_comments,
                                                                                   user_comment_date,
                                                                                   user_comment_id,
                                                                                   user_comment_likes,
                                                                                   user_comment_app_rating):
            app_user_comments.append({
                "user_name": name,
                "user_avatar": avatar,
                "comment": comment,
                "user_app_rating": user_app_rating,
                "user__comment_likes": likes,
                "user_comment_published_at": date,
                "user_comment_id": comment_id
            })
        app_data.append({
            "app_name": app_name,
            "app_type": app_type,
            "app_url": app_url,
            "app_main_thumbnail": app_main_thumbnail,
            "app_description": app_description,
            "app_content_rating": app_content_rating,
            "app_category": app_category,
            "app_operating_system": app_operating_system,
            "app_rating": app_rating,
            "app_reviews": app_reviews,
            "app_author": app_author,
            "app_author_url": app_author_url,
            "app_screenshots": app_images
        })
        return {"app_data": app_data, "app_user_comments": app_user_comments}

for i in range(1,17): #range is given 1,2 then 1 acccessed  only
    df = pd.DataFrame(
        columns=["App Name", "Rating", "Total reviews", "Comment", "Commented On", "User Name", "User Rating",
                 "user comment likes", "Predicted Tag"
                 ])
    l = driver.find_element(By.CSS_SELECTOR, "div.ZmHEEd > div:nth-child("+str(i)+")> c-wiz > div > div > div.uzcko > div > div > a")
    time.sleep(1)
    url=l.get_attribute("href")#+'&showAllReviews=true'
    print(url)
    results=(json.dumps(scrape_google_store_app(url), indent=2))
    time.sleep(1)
    results=json.loads(results)
    #print(type(results))
    for repo in results["app_data"]:
        d = {'App Name': repo["app_name"], 'Rating': repo["app_rating"], "Total reviews": repo["app_reviews"]}
        df = df.append(d, ignore_index=True)
    for reviews in results['app_user_comments']:
        d = {'User Name': reviews["user_name"], 'Comment': reviews["comment"],
             "User Rating": reviews["user_app_rating"], "user comment likes": reviews["user__comment_likes"],
             "Commented On": reviews["user_comment_published_at"]}
        df = df.append(d, ignore_index=True)

    time.sleep(1)
    if not os.path.exists('reviews/'):
        os.makedirs('reviews/')
    df.to_csv("reviews/"+repo["app_name"]+"_reviews.csv", index=False)
    time.sleep(2)
    #driver.get("https://play.google.com/store/search?q=games&c=apps")

driver.quit()




