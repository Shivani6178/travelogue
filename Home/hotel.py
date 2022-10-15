
import geocoder
import time
import asyncio
import aiohttp

url = "https://apidojo-booking-v1.p.rapidapi.com/"

headers = {
            "X-RapidAPI-Key": "40f6cfd24cmsh7933add03995607p1245eejsnfaa578e0e229",
            "X-RapidAPI-Host": "apidojo-booking-v1.p.rapidapi.com"
    }

async def locationgeocode(location):
    location_code = geocoder.osm(location)
    async with aiohttp.ClientSession() as session:
        endpoint = f'properties/list-by-map'
        querystring = {
            "arrival_date": "2022-11-11",
            "departure_date": "2022-11-14",
            "room_qty":"1",
            "guest_qty":"1",
            "bbox": f'{location_code.southwest[0]},{location_code.northeast[0]},{location_code.southwest[1]},{location_code.northeast[0]}',
            "search_id":"none",
            "children_age":"11,5",
            "price_filter_currencycode":"INR",
            "categories_filter":"class::1,class::2,class::3",
            "languagecode":"en-us",
            "travel_purpose":"leisure",
            "children_qty":"2",
            "order_by":"popularity"}
        response = await session.get(url+endpoint, headers=headers, params=querystring)
        result = await response.json()
        search_id = result['search_id']
        hotel_id = []
        for i in range(len(result['result'])):
            hotel_id.append(result['result'][i]['hotel_id'])
                
        await getdetails(hotel_id, search_id)
    # print(hotel_id)
    
    
# ============= Get details api calling===========
async def getdetails(hotel_id, search_id):
    async with aiohttp.ClientSession() as session:
        for i in range(len(hotel_id)):
            endpoint = "properties/detail"
            querystring1= {
                "hotel_id": hotel_id[i],
                "search_id": search_id,
                "departure_date": "2022-11-14",
                "arrival_date": "2022-11-11",
                "rec_guest_qty":"2",
                "rec_room_qty":"1",
                "recommend_for":"3",
                "languagecode":"en-us",
                "currency_code":"USD",
                "units":"imperial"}

            response = await session.get(url+endpoint, headers=headers, params=querystring1)
            result = await response.json()
            print(result[0]['hotel_name'])


# 32.697919607162476
# 24.080922603607178