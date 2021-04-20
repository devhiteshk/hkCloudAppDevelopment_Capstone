from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
def logout_request(request):
    context = {}
    logout(request)
    return render(request, 'djangoapp/index.html', context)

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            pass
        if not user_exist:
            user = User.objects.create_user(username=username, 
                                            first_name=first_name, 
                                            last_name=last_name,
                                            password=password)
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        dealerships = get_dealers_from_cf("https://af176ef2.us-south.apigw.appdomain.cloud/api/dealership/")
        context['dealer_list'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        # Get reviews from the URL
        reviews = get_dealer_reviews_from_cf("https://af176ef2.us-south.apigw.appdomain.cloud/api/review/", dealer_id)
        context['review_list'] = reviews
        context['dealer_id'] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    if request.method == "GET":
        context["dealer_id"] = dealer_id
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            context["error_message"] = "Please, login at first"
            context["dealer_id"] = dealer_id
            return render(request, 'djangoapp/add_review.html', context)

        review = {}
        review["id"] = 0
        review["name"] = request.POST["createreviewform_name"]
        review["dealership"] = dealer_id
        review["review"] = request.POST["createreviewform_review"]
        review["purchase"] = request.POST["createreviewform_purchase"]
        review["purchase_date"] = request.POST["createreviewform_purchase_date"]
        review["car_make"] = request.POST["createreviewform_car_make"]
        review["car_model"] = request.POST["createreviewform_car_model"]
        review["car_year"] = request.POST["createreviewform_car_year"]
        json_payload = {}
        json_payload["review"] = review
        json_result = post_request("https://af176ef2.us-south.apigw.appdomain.cloud/api/review/", json_payload, dealerId=dealer_id)
        print("POST request result: ", json_result)
        if json_result["status"] == 200:
            context["success_message"] = "Review submitted!"
        else:
            context["error_message"] = "ERROR: Review not submitted."
        context["dealer_id"] = dealer_id
        return render(request, 'djangoapp/add_review.html', context)