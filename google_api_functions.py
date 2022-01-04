# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 15:54:11 2021

@author: crocs
"""

#import libraries:
import time
import pandas as pd
import googlemaps 
import random

#global variable
loc_list =[]

#My API_Key:
API_Key = "AIzaSyDpy1uw8_RvkLGFEGEydm1Yon_1fMPIZhM"

#Running googlemaps key:
map_client = googlemaps.Client(API_Key)

#Function to get places:
def get_place_info(location_name):
    try:
        response = map_client.places(query=location_name)
        results = response.get("results")
        return results 

    except:
        print("could not find")
        return None
 
#Ask the user to input a place address or city, searching the input on the get_place_info function:
result_list = get_place_info(input("search for a place/address/city in Portugal: "))


#Function to get the longitude and latitude of the place we chose in result_list:    
def get_latlog(result_list):
    locations_data = []
    lat_log = []
    final_latlog = []
    for information in result_list[0].values():
        locations_data.append(information)
    
    for info_loc in locations_data[2].values():
        lat_log.append(info_loc)
        
    for lat_log_values in lat_log[0].values():
        final_latlog.append(lat_log_values)
    
    # put the lat and lot in the list
    loc_dict = {'lat': final_latlog[0], 'long': final_latlog[1]}
    loc_list.append(loc_dict)

    return final_latlog

lati_logi_info = get_latlog(result_list)


"""Next we will Search for restaurants that are in a X meter distance 
from the place we chose, by getting the latitude and longitude from
get_latlog function: """

def restaurants_nearby(lati_logi_info):
    map_client = googlemaps.Client(API_Key)
    lat_log = (lati_logi_info[0],lati_logi_info[1])
    search_string = input("what kind of food would you like to eat there?")
    distance = input("What is your radius distance in meters?")
    while int(distance) > 2000:
            print("Ohh, don't walk that much, choose a distance inferior of 2000 m")
            distance = input("What is your radius distance in meters?")   
    business_list = []

    response = map_client.places_nearby(
    location = lat_log,
    keyword = search_string,
    type = "restaurant",
    radius = distance,
    )

    business_list.extend(response.get("results"))
    next_page_token = response.get("next_page_token")

    while next_page_token:
        time.sleep(random.random()+2)
        response = map_client.places_nearby(
        location = lat_log,
        keyword = search_string,
        type = "restaurant",
        radius = distance,
        page_token = next_page_token
    )
        business_list.extend(response.get("results"))
        next_page_token = response.get("next_page_token")
    
    return business_list

#Display maps_df table:
maps_df = pd.DataFrame(restaurants_nearby(lati_logi_info))
maps_df["url"] = "https://google.com/maps/place/?q=place_id:" + maps_df["place_id"]



#######Now the functions for DataFrame filtering and get the values:
    
#Read the zoomato csv with all values scraped:
zomato_df = pd.read_csv(r"lisbon_list_final.csv")


"""this function grabs both dataframes and drops the unwanted tables and any duplicate if there are any"""

def treating_dataframes(maps_df, zomato_df):
    merged_df = pd.merge(maps_df, zomato_df, how='inner', left_on = 'name', right_on = 'name')
    
    merged_df["price_per_person"]= merged_df["price"].astype(float) / 2
    
    filtered_table = merged_df.drop(labels= ['business_status', 'geometry', 'icon',
       'icon_background_color', 'icon_mask_base_uri','opening_hours',
       'photos', 'place_id', 'plus_code','reference', 'scope',
       'types', 'url_x', 'url_y',], axis=1).drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False)
    return filtered_table

treating_dataframes(maps_df, zomato_df)

"""this function let's users decide which restaurant they want based on:
1st - price range [1 to 4]
2nd - sort by highest rating

After it, will ask to input the name of the restaurant based on their parameters they chose
After it, it will get the price per person and deduct on their travel budget"""

budget = float(input("How much money do you have to visit all around in Lisbon?"))
def filtering_with_inputs(filtered_table):
    global budget
    price_range = input("From 1 to 4 choose a price range. Being 1 the cheapest and 4 the most expensive:")
    while float(price_range)  not in [1.0,2.0,3.0,4.0]:
            print("Choose a number from 1 to 4")
            price_range = input("From 1 to 4 choose a price range. Being 1 the cheapest and 4 the most expensive:")   
    #filtered_table[filtered_table["price_level"] == float(price_range)].sort_values(by='rating', ascending=False)
    print(filtered_table[filtered_table["price_level"] == float(price_range)].sort_values(by='rating', ascending=False))
    restaurant_choice = input("From the table you have choose the restaurant and write it here:  ")
    
    restaurant_price = filtered_table[filtered_table["name"] == restaurant_choice]
    #print(type(restaurant_price))
    difference = budget - float(restaurant_price["price_per_person"])
    budget = difference
    return print("you still have:", difference)

filtering_with_inputs(treating_dataframes(maps_df, zomato_df))