import os
from random import random
import time

import requests
from bs4 import BeautifulSoup

# Links keeps track of all URLs visited
if not os.path.isfile("links.py"):
    with open("links.py", "w") as output:
        output.write("links = set()")

from links import links


BASE_URL = "https://pitchfork.com"
REVIEWS_URL = f"{BASE_URL}/reviews/albums"

OUTPUT = "reviews.csv"
HEADER = "text;genre;year;author;score\n"


def get_review_links(page_index):
    reviews_url = f"{REVIEWS_URL}/?page={page_index}"
    reviews_page = requests.get(reviews_url)

    if reviews_page.status_code != 200:
        print(f"Failed page {page_index}\nError: {reviews_page.status_code}")
        return None

    soup = BeautifulSoup(reviews_page.content, "html.parser")
    reviews = soup.find_all("div", class_="review")

    review_urls = list()

    for review in reviews:
        album_link = review.find('a', class_='review__link').attrs['href']
        review_urls.append(f"{BASE_URL}{album_link}")

    return review_urls


def get_review_info(url):
    review = requests.get(url)

    if review.status_code != 200:
        print(f"Failed page {page_index}\nError: {review.status_code}")
        return None

    soup = BeautifulSoup(review.content, "html.parser")

    score = soup.find_all("span", class_="score")[0].text
    genre = soup.find_all(
        "a", class_="genre-list__link"
    )[0].text  # Get first genre
    year = soup.find_all(
        "span", class_="single-album-tombstone__meta-year"
    )[0].text[-4:]  # Last 4 digits are the year
    author = soup.find_all(
        "span", class_="authors-detail__title"
    )[0].text  # Author type (contributor, associante, etc.)

    # Get review content
    text = str()
    paragraphs = soup.find_all("p")

    for paragraph in paragraphs:
        # Concatenate the paragraphs
        text = f"{text} {paragraph.get_text()}"

    # Remove line breaks and semicolons
    text = text.replace('\n', ' ').replace(';', ',')

    return text, genre, year, author, score


# Create output file
if not os.path.isfile(OUTPUT):
    with open(OUTPUT, "w") as output:
        output.write(HEADER)


for page_index in range(1, 501):
    review_urls = get_review_links(page_index)

    # Sleep for 0-3 seconds to avoid scraping time out
    time.sleep(random() * 3)

    if review_urls is None:
        continue

    for url in review_urls:
        if url in links:
            print(f"Skipping {url}")
            continue

        print(f"Reading {url}")

        try:
            info = get_review_info(url)
        except IndexError:
            links.add(url)
            print("Information unavailable")
            continue

        # Sleep for 0-3 seconds to avoid scraping time out
        time.sleep(random() * 3)

        if info is None:
            continue

        text, genre, year, author, score = info

        # Create output file
        with open(OUTPUT, "a") as output:
            output.write(f'"{text}";{genre};{year};{author};{score}\n')

        links.add(url)

        with open("links.py", "w") as links_file:
            links_file.write(f"links = {links}")


# pprint(review_urls)
