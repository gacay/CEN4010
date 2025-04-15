import os
import re
import requests
import random
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


@api_view(['GET'])
def test_view(request):
    return Response({"message": "Hello from DateDash backend!"})


@api_view(['POST'])
def recommend_view(request):
    try:
        zipcode = request.data.get("zipcode")
        category = request.data.get("category")

        print("📩 Received request with:", {"zipcode": zipcode, "category": category})
        print("🔑 GOOGLE_API_KEY:", "SET" if GOOGLE_API_KEY else "MISSING")

        # Validate input
        if not zipcode or not re.fullmatch(r"\d{5}", zipcode):
            return Response({"error": "Invalid zip code."}, status=status.HTTP_400_BAD_REQUEST)

        if not category:
            return Response({"error": "Category is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Convert zip code to lat/lng using Google Geocoding API
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zipcode}&key={GOOGLE_API_KEY}"
        print("🌍 Geocode URL:", geocode_url)

        geo_response = requests.get(geocode_url).json()
        print("📍 Geocode Response:", geo_response)

        if geo_response["status"] != "OK":
            return Response({"error": "Failed to geocode zip code."}, status=status.HTTP_400_BAD_REQUEST)

        location = geo_response["results"][0]["geometry"]["location"]
        lat, lng = location["lat"], location["lng"]

        # Step 2: Call Google Places API
        places_url = (
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}"
            f"&radius=5000"
            f"&type={category}"
            f"&key={GOOGLE_API_KEY}"
        )
        print("📍 Places URL:", places_url)

        places_response = requests.get(places_url).json()
        print("🏙️ Places Response:", places_response)

        if places_response["status"] != "OK" or not places_response.get("results"):
            return Response({"error": "No places found for this category and zip code."}, status=status.HTTP_404_NOT_FOUND)

        # Step 3: Pick a random result and return
        random_place = random.choice(places_response["results"])
        name = random_place.get("name")
        address = random_place.get("vicinity")

        return Response({
            "name": name,
            "address": address,
            "category": category,
            "zipcode": zipcode
        })

    except Exception as e:
        print("❌ ERROR in recommend_view:", e)
        return Response({
            "error": "Internal server error",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
