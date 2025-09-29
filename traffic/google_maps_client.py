import os
import time
import requests

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

class Eta:
    def __init__(self, origin, destination, distance_meters, duration_seconds, duration_in_traffic_seconds):
        self.origin = origin
        self.destination = destination
        self.distance_meters = distance_meters
        self.duration_seconds = duration_seconds
        self.duration_in_traffic_seconds = duration_in_traffic_seconds

class GoogleMapsClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or API_KEY
        self.url = "https://maps.googleapis.com/maps/api/directions/json"

    def get_route_eta(self, origin: str, destination: str):
        params = {
            "origin": origin,
            "destination": destination,
            "departure_time": "now",
            "key": self.api_key,
        }
        backoff = 1.0
        for _ in range(4):
            r = requests.get(self.url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                if status == "OK":
                    leg = data["routes"][0]["legs"][0]
                    dist = leg.get("distance", {}).get("value", 0)
                    dur = leg.get("duration", {}).get("value", 0)
                    dur_traf = leg.get("duration_in_traffic", {}).get("value", dur)
                    return Eta(origin, destination, dist, dur, dur_traf)
                if status in ("OVER_QUERY_LIMIT", "RESOURCE_EXHAUSTED"):
                    time.sleep(backoff)
                    backoff *= 2
                    continue
            time.sleep(backoff)
            backoff *= 2
        return None
