
import numpy as np
import pandas as pd
import pickle

import bs4 as bs
import urllib.request
import json
from bs4 import BeautifulSoup
import requests
import re
from collections import Counter
import http.client as http

import MySQLdb, pickle
from sqlalchemy import create_engine

# Create a data frame to store crawling data
df = pd.DataFrame(columns = ['year', 'title','brand','model','miles','exterior_color','interior_color','transmission','drivetrain','review_no','price'])

# Getting data from cars.com
for page in range(0,50):
    # Cars.com URL
    url = 'https://www.cars.com/for-sale/searchresults.action/?page='+str(page)+'&perPage=100&searchSource=PAGINATION&shippable-dealers-checkbox=true&sort=relevance&stkTypId=28881&zc=30309&localVehicles=false'  
    
    try:
        # Requesting data 
        sauce = urllib.request.urlopen(url).read()
        
    except (http.IncompleteRead) as e:
        sauce = e.partial
    
    # Parsing data with lxml
    soup = bs.BeautifulSoup(sauce, 'lxml')
    
    # All of the data comes with listing-row__details as the class name
    specificSoup = soup.find_all('div', class_='listing-row__details')

    
    # Put the imported data in the data frame
    for div in specificSoup:
#         print(div)
        
        # Put information about the name of the car in the name variable
        try:
            name_index = div.find('h2', {'class' :'listing-row__title'}).text
#           print(name_index)
        
            name = name_index.split("\n")[1]
#           print(name)
        
            # Get only the car's year out of the car information in the name variable
            year_index = re.findall('[0-9]{4}',name)[0:1]
            year = year_index[0]
#           print(year)

            # Get only the car's title out of the car information in the name variable
            title_index = name.split(" ")[29:34]
            title = " ".join(title_index)
#           print(title)

            # Get the car's brand out of the car information in the title variable
            brand = title.split(" ")[0]
#           print(brand)
        
            # If there hasn't model information, model will be as a brand
            try:
                model = title.split(" ")[1]
            except:
                model = brand

            # The miles of the car 
            mile_index = div.find('span', {'class' : 'listing-row__mileage'}).text       
            miles = mile_index.split("\n")[1].strip()
            regex = re.compile("\d+")
            miles = regex.findall(miles) 
            miles = ''.join(miles)
            miles = miles.strip()
        
            if miles == "":
                miles = 0
            else:
                miles

            # Exterior color
            exterior_color = div.find('ul', {'class' : 'listing-row__meta'}).text
            try:
                exterior_color = re.sub('\n', ' ',exterior_color).split(" ")[45]
            except:
                exterior_color = 'black'

    #         print(exterior_color)

            # Interior color
            interior_color = div.find('ul', {'class' : 'listing-row__meta'}).text
            try:
                interior_color = re.sub('\n', ' ',interior_color).split(" ")[119]
            except:
                interior_color = "black"
    #         print(interior_color)

            # Transmission type
            transmission = div.find('ul', {'class' : 'listing-row__meta'})
            try:
                transmission = list(transmission)[5].text.split(" ")[40]
                transmission = re.sub('\n', ' ',transmission)
            except:
                transmission = "6-speed"


            # Drivetrain type
            drivetrain = div.find('ul', {'class' : 'listing-row__meta'})
            try:
                drivetrain = list(drivetrain)[7].text.split(" ")[40]
                drivetrain = re.sub('\n', ' ',drivetrain)
            except: 
                drivetrain = 'fwd'
            if drivetrain == 'rear wheel drive':
                drivetrain = 'rwd'
            elif drivetrain == 'front wheel drive':
                drivetrain = 'fwd'
            elif drivetrain == 'Unknown':
                drivetrain = 'fwd'
            elif drivetrain == 'all wheel drive':
                drivetrain = '4wd'
            elif drivetrain == '4x4/4-wheel':
                drivetrain = '4wd'           
            
        # Number of star
#         if div.find('div',{'class' : 'dealer-rating-stars'}) == None:
#             star = 0
#         else:
#             star_index =div.find('div',{'class' : 'dealer-rating-stars'}).text
#             print(star_index)
#             star = star_index.split(" ")[40]
#             regex = re.compile("\d")
#             star = regex.findall(star)[0] 

             # Number of review
            if div.find('span',{'class' : 'listing-row__review-number'}) == None:
                review_no = 0
            else:
                review_index =div.find('span',{'class' : 'listing-row__review-number'}).text
                review_no = re.sub('\n', '',review_index.split(" ")[1])
                try:
                    review_no = re.sub('[()]', '',review_no)
                except:
                    review_no = review_no
    #             print(review_no)

            # Car price
            if div.find('span', {'class' : 'listing-row__price'}) == None:
                price = 0
            else:
                price_index = div.find('span', {'class' : 'listing-row__price'}).text
                price = price_index.split("\n")[1]
                regex = re.compile("\d")
                price = ''.join(regex.findall(price))
    #         print(price)


            # Entering crawled data into a data frame
            data = { 
                    'year' : year,
                    'title' : title.lower(),
                    'brand': brand.lower(),
                    'model': model.lower(),
                    'miles' : miles,
                    'exterior_color' : exterior_color.lower(),
                    'interior_color' : interior_color.lower(),
                    'transmission' : transmission.lower(),
                    'drivetrain' : drivetrain.lower(),
    #                 'star': star,
                    'review_no' : review_no,
                    'price': price,
                        }


            df.loc[len(df)] = data
        except:
            continue
            

# Exclude prices and non-branded data
df = df[df["price"] != ""]
df = df[df["brand"] != ""]

# Transforming data for data processing
df["year"] = df["year"].astype('int')
df["miles"] = df["miles"].astype('int')
# df["star"] = df["star"].astype('int')
df["review_no"] = df["review_no"].astype('int')
df["price"] = df["price"].astype('int')

### Put Crawled data into Database (MySQL) at Amazon web service cloud

# Load pickle file as database password
pw = pickle.load(open('./Flask/models/pw.plk','rb'))

# Saving data to the database(MySQL at Amazon Web Service Cloud )
engine = create_engine("mysql+mysqldb://root:" + pw + "@ec2-3-133-82-223.us-east-2.compute.amazonaws.com/car", pool_pre_ping=True)
df.to_sql(name="car", con=engine, if_exists='replace')
