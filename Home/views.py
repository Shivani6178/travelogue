
import email
from os import name
from django.shortcuts import render, redirect
from django.http import HttpResponse,HttpResponseRedirect
from .forms import CreateUserCustomer
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.models import Group, User
from .email import send_account_activation_email
from .models import *
import uuid
import folium
import geocoder
import requests
import geocoder
import stripe
from django.conf import settings

# This is your test secret API key.
stripe.api_key = settings.STRIPE_SECRET_KEY
# from .hotel import locationgeocode
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# @unauthenticated_user
# @csrf_exempt
def register(request):
        form = CreateUserCustomer()
        if request.method == 'POST':
            form = CreateUserCustomer(request.POST)
            email = request.POST.get('email')
            user_obj = User.objects.filter(email = email)
            print(user_obj)
            if user_obj.exists():
                messages.warning(request,'Email is already taken!')
                return HttpResponseRedirect(request.path_info)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                group = Group.objects.get(name = 'customer')
                user.groups.add(group)
                email_token = str(uuid.uuid4())
                CustomerProfile.objects.create(user = user, email_token = email_token)
                print(email)
                try:
                    send_account_activation_email(email, email_token)
                except Exception as e:
                    print(e)
                messages.success(request, username + "! Email has been sent to your mail. Please verify before logging in!")
                return redirect('login/')
        context = {'form': form}
        return render(request, 'register.html', context)   

def verify(request, email_token):
    try:
        profile_obj = CustomerProfile.objects.filter(email_token = email_token).first()
        if profile_obj:
            profile_obj.is_email_verified = True
            profile_obj.save()
            messages.success(request, "Your account has been verified!")
            return redirect('/login/')
        else:
            return redirect('error/')
    except Exception as e:
        print(e)

def error(request):
    return render(request, 'error.html')

def loginUser(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(email = email).first()
        if not user_obj:
            messages.warning(request, "User not found. Please create an account before loggin in!")
            return HttpResponseRedirect(request.path_info)
        
        profile_obj = CustomerProfile.objects.filter(user = user_obj).first()
        print(profile_obj.is_email_verified)
        if not profile_obj.is_email_verified:
            messages.warning(request, "Please verify your account before logging in!")
            return HttpResponseRedirect(request.path_info)
        else:
            # print(email)
            # print(password)
            user = authenticate(request, username = user_obj.username, password = password)
            # print(user)
            if user is not None:
                login(request, user)
                # print(str(user_obj.id))
                return redirect('/index/'+ str(user_obj.id))
            else: 
                messages.info(request, "Username or password is Incorrect!")
                return HttpResponseRedirect(request.path_info)
    context = {}
    return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('/login/')  

@login_required(login_url='loginUser')
@allowed_users(allowed_roles=['customer','admin']) 
def index(request, user):
    if user:
        customer = CustomerProfile.objects.get(user = user)
        orders = customer.bookings_set.all()
    elif not user:
        messages.info(request, "Page not found for this User!")
        return redirect('/error/')
    context = {'customer': customer, 'orders': orders, 'navbar': 'home'}
    return render(request, 'home.html', context)

@login_required(login_url='loginUser')
def home(request):
    context = {'navbar': 'home'}
    return render(request, 'home.html', context)

@login_required(login_url='loginUser')
def hotel(request):
    location = request.POST.get('placename')
    check_in = request.POST.get('check_in')
    check_out = request.POST.get('check_out')
    results = []
    try:
        search_id = None
        if location:    
            response = {
                            "result": [
                            {
                                "review_score": 6.1,
                                "hotel_id": 1173150,
                                "distance": "0.88",
                                "extended": 0,
                                "checkout": {
                                "from": "",
                                "until": "12:00"
                                },
                                "url": "https://www.booking.com/hotel/in/balwas.html",
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "localized_area": "null",
                                    "unit_type_id": 9
                                }
                                },
                                "hotel_has_vb_boost": 0,
                                "city_name_en": "Mumbai",
                                "main_photo_id": 373263707,
                                "cc1": "in",
                                "urgency_room_msg": "Deluxe Double Room",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "is_city_center": 1,
                                "district": "South Mumbai",
                                "is_no_prepayment_block": 1,
                                "districts": "2379,17337",
                                "hotel_name": "Hotel Balwas",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "native_ads_tracking": "",
                                "is_geo_rate": "",
                                "default_language": "xu",
                                "review_nr": 8,
                                "hotel_name_trans": "Hotel Balwas",
                                "class": 2,
                                "city": "Mumbai",
                                "soldout": 0,
                                "hotel_include_breakfast": 0,
                                "accommodation_type_name": "Hotels",
                                "longitude": 72.8215692649429,
                                "min_total_price": 21546,
                                "hotel_facilities": "109,48,15,425,419,421,25,222,423,158,305,163,8,23,107,142,5,47,418,44,96,64,424,185,22,53,304,129,134",
                                "cc_required": 1,
                                "wishlist_count": 0,
                                "mobile_discount_percentage": 2394,
                                "latitude": 18.961454675844,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "in_best_district": 0,
                                "review_score_word": "Pleasant",
                                "badges": [
                                {
                                    "text": "Mobile-only price",
                                    "id": "mobile_price",
                                    "badge_variant": "constructive"
                                }
                                ],
                                "city_trans": "Mumbai",
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "countrycode": "in",
                                "price_breakdown": {
                                "has_tax_exceptions": 0,
                                "has_incalculable_charges": 0,
                                "currency": "INR",
                                "sum_excluded_raw": 2585.52,
                                "has_fine_print_charges": 0,
                                "all_inclusive_price": 24131.52,
                                "gross_price": "21546.00"
                                },
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/373263707.jpg?k=6a433c2c1199b61afcfb8b8a97ca8cd3043530e5613f89142f2281c62d70eb52&o=",
                                "preferred": 1,
                                "currency_code": "INR",
                                "checkin": {
                                "from": "12:00",
                                "until": ""
                                },
                                "preferred_plus": 0,
                                "district_id": 2379,
                                "accommodation_type": 204,
                                "distance_to_cc": "0.90",
                                "deals": {
                                "deal_attributes": {},
                                "deals_available": {},
                                "deal_events_killswitch": 0
                                },
                                "currencycode": "INR",
                                "selected_review_topic": "null",
                                "id": "property_card_1173150",
                                "review_recommendation": "",
                                "is_smart_deal": 0,
                                "cant_book": 0,
                                "country_trans": "India",
                                "city_in_trans": "in Mumbai",
                                "default_wishlist_name": "Mumbai",
                                "zip": "400007",
                                "block_ids": [
                                "117315004_218048506_2_2_0"
                                ],
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "address_trans": "323, Opposite Super Cinema, 12th Lane, Grant Road",
                                "type": "property_card",
                                "is_mobile_deal": 1,
                                "native_ads_cpc": 0,
                                "address": "323, Opposite Super Cinema, 12th Lane, Grant Road",
                                "is_free_cancellable": 1
                            },
                            {
                                "checkin": {
                                "until": "",
                                "from": "14:00"
                                },
                                "preferred_plus": 0,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/32810813.jpg?k=7b5f861c6aad4e51ef13e55c8b68ac945cebdf77aeca84d9c2798bb9af46d24d&o=",
                                "currency_code": "INR",
                                "preferred": 1,
                                "price_breakdown": {
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "has_incalculable_charges": 0,
                                "gross_price": "132525.00",
                                "all_inclusive_price": 156379.5,
                                "has_fine_print_charges": 0,
                                "sum_excluded_raw": "23854.50"
                                },
                                "countrycode": "in",
                                "selected_review_topic": "null",
                                "distance_to_cc": "4.60",
                                "currencycode": "INR",
                                "deals": {
                                "deal_events_killswitch": 0,
                                "deals_available": {},
                                "deal_attributes": {}
                                },
                                "district_id": 2379,
                                "accommodation_type": 204,
                                "hotel_facilities": "236,43,234,78,11,46,119,494,496,3,221,402,450,231,16,235,233,493,73,48,495,491,57,257,400,452,140,81,226,76,506,6,229,21,433,463,134,408,461,111,407,486,28,64,484,457,458,426,22,219,424,5,436,161,23,107,163,301,305,133,464,54,124,485,49,423,158,239,425,421,184,459,420,14,7,27,243,96,227,228,422,256,203,176,8,205,462,238,44,244,237,159,75,110,460,449,109,253,91,17,403,232,468,62,117,467,405,444,490,446,104,492,453,2,53,127,230,455,451,220,52,20,404,58,445,418,47,51,488,487,454,456,25",
                                "cc_required": 1,
                                "min_total_price": 132525,
                                "longitude": 72.8205800056458,
                                "soldout": 0,
                                "hotel_include_breakfast": 1,
                                "accommodation_type_name": "Hotels",
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "review_score_word": "Excellent",
                                "in_best_district": 0,
                                "badges": [
                                {
                                    "text": "Mobile-only price",
                                    "id": "mobile_price",
                                    "badge_variant": "constructive"
                                }
                                ],
                                "city_trans": "Mumbai",
                                "latitude": 18.9276509091609,
                                "mobile_discount_percentage": 14725,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "wishlist_count": 0,
                                "is_mobile_deal": 1,
                                "type": "property_card",
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "address_trans": "Nariman Point",
                                "is_free_cancellable": 1,
                                "address": "Nariman Point",
                                "native_ads_cpc": 0,
                                "is_smart_deal": 0,
                                "cant_book": 0,
                                "id": "property_card_78794",
                                "review_recommendation": "",
                                "zip": "400021",
                                "block_ids": [
                                "7879404_356687655_1_1_0"
                                ],
                                "default_wishlist_name": "Mumbai",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 4,
                                    "localized_area": "null"
                                }
                                },
                                "has_swimming_pool": 1,
                                "checkout": {
                                "from": "",
                                "until": "12:00"
                                },
                                "url": "https://www.booking.com/hotel/in/trident-nariman-point.html",
                                "district": "South Mumbai",
                                "urgency_room_msg": "Premier Double or Twin Room with Ocean View",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "is_city_center": 1,
                                "main_photo_id": 32810813,
                                "city_name_en": "Mumbai",
                                "cc1": "in",
                                "hotel_has_vb_boost": 0,
                                "review_score": 8.9,
                                "extended": 0,
                                "distance": "4.60",
                                "hotel_id": 78794,
                                "default_language": "en",
                                "review_nr": 3611,
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "has_free_parking": 1,
                                "class": 5,
                                "city": "Mumbai",
                                "hotel_name_trans": "Trident Nariman Point",
                                "hotel_name": "Trident Nariman Point",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "districts": "2379,3447,17444",
                                "is_no_prepayment_block": 0
                            },
                            {
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "localized_area": "null",
                                    "unit_type_id": 7
                                }
                                },
                                "has_swimming_pool": 1,
                                "url": "https://www.booking.com/hotel/in/the-taj-mahal-palace-tower.html",
                                "checkout": {
                                "from": "",
                                "until": "11:00"
                                },
                                "urgency_room_msg": "Deluxe Room City View King Bed",
                                "is_city_center": 0,
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "district": "Colaba",
                                "hotel_has_vb_boost": 0,
                                "city_name_en": "Mumbai",
                                "main_photo_id": 31204963,
                                "cc1": "in",
                                "review_score": 8.9,
                                "distance": "5.49",
                                "extended": 0,
                                "hotel_id": 74717,
                                "default_language": "en",
                                "review_nr": 3872,
                                "native_ads_tracking": "",
                                "is_geo_rate": "",
                                "has_free_parking": 1,
                                "hotel_name_trans": "The Taj Mahal Tower Mumbai",
                                "class": 5,
                                "city": "Mumbai",
                                "hotel_name": "The Taj Mahal Tower Mumbai",
                                "class_is_estimated": 0,
                                "genius_discount_percentage": 0,
                                "is_no_prepayment_block": 0,
                                "districts": "3448,2379,17444",
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/31204963.jpg?k=90c11832231c37a814e9631123bd28820e8ad8cd983b78ad529ea139791653d1&o=",
                                "preferred": 1,
                                "currency_code": "INR",
                                "checkin": {
                                "from": "15:00",
                                "until": ""
                                },
                                "preferred_plus": 0,
                                "countrycode": "in",
                                "price_breakdown": {
                                "has_tax_exceptions": 0,
                                "has_incalculable_charges": 0,
                                "currency": "INR",
                                "all_inclusive_price": 216577.2,
                                "gross_price": "183540.00",
                                "sum_excluded_raw": "33037.20",
                                "has_fine_print_charges": 1
                                },
                                "distance_to_cc": "5.50",
                                "currencycode": "INR",
                                "deals": {
                                "deals_available": {},
                                "deal_attributes": {},
                                "deal_events_killswitch": 0
                                },
                                "selected_review_topic": "null",
                                "district_id": 3448,
                                "accommodation_type": 204,
                                "min_total_price": 183540,
                                "longitude": 72.8332896530628,
                                "hotel_facilities": "433,304,55,229,21,6,408,134,465,461,407,111,457,458,470,28,64,219,22,424,185,305,163,301,5,411,107,23,436,242,133,499,240,49,124,54,421,425,158,423,248,78,234,247,11,46,129,494,496,119,505,3,233,402,450,16,231,235,495,257,73,493,48,506,226,400,81,452,140,232,468,118,467,117,403,17,444,104,490,446,249,492,455,451,230,2,453,127,53,20,52,406,404,220,47,418,445,454,210,25,209,51,502,222,63,459,420,27,243,7,245,227,198,96,410,256,254,422,205,176,180,203,8,75,44,462,238,246,244,10,449,109,460,110,497,251,91,498,253",
                                "cc_required": 1,
                                "soldout": 0,
                                "hotel_include_breakfast": 1,
                                "accommodation_type_name": "Hotels",
                                "review_score_word": "Excellent",
                                "in_best_district": 0,
                                "city_trans": "Mumbai",
                                "badges": [],
                                "ufi": -2092174,
                                "children_not_allowed": 0,
                                "wishlist_count": 0,
                                "latitude": 18.9215006738599,
                                "mobile_discount_percentage": 0,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "type": "property_card",
                                "is_mobile_deal": 0,
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "address_trans": "Apollo Bunder",
                                "is_free_cancellable": 1,
                                "native_ads_cpc": 0,
                                "address": "Apollo Bunder",
                                "id": "property_card_74717",
                                "review_recommendation": "",
                                "is_smart_deal": 0,
                                "cant_book": 0,
                                "default_wishlist_name": "Mumbai",
                                "block_ids": [
                                "7471705_158036154_1_1_0"
                                ],
                                "zip": "400001",
                                "country_trans": "India",
                                "city_in_trans": "in Mumbai"
                            },
                            {
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "default_language": "en",
                                "review_nr": 341,
                                "class": 5,
                                "city": "Mumbai",
                                "hotel_name_trans": "InterContinental Marine Drive Mumbai, an IHG Hotel",
                                "has_free_parking": 1,
                                "districts": "3451,2379,17444",
                                "is_no_prepayment_block": 0,
                                "hotel_name": "InterContinental Marine Drive Mumbai, an IHG Hotel",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "has_swimming_pool": 1,
                                "url": "https://www.booking.com/hotel/in/intercontinental-marine-drive-mumbai.html",
                                "checkout": {
                                "until": "12:00",
                                "from": ""
                                },
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 7,
                                    "localized_area": "null"
                                }
                                },
                                "main_photo_id": 245805125,
                                "city_name_en": "Mumbai",
                                "cc1": "in",
                                "hotel_has_vb_boost": 0,
                                "district": "Churchgate",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "urgency_room_msg": "1 King Bed Classic Bay View Smoking",
                                "is_city_center": 0,
                                "review_score": 8.5,
                                "hotel_id": 237786,
                                "extended": 0,
                                "distance": "3.82",
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "address_trans": "135 Marine Drive",
                                "is_mobile_deal": 0,
                                "type": "property_card",
                                "address": "135 Marine Drive",
                                "native_ads_cpc": 0,
                                "is_free_cancellable": 1,
                                "is_smart_deal": 0,
                                "cant_book": 0,
                                "id": "property_card_237786",
                                "review_recommendation": "",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "zip": "400020",
                                "block_ids": [
                                "23778635_328517060_1_2_0"
                                ],
                                "default_wishlist_name": "Mumbai",
                                "price_breakdown": {
                                "all_inclusive_price": 160362,
                                "gross_price": "135900.00",
                                "sum_excluded_raw": "24462.00",
                                "has_fine_print_charges": 0,
                                "has_tax_exceptions": 0,
                                "has_incalculable_charges": 0,
                                "currency": "INR"
                                },
                                "countrycode": "in",
                                "preferred_plus": 0,
                                "checkin": {
                                "until": "",
                                "from": "14:00"
                                },
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/245805125.jpg?k=ede568d16b8d6c118467f6be0be00f7564d85888b2e5b57e7fa10a9dab91d1bf&o=",
                                "preferred": 1,
                                "currency_code": "INR",
                                "district_id": 3451,
                                "accommodation_type": 204,
                                "selected_review_topic": "null",
                                "distance_to_cc": "3.85",
                                "deals": {
                                "deals_available": {
                                    "has_preset": 1
                                },
                                "deal_events": [
                                    {
                                    "localized_description": "You’re getting a reduced rate because this property is offering a discount on stays between April 4 and September 30, 2022.",
                                    "preset_id": "null",
                                    "localized_name": "Getaway Deal",
                                    "icon_url": "https://summer_deal.com",
                                    "description_translation_tag": "deals_getaway22_customer_tooltip_ext",
                                    "disabled": 0,
                                    "icon_name": "percentage-circle",
                                    "name_translation_tag": "deals_getaway22_customer_label",
                                    "bg_color": "#FF8000",
                                    "text_color": "#FFFFFF",
                                    "code": 123,
                                    "discount_percentage": 40
                                    }
                                ],
                                "deal_attributes": {},
                                "deal_events_killswitch": 0
                                },
                                "currencycode": "INR",
                                "soldout": 0,
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 0,
                                "hotel_facilities": "176,180,203,8,205,44,462,246,244,75,460,110,15,449,109,253,497,91,251,420,459,245,7,198,96,422,409,160,256,80,220,20,406,52,404,445,418,101,443,47,209,488,51,502,487,454,25,210,456,17,468,467,117,401,104,490,446,492,249,2,453,127,53,455,451,402,450,16,142,73,493,48,491,257,400,140,452,81,506,419,43,78,247,46,129,11,494,496,440,3,439,5,23,107,411,161,436,163,301,305,133,499,464,485,124,54,240,49,423,158,421,425,21,250,6,433,304,55,463,134,408,465,461,470,486,484,64,457,458,219,22,426,424,185",
                                "cc_required": 1,
                                "longitude": 72.8240829706192,
                                "min_total_price": 135900,
                                "mobile_discount_percentage": 0,
                                "latitude": 18.9349375286069,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "wishlist_count": 0,
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "in_best_district": 0,
                                "review_score_word": "Very Good",
                                "city_trans": "Mumbai",
                                "badges": [
                                {
                                    "text": "Getaway Deal ",
                                    "badge_variant": "constructive",
                                    "id": "getaway_2021_deals"
                                }
                                ]
                            },
                            {
                                "is_mobile_deal": 0,
                                "type": "property_card",
                                "address_trans": "Marol Maroshi Road, Near Marol Metro Station, Andheri East, Mumbai-400059, India",
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "is_free_cancellable": 1,
                                "address": "Marol Maroshi Road, Near Marol Metro Station, Andheri East, Mumbai-400059, India",
                                "native_ads_cpc": 0,
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "review_recommendation": "",
                                "id": "property_card_6832186",
                                "block_ids": [
                                "683218601_279330376_3_42_0"
                                ],
                                "zip": "400059",
                                "default_wishlist_name": "Mumbai",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "preferred_plus": 0,
                                "checkin": {
                                "until": "",
                                "from": "15:00"
                                },
                                "currency_code": "INR",
                                "preferred": 1,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/331987485.jpg?k=b48275c360a3d5ccc3d043c7812f2a9314476ace203067eba112bc27421efd6c&o=",
                                "price_breakdown": {
                                "has_fine_print_charges": 0,
                                "sum_excluded_raw": "25110.00",
                                "gross_price": "139500.00",
                                "all_inclusive_price": 164610,
                                "has_incalculable_charges": 0,
                                "has_tax_exceptions": 0,
                                "currency": "INR"
                                },
                                "countrycode": "in",
                                "selected_review_topic": "null",
                                "currencycode": "INR",
                                "deals": {
                                "deal_events_killswitch": 0,
                                "deals_available": {},
                                "deal_attributes": {}
                                },
                                "distance_to_cc": "16.75",
                                "accommodation_type": 204,
                                "district_id": 3287,
                                "cc_required": 1,
                                "hotel_facilities": "490,446,104,467,143,17,451,455,453,2,53,127,492,443,47,445,441,418,52,406,20,454,192,456,210,25,51,209,488,487,222,502,243,7,241,14,420,459,160,422,96,159,75,44,462,10,244,205,203,176,8,497,91,253,449,109,110,460,15,134,461,433,55,6,435,426,219,22,424,200,457,458,486,470,484,242,499,133,163,301,305,5,436,448,23,107,161,421,184,425,158,423,49,240,54,485,124,46,442,11,43,505,193,225,439,503,3,494,440,496,119,489,16,450,142,226,506,140,81,491,495,73,493,48",
                                "min_total_price": 139500,
                                "longitude": 72.8794292490883,
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 0,
                                "soldout": 0,
                                "ufi": -2092174,
                                "children_not_allowed": 0,
                                "city_trans": "Mumbai",
                                "badges": [],
                                "review_score_word": "Very Good",
                                "in_best_district": 0,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "latitude": 19.108043031195,
                                "mobile_discount_percentage": 0,
                                "wishlist_count": 0,
                                "review_nr": 1162,
                                "default_language": "en",
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "has_free_parking": 1,
                                "city": "Mumbai",
                                "class": 5,
                                "hotel_name_trans": "Radisson Blu Mumbai International Airport",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "Radisson Blu Mumbai International Airport",
                                "districts": "3287,3712",
                                "is_no_prepayment_block": 1,
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 24,
                                    "localized_area": "null"
                                }
                                },
                                "checkout": {
                                "until": "12:00",
                                "from": ""
                                },
                                "url": "https://www.booking.com/hotel/in/radisson-blu-mumbai-international-airport.html",
                                "has_swimming_pool": 1,
                                "district": "Western Suburbs",
                                "is_city_center": 0,
                                "urgency_room_msg": "Superior Double or Twin Room",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "cc1": "in",
                                "main_photo_id": 331987485,
                                "city_name_en": "Mumbai",
                                "hotel_has_vb_boost": 0,
                                "review_score": 8.2,
                                "extended": 0,
                                "distance": "16.72",
                                "hotel_id": 6832186
                            },
                            {
                                "class_is_estimated": 0,
                                "genius_discount_percentage": 0,
                                "hotel_name": "Grand Hyatt Mumbai Hotel and Residences",
                                "is_no_prepayment_block": 1,
                                "districts": "3619,3287",
                                "has_free_parking": 1,
                                "hotel_name_trans": "Grand Hyatt Mumbai Hotel and Residences",
                                "city": "Mumbai",
                                "class": 5,
                                "review_nr": 1966,
                                "default_language": "en",
                                "native_ads_tracking": "",
                                "is_geo_rate": "",
                                "distance": "12.46",
                                "extended": 0,
                                "hotel_id": 390419,
                                "review_score": 8.3,
                                "is_city_center": 0,
                                "urgency_room_msg": "Club Queen Room with Evening Cocktails ",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "district": "Santacruz",
                                "hotel_has_vb_boost": 0,
                                "cc1": "in",
                                "city_name_en": "Mumbai",
                                "main_photo_id": 373741592,
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 9,
                                    "localized_area": "null"
                                }
                                },
                                "checkout": {
                                "from": "00:00",
                                "until": "12:00"
                                },
                                "url": "https://www.booking.com/hotel/in/grand-hyatt.html",
                                "has_swimming_pool": 1,
                                "default_wishlist_name": "Mumbai",
                                "zip": "400055",
                                "block_ids": [
                                "39041911_285745641_2_41_0"
                                ],
                                "country_trans": "India",
                                "city_in_trans": "in Mumbai",
                                "review_recommendation": "",
                                "id": "property_card_390419",
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "is_free_cancellable": 1,
                                "native_ads_cpc": 0,
                                "address": "Off Western Express Highway Santacruz (E)",
                                "type": "property_card",
                                "is_mobile_deal": 0,
                                "address_trans": "Off Western Express Highway Santacruz (E)",
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "badges": [],
                                "city_trans": "Mumbai",
                                "in_best_district": 0,
                                "review_score_word": "Very Good",
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "wishlist_count": 0,
                                "native_ad_id": "",
                                "timezone": "Asia/Kolkata",
                                "latitude": 19.0767956376696,
                                "mobile_discount_percentage": 0,
                                "longitude": 72.851240336895,
                                "min_total_price": 172800,
                                "cc_required": 1,
                                "hotel_facilities": "454,488,51,502,63,20,406,212,220,443,47,445,492,451,230,127,468,405,438,104,446,449,255,4,253,176,8,159,462,10,244,237,227,96,160,256,422,409,14,241,218,49,54,186,421,301,413,163,108,447,242,464,133,458,484,185,424,199,304,250,21,229,6,461,111,407,472,491,257,48,419,226,400,452,478,233,235,142,440,211,248,43,236,189,11,46,129,177,210,25,456,209,487,222,52,404,138,418,56,249,455,2,453,53,232,467,117,143,17,437,444,109,110,460,497,91,251,205,203,75,59,44,238,246,228,198,254,80,420,459,27,243,217,245,7,240,483,485,124,184,425,423,158,305,5,411,23,107,161,448,436,499,457,28,470,486,64,22,219,426,252,200,433,79,55,134,147,408,465,463,258,495,73,194,81,140,450,16,231,489,496,119,221,439,505,3,78,247,234,442",
                                "hotel_include_breakfast": 0,
                                "accommodation_type_name": "Hotels",
                                "soldout": 0,
                                "currencycode": "INR",
                                "deals": {
                                "deal_events_killswitch": 0,
                                "deal_attributes": {},
                                "deals_available": {}
                                },
                                "distance_to_cc": "12.50",
                                "selected_review_topic": "null",
                                "accommodation_type": 204,
                                "district_id": 3619,
                                "currency_code": "INR",
                                "preferred": 1,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/373741592.jpg?k=9fdd78ecf2da45ebe7bae3971950541ba2f5a5dc3977b1b71def13c8dcf96b13&o=",
                                "checkin": {
                                "until": "00:00",
                                "from": "15:00"
                                },
                                "preferred_plus": 0,
                                "countrycode": "in",
                                "price_breakdown": {
                                "has_fine_print_charges": 1,
                                "sum_excluded_raw": "31104.00",
                                "gross_price": "172800.00",
                                "all_inclusive_price": 203904,
                                "has_tax_exceptions": 0,
                                "has_incalculable_charges": 0,
                                "currency": "INR"
                                }
                            },
                            {
                                "hotel_id": 743959,
                                "distance": "0.45",
                                "extended": 0,
                                "review_score": 7.4,
                                "hotel_has_vb_boost": 0,
                                "cc1": "in",
                                "city_name_en": "Mumbai",
                                "main_photo_id": 102803378,
                                "urgency_room_msg": "Deluxe Double Room",
                                "is_city_center": 1,
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "district": "South Mumbai",
                                "checkout": {
                                "from": "",
                                "until": "09:30"
                                },
                                "url": "https://www.booking.com/hotel/in/kumkum.html",
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "localized_area": "null",
                                    "unit_type_id": 9
                                }
                                },
                                "is_no_prepayment_block": 0,
                                "districts": "2379,17337",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "Hotel Kumkum",
                                "hotel_name_trans": "Hotel Kumkum",
                                "city": "Mumbai",
                                "class": 0,
                                "native_ads_tracking": "",
                                "is_geo_rate": 1,
                                "review_nr": 151,
                                "default_language": "en",
                                "wishlist_count": 0,
                                "native_ad_id": "",
                                "timezone": "Asia/Kolkata",
                                "mobile_discount_percentage": 0,
                                "latitude": 18.9649534232939,
                                "badges": [],
                                "city_trans": "Mumbai",
                                "in_best_district": 0,
                                "review_score_word": "Good",
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 0,
                                "soldout": 0,
                                "longitude": 72.8189465403557,
                                "min_total_price": 21802.5,
                                "cc_required": 1,
                                "hotel_facilities": "23,107,5,163,305,47,464,124,485,158,487,488,209,51,210,456,454,17,467,468,461,28,458,457,453,455,22,451,16,450,8,44,462,75,15,460,109,449,140,81,91,43,459,96,3",
                                "accommodation_type": 204,
                                "district_id": 2379,
                                "currencycode": "INR",
                                "deals": {
                                "deal_attributes": {},
                                "deals_available": {},
                                "deal_events_killswitch": 0
                                },
                                "distance_to_cc": "0.45",
                                "selected_review_topic": "null",
                                "countrycode": "in",
                                "price_breakdown": {
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "has_incalculable_charges": 0,
                                "sum_excluded_raw": "2616.30",
                                "has_fine_print_charges": 0,
                                "all_inclusive_price": 24418.8,
                                "gross_price": "21802.50"
                                },
                                "preferred": 1,
                                "currency_code": "INR",
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/102803378.jpg?k=c6a1e4956fb584ce09a22a8c375de71eae4844cae4730b65505382d422330825&o=",
                                "preferred_plus": 0,
                                "checkin": {
                                "until": "23:30",
                                "from": "11:00"
                                },
                                "country_trans": "India",
                                "city_in_trans": "in Mumbai",
                                "default_wishlist_name": "Mumbai",
                                "block_ids": [
                                "74395903_348785298_2_2_0"
                                ],
                                "zip": "400007",
                                "review_recommendation": "",
                                "id": "property_card_743959",
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "native_ads_cpc": 0,
                                "address": "165, Lamington Road",
                                "is_free_cancellable": 1,
                                "address_trans": "165, Lamington Road",
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "type": "property_card",
                                "is_mobile_deal": 0
                            },
                            {
                                "price_breakdown": {
                                "has_tax_exceptions": 0,
                                "has_incalculable_charges": 0,
                                "currency": "INR",
                                "gross_price": "62532.00",
                                "all_inclusive_price": 70035.84,
                                "has_fine_print_charges": 0,
                                "sum_excluded_raw": 7503.84
                                },
                                "countrycode": "in",
                                "checkin": {
                                "until": "",
                                "from": "12:00"
                                },
                                "preferred_plus": 0,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/203323501.jpg?k=f78c52453dce2f84c86581522206c0f0835222316d599c90c0e19088d226b3e1&o=",
                                "currency_code": "INR",
                                "preferred": 1,
                                "accommodation_type": 204,
                                "district_id": 3448,
                                "selected_review_topic": "null",
                                "distance_to_cc": "5.70",
                                "currencycode": "INR",
                                "deals": {
                                "deal_events_killswitch": 0,
                                "deals_available": {},
                                "deal_attributes": {}
                                },
                                "soldout": 0,
                                "hotel_include_breakfast": 0,
                                "accommodation_type_name": "Hotels",
                                "hotel_facilities": "75,44,462,205,8,16,450,142,203,419,91,452,109,449,48,460,110,15,129,7,78,43,459,420,3,96,47,466,418,305,163,20,107,5,456,425,25,454,423,487,222,158,488,461,467,304,468,6,185,424,455,22,451,53,453,458,457,484,64,486,28",
                                "cc_required": 1,
                                "min_total_price": 62532,
                                "longitude": 72.8302882611752,
                                "mobile_discount_percentage": 6948,
                                "latitude": 18.919130844573,
                                "native_ad_id": "",
                                "timezone": "Asia/Kolkata",
                                "wishlist_count": 0,
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "review_score_word": "Pleasant",
                                "in_best_district": 0,
                                "badges": [
                                {
                                    "text": "Mobile-only price",
                                    "badge_variant": "constructive",
                                    "id": "mobile_price"
                                }
                                ],
                                "city_trans": "Mumbai",
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "address_trans": "41, Garden Road, Colaba Causeway",
                                "is_mobile_deal": 1,
                                "type": "property_card",
                                "address": "41, Garden Road, Colaba Causeway",
                                "native_ads_cpc": 0,
                                "is_free_cancellable": 1,
                                "is_smart_deal": 0,
                                "cant_book": 0,
                                "id": "property_card_441342",
                                "review_recommendation": "",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "zip": "400001",
                                "block_ids": [
                                "44134202_298456350_3_1_0"
                                ],
                                "default_wishlist_name": "Mumbai",
                                "url": "https://www.booking.com/hotel/in/godwin-mumbai.html",
                                "checkout": {
                                "from": "",
                                "until": "12:00"
                                },
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "localized_area": "null",
                                    "unit_type_id": 24
                                }
                                },
                                "city_name_en": "Mumbai ",
                                "main_photo_id": 203323501,
                                "cc1": "in",
                                "hotel_has_vb_boost": 0,
                                "district": "Colaba",
                                "is_city_center": 0,
                                "urgency_room_msg": "Deluxe Double or Twin Room",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "review_score": 6.9,
                                "hotel_id": 441342,
                                "extended": 0,
                                "distance": "5.67",
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "default_language": "en",
                                "review_nr": 130,
                                "class": 4,
                                "city": "Mumbai ",
                                "hotel_name_trans": "Hotel Godwin - Colaba",
                                "districts": "3448,2379,17444",
                                "is_no_prepayment_block": 1,
                                "hotel_name": "Hotel Godwin - Colaba",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0
                            },
                            {
                                "districts": "3449,2379",
                                "is_no_prepayment_block": 1,
                                "hotel_name": "Bloom Hotel - Worli South Mumbai",
                                "class_is_estimated": 0,
                                "genius_discount_percentage": 0,
                                "class": 4,
                                "city": "Mumbai",
                                "hotel_name_trans": "Bloom Hotel - Worli South Mumbai",
                                "has_free_parking": 1,
                                "is_geo_rate": 1,
                                "native_ads_tracking": "",
                                "default_language": "en",
                                "review_nr": 184,
                                "hotel_id": 7386293,
                                "extended": 0,
                                "distance": "2.59",
                                "review_score": 7.1,
                                "city_name_en": "Mumbai",
                                "main_photo_id": 321082856,
                                "cc1": "in",
                                "hotel_has_vb_boost": 0,
                                "district": "Worli",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "urgency_room_msg": "Standard Queen Room",
                                "is_city_center": 0,
                                "checkout": {
                                "from": "",
                                "until": "11:00"
                                },
                                "url": "https://www.booking.com/hotel/in/bloom-worli.html",
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "localized_area": "null",
                                    "unit_type_id": 9
                                }
                                },
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "block_ids": [
                                "738629301_339914441_2_2_0"
                                ],
                                "zip": "400018",
                                "default_wishlist_name": "Mumbai",
                                "is_smart_deal": 0,
                                "cant_book": 0,
                                "id": "property_card_7386293",
                                "review_recommendation": "",
                                "address": "Dr. E Moses Rd, Gandhi Nagar Upper Worli, Mahalakshmi",
                                "native_ads_cpc": 0,
                                "is_free_cancellable": 1,
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "address_trans": "Dr. E Moses Rd, Gandhi Nagar Upper Worli, Mahalakshmi",
                                "is_mobile_deal": 0,
                                "type": "property_card",
                                "latitude": 18.992166,
                                "mobile_discount_percentage": 0,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "wishlist_count": 0,
                                "ufi": -2092174,
                                "children_not_allowed": 0,
                                "review_score_word": "Good",
                                "in_best_district": 0,
                                "city_trans": "Mumbai",
                                "badges": [],
                                "soldout": 0,
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 0,
                                "hotel_facilities": "459,420,422,149,80,160,96,462,44,471,75,174,8,176,205,91,460,110,109,449,490,446,437,444,17,467,117,468,2,453,179,455,445,418,47,443,20,406,487,488,209,51,210,454,177,46,129,43,3,503,439,440,496,494,142,16,450,140,81,419,73,493,461,465,134,435,304,424,22,219,426,64,470,486,457,133,499,464,466,23,161,107,436,108,5,305,163,423,158,421,184,425,124,485,49",
                                "cc_required": 1,
                                "min_total_price": 48600,
                                "longitude": 72.82083,
                                "district_id": 3449,
                                "accommodation_type": 204,
                                "selected_review_topic": "null",
                                "distance_to_cc": "2.60",
                                "currencycode": "INR",
                                "deals": {
                                "deals_available": {},
                                "deal_attributes": {},
                                "deal_events_killswitch": 0
                                },
                                "price_breakdown": {
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "has_incalculable_charges": 0,
                                "sum_excluded_raw": "5832.00",
                                "has_fine_print_charges": 0,
                                "all_inclusive_price": 54432,
                                "gross_price": "48600.00"
                                },
                                "countrycode": "in",
                                "preferred_plus": 0,
                                "checkin": {
                                "until": "",
                                "from": "14:00"
                                },
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/321082856.jpg?k=b6594a2102dd308c1cf9dbe546abec84072d1d4b5b9d49d7c456f662261391a6&o=",
                                "currency_code": "INR",
                                "preferred": 1
                            },
                            {
                                "review_nr": 2475,
                                "default_language": "en",
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "has_free_parking": 1,
                                "city": "Mumbai",
                                "class": 5,
                                "hotel_name_trans": "The Orchid Hotel Mumbai Vile Parle",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "The Orchid Hotel Mumbai Vile Parle",
                                "districts": "3287",
                                "is_no_prepayment_block": 0,
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 8,
                                    "localized_area": "null"
                                }
                                },
                                "checkout": {
                                "until": "12:00",
                                "from": "00:30"
                                },
                                "url": "https://www.booking.com/hotel/in/the-orchid-mumbai.html",
                                "has_swimming_pool": 1,
                                "district": "Western Suburbs",
                                "urgency_room_msg": "Deluxe Room Twin Bed with Bathtub",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "is_city_center": 0,
                                "cc1": "in",
                                "city_name_en": "Mumbai",
                                "main_photo_id": 248811829,
                                "hotel_has_vb_boost": 0,
                                "review_score": 7.1,
                                "extended": 0,
                                "distance": "14.73",
                                "hotel_id": 261607,
                                "is_mobile_deal": 1,
                                "type": "property_card",
                                "address_trans": "Nehru Road, Vile Parle (East), Adjacent To Domestic Airport",
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "is_free_cancellable": 1,
                                "address": "Nehru Road, Vile Parle (East), Adjacent To Domestic Airport",
                                "native_ads_cpc": 0,
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "review_recommendation": "",
                                "id": "property_card_261607",
                                "block_ids": [
                                "26160710_350213067_3_42_0"
                                ],
                                "zip": "400099",
                                "default_wishlist_name": "Mumbai",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "checkin": {
                                "from": "14:00",
                                "until": "23:30"
                                },
                                "preferred_plus": 0,
                                "currency_code": "INR",
                                "preferred": 1,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/248811829.jpg?k=9ffb59d63eed10c16e92fd67e9924b4a9950a5579a75fe2968fde0b6359068fd&o=",
                                "price_breakdown": {
                                "has_incalculable_charges": 0,
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "sum_excluded_raw": "19528.70",
                                "has_fine_print_charges": 0,
                                "all_inclusive_price": 128021.5,
                                "gross_price": "108492.80"
                                },
                                "countrycode": "in",
                                "selected_review_topic": "null",
                                "currencycode": "INR",
                                "deals": {
                                "deal_events_killswitch": 0,
                                "deal_attributes": {},
                                "deals_available": {}
                                },
                                "distance_to_cc": "14.75",
                                "accommodation_type": 204,
                                "district_id": 3287,
                                "cc_required": 1,
                                "hotel_facilities": "494,440,505,221,439,3,247,78,129,442,11,46,491,495,257,493,48,504,419,140,452,81,450,142,16,489,457,458,64,22,219,424,433,55,304,6,21,250,435,134,461,49,240,54,124,425,421,158,423,301,163,305,5,108,436,107,448,23,466,464,133,96,198,160,422,14,420,459,241,245,7,449,109,460,110,497,498,91,253,205,203,176,8,75,59,246,44,462,10,244,249,492,451,455,453,2,127,118,468,117,467,143,17,444,104,454,456,25,210,51,209,488,487,52,20,220,443,47,418,445,441",
                                "min_total_price": 108492.8,
                                "longitude": 72.8546901183075,
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 0,
                                "soldout": 0,
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "badges": [
                                {
                                    "id": "mobile_price",
                                    "badge_variant": "constructive",
                                    "text": "Mobile-only price"
                                }
                                ],
                                "city_trans": "Mumbai",
                                "review_score_word": "Good",
                                "in_best_district": 0,
                                "native_ad_id": "",
                                "timezone": "Asia/Kolkata",
                                "mobile_discount_percentage": 27123.2,
                                "latitude": 19.0970935604404,
                                "wishlist_count": 0
                            },
                            {
                                "default_wishlist_name": "Mumbai",
                                "block_ids": [
                                "29408601_94398656_2_2_0"
                                ],
                                "zip": "400051",
                                "country_trans": "India",
                                "city_in_trans": "in Mumbai",
                                "review_recommendation": "",
                                "id": "property_card_294086",
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "is_free_cancellable": 1,
                                "native_ads_cpc": 0,
                                "address": "C-57, Bandra Kurla Complex",
                                "type": "property_card",
                                "is_mobile_deal": 0,
                                "address_trans": "C-57, Bandra Kurla Complex",
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "badges": [],
                                "city_trans": "Mumbai",
                                "in_best_district": 0,
                                "review_score_word": "Very Good",
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "wishlist_count": 0,
                                "native_ad_id": "",
                                "timezone": "Asia/Kolkata",
                                "mobile_discount_percentage": 0,
                                "latitude": 19.0675024126694,
                                "min_total_price": 123500,
                                "longitude": 72.869256734848,
                                "cc_required": 1,
                                "hotel_facilities": "16,450,489,491,495,257,73,493,48,226,506,81,452,43,78,11,46,442,129,177,494,496,440,119,505,439,221,3,301,163,305,108,5,436,23,448,107,161,242,466,464,133,49,240,54,485,124,184,158,433,55,304,6,21,134,465,461,111,457,458,486,470,484,426,219,22,200,205,203,176,8,75,44,462,10,449,109,460,15,110,497,498,91,253,4,459,27,7,241,96,198,256,160,254,52,20,220,443,47,445,441,454,456,192,210,25,51,488,209,487,222,63,502,468,467,117,17,444,490,446,104,492,451,455,453,2,53,127",
                                "hotel_include_breakfast": 0,
                                "accommodation_type_name": "Hotels",
                                "soldout": 0,
                                "deals": {
                                "deal_events_killswitch": 0,
                                "deals_available": {},
                                "deal_attributes": {}
                                },
                                "currencycode": "INR",
                                "distance_to_cc": "12.20",
                                "selected_review_topic": "null",
                                "accommodation_type": 204,
                                "district_id": 3445,
                                "preferred": 1,
                                "currency_code": "INR",
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/271473562.jpg?k=b0269ab41912cedcbb17fee4f68f69da0197ce837f30aeb6abef8e05d51be7b7&o=",
                                "preferred_plus": 0,
                                "checkin": {
                                "from": "14:00",
                                "until": ""
                                },
                                "countrycode": "in",
                                "price_breakdown": {
                                "has_incalculable_charges": 0,
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "gross_price": "123500.00",
                                "all_inclusive_price": 145730,
                                "has_fine_print_charges": 0,
                                "sum_excluded_raw": "22230.00"
                                },
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "Sofitel Mumbai BKC",
                                "is_no_prepayment_block": 1,
                                "districts": "3445,3446",
                                "has_free_parking": 1,
                                "hotel_name_trans": "Sofitel Mumbai BKC",
                                "city": "Mumbai",
                                "class": 5,
                                "review_nr": 2638,
                                "default_language": "en",
                                "native_ads_tracking": "",
                                "is_geo_rate": "",
                                "distance": "12.16",
                                "extended": 0,
                                "hotel_id": 294086,
                                "review_score": 8.2,
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "urgency_room_msg": "Luxury King Room",
                                "is_city_center": 0,
                                "district": "Bandra",
                                "hotel_has_vb_boost": 0,
                                "cc1": "in",
                                "main_photo_id": 271473562,
                                "city_name_en": "Mumbai",
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 9,
                                    "localized_area": "null"
                                }
                                },
                                "checkout": {
                                "until": "12:00",
                                "from": ""
                                },
                                "url": "https://www.booking.com/hotel/in/sofitel-mumbai-bkc.html",
                                "has_swimming_pool": 1
                            },
                            {
                                "review_nr": 60,
                                "default_language": "xu",
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "city": "Mumbai",
                                "class": 2,
                                "hotel_name_trans": "Hotel Al Madina palace",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "Hotel Al Madina palace",
                                "districts": "2379",
                                "is_no_prepayment_block": 1,
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 7,
                                    "localized_area": "null"
                                }
                                },
                                "url": "https://www.booking.com/hotel/in/al-madina.html",
                                "checkout": {
                                "until": "11:30",
                                "from": ""
                                },
                                "district": "South Mumbai",
                                "urgency_room_msg": "Economy Triple Room with Shared Bathroom",
                                "is_city_center": 1,
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "cc1": "in",
                                "city_name_en": "Mumbai",
                                "main_photo_id": 238932524,
                                "hotel_has_vb_boost": 0,
                                "review_score": 6,
                                "extended": 0,
                                "distance": "1.89",
                                "hotel_id": 1223979,
                                "is_mobile_deal": 1,
                                "type": "property_card",
                                "address_trans": "73 Ismail Curtay Road, Kazi Mohalla, Near Mandvi Telephone Exchange, Pydhonie,",
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "is_free_cancellable": 1,
                                "address": "73 Ismail Curtay Road, Kazi Mohalla, Near Mandvi Telephone Exchange, Pydhonie,",
                                "native_ads_cpc": 0,
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "review_recommendation": "",
                                "id": "property_card_1223979",
                                "block_ids": [
                                "122397912_223075939_2_42_0"
                                ],
                                "zip": "400003",
                                "default_wishlist_name": "Mumbai",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "preferred_plus": 0,
                                "checkin": {
                                "from": "12:00",
                                "until": ""
                                },
                                "preferred": 0,
                                "currency_code": "INR",
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/238932524.jpg?k=e28a733d8db00947e28ef2ff78afa9cbc04cf1937cfe3065f4cdab104cd2a4e6&o=",
                                "price_breakdown": {
                                "all_inclusive_price": 12337.92,
                                "gross_price": "11016.00",
                                "sum_excluded_raw": 1321.92,
                                "has_fine_print_charges": 0,
                                "has_tax_exceptions": 0,
                                "has_incalculable_charges": 0,
                                "currency": "INR"
                                },
                                "countrycode": "in",
                                "selected_review_topic": "null",
                                "deals": {
                                "deal_attributes": {},
                                "deals_available": {},
                                "deal_events_killswitch": 0
                                },
                                "currencycode": "INR",
                                "distance_to_cc": "1.90",
                                "district_id": 2379,
                                "accommodation_type": 204,
                                "cc_required": 1,
                                "hotel_facilities": "51,158,487,454,456,485,418,466,464,47,5,108,23,107,305,453,53,455,22,451,426,28,470,486,484,457,458,446,134,461,229,17,468,467,253,81,452,419,91,226,73,460,110,48,449,109,44,462,235,142,450,8,205,233,96,459,43,78,234",
                                "longitude": 72.8302198648453,
                                "min_total_price": 11016,
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 0,
                                "soldout": 0,
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "city_trans": "Mumbai",
                                "badges": [
                                {
                                    "text": "Mobile-only price",
                                    "id": "mobile_price",
                                    "badge_variant": "constructive"
                                }
                                ],
                                "in_best_district": 0,
                                "review_score_word": "Pleasant",
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "mobile_discount_percentage": 1944,
                                "latitude": 18.9556717012602,
                                "wishlist_count": 0
                            },
                            {
                                "url": "https://www.booking.com/hotel/in/sun-n-sand-mumbai.html",
                                "checkout": {
                                "from": "",
                                "until": "12:00"
                                },
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "localized_area": "null",
                                    "unit_type_id": 24
                                }
                                },
                                "city_name_en": "Mumbai",
                                "main_photo_id": 11467865,
                                "cc1": "in",
                                "hotel_has_vb_boost": 0,
                                "district": "Juhu",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "urgency_room_msg": "Superior Double or Twin Room with City View 15% Discount on Food and Beverage",
                                "is_city_center": 0,
                                "review_score": 7.5,
                                "hotel_id": 252104,
                                "extended": 0,
                                "distance": "15.63",
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "default_language": "en",
                                "review_nr": 361,
                                "class": 5,
                                "city": "Mumbai",
                                "hotel_name_trans": "Sun-n-Sand Mumbai Juhu Beach",
                                "has_free_parking": 1,
                                "districts": "2375,3287",
                                "is_no_prepayment_block": 1,
                                "hotel_name": "Sun-n-Sand Mumbai Juhu Beach",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "price_breakdown": {
                                "sum_excluded_raw": "22275.00",
                                "has_fine_print_charges": 0,
                                "all_inclusive_price": 146025,
                                "gross_price": "123750.00",
                                "has_incalculable_charges": 0,
                                "has_tax_exceptions": 0,
                                "currency": "INR"
                                },
                                "countrycode": "in",
                                "checkin": {
                                "until": "00:00",
                                "from": "14:00"
                                },
                                "preferred_plus": 0,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/11467865.jpg?k=d04b316383601e27b9f7d08a6f70c46ebd63be5b0c7a884d55c85c32b533e959&o=",
                                "currency_code": "INR",
                                "preferred": 1,
                                "district_id": 2375,
                                "accommodation_type": 204,
                                "selected_review_topic": "null",
                                "distance_to_cc": "15.65",
                                "deals": {
                                "deals_available": {},
                                "deal_attributes": {},
                                "deal_events_killswitch": 0
                                },
                                "currencycode": "INR",
                                "soldout": 0,
                                "hotel_include_breakfast": 0,
                                "accommodation_type_name": "Hotels",
                                "hotel_facilities": "452,81,140,498,91,506,48,460,15,110,73,109,491,449,44,462,75,8,142,450,16,3,505,160,439,96,496,7,46,11,27,78,43,459,302,14,487,51,488,456,25,454,54,485,49,499,133,47,464,466,161,107,23,108,5,163,305,146,20,53,453,2,455,451,22,484,492,486,458,457,446,444,461,17,6,143,55,117,467,118,468,145",
                                "cc_required": 1,
                                "longitude": 72.8243431448936,
                                "min_total_price": 123750,
                                "latitude": 19.1094876241502,
                                "mobile_discount_percentage": 0,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "wishlist_count": 0,
                                "ufi": -2092174,
                                "children_not_allowed": 0,
                                "review_score_word": "Good",
                                "in_best_district": 0,
                                "city_trans": "Mumbai",
                                "badges": [],
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "address_trans": "39 Juhu Beach",
                                "is_mobile_deal": 0,
                                "type": "property_card",
                                "address": "39 Juhu Beach",
                                "native_ads_cpc": 0,
                                "is_free_cancellable": 1,
                                "is_smart_deal": 0,
                                "cant_book": 0,
                                "id": "property_card_252104",
                                "review_recommendation": "",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "zip": "400049",
                                "block_ids": [
                                "25210401_270404386_2_0_0"
                                ],
                                "default_wishlist_name": "Mumbai"
                            },
                            {
                                "preferred": 1,
                                "currency_code": "INR",
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/103705059.jpg?k=9e078265b31ad1815a573da8ed2a665f863e3925e1efd730df703421868a2ada&o=",
                                "checkin": {
                                "until": "",
                                "from": "15:00"
                                },
                                "preferred_plus": 0,
                                "countrycode": "in",
                                "price_breakdown": {
                                "has_fine_print_charges": 1,
                                "sum_excluded_raw": 49895.45,
                                "gross_price": 277196.92,
                                "all_inclusive_price": 327092.37,
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "has_incalculable_charges": 0
                                },
                                "deals": {
                                "deal_events_killswitch": 0,
                                "deals_available": {},
                                "deal_attributes": {}
                                },
                                "currencycode": "INR",
                                "distance_to_cc": "5.50",
                                "selected_review_topic": "null",
                                "accommodation_type": 204,
                                "district_id": 3448,
                                "min_total_price": 277196.92,
                                "longitude": 72.8331752172471,
                                "cc_required": 1,
                                "hotel_facilities": "199,433,79,304,55,21,229,6,408,134,111,461,407,457,458,28,64,22,219,185,424,200,301,305,163,5,411,107,23,436,242,133,499,240,49,124,54,425,421,423,158,43,236,78,234,72,11,46,129,494,496,119,221,505,3,233,402,16,450,231,235,495,257,493,73,48,419,506,226,400,81,452,140,468,232,118,467,117,403,17,444,104,490,446,492,451,455,230,77,2,453,127,53,20,406,52,404,220,47,445,418,167,454,25,210,209,502,63,222,420,459,27,243,241,7,227,228,198,96,410,256,254,422,205,176,203,180,8,75,238,462,44,244,237,10,449,109,110,460,15,497,91,255,498,253",
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 1,
                                "soldout": 0,
                                "badges": [],
                                "city_trans": "Mumbai",
                                "in_best_district": 0,
                                "review_score_word": "Wonderful",
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "wishlist_count": 0,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "mobile_discount_percentage": 0,
                                "latitude": 18.9216373548013,
                                "type": "property_card",
                                "is_mobile_deal": 0,
                                "address_trans": "Apollo Bunder Road The Taj Mahal Palace",
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "is_free_cancellable": 1,
                                "native_ads_cpc": 0,
                                "address": "Apollo Bunder Road The Taj Mahal Palace",
                                "review_recommendation": "",
                                "id": "property_card_2451595",
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "default_wishlist_name": "Mumbai",
                                "block_ids": [
                                "245159501_137748730_1_1_0"
                                ],
                                "zip": "400001",
                                "country_trans": "India",
                                "city_in_trans": "in Mumbai",
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 7,
                                    "localized_area": "null"
                                }
                                },
                                "url": "https://www.booking.com/hotel/in/the-taj-mahal-palace-mumbai.html",
                                "checkout": {
                                "from": "",
                                "until": "11:00"
                                },
                                "has_swimming_pool": 1,
                                "is_city_center": 0,
                                "urgency_room_msg": "Luxury Grande Room City View",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "district": "Colaba",
                                "hotel_has_vb_boost": 0,
                                "cc1": "in",
                                "city_name_en": "Mumbai",
                                "main_photo_id": 103705059,
                                "review_score": 9,
                                "distance": "5.47",
                                "extended": 0,
                                "hotel_id": 2451595,
                                "review_nr": 755,
                                "default_language": "xu",
                                "native_ads_tracking": "",
                                "is_geo_rate": "",
                                "has_free_parking": 1,
                                "hotel_name_trans": "The Taj Mahal Palace, Mumbai",
                                "city": "Mumbai",
                                "class": 5,
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "The Taj Mahal Palace, Mumbai",
                                "is_no_prepayment_block": 1,
                                "districts": "3448,2379,17444"
                            },
                            {
                                "mobile_discount_percentage": 17100,
                                "latitude": 19.0666404941471,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "wishlist_count": 0,
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "in_best_district": 0,
                                "review_score_word": "Excellent",
                                "city_trans": "Mumbai",
                                "badges": [
                                {
                                    "text": "Mobile-only price",
                                    "badge_variant": "constructive",
                                    "id": "mobile_price"
                                }
                                ],
                                "soldout": 0,
                                "hotel_include_breakfast": 1,
                                "accommodation_type_name": "Hotels",
                                "hotel_facilities": "420,459,7,27,96,422,149,256,160,203,176,8,205,462,44,75,110,460,449,109,253,91,17,468,467,117,444,490,446,104,492,188,187,453,2,53,455,451,406,52,20,445,418,101,47,51,209,454,456,210,25,43,189,78,129,46,11,119,494,496,3,16,450,493,73,48,495,491,257,140,452,81,226,419,506,6,21,79,433,304,463,134,461,64,457,458,426,22,219,424,185,5,436,23,107,161,163,305,301,133,464,124,49,423,158,186,425,184,421",
                                "cc_required": 1,
                                "min_total_price": 153900,
                                "longitude": 72.8675293922424,
                                "accommodation_type": 204,
                                "district_id": 3445,
                                "selected_review_topic": "null",
                                "distance_to_cc": "12.00",
                                "currencycode": "INR",
                                "deals": {
                                "deal_events_killswitch": 0,
                                "deals_available": {},
                                "deal_attributes": {}
                                },
                                "price_breakdown": {
                                "currency": "INR",
                                "has_tax_exceptions": 0,
                                "has_incalculable_charges": 0,
                                "gross_price": "153900.00",
                                "all_inclusive_price": 181602,
                                "has_fine_print_charges": 0,
                                "sum_excluded_raw": "27702.00"
                                },
                                "countrycode": "in",
                                "preferred_plus": 0,
                                "checkin": {
                                "from": "14:00",
                                "until": ""
                                },
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/33034375.jpg?k=ebad21bc68081acf90d3fc69b50bc8a713a60df7eb219351be8ca0e409473758&o=",
                                "currency_code": "INR",
                                "preferred": 1,
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "zip": "400051",
                                "block_ids": [
                                "39920811_352834357_1_41_0"
                                ],
                                "default_wishlist_name": "Mumbai",
                                "is_smart_deal": 0,
                                "cant_book": 0,
                                "id": "property_card_399208",
                                "review_recommendation": "",
                                "address": "C-56, G Block, Bandra Kurla Complex",
                                "native_ads_cpc": 0,
                                "is_free_cancellable": 1,
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "address_trans": "C-56, G Block, Bandra Kurla Complex",
                                "is_mobile_deal": 1,
                                "type": "property_card",
                                "hotel_id": 399208,
                                "extended": 0,
                                "distance": "12.00",
                                "review_score": 8.9,
                                "city_name_en": "Mumbai",
                                "main_photo_id": 33034375,
                                "cc1": "in",
                                "hotel_has_vb_boost": 0,
                                "district": "Bandra",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "urgency_room_msg": "Deluxe Room (Twin Beds)",
                                "is_city_center": 0,
                                "has_swimming_pool": 1,
                                "url": "https://www.booking.com/hotel/in/the-trident-bandra-kurla.html",
                                "checkout": {
                                "until": "12:00",
                                "from": ""
                                },
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 8,
                                    "localized_area": "null"
                                }
                                },
                                "districts": "3445,3446",
                                "is_no_prepayment_block": 0,
                                "hotel_name": "Trident Bandra Kurla",
                                "class_is_estimated": 0,
                                "genius_discount_percentage": 0,
                                "class": 5,
                                "city": "Mumbai",
                                "hotel_name_trans": "Trident Bandra Kurla",
                                "has_free_parking": 1,
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "default_language": "en",
                                "review_nr": 2905
                            },
                            {
                                "is_city_center": 0,
                                "urgency_room_msg": "Superior Triple Room",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "district": "Churchgate",
                                "hotel_has_vb_boost": 0,
                                "cc1": "in",
                                "main_photo_id": 222648048,
                                "city_name_en": "Mumbai",
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 9,
                                    "localized_area": "null"
                                }
                                },
                                "url": "https://www.booking.com/hotel/in/chateau-windsor.html",
                                "checkout": {
                                "until": "11:00",
                                "from": ""
                                },
                                "distance": "4.00",
                                "extended": 0,
                                "hotel_id": 244894,
                                "review_score": 7.6,
                                "has_free_parking": 1,
                                "hotel_name_trans": "Chateau Windsor Hotel - Marine Drive",
                                "city": "Mumbai",
                                "class": 3,
                                "review_nr": 264,
                                "default_language": "en",
                                "native_ads_tracking": "",
                                "is_geo_rate": "",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "Chateau Windsor Hotel - Marine Drive",
                                "is_no_prepayment_block": 0,
                                "districts": "3451,2379,17444",
                                "deals": {
                                "deal_attributes": {},
                                "deals_available": {},
                                "deal_events_killswitch": 0
                                },
                                "currencycode": "INR",
                                "distance_to_cc": "4.00",
                                "selected_review_topic": "null",
                                "district_id": 3451,
                                "accommodation_type": 204,
                                "preferred": 1,
                                "currency_code": "INR",
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/222648048.jpg?k=0d92594dc18879a243b2ca79c8e4f0cf26e25e25dbe8c9378369104a7c6ac1f5&o=",
                                "preferred_plus": 0,
                                "checkin": {
                                "from": "12:00",
                                "until": ""
                                },
                                "countrycode": "in",
                                "price_breakdown": {
                                "has_fine_print_charges": 1,
                                "sum_excluded_raw": 5870.88,
                                "gross_price": "48924.00",
                                "all_inclusive_price": 54794.88,
                                "has_incalculable_charges": 0,
                                "has_tax_exceptions": 0,
                                "currency": "INR"
                                },
                                "badges": [
                                {
                                    "id": "mobile_price",
                                    "badge_variant": "constructive",
                                    "text": "Mobile-only price"
                                }
                                ],
                                "city_trans": "Mumbai",
                                "review_score_word": "Good",
                                "in_best_district": 0,
                                "ufi": -2092174,
                                "children_not_allowed": 0,
                                "wishlist_count": 0,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "latitude": 18.9335066158854,
                                "mobile_discount_percentage": 5436,
                                "min_total_price": 48924,
                                "longitude": 72.825134396553,
                                "cc_required": 1,
                                "hotel_facilities": "81,452,91,419,460,15,48,449,109,44,462,75,8,16,450,142,160,96,46,129,459,43,51,423,487,158,454,456,421,425,485,124,418,101,466,47,464,5,161,107,23,52,20,163,305,2,451,455,22,424,179,486,457,458,134,461,111,468,118,304,467",
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 0,
                                "soldout": 0,
                                "is_free_cancellable": 1,
                                "native_ads_cpc": 0,
                                "address": "86 Veer Nariman Road, Churchgate",
                                "type": "property_card",
                                "is_mobile_deal": 1,
                                "address_trans": "86 Veer Nariman Road, Churchgate",
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "default_wishlist_name": "Mumbai",
                                "zip": "400020",
                                "block_ids": [
                                "24489404_273005843_3_34_0"
                                ],
                                "country_trans": "India",
                                "city_in_trans": "in Mumbai",
                                "review_recommendation": "",
                                "id": "property_card_244894",
                                "cant_book": 0,
                                "is_smart_deal": 0
                            },
                            {
                                "review_nr": 220,
                                "default_language": "en",
                                "is_geo_rate": 1,
                                "native_ads_tracking": "",
                                "has_free_parking": 1,
                                "city": "Mumbai",
                                "class": 3,
                                "hotel_name_trans": "Sea Green Hotel",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "Sea Green Hotel",
                                "districts": "3451,2379,17444",
                                "is_no_prepayment_block": 0,
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "localized_area": "null",
                                    "unit_type_id": 24
                                }
                                },
                                "url": "https://www.booking.com/hotel/in/sea-green.html",
                                "checkout": {
                                "from": "",
                                "until": "12:00"
                                },
                                "district": "Churchgate",
                                "is_city_center": 0,
                                "urgency_room_msg": "Superior Sea View with Balcony",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "cc1": "in",
                                "main_photo_id": 62666833,
                                "city_name_en": "Mumbai",
                                "hotel_has_vb_boost": 0,
                                "review_score": 7,
                                "extended": 0,
                                "distance": "4.06",
                                "hotel_id": 334851,
                                "is_mobile_deal": 0,
                                "type": "property_card",
                                "address_trans": "145 Marine Drive",
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "is_free_cancellable": 1,
                                "address": "145 Marine Drive",
                                "native_ads_cpc": 0,
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "review_recommendation": "",
                                "id": "property_card_334851",
                                "block_ids": [
                                "33485108_360655659_3_1_0"
                                ],
                                "zip": "400020",
                                "default_wishlist_name": "Mumbai",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "preferred_plus": 0,
                                "checkin": {
                                "from": "14:00",
                                "until": ""
                                },
                                "preferred": 1,
                                "currency_code": "INR",
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/62666833.jpg?k=e52c673ffd3c015c055c58262ce446059b20b966a56a7115eb323bfb70069d95&o=",
                                "price_breakdown": {
                                "has_fine_print_charges": 0,
                                "sum_excluded_raw": 12177.84,
                                "gross_price": 67654.66,
                                "all_inclusive_price": 79832.5,
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "has_incalculable_charges": 0
                                },
                                "countrycode": "in",
                                "selected_review_topic": "null",
                                "deals": {
                                "deals_available": {},
                                "deal_attributes": {},
                                "deal_events_killswitch": 0
                                },
                                "currencycode": "INR",
                                "distance_to_cc": "4.10",
                                "accommodation_type": 204,
                                "district_id": 3451,
                                "cc_required": 1,
                                "hotel_facilities": "466,443,47,464,445,441,499,163,305,448,161,107,436,454,456,488,51,487,158,485,461,444,446,468,467,455,451,2,453,53,457,458,28,486,492,462,16,450,8,506,91,452,449,495,109,493,110,46,442,43,160,439,494,496,440,96",
                                "min_total_price": 67654.66,
                                "longitude": 72.8235465288162,
                                "hotel_include_breakfast": 1,
                                "accommodation_type_name": "Hotels",
                                "soldout": 0,
                                "children_not_allowed": 0,
                                "ufi": -2092174,
                                "city_trans": "Mumbai",
                                "badges": [],
                                "review_score_word": "Good",
                                "in_best_district": 0,
                                "native_ad_id": "",
                                "timezone": "Asia/Kolkata",
                                "mobile_discount_percentage": 0,
                                "latitude": 18.932763246814,
                                "wishlist_count": 0
                            },
                            {
                                "district": "Western Suburbs",
                                "urgency_room_msg": "Classic Room",
                                "is_city_center": 0,
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "cc1": "in",
                                "city_name_en": "Mumbai",
                                "main_photo_id": 342883399,
                                "hotel_has_vb_boost": 0,
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "localized_area": "null",
                                    "unit_type_id": 9
                                }
                                },
                                "checkout": {
                                "from": "",
                                "until": "12:00"
                                },
                                "url": "https://www.booking.com/hotel/in/suresha.html",
                                "extended": 0,
                                "distance": "16.09",
                                "hotel_id": 401149,
                                "review_score": 8.1,
                                "city": "Mumbai",
                                "class": 4,
                                "hotel_name_trans": "Hotel Oriental Aster- Mumbai International Airport",
                                "review_nr": 898,
                                "default_language": "en",
                                "is_geo_rate": "",
                                "native_ads_tracking": "",
                                "genius_discount_percentage": 0,
                                "class_is_estimated": 0,
                                "hotel_name": "Hotel Oriental Aster- Mumbai International Airport",
                                "districts": "3287,3712",
                                "is_no_prepayment_block": 0,
                                "selected_review_topic": "null",
                                "deals": {
                                "deal_attributes": {},
                                "deals_available": {},
                                "deal_events_killswitch": 0
                                },
                                "currencycode": "INR",
                                "distance_to_cc": "16.10",
                                "accommodation_type": 204,
                                "district_id": 3287,
                                "preferred_plus": 0,
                                "checkin": {
                                "from": "13:00",
                                "until": ""
                                },
                                "currency_code": "INR",
                                "preferred": 1,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/342883399.jpg?k=e2713955a2bcb82f59cb344396d359f1385a6454213a3bdd62be5f80c25ac283&o=",
                                "price_breakdown": {
                                "has_incalculable_charges": 0,
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "sum_excluded_raw": "6393.60",
                                "has_fine_print_charges": 0,
                                "all_inclusive_price": 59673.6,
                                "gross_price": "53280.00"
                                },
                                "countrycode": "in",
                                "ufi": -2092174,
                                "children_not_allowed": 0,
                                "badges": [
                                {
                                    "id": "mobile_price",
                                    "badge_variant": "constructive",
                                    "text": "Mobile-only price"
                                }
                                ],
                                "city_trans": "Mumbai",
                                "review_score_word": "Very Good",
                                "in_best_district": 0,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "latitude": 19.1079188199381,
                                "mobile_discount_percentage": 79920,
                                "wishlist_count": 0,
                                "cc_required": 1,
                                "hotel_facilities": "91,497,110,109,449,44,462,75,8,176,203,205,422,410,96,7,420,459,14,502,487,488,209,51,210,454,445,441,418,47,443,20,406,53,453,128,455,451,492,446,444,17,467,62,468,81,140,48,493,73,491,495,16,142,450,3,439,496,440,494,442,78,158,423,421,425,485,124,126,133,464,411,23,107,448,436,5,163,305,424,219,22,484,486,458,457,463,407,461,134,435,6,304",
                                "longitude": 72.8616258502007,
                                "min_total_price": 53280,
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 1,
                                "soldout": 0,
                                "is_free_cancellable": 1,
                                "address": "45, Tarun Bharat Co Op Society, Chakala, Andheri East",
                                "native_ads_cpc": 0,
                                "is_mobile_deal": 1,
                                "type": "property_card",
                                "address_trans": "45, Tarun Bharat Co Op Society, Chakala, Andheri East",
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "block_ids": [
                                "40114904_232275245_0_1_0"
                                ],
                                "zip": "400099",
                                "default_wishlist_name": "Mumbai",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India",
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "review_recommendation": "",
                                "id": "property_card_401149"
                            },
                            {
                                "is_no_prepayment_block": 1,
                                "districts": "3448,2379,17444",
                                "class_is_estimated": 0,
                                "genius_discount_percentage": 0,
                                "hotel_name": "Hotel Causeway, Colaba",
                                "hotel_name_trans": "Hotel Causeway, Colaba",
                                "city": "Mumbai",
                                "class": 1,
                                "has_free_parking": 1,
                                "native_ads_tracking": "",
                                "is_geo_rate": "",
                                "review_nr": 198,
                                "default_language": "xu",
                                "hotel_id": 1087584,
                                "distance": "5.34",
                                "extended": 0,
                                "review_score": 7.3,
                                "hotel_has_vb_boost": 0,
                                "cc1": "in",
                                "city_name_en": "Mumbai",
                                "main_photo_id": 89782712,
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "urgency_room_msg": "Deluxe Double or Twin Room",
                                "is_city_center": 0,
                                "district": "Colaba",
                                "checkout": {
                                "from": "",
                                "until": "12:00"
                                },
                                "url": "https://www.booking.com/hotel/in/causeway-mumbai.html",
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 24,
                                    "localized_area": "null"
                                }
                                },
                                "country_trans": "India",
                                "city_in_trans": "in Mumbai",
                                "default_wishlist_name": "Mumbai",
                                "block_ids": [
                                "108758401_198493559_0_0_0"
                                ],
                                "zip": "400039",
                                "review_recommendation": "",
                                "id": "property_card_1087584",
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "native_ads_cpc": 0,
                                "address": "43/45 Mathuradas Estate, 3rd Floor, Shahid Bhagat Singh Road, Opp Colaba Police Station ",
                                "is_free_cancellable": 1,
                                "address_trans": "43/45 Mathuradas Estate, 3rd Floor, Shahid Bhagat Singh Road, Opp Colaba Police Station ",
                                "price_is_final": 0,
                                "is_genius_deal": 0,
                                "type": "property_card",
                                "is_mobile_deal": 0,
                                "wishlist_count": 0,
                                "native_ad_id": "",
                                "timezone": "Asia/Kolkata",
                                "latitude": 18.9224337086062,
                                "mobile_discount_percentage": 0,
                                "badges": [],
                                "city_trans": "Mumbai",
                                "review_score_word": "Good",
                                "in_best_district": 0,
                                "ufi": -2092174,
                                "children_not_allowed": 0,
                                "accommodation_type_name": "Hotels",
                                "hotel_include_breakfast": 0,
                                "soldout": 0,
                                "longitude": 72.8315877914429,
                                "min_total_price": 30600,
                                "cc_required": 1,
                                "hotel_facilities": "452,140,81,91,48,15,73,109,449,462,44,159,75,8,450,16,180,176,205,80,96,46,129,78,459,43,487,158,51,488,209,25,210,454,485,47,466,23,107,447,5,305,53,183,453,2,455,451,22,484,486,458,457,111,134,17,467,117,304,468,141",
                                "accommodation_type": 204,
                                "district_id": 3448,
                                "deals": {
                                "deal_attributes": {},
                                "deals_available": {},
                                "deal_events_killswitch": 0
                                },
                                "currencycode": "INR",
                                "distance_to_cc": "5.35",
                                "selected_review_topic": "null",
                                "countrycode": "in",
                                "price_breakdown": {
                                "has_tax_exceptions": 0,
                                "currency": "INR",
                                "has_incalculable_charges": 0,
                                "has_fine_print_charges": 0,
                                "sum_excluded_raw": "3672.00",
                                "gross_price": "30600.00",
                                "all_inclusive_price": 34272
                                },
                                "currency_code": "INR",
                                "preferred": 1,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/89782712.jpg?k=dacb4a8b84518268170a3af0dcff604510a4e24412dbfccbce9e01fe5ada1d01&o=",
                                "preferred_plus": 0,
                                "checkin": {
                                "from": "12:00",
                                "until": ""
                                }
                            },
                            {
                                "matching_units_configuration": {
                                "matching_units_common_config": {
                                    "unit_type_id": 13,
                                    "localized_area": "null"
                                }
                                },
                                "checkout": {
                                "until": "12:00",
                                "from": ""
                                },
                                "url": "https://www.booking.com/hotel/in/grand-mumbai.html",
                                "district": "South Mumbai",
                                "urgency_room_msg": "Family Room",
                                "bwallet": {
                                "hotel_eligibility": 0
                                },
                                "is_city_center": 1,
                                "cc1": "in",
                                "main_photo_id": 309179823,
                                "city_name_en": "Mumbai",
                                "hotel_has_vb_boost": 0,
                                "review_score": 7,
                                "extended": 0,
                                "distance": "4.29",
                                "hotel_id": 350329,
                                "review_nr": 211,
                                "default_language": "en",
                                "is_geo_rate": 1,
                                "native_ads_tracking": "",
                                "city": "Mumbai",
                                "class": 3,
                                "hotel_name_trans": "Grand Hotel Mumbai - Ballard Estate, Fort",
                                "class_is_estimated": 0,
                                "genius_discount_percentage": 0,
                                "hotel_name": "Grand Hotel Mumbai - Ballard Estate, Fort",
                                "districts": "2379,17444",
                                "is_no_prepayment_block": 1,
                                "preferred_plus": 0,
                                "checkin": {
                                "until": "",
                                "from": "14:00"
                                },
                                "currency_code": "INR",
                                "preferred": 1,
                                "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/309179823.jpg?k=53b55d5d5014e77e4629c97d3232f10512c5cdd8ec11bac91946ca4caac3dd19&o=",
                                "price_breakdown": {
                                "all_inclusive_price": 75596.98,
                                "gross_price": "67497.30",
                                "sum_excluded_raw": 8099.68,
                                "has_fine_print_charges": 1,
                                "has_tax_exceptions": 0,
                                "has_incalculable_charges": 0,
                                "currency": "INR"
                                },
                                "countrycode": "in",
                                "selected_review_topic": "null",
                                "currencycode": "INR",
                                "deals": {
                                "deals_available": {},
                                "deal_attributes": {},
                                "deal_events_killswitch": 0
                                },
                                "distance_to_cc": "4.30",
                                "district_id": 2379,
                                "accommodation_type": 204,
                                "cc_required": 1,
                                "hotel_facilities": "48,73,491,140,81,419,506,450,142,16,489,440,496,3,505,439,129,11,485,124,158,423,421,425,184,436,448,23,107,5,163,305,499,133,464,466,484,486,470,28,458,457,185,424,426,22,6,435,304,472,461,465,134,460,110,109,449,253,91,8,180,462,44,75,96,422,420,459,487,51,488,456,25,454,20,445,418,47,492,53,453,2,455,451,17,467,468,446,490,444,437",
                                "min_total_price": 67497.3,
                                "longitude": 72.8406912088394,
                                "hotel_include_breakfast": 0,
                                "accommodation_type_name": "Hotels",
                                "soldout": 0,
                                "ufi": -2092174,
                                "children_not_allowed": 0,
                                "badges": [],
                                "city_trans": "Mumbai",
                                "review_score_word": "Good",
                                "in_best_district": 0,
                                "timezone": "Asia/Kolkata",
                                "native_ad_id": "",
                                "latitude": 18.9362847065073,
                                "mobile_discount_percentage": 0,
                                "wishlist_count": 0,
                                "is_mobile_deal": 0,
                                "type": "property_card",
                                "address_trans": "17, Shri S.R. Marg, Ballard Estate ",
                                "is_genius_deal": 0,
                                "price_is_final": 0,
                                "is_free_cancellable": 1,
                                "address": "17, Shri S.R. Marg, Ballard Estate ",
                                "native_ads_cpc": 0,
                                "cant_book": 0,
                                "is_smart_deal": 0,
                                "review_recommendation": "",
                                "id": "property_card_350329",
                                "block_ids": [
                                "35032903_285673400_0_33_0"
                                ],
                                "zip": "400001",
                                "default_wishlist_name": "Mumbai",
                                "city_in_trans": "in Mumbai",
                                "country_trans": "India"
                            }
                            ]
                        }
            for item in range(len(response['result'])):
                results.append(response['result'][item])   
    except Exception as e:
        print(f'Error: {e}')
    context = {'results': results,'navbar': 'hotel', 'search_id': search_id}
    # print(results)
    return render(request, 'pages/hotel.html', context)

@login_required(login_url='loginUser')
def hotelinfo(request, hotel_id):
    response_hotel = None
    response_rooms = None
    
    if hotel_id:
        response_hotel = {
                        "review_score": 6.1,
                        "hotel_id": 1173150,
                        "distance": "0.88",
                        "extended": 0,
                        "checkout": {
                        "from": "",
                        "until": "12:00"
                        },
                        "url": "https://www.booking.com/hotel/in/balwas.html",

                        "hotel_has_vb_boost": 0,
                        "city_name_en": "Mumbai",
                        "main_photo_id": 373263707,
                        "cc1": "in",
                        "urgency_room_msg": "Deluxe Double Room",
                        "district": "South Mumbai",
                        "is_no_prepayment_block": 1,
                        "districts": "2379,17337",
                        "hotel_name": "Hotel Balwas",
                        "genius_discount_percentage": 0,
                        "class_is_estimated": 0,
                        "native_ads_tracking": "",
                        "is_geo_rate": "",
                        "default_language": "xu",
                        "review_nr": 8,
                        "hotel_name_trans": "Hotel Balwas",
                        "class": 2,
                        "city": "Mumbai",
                        "soldout": 0,
                        "hotel_include_breakfast": 0,
                        "accommodation_type_name": "Hotels",
                        "longitude": 72.8215692649429,
                        "min_total_price": 21546,
                        "cc_required": 1,
                        "wishlist_count": 0,
                        "mobile_discount_percentage": 2394,
                        "latitude": 18.961454675844,
                        "timezone": "Asia/Kolkata",
                        "review_score_word": "Pleasant",
                        "city_trans": "Mumbai",
                        "children_not_allowed": 0,
                        "ufi": -2092174,
                        "countrycode": "in",
                        "price_breakdown": {
                        "has_tax_exceptions": 0,
                        "has_incalculable_charges": 0,
                        "currency": "INR",
                        "sum_excluded_raw": 2585.52,
                        "has_fine_print_charges": 0,
                        "all_inclusive_price": 24131.52,
                        "gross_price": "21546.00"
                        },
                        "main_photo_url": "https://cf.bstatic.com/xdata/images/hotel/square300/373263707.jpg?k=6a433c2c1199b61afcfb8b8a97ca8cd3043530e5613f89142f2281c62d70eb52&o=",
                        "preferred": 1,
                        "currency_code": "INR",
                        "checkin": {
                        "from": "12:00",
                        "until": ""
                        },
                        "preferred_plus": 0,
                        "district_id": 2379,
                        "accommodation_type": 204,
                        "distance_to_cc": "0.90",
                        "deals": {
                        "deal_attributes": {},
                        "deals_available": {},
                        "deal_events_killswitch": 0
                        },
                        "currencycode": "INR",
                        "selected_review_topic": "null",
                        "id": "property_card_1173150",
                        "review_recommendation": "",
                        "is_smart_deal": 0,
                        "cant_book": 0,
                        "country_trans": "India",
                        "city_in_trans": "in Mumbai",
                        "default_wishlist_name": "Mumbai",
                        "zip": "400007",
                        "block_ids": [
                        "117315004_218048506_2_2_0"
                        ],
                        "price_is_final": 0,
                        "is_genius_deal": 0,
                        "address_trans": "323, Opposite Super Cinema, 12th Lane, Grant Road",
                        "type": "property_card",
                        "is_mobile_deal": 1,
                        "native_ads_cpc": 0,
                        "address": "323, Opposite Super Cinema, 12th Lane, Grant Road",
                        "is_free_cancellable": 1
                }
        response_rooms = {
                "duplicate_rates_removed": 0,
                "cc_required": "1",
                "hotel_id": 1173150,
                "is_cpv2_property": 1,
                "min_room_distribution": {
                    "adults": 2,
                    "children": []
                },
                "soldout_rooms": [],
                "top_ufi_benefits": [
                    {
                        "translated_name": "WiFi",
                        "icon": "wifi"
                    },
                    {
                        "translated_name": "Room service",
                        "icon": "clean"
                    },
                    {
                        "translated_name": "24-hour front desk",
                        "icon": "frontdesk"
                    },
                    {
                        "translated_name": "Facilities for disabled guests",
                        "icon": "disabled"
                    },
                    {
                        "translated_name": "Elevator",
                        "icon": "elevator"
                    },
                    {
                        "icon": "snowflake",
                        "translated_name": "Air conditioning"
                    }
                ],
                "cvc_required": "0",
                "tax_exceptions": [],
                "departure_date": "2022-12-10",
                "address_required": 0,
                "use_new_bui_icon_highlight": 0,
                "qualifies_for_no_cc_reservation": 0,
                "is_exclusive": "null",
                "max_rooms_in_reservation": 10,
                "block": [
                    {
                        "name_without_policy": "Deluxe Double Room",
                        "room_surface_in_feet2": 118.4030144,
                        "refundable": 1,
                        "smoking": 2,
                        "b_bsb_campaigns": [],
                        "dinner_included": 0,
                        "babycots_available_amount": "null",
                        "block_id": "117315004_218048506_2_2_0",
                        "children_ages": [],
                        "is_block_fit": 1,
                        "max_occupancy": 2,
                        "room_name": "Deluxe Double Room",
                        "room_count": 6,
                        "extrabed_available": 0,
                        "is_last_minute_deal": 0,
                        "mealplan": "Breakfast: Rs. 250 per person, per night",
                        "babycots_available": 0,
                        "is_secret_deal": 0,
                        "max_children_free_age": 7,
                        "highlights": [
                            {
                                "translated_name": "Free WiFi",
                                "icon": "icon_wifi",
                                "key": "wifi"
                            },
                            {
                                "id": 11,
                                "translated_name": "Air conditioning",
                                "icon": "icon_airconditioning"
                            },
                            {
                                "id": 38,
                                "translated_name": "Private bathroom",
                                "icon": "icon_private-shower"
                            },
                            {
                                "id": 75,
                                "translated_name": "Flat-screen TV",
                                "icon": "icon_flattv"
                            }
                        ],
                        "private_bathroom_count": 0,
                        "children_and_beds_text": {
                            "cribs_and_extra_beds": [
                                {
                                    "highlight": 0,
                                    "text": "Additional fees are not calculated automatically in the total cost and will have to be paid for separately during your stay."
                                },
                                {
                                    "text": "The maximum number of cribs, extra beds, and children allowed in existing beds can vary depending on the option booked.",
                                    "highlight": 0
                                },
                                {
                                    "text": "All cribs and extra beds are subject to availability.",
                                    "highlight": 0
                                },
                                {
                                    "text": "No capacity for cribs.",
                                    "highlight": 0
                                }
                            ],
                            "children_at_the_property": [
                                {
                                    "highlight": 0,
                                    "text": "Children of all ages are welcome."
                                },
                                {
                                    "text": "Children 18 and above are considered adults at this property.",
                                    "highlight": 0
                                },
                                {
                                    "text": "To see correct prices and occupancy info, add the number and ages of children in your group to your search.",
                                    "highlight": 1
                                }
                            ],
                            "allow_children": 1,
                            "age_intervals": [
                                {
                                    "min_age": 6,
                                    "max_age": 255,
                                    "group_by_price": {
                                        "fixed,per_night,708.00": [
                                            "extra_bed"
                                        ]
                                    },
                                    "extra_bed": {
                                        "price_type": "fixed",
                                        "id": 22624925,
                                        "price_mode_n": 0,
                                        "price_type_n": 2,
                                        "price": "Rs. 708",
                                        "price_mode": "per_night"
                                    },
                                    "types_by_price": [
                                        [
                                            "extra_bed"
                                        ]
                                    ]
                                }
                            ]
                        },
                        "facilities": [
                            {
                                "name": "swimming poo"
                            },
                            {
                                "name": " Free WiFi"
                            },
                            {
                                "name": "Airport shuttle"
                            },
                            {
                                "name": "Family rooms"
                            },
                            {
                                "name": "Free parking"
                            },

                        ],
                        "photos_may_sorted": 1,
                        "bed_configurations": [
                            {
                                "bed_types": [
                                    {
                                        "name_with_count": "2 twin beds",
                                        "description_localized": "null",
                                        "description_imperial": "35-51 inches wide",
                                        "name": "Twin bed(s)",
                                        "count": 2,
                                        "bed_type": 1,
                                        "description": "90-130 cm wide"
                                    }
                                ]
                            }
                        ],
                        "description": "This guest room is furnished with twin beds.  Master bed can be arranged if informed prior, but as per availability.  The room is approximately 120 square feet.  There is a 32\" LCD TV with set top box connection.  Complimentary WiFi.  Window air conditioner.  Mini refrigerator.  This room is both smoking and nonsmoking.",
                        "private_bathroom_highlight": {
                            "has_highlight": 1,
                            "text": "Private bathroom with shower"
                        },
                        "is_high_floor_guaranteed": 0,
                        "photo_last_update": "2022-07-05",
                        "photos": "https://cf.bstatic.com/xdata/images/hotel/max500/373263707.jpg?k=4231050bef445fca5d7809c74cba2f3f80aea6a551474246348c5791d237f09e&o=",
                        "block_text": {
                            "policies": [
                                {
                                    "content": "You can cancel for free until 1 day before arrival. You’ll be charged the cost of the first night if you cancel within 1 day of arrival.",
                                    "class": "POLICY_CANCELLATION"
                                },
                                {
                                    "content": "No prepayment is needed.",
                                    "class": "POLICY_PREPAY"
                                },
                                {
                                    "class": "POLICY_HOTEL_MEALPLAN",
                                    "content": "Breakfast: Rs. 250 per person, per night",
                                    "mealplan_vector": "2",
                                    "price": 250,
                                    "currencycode": "INR"
                                },
                                {
                                    "content": "General",
                                    "class": "POLICY_TITLE"
                                }
                            ]
                        },
                        "name": "Deluxe Double Room - Free cancellation",
                        "refundable_until": "2022-11-29 23:59:59 +0530",
                        "detail_mealplan": [
                            {
                                "price": 250,
                                "icon": "coffee",
                                "currency": "INR",
                                "title": "Breakfast available (Vegetarian, Halal)"
                            }
                        ],
                        "paymentterms": {
                            "cancellation": {
                                "bucket": "SMP_FLEX",
                                "type_translation": "Free to cancel",
                                "info": {
                                    "date": "November 30, 2022",
                                    "date_raw": "2022-11-30 00:00:00",
                                    "timezone_offset": "19800",
                                    "date_before_raw": "2022-11-29",
                                    "refundable": 1,
                                    "time": "12:00 AM",
                                    "timezone": "IST",
                                    "date_before": "November 29, 2022",
                                    "time_before_midnight": "11:59 PM",
                                    "is_midnight": 1
                                },
                                "guaranteed_non_refundable": 0,
                                "timeline": {
                                    "currency_code": "INR",
                                    "nr_stages": 2,
                                    "policygroup_instance_id": "36/152/-",
                                    "u_currency_code": "INR",
                                    "stages": [
                                        {
                                            "fee_remaining": 21546,
                                            "text_refundable": "You'll get a full refund if you cancel before 11:59 PM on November 29, 2022.",
                                            "b_number": 0,
                                            "limit_until_raw": "2022-11-29 23:59:59",
                                            "limit_from_raw": "2022-09-26 10:04:10",
                                            "limit_until_time": "11:59 PM",
                                            "u_fee_remaining": "21546.00",
                                            "limit_timezone": "Mumbai",
                                            "u_fee_pretty": "INR 0",
                                            "u_stage_fee": "0.00",
                                            "b_state": "FREE",
                                            "effective_number": 0,
                                            "is_effective": 1,
                                            "fee": 0,
                                            "date_until": "2022-11-29 23:59:59 +0530",
                                            "limit_until_date": "November 29, 2022",
                                            "is_free": 1,
                                            "stage_fee_pretty": "INR 0",
                                            "stage_translation": "Free to cancel",
                                            "u_fee_remaining_pretty": "INR 21546",
                                            "limit_until": "November 29, 2022 11:59 PM",
                                            "current_stage": 1,
                                            "limit_from_date": "September 26, 2022",
                                            "stage_fee": 0,
                                            "u_fee": "0.00",
                                            "fee_rounded": 0,
                                            "limit_from": "September 26, 2022 10:04 AM",
                                            "text": "Free cancellation until 11:59 PM on Nov 29",
                                            "u_stage_fee_pretty": "INR 0",
                                            "limit_from_time": "10:04 AM",
                                            "fee_pretty": "INR 0",
                                            "fee_remaining_pretty": "INR 21546"
                                        },
                                        {
                                            "b_state": "PAID",
                                            "u_stage_fee": "2394.00",
                                            "u_fee_pretty": "INR 2394",
                                            "limit_until_date": "November 30, 2022",
                                            "amount": "2394.00",
                                            "fee": 2394,
                                            "is_effective": 1,
                                            "effective_number": 1,
                                            "text_refundable": "If you cancel before 12:00 AM on November 30, 2022, you'll get a INR 19152 refund.",
                                            "fee_remaining": 19152,
                                            "limit_timezone": "Mumbai",
                                            "u_fee_remaining": "19152.00",
                                            "amount_pretty": "INR 2394",
                                            "limit_until_time": "12:00 AM",
                                            "limit_until_raw": "2022-11-30 00:00:00",
                                            "limit_from_raw": "2022-11-30 00:00:00",
                                            "b_number": 1,
                                            "text": "From 12:00 AM on Nov 30",
                                            "limit_from": "November 30, 2022 12:00 AM",
                                            "fee_rounded": 2394,
                                            "u_fee": "2394.00",
                                            "fee_remaining_pretty": "INR 19152",
                                            "fee_pretty": "INR 2394",
                                            "limit_from_time": "12:00 AM",
                                            "u_stage_fee_pretty": "INR 2394",
                                            "limit_until": "November 30, 2022 12:00 AM",
                                            "u_fee_remaining_pretty": "INR 19152",
                                            "stage_translation": "Partial refund if you cancel",
                                            "is_free": 0,
                                            "stage_fee_pretty": "INR 2394",
                                            "date_from": "2022-11-30 00:00:00 +0530",
                                            "stage_fee": 2394,
                                            "limit_from_date": "November 30, 2022",
                                            "current_stage": 0
                                        }
                                    ]
                                },
                                "description": "You can cancel for free until 1 day before arrival. You’ll be charged the cost of the first night if you cancel within 1 day of arrival.",
                                "non_refundable_anymore": 0,
                                "type": "free_cancellation"
                            },
                            "prepayment": {
                                "info": {
                                    "timezone_offset": "null",
                                    "date": "null",
                                    "time": "null",
                                    "refundable": "anytime",
                                    "date_before": "null",
                                    "prepayment_at_booktime": 0,
                                    "timezone": "null",
                                    "time_before_midnight": "null",
                                    "is_midnight": ''
                                },
                                "type_translation": "No payment needed today",
                                "extended_type_translation": "No payment needed today",
                                "type": "no_prepayment",
                                "description": "You'll pay during your stay.",
                                "type_extended": "non_refundable_prepayment",
                                "timeline": {
                                    "currency_code": "INR",
                                    "policygroup_instance_id": "36/152/-",
                                    "nr_stages": 2,
                                    "u_currency_code": "INR",
                                    "stages": [
                                        {
                                            "stage_fee": 0,
                                            "limit_from_date": "September 26, 2022",
                                            "current_stage": 1,
                                            "limit_until": "December 1, 2022 11:59 PM",
                                            "stage_fee_pretty": "INR 0",
                                            "is_free": 1,
                                            "u_fee_remaining_pretty": "INR 21546",
                                            "fee_remaining_pretty": "INR 21546",
                                            "fee_pretty": "INR 0",
                                            "u_stage_fee_pretty": "INR 0",
                                            "limit_from_time": "10:04 AM",
                                            "text": "Before you stay you'll pay",
                                            "limit_from": "September 26, 2022 10:04 AM",
                                            "u_fee": "0.00",
                                            "fee_rounded": 0,
                                            "amount_pretty": "INR 0",
                                            "u_fee_remaining": "21546.00",
                                            "limit_timezone": "Mumbai",
                                            "limit_until_time": "11:59 PM",
                                            "b_number": 0,
                                            "limit_until_raw": "2022-12-01 23:59:59",
                                            "limit_from_raw": "2022-09-26 10:04:10",
                                            "fee_remaining": 21546,
                                            "limit_until_date": "December 1, 2022",
                                            "fee": 0,
                                            "amount": "0.00",
                                            "effective_number": 0,
                                            "is_effective": 1,
                                            "b_state": "FREE",
                                            "u_stage_fee": "0.00",
                                            "u_fee_pretty": "INR 0"
                                        },
                                        {
                                            "after_checkin": 1,
                                            "is_free": 0,
                                            "amount_pretty": "INR 21546",
                                            "text": "At the property you'll pay",
                                            "amount": "21546.00"
                                        }
                                    ]
                                },
                                "simple_translation": "No prepayment"
                            }
                        },
                        "product_price_breakdown": {
                            "discounted_amount": {
                                "value": 3654,
                                "currency": "INR"
                            },
                            "all_inclusive_amount": {
                                "value": 24131.5199422091,
                                "currency": "INR"
                            },
                            "gross_amount": {
                                "value": 21546,
                                "currency": "INR"
                            },
                            "nr_stays": 3,
                            "net_amount": {
                                "currency": "INR",
                                "value": 21546
                            },
                            "strikethrough_amount_per_night": {
                                "value": 2800,
                                "currency": "INR"
                            },
                            "has_long_stays_monthly_rate_price": 0,
                            "gross_amount_hotel_currency": {
                                "currency": "INR",
                                "value": 21546
                            },
                            "included_taxes_and_charges_amount": {
                                "value": 0,
                                "currency": "INR"
                            },
                            "gross_amount_per_night": {
                                "value": 2394,
                                "currency": "INR"
                            }
                        }
                    }
                ],
                "room_recommendation": [
                    {
                        "adults": 2,
                        "total_extra_bed_price_in_hotel_currency": 0,
                        "number_of_extra_beds": 0,
                        "babies": 0,
                        "children": 0,
                        "total_extra_bed_price": 0,
                        "block_id": "117315004_218048506_2_2_0"
                    }
                ],
                "total_blocks": 4
            }
    
    map = folium.Map(location=[response_hotel['latitude'], response_hotel['longitude']], zoom_start= 14, width='100%', height=700)
    folium.Marker([response_hotel['latitude'], response_hotel['longitude']]).add_to(map)
    map = map._repr_html_()
    context = {'navbar': 'hotelinfo', 'response_rooms': response_rooms, 'response_hotel': response_hotel ,'map': map}
    return render(request, 'pages/hotelinfo.html', context)

@login_required(login_url='loginUser')
def bookings(request, hotel_name):
    response_rooms = {             
                "hotel_name": "Hotel Balwas",
                "address": "323, Opposite Super Cinema, 12th Lane, Grant Road",

                "min_room_distribution": {
                    "adults": 2,
                    "children": []
                },
                "ratings": "5.7",
                "soldout_rooms": [],
                "tax_exceptions": [],
                "start_date": "2022-01-10",
                "departure_date": "2022-12-10",
                "address_required": 0,
                "use_new_bui_icon_highlight": 0,
                "qualifies_for_no_cc_reservation": 0,
                "is_exclusive": "null",
                "max_rooms_in_reservation": 10,
                "block": [
                    {
                        "name_without_policy": "Deluxe Double Room",
                        "room_surface_in_feet2": 118.4030144,
                        "refundable": 1,
                        "smoking": 2,
                        "b_bsb_campaigns": [],
                        "dinner_included": 0,
                        "babycots_available_amount": "null",
                        "block_id": "117315004_218048506_2_2_0",
                        "children_ages": [],
                        "is_block_fit": 1,
                        "max_occupancy": 2,
                        "room_name": "Deluxe Double Room",
                        "room_count": 6,
                        "extrabed_available": 0,
                        "is_last_minute_deal": 0,
                        "mealplan": "Breakfast: Rs. 250 per person, per night",
                        "babycots_available": 0,
                        "is_secret_deal": 0,
                        "max_children_free_age": 7,
                        "highlights": [
                            {
                                "translated_name": "Free WiFi",
                                "icon": "icon_wifi",
                                "key": "wifi"
                            },
                            {
                                "id": 11,
                                "translated_name": "Air conditioning",
                                "icon": "icon_airconditioning"
                            },
                            {
                                "id": 38,
                                "translated_name": "Private bathroom",
                                "icon": "icon_private-shower"
                            },
                            {
                                "id": 75,
                                "translated_name": "Flat-screen TV",
                                "icon": "icon_flattv"
                            }
                        ],
                        "private_bathroom_count": 0,
                        "children_and_beds_text": {
                            "cribs_and_extra_beds": [
                                {
                                    "highlight": 0,
                                    "text": "Additional fees are not calculated automatically in the total cost and will have to be paid for separately during your stay."
                                },
                                {
                                    "text": "The maximum number of cribs, extra beds, and children allowed in existing beds can vary depending on the option booked.",
                                    "highlight": 0
                                },
                                {
                                    "text": "All cribs and extra beds are subject to availability.",
                                    "highlight": 0
                                },
                                {
                                    "text": "No capacity for cribs.",
                                    "highlight": 0
                                }
                            ],
                            "children_at_the_property": [
                                {
                                    "highlight": 0,
                                    "text": "Children of all ages are welcome."
                                },
                                {
                                    "text": "Children 18 and above are considered adults at this property.",
                                    "highlight": 0
                                },
                                {
                                    "text": "To see correct prices and occupancy info, add the number and ages of children in your group to your search.",
                                    "highlight": 1
                                }
                            ],
                            "allow_children": 1,
                            "age_intervals": [
                                {
                                    "min_age": 6,
                                    "max_age": 255,
                                    "group_by_price": {
                                        "fixed,per_night,708.00": [
                                            "extra_bed"
                                        ]
                                    },
                                    "extra_bed": {
                                        "price_type": "fixed",
                                        "id": 22624925,
                                        "price_mode_n": 0,
                                        "price_type_n": 2,
                                        "price": "Rs. 708",
                                        "price_mode": "per_night"
                                    },
                                    "types_by_price": [
                                        [
                                            "extra_bed"
                                        ]
                                    ]
                                }
                            ]
                        },
                        "facilities": [
                            {
                                "name": "swimming poo"
                            },
                            {
                                "name": " Free WiFi"
                            },
                            {
                                "name": "Airport shuttle"
                            },
                            {
                                "name": "Family rooms"
                            },
                            {
                                "name": "Free parking"
                            },

                        ],
                        "photos_may_sorted": 1,
                        "bed_configurations": [
                            {
                                "bed_types": [
                                    {
                                        "name_with_count": "2 twin beds",
                                        "description_localized": "null",
                                        "description_imperial": "35-51 inches wide",
                                        "name": "Twin bed(s)",
                                        "count": 2,
                                        "bed_type": 1,
                                        "description": "90-130 cm wide"
                                    }
                                ]
                            }
                        ],
                        "description": "This guest room is furnished with twin beds.  Master bed can be arranged if informed prior, but as per availability.  The room is approximately 120 square feet.  There is a 32\" LCD TV with set top box connection.  Complimentary WiFi.  Window air conditioner.  Mini refrigerator.  This room is both smoking and nonsmoking.",
                        "private_bathroom_highlight": {
                            "has_highlight": 1,
                            "text": "Private bathroom with shower"
                        },
                        "is_high_floor_guaranteed": 0,
                        "photo_last_update": "2022-07-05",
                        "photos": "https://cf.bstatic.com/xdata/images/hotel/max500/373263707.jpg?k=4231050bef445fca5d7809c74cba2f3f80aea6a551474246348c5791d237f09e&o=",
                        "block_text": {
                            "policies": [
                                {
                                    "content": "You can cancel for free until 1 day before arrival. You’ll be charged the cost of the first night if you cancel within 1 day of arrival.",
                                    "class": "POLICY_CANCELLATION"
                                },
                                {
                                    "content": "No prepayment is needed.",
                                    "class": "POLICY_PREPAY"
                                },
                                {
                                    "class": "POLICY_HOTEL_MEALPLAN",
                                    "content": "Breakfast: Rs. 250 per person, per night",
                                    "mealplan_vector": "2",
                                    "price": 250,
                                    "currencycode": "INR"
                                },
                                {
                                    "content": "General",
                                    "class": "POLICY_TITLE"
                                }
                            ]
                        },
                        "name": "Deluxe Double Room - Free cancellation",
                        "refundable_until": "2022-11-29 23:59:59 +0530",
                        "detail_mealplan": [
                            {
                                "price": 250,
                                "icon": "coffee",
                                "currency": "INR",
                                "title": "Breakfast available (Vegetarian, Halal)"
                            }
                        ],
                        "paymentterms": {
                            "cancellation": {
                                "bucket": "SMP_FLEX",
                                "type_translation": "Free to cancel",
                                "info": {
                                    "date": "November 30, 2022",
                                    "date_raw": "2022-11-30 00:00:00",
                                    "timezone_offset": "19800",
                                    "date_before_raw": "2022-11-29",
                                    "refundable": 1,
                                    "time": "12:00 AM",
                                    "timezone": "IST",
                                    "date_before": "November 29, 2022",
                                    "time_before_midnight": "11:59 PM",
                                    "is_midnight": 1
                                },
                                "guaranteed_non_refundable": 0,
                                "timeline": {
                                    "currency_code": "INR",
                                    "nr_stages": 2,
                                    "policygroup_instance_id": "36/152/-",
                                    "u_currency_code": "INR",
                                    "stages": [
                                        {
                                            "fee_remaining": 21546,
                                            "text_refundable": "You'll get a full refund if you cancel before 11:59 PM on November 29, 2022.",
                                            "b_number": 0,
                                            "limit_until_raw": "2022-11-29 23:59:59",
                                            "limit_from_raw": "2022-09-26 10:04:10",
                                            "limit_until_time": "11:59 PM",
                                            "u_fee_remaining": "21546.00",
                                            "limit_timezone": "Mumbai",
                                            "u_fee_pretty": "INR 0",
                                            "u_stage_fee": "0.00",
                                            "b_state": "FREE",
                                            "effective_number": 0,
                                            "is_effective": 1,
                                            "fee": 0,
                                            "date_until": "2022-11-29 23:59:59 +0530",
                                            "limit_until_date": "November 29, 2022",
                                            "is_free": 1,
                                            "stage_fee_pretty": "INR 0",
                                            "stage_translation": "Free to cancel",
                                            "u_fee_remaining_pretty": "INR 21546",
                                            "limit_until": "November 29, 2022 11:59 PM",
                                            "current_stage": 1,
                                            "limit_from_date": "September 26, 2022",
                                            "stage_fee": 0,
                                            "u_fee": "0.00",
                                            "fee_rounded": 0,
                                            "limit_from": "September 26, 2022 10:04 AM",
                                            "text": "Free cancellation until 11:59 PM on Nov 29",
                                            "u_stage_fee_pretty": "INR 0",
                                            "limit_from_time": "10:04 AM",
                                            "fee_pretty": "INR 0",
                                            "fee_remaining_pretty": "INR 21546"
                                        },
                                        {
                                            "b_state": "PAID",
                                            "u_stage_fee": "2394.00",
                                            "u_fee_pretty": "INR 2394",
                                            "limit_until_date": "November 30, 2022",
                                            "amount": "2394.00",
                                            "fee": 2394,
                                            "is_effective": 1,
                                            "effective_number": 1,
                                            "text_refundable": "If you cancel before 12:00 AM on November 30, 2022, you'll get a INR 19152 refund.",
                                            "fee_remaining": 19152,
                                            "limit_timezone": "Mumbai",
                                            "u_fee_remaining": "19152.00",
                                            "amount_pretty": "INR 2394",
                                            "limit_until_time": "12:00 AM",
                                            "limit_until_raw": "2022-11-30 00:00:00",
                                            "limit_from_raw": "2022-11-30 00:00:00",
                                            "b_number": 1,
                                            "text": "From 12:00 AM on Nov 30",
                                            "limit_from": "November 30, 2022 12:00 AM",
                                            "fee_rounded": 2394,
                                            "u_fee": "2394.00",
                                            "fee_remaining_pretty": "INR 19152",
                                            "fee_pretty": "INR 2394",
                                            "limit_from_time": "12:00 AM",
                                            "u_stage_fee_pretty": "INR 2394",
                                            "limit_until": "November 30, 2022 12:00 AM",
                                            "u_fee_remaining_pretty": "INR 19152",
                                            "stage_translation": "Partial refund if you cancel",
                                            "is_free": 0,
                                            "stage_fee_pretty": "INR 2394",
                                            "date_from": "2022-11-30 00:00:00 +0530",
                                            "stage_fee": 2394,
                                            "limit_from_date": "November 30, 2022",
                                            "current_stage": 0
                                        }
                                    ]
                                },
                                "description": "You can cancel for free until 1 day before arrival. You’ll be charged the cost of the first night if you cancel within 1 day of arrival.",
                                "non_refundable_anymore": 0,
                                "type": "free_cancellation"
                            },
                            "prepayment": {
                                "info": {
                                    "timezone_offset": "null",
                                    "date": "null",
                                    "time": "null",
                                    "refundable": "anytime",
                                    "date_before": "null",
                                    "prepayment_at_booktime": 0,
                                    "timezone": "null",
                                    "time_before_midnight": "null",
                                    "is_midnight": ''
                                },
                                "type_translation": "No payment needed today",
                                "extended_type_translation": "No payment needed today",
                                "type": "no_prepayment",
                                "description": "You'll pay during your stay.",
                                "type_extended": "non_refundable_prepayment",
                                "timeline": {
                                    "currency_code": "INR",
                                    "policygroup_instance_id": "36/152/-",
                                    "nr_stages": 2,
                                    "u_currency_code": "INR",
                                    "stages": [
                                        {
                                            "stage_fee": 0,
                                            "limit_from_date": "September 26, 2022",
                                            "current_stage": 1,
                                            "limit_until": "December 1, 2022 11:59 PM",
                                            "stage_fee_pretty": "INR 0",
                                            "is_free": 1,
                                            "u_fee_remaining_pretty": "INR 21546",
                                            "fee_remaining_pretty": "INR 21546",
                                            "fee_pretty": "INR 0",
                                            "u_stage_fee_pretty": "INR 0",
                                            "limit_from_time": "10:04 AM",
                                            "text": "Before you stay you'll pay",
                                            "limit_from": "September 26, 2022 10:04 AM",
                                            "u_fee": "0.00",
                                            "fee_rounded": 0,
                                            "amount_pretty": "INR 0",
                                            "u_fee_remaining": "21546.00",
                                            "limit_timezone": "Mumbai",
                                            "limit_until_time": "11:59 PM",
                                            "b_number": 0,
                                            "limit_until_raw": "2022-12-01 23:59:59",
                                            "limit_from_raw": "2022-09-26 10:04:10",
                                            "fee_remaining": 21546,
                                            "limit_until_date": "December 1, 2022",
                                            "fee": 0,
                                            "amount": "0.00",
                                            "effective_number": 0,
                                            "is_effective": 1,
                                            "b_state": "FREE",
                                            "u_stage_fee": "0.00",
                                            "u_fee_pretty": "INR 0"
                                        },
                                        {
                                            "after_checkin": 1,
                                            "is_free": 0,
                                            "amount_pretty": "INR 21546",
                                            "text": "At the property you'll pay",
                                            "amount": "21546.00"
                                        }
                                    ]
                                },
                                "simple_translation": "No prepayment"
                            }
                        },
                        "product_price_breakdown": {
                            "discounted_amount": {
                                "value": 3654,
                                "currency": "INR"
                            },
                            "all_inclusive_amount": {
                                "value": 24131.5199422091,
                                "currency": "INR"
                            },
                            "gross_amount": {
                                "value": 21546,
                                "currency": "INR"
                            },
                            "nr_stays": 3,
                            "net_amount": {
                                "currency": "INR",
                                "value": 21546
                            },
                            "strikethrough_amount_per_night": {
                                "value": 2800,
                                "currency": "INR"
                            },
                            "has_long_stays_monthly_rate_price": 0,
                            "gross_amount_hotel_currency": {
                                "currency": "INR",
                                "value": 21546
                            },
                            "included_taxes_and_charges_amount": {
                                "value": 0,
                                "currency": "INR"
                            },
                            "gross_amount_per_night": {
                                "value": 2394,
                                "currency": "INR"
                            }
                        }
                    }
                ],
                "room_recommendation": [
                    {
                        "adults": 2,
                        "total_extra_bed_price_in_hotel_currency": 0,
                        "number_of_extra_beds": 0,
                        "babies": 0,
                        "children": 0,
                        "total_extra_bed_price": 0,
                        "block_id": "117315004_218048506_2_2_0"
                    }
                ],
                "total_blocks": 4
            }
    hotelname = response_rooms['hotel_name']
    hotel_img = response_rooms['block'][0]['photos']
    location = response_rooms['address']
    room_name = response_rooms['block'][0]['room_name']
    total_amount= response_rooms['block'][0]['product_price_breakdown']['gross_amount']['value']
    start_date = response_rooms['start_date']
    end_date = response_rooms['departure_date']
    print(hotel_name, hotel_img, location, room_name, total_amount, start_date, end_date)
    if request.method == 'POST':
        email = request.POST.get('email_input')
        user_obj = User.objects.filter(email = email).first()
        profile_obj = CustomerProfile.objects.filter(user = user_obj).first()
        book = Bookings(customer = profile_obj, hotelname =  hotelname, hotel_img = hotel_img,room_des = room_name, total_amount = total_amount, location = location,start_date = start_date, end_date = end_date)
        book.save()
        return redirect('/checkout/'+ str(email) +'/'+ str(hotel_name) +'/'+ str(total_amount))
    context = {'navbar': 'bookings', 'response_rooms': response_rooms}
    return render(request, 'pages/booking.html',context)

@login_required(login_url='loginUser')
def aboutus(request):
    context = {'navbar': 'aboutus'}
    return render(request, 'pages/aboutus.html', context)

@login_required(login_url='loginUser')
def contactus(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        user_obj = User.objects.filter(email = email).first()
        profile_obj = CustomerProfile.objects.filter(user = user_obj).first()
        contact = Contact(customer= profile_obj, name= name, email= email, subject= subject, message= message)
        contact.save()
        messages.success(request, 'Your message is sent successfully!')
        return HttpResponseRedirect(request.path_info)
    context = {'navbar': 'contactus'}
    return render(request, 'pages/contactus.html',context)

@login_required(login_url='loginUser')
def destination(request):
    location = request.GET.get('placename')
    min_rating = request.GET.get('min_rating')
    print(min_rating)
    location_code = geocoder.osm(location)
    results = None
    rate_list = [1,2,3,4,5]
    if location:
        url = "https://travel-advisor.p.rapidapi.com/attractions/list-in-boundary"
        querystring = {
            "tr_longitude":location_code.northeast[1],
            "tr_latitude":location_code.northeast[0],
            "bl_longitude":location_code.southwest[1],
            "bl_latitude": location_code.southwest[0],
            "min_rating":min_rating,
            "currency":"INR",
            "lunit":"km",
            "lang":"en_US"}

        headers = {
            "X-RapidAPI-Key": settings.RAPID_API_KEY,
            "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring).json()
        results = response['data']

    context = {'navbar': 'destination', 'results': results , 'location': location, 'rate_list': rate_list}
    return render(request, 'pages/destination.html', context)

@login_required(login_url='loginUser')
def destinationinfo(request, location_id):
    url = "https://travel-advisor.p.rapidapi.com/attractions/list"

    querystring = {"location_id": f'{location_id}',
                   "currency":"INR",
                   "lang":"en_US",
                   "lunit":"km",
                   "sort":"recommended"}

    headers = {
        "X-RapidAPI-Key": settings.RAPID_API_KEY,
        "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    result = response['data'][0]
    map = folium.Map(location=[result['latitude'], result['longitude']], zoom_start= 13, width='100%', height=700)
    folium.Marker([result['latitude'], result['longitude']]).add_to(map)
    map = map._repr_html_()
    # pprint.pprint(result)
    context = {'navbar': 'destinationinfo', 'result' : result, 'map': map}
    return render(request, 'pages/destinationinfo.html', context)

@login_required(login_url='loginUser')
def profile(request, user):
    user_obj = User.objects.filter(username = user).first()
    profile_obj = CustomerProfile.objects.get(user = user_obj.id)
    # customer = CustomerProfile.objects.get(user = user)
    # print(customer)
    orders = profile_obj.bookings_set.all()
    print(orders)
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    gender = request.POST.get('gender')
    profile_img = request.POST.get('profile_img')
    phonenumber = request.POST.get('phonenumber')
    country = request.POST.get('country')
    state = request.POST.get('state')
    city = request.POST.get('city')
    street = request.POST.get('street')
    pincode = request.POST.get('pincode')
    if request.method == 'POST':
        profile_obj.firstname = firstname 
        profile_obj.lastname = lastname
        profile_obj.gender = gender
        profile_obj.phonenumber = phonenumber
        profile_obj.country = country
        profile_obj.state = state
        profile_obj.city = city
        profile_obj.street = street
        profile_obj.pincode = pincode
        profile_obj.profile_img = profile_img
        profile_obj.save()
        messages.success(request, "Your Profile has been modified!")
        return HttpResponseRedirect(request.path_info)

    
    context = {'navbar': 'profile','user_obj': user_obj ,'profile_obj': profile_obj, 'orders': orders}
    return render(request, 'pages/profile.html', context)

@login_required(login_url='loginUser')
def transport(request):
    context = {'navbar': 'transport'}
    return render(request, 'pages/transport.html', context)

def calculate(amount):
    return amount * 100

def checkout(request, email, hotel_name, hotel_price):
    YOUR_DOMAIN = 'http://127.0.0.1:8000/payment/'
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                # TODO - replace hardcoded value of product price id to dynamic 
                'price_data':{
                    'currency': 'inr',
                    'unit_amount': calculate(hotel_price),
                    'product_data':{
                        'name': hotel_name,
                    },
                }, 
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=YOUR_DOMAIN + 'success' + '/' + str(email),
        cancel_url=YOUR_DOMAIN + 'cancel',
    )
    
    return redirect(checkout_session.url, code=303)

def success(request, email):
    user_obj = User.objects.filter(email = email).first()
    profile_obj = CustomerProfile.objects.filter(user = user_obj).first()
    book_obj = Bookings.objects.filter(customer = profile_obj).first()
    if book_obj:
        book_obj.payment_status = True
        book_obj.status = 'Pending'
        book_obj.save()
    return render(request, 'payment/success.html')

def cancel(request):
    return render(request, 'payment/cancel.html')












