from datetime import datetime, timezone
from .dynamo_repo import DynamoRepo
from .google_maps_client import GoogleMapsClient

def ingestion_handler(event, context):
    rid = str(event.get("route_id"))
    origin = event.get("origin")
    destination = event.get("destination")
    if not (rid and origin and destination):
        return {"ok": False, "error": "missing params"}
    gm = GoogleMapsClient()
    eta = gm.get_route_eta(origin, destination)
    if not eta:
        return {"ok": False, "error": "no eta"}
    repo = DynamoRepo()
    now = datetime.now(timezone.utc).isoformat()
    repo.put_snapshot({
        "route_id": rid,
        "timestamp_iso": now,
        "distance_m": eta.distance_meters or 0,
        "duration_s": eta.duration_seconds or 0,
        "duration_in_traffic_s": eta.duration_in_traffic_seconds or 0,
        "source": "google_maps",
    })
    return {"ok": True}
