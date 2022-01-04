BEGIN = {
    "counter" : 0,
    "loc_list": [],
    'budget' : 0,
    'people': 0,
    'plan_list': []
}

#import libraries:
import time
import pandas as pd
import googlemaps 
import random
from math import radians, cos, sin, asin, sqrt
from IPython.display import display


#My API_Key:
API_Key = "AIzaSyDpy1uw8_RvkLGFEGEydm1Yon_1fMPIZhM"

#Running googlemaps key:
map_client = googlemaps.Client(API_Key)


# function to start
def start_game():
    """
    This function starts the program by asking for the number of people,budget, and starting point.
    And it keeps on playing the round to ask where the user wants to go until it reaches 3 times.
    If it reached 3 rounds, the program finished and print the location the user chose and the 
    amount of money spent on each place (restaurant price & gas price).
    """
    if(BEGIN["counter"] == 0):
        # ask for how many people are coming in the trip
        BEGIN['people'] = float(input("""
                     You are going on a journey to Lisbon!
                     You may go to 3 typical Lisbon places, each in a different area.
                     How many people are coming?
                     """))
        # ask for the budget
        BEGIN['budget'] = float(input("""
                     How much money do you have to visit all around in Lisbon?
                     """))
        # ask for the starting point
        starting_point = input("""
                     Where will be your starting point?
                     """)
        # call function to store the starting point
        append_starting_point(starting_point)
    # if the round is less than 3 times
    # ask for the location to go
    elif(BEGIN["counter"] <= 3):
        location_name = input("""
                     Search for a place/address/city in Portugal:  
                     """)  
        get_place_info(location_name)
    # if it's already 3 rounds
    # the program finished
    elif( BEGIN["counter"] == 4):
        print("""
                You finished planning your trip!
                """)
        print(pd.DataFrame(BEGIN['plan_list']))


def append_starting_point(starting_point):
    """
    Function to append starting point to BEGIN["loc_list"].
    Get the latitude and longitude information of the starting place using
    Google Maps API and store the information in a dictionary,
    so we can calculate the distance to the next place.
    """
    response = map_client.places(query=starting_point)
    results = response.get("results")    
    locations_data = []
    lat_log = []
    final_latlog = []
    for information in results[0].values():
        locations_data.append(information)
    
    for info_loc in locations_data[2].values():
        lat_log.append(info_loc)
        
    for lat_log_values in lat_log[0].values():
        final_latlog.append(lat_log_values)
    
    # put the lat and lot in the list
    loc_dict = {'lat': final_latlog[0], 'long': final_latlog[1]}
    BEGIN['loc_list'].append(loc_dict)    

    # increase the counter
    BEGIN['counter'] +=1  
    start_game() 


def get_place_info(location_name):
    """
    Function to get the place that is inputted by the user, making sure
    the place exists in Google Map.
    Then call the function to get the latitude and longitude of the place.
    """
    try:
        response = map_client.places(query=location_name)
        results = response.get("results")
        # increase the counter
        BEGIN['counter'] +=1
        get_latlog(results)

    except:
        print("""
              We couldn't find the place you were looking for, type it again please!""")
        # if the place does not exists, we decrease the counter because the round does not finish
        BEGIN['counter'] -=1
        return start_game()
 
    
def get_latlog(result_list):
    """
    Function to get the longitude and latitude of the place 
    inputted by the user in the function get_place_info.
    Store the lat and long in a dictionary, so we can calculate the distance 
    from the previous place.
    Then call the function restaurant_nearby to get the restaurant near the area.
    """
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
    BEGIN['loc_list'].append(loc_dict)
    # call function
    restaurants_nearby(final_latlog)


def restaurants_nearby(lati_logi_info):
    """
    This function ask the user what kind of food they would like to eat, 
    and then call the Google Map API to get the restaurant 5km away 
    from the lat and long of the place the user chose.
    """
    map_client = googlemaps.Client(API_Key)
    lat_log = (lati_logi_info[0],lati_logi_info[1])
    search_string = input("""
                     What kind of food would you like to eat there?
                    """)
    distance = 5000  
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
    
    #Turning the result we got from Google API into a dataFrame:
    maps_df = pd.DataFrame(business_list)
    maps_df["url"] = "https://google.com/maps/place/?q=place_id:" + maps_df["place_id"]

    #Read the zoomato csv with all values scraped:
    zomato_df = pd.read_csv(r"zomato_data.csv")

    #Call the function treating_dataframes that merge zomato_df and mo 
    treating_dataframes(maps_df, zomato_df)


def merging_zomatos(zomato_price_df,zomato_address_df):
    """
    Once we get the data from the API, we match the name of the restaurant
    with the data that we webscrap from zomato.
    """
    merged_zomato_df = pd.merge(zomato_price_df, zomato_address_df, how='inner', left_on = 'name', right_on = 'Name')
    merged_zomato = merged_zomato_df.drop(["Unnamed: 0_x", "Unnamed: 0_y", "url"],axis=1)
    return merged_zomato

def treating_dataframes(maps_df, zomato_df):
    """
    This function clean the data that we have, from the Google Maps API and the zomato webscrap
    and put it in a dataframe to show the user, sorted by the highest rated in zomato.
    """

    #Read the zomato csv with all values scraped:
    zomato_price_df = pd.read_csv(r"lisbon_list_final.csv")
    #Treating the data, merging zomato tables, drop unwanted columns and drop any existing duplicate:
    merged_zomato=merging_zomatos(zomato_price_df, zomato_df)
    merged_df = pd.merge(maps_df, merged_zomato, how='inner', left_on = 'name', right_on = 'Name')
    merged_df["price"] = merged_df["price"].astype(float)
    merged_df["price_per_person"]= merged_df["price"] / 2
    filtered_table = merged_df.drop(labels= ['business_status', 'geometry', 'icon',
       'icon_background_color', 'icon_mask_base_uri','opening_hours',
       'photos', 'place_id', 'plus_code','reference', 'scope',
       'types',"vicinity", 'url', 'Address', 'Location', 'permanently_closed', 'Name', 'name_y', 'price'], axis=1).drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False)

    # sort by zomato's rating
    display(filtered_table.sort_values(by= 'Ratings', ascending= False))
    filtering_with_inputs(filtered_table)


def filtering_with_inputs(filtered_table):
    """
    This function let the user choose the restaurant they want from the dataframe 
    that we show, making sure the name matches.
    Then calculate the price of the restaurant (no. of people * average restaurang price)
    and call the function to calculate the gas price.
    Reducing the budget by the total cost of both.
    """
    restaurant_choice = input("""
                    From the table you have choose the restaurant and write it here:  
                    """)
    bag_of_restaurants_names = filtered_table['name_x'].tolist()
    while str(restaurant_choice) not in bag_of_restaurants_names:
        print("\n Ohh, you probably mispelled your restaurant, type it again please:")
        restaurant_choice = input("From the table you have choose the restaurant and write it here:  ") 

    restaurant_price = filtered_table[filtered_table["name_x"] == str(restaurant_choice)]
    print("\n You spent ",float(restaurant_price["price_per_person"]* BEGIN['people']),"€ on your meal and ", get_price_per_distance(BEGIN['loc_list']),"€ by driving from your previus point to the restaurant" )
    total_price = (float(restaurant_price["price_per_person"])* BEGIN['people']) + get_price_per_distance(BEGIN['loc_list'])
    difference = (BEGIN['budget'] - (float(restaurant_price["price_per_person"])* BEGIN['people'])) - get_price_per_distance(BEGIN['loc_list'])
    BEGIN['budget'] = difference
   
    #If you don't have enough budget it will break, if you can it will start again:
    if BEGIN['budget'] < (float(restaurant_price["price_per_person"]) * BEGIN['people']):
        print("""
                    Uppps. You do not have enough money to eat here!
                """)
        filtering_with_inputs(filtered_table)
    else:
        BEGIN['budget'] = difference
        print("""
                    You still have: """, difference)
        plan_dict ={'Restaurant Name': restaurant_choice, 'Total Price': total_price}
        BEGIN['plan_list'].append(plan_dict)

    return start_game()


def get_price_per_distance(list_ini):
    """
    This funtion calculate the gas price by considering the latitude and longitude
    of one point and another
    """
    for dictio in list_ini[-2: ]:
        if dictio == list_ini[-1]:
            lon2 = list(list_ini[-1].values())[1]
            lat2 = list(list_ini[-1].values())[0]
        else : 
            lon1 = list(list_ini[-2].values())[1]
            lat1 = list(list_ini[-2].values())[0]
  
    lon1, lat1, lon2, lat2 = map(radians, [lon1,lat1,lon2,lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2 
    c = 2 * asin(sqrt(a)) 

    price_per_km = 1.744 * 0.7
    ratio_increment = 1.5
    # Radius of earth in kilometers is 6371
    price_distance = round(6371* c * price_per_km *ratio_increment, 2)

    return price_distance


start_game()