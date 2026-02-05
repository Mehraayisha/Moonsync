from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings

def get_nearby_doctors(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if not lat or not lon:
        return JsonResponse({"error": "Location not provided"}, status=400)

    # Geoapify API key from settings.py
    geoapify_key =  settings.GEOAPIFY_API_KEY

    # Geoapify URL (gynecology doctors)
    url = (
        "https://api.geoapify.com/v2/places?"
        "categories=healthcare.clinic_or_praxis.gynaecology"
        f"&bias=circle:{lon},{lat},10000"
        "&limit=20"
        f"&apiKey={geoapify_key}"
    )

    response = requests.get(url)
    data = response.json()

    doctors = []

    # Check if data available
    if "features" in data:
        for place in data["features"]:
            props = place.get("properties", {})

            doctor = {
                "name": props.get("name", "No name available"),
                "address": props.get("formatted", "No address available"),
                "phone": props.get("contact", {}).get("phone", "N/A"),
                "website": props.get("website", "#"),
                "distance": props.get("distance", 0),
            }

            doctors.append(doctor)

        return JsonResponse({"doctors": doctors})

    return JsonResponse({"error": "No doctors found nearby"})
