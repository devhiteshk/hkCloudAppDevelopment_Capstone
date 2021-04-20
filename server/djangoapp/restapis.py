import requests
import json
import urllib
import datetime
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


def get_req(url, api_key=None, **kwargs):
    print(kwargs)
    print(f"GET {url}")
    try:
        if api_key:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except Exception as e:
        print("ERROR: ", e)
    print(f"Status Code: {response.status_code}")
    json_data = json.loads(response.text)
    return json_data

def post_request(url, json_payload, **kwargs):
    print("Payload: ", json_payload, ". Params: ", kwargs)
    print(f"POST {url}")
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                json=json_payload, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def get_dealers_from_cf(url, state=""):
    results = []
    if state == "":
        json_result = get_req(url)
    else:
        json_result = get_req(url, state=state)
    if json_result:
        dealers = json_result["entries"]
        for dealer in dealers:
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],state=dealer["state"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    return results


def get_dealer_by_id_from_cf(url, dealer_id):
    json_result = get_req(url, id=dealer_id)

    if json_result:
        dealers = json_result["entries"]
        for dealer in dealers:
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],state=dealer["state"],
                                   st=dealer["st"], zip=dealer["zip"])
            return dealer_obj

    return None

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_req(url, dealerId=dealer_id)
    if json_result:
        reviews = json_result["entries"]
        for review in reviews:
            if review["purchase"]:
                review_obj = DealerReview(make=review["car_make"], model=review["car_model"], 
                                    year=review["car_year"], dealer_id=review["dealership"], 
                                    id=review["id"], name=review["name"], purchase=review["purchase"], 
                                    purchase_date=review["purchase_date"], review=review["review"])
            else:
                review_obj = DealerReview(dealer_id=review["dealership"], 
                                    id=review["id"], name=review["name"], purchase=review["purchase"], 
                                    review=review["review"])
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)

    return results

def analyze_review_sentiments(text):
    result = "Not checked"
    try:
        json_result = get_req(url="https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/c87588c7-d3f9-44df-abdd-a33cdbb78b2d", 
                        api_key="L-gngL9J4fA1sHEIKdva3bLcj-DIPC5pbNGrr9ASD-k1", 
                        version="2021-03-25",
                        features="sentiment",
                        text=urllib.parse.quote_plus(text))
        result = json_result["sentiment"]["document"]["label"]
    finally:
        return result