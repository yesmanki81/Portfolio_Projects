import lxml
import re
from lxml.html import fromstring, tostring
import requests
import pandas as pd
import pickle

#SQL
import config
import mysql.connector
from sqlalchemy import create_engine



def main():
    # Create a data frame to store crawling data
    global df
    df = pd.DataFrame(
        columns=['listing_id', 'title', 'year', 'brand', 'model', 'deal', 'price', 'miles', 'carfax', 'dealer'])

    # Getting data from Cars.com
    page = 50
    loop_url(page)
    exclude_non_value(df)


def loop_url(page):
    for page in range(1, int(page) + 1):
        url = 'https://www.cars.com/shopping/results/?page=' + str(
            page) + '&page_size=100&list_price_max=&makes[]=&maximum_distance=all&models[]=&stock_type=used&zip=22031'
        response = requests.get(url)
        scrape_news_list_page(response)


def scrape_news_list_page(response):
    root = fromstring(response.content)
    for info in root.xpath(
            '//div[@id="vehicle-cards-container"]/div[@class="vehicle-card   "]/div[@class="vehicle-card-main js-gallery-click-card"]'):
        listing_id = extract_listing_id(info)
        title = extract_title(info)
        year = extract_year(title)
        brand = extract_brand(title)
        model = extract_model(title)

        deal = extract_deal(info)
        price = extract_price(info)
        miles = extract_mileage(info)
        carfax = extract_carfax(info)
        dealer = extract_dealer(info)

        # Entering crawled data into a data frame
        data = {
            'listing_id': listing_id,
            'title': title,
            'year': int(year),
            'brand': brand.upper(),
            'model': model.upper(),
            'deal': deal.upper(),
            'price': int(price),
            'miles': int(miles),
            'carfax': carfax.upper(),
            'dealer': dealer.upper()
        }
        df.loc[len(df)] = data


def extract_listing_id(info):
    try:
        listing_id = info.xpath('./div[@class="contact-buttons"]')
        listing_id = listing_id[0].get('id')
        return listing_id
    except:
        listing_id = ""
        return listing_id


def extract_deal(info):
    try:
        deal = info.xpath(
            './div[@class="vehicle-details"]/div[@class="vehicle-badging"]/div/span[@class="sds-badge__label"]')
        deal = deal[0].text
        return deal
    except:
        deal = ""
        return deal


def exclude_non_value(df):
    # Exclude prices and non-branded data
    df = df[df["listing_id"] != ""]
    df = df[df["year"] != ""]
    df = df[df["brand"] != ""]
    df = df[df["model"] != ""]
    df = df[df["price"] != 0]
    df = df[df["miles"] != 0]
    return df


def extract_title(info):
    title = info.xpath('./div[@class="vehicle-details"]/a/h2')
    title = title[0].text
    return title


def extract_brand(title):
    brand = title.split(" ")[1]
    return brand


def extract_model(title):
    model = title.split(" ")[2:3]
    model = " ".join(model)
    return model


def extract_year(title):
    p = re.compile('^[0-9]+')
    year = p.match(title).group()
    return year


def extract_price(info):
    price = info.xpath(
        './div[@class="vehicle-details"]/div[@class="price-section price-section-vehicle-card"]/span[@class="primary-price"]')
    price = price[0].text
    price = re.sub(r'[^0-9]', '', price)
    try:
        price = int(price)
        return price
    except:
        price = 0
        return price


def extract_mileage(info):
    try:
        miles = info.xpath('./div[@class="vehicle-details"]/div[@class="mileage"]')
        miles = miles[0].text
        miles = re.sub(r'[^0-9]', '', miles)
        return miles
    except:
        miles = 0
        return miles


def extract_carfax(info):
    try:
        carfax = info.xpath('./div[@class="vehicle-details"]/div[@class="vehicle-links external-links"]/div/a')
        carfax = carfax[0].get('aria-label')
        carfax = carfax.split(',')[0]
        return carfax
    except:
        carfax = "NO CARFAX"
        return carfax


def extract_dealer(info):
    try:
        dealer = info.xpath(
            './div[@class="vehicle-details"]/div[@class="vehicle-dealer"]/div[@class="dealer-name"]/strong')
        dealer = dealer[0].text
        return dealer
    except:
        dealer = "NO DEALER"
        return dealer




def load_database(df):
    pw = pickle.load(open('./Flask/models/pw.plk', 'rb'))

    engine = create_engine("mysql+mysqlconnector://root:" + pw + "@cars.c3d1kxjihbmh.us-east-1.rds.amazonaws.com/cars", pool_pre_ping=True)
    df.to_sql(name="used_car", con=engine, if_exists='append')



# 스크래핑 시작
if __name__ == "__main__":
    main()
    print(df)
    load_database(df)




