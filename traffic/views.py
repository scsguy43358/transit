import os
import pandas as pd
from datetime import datetime, timezone
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .google_maps_client import GoogleMapsClient
from .dynamo_repo import DynamoRepo

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return JsonResponse({"ok": True})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def routes(request):
    data_dir = os.path.join(settings.BASE_DIR, "traffic", "data")
    route_ids = set()
    for file in os.listdir(data_dir):
        if file.endswith(".csv"):
            p = os.path.join(data_dir, file)
            try:
                df = pd.read_csv(p)
                route_ids.update(df.columns[1:])
            except Exception:
                pass
    return JsonResponse({"routes": sorted(list(route_ids))})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def eta(request):
    origin = request.GET.get("origin")
    destination = request.GET.get("destination")
    if not origin or not destination:
        return JsonResponse({"error": "origin and destination are required"}, status=400)
    gm = GoogleMapsClient()
    e = gm.get_route_eta(origin, destination)
    if not e:
        return JsonResponse({"error": "no route found"}, status=404)
    return JsonResponse({
        "origin": e.origin,
        "destination": e.destination,
        "distance_m": e.distance_meters,
        "duration_s": e.duration_seconds,
        "duration_in_traffic_s": e.duration_in_traffic_seconds,
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def predictions(request):
    rid = request.GET.get("route_id")
    if not rid:
        return JsonResponse({"error": "route_id required"}, status=400)
    repo = DynamoRepo()
    items = repo.get_predictions_by_route(rid, limit=120)
    return JsonResponse({"route_id": rid, "predictions": items})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def schedule(request):
    rid = request.GET.get("route_id")
    if not rid:
        return JsonResponse({"error": "route_id required"}, status=400)
    repo = DynamoRepo()
    item = repo.get_latest_schedule(rid)
    if not item:
        return JsonResponse({"error": "no schedule"}, status=404)
    return JsonResponse(item)

# ✅ new route mapping endpoint
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_route_mapping(request):
    rid = request.GET.get("route_id")
    if not rid:
        return JsonResponse({"error": "route_id required"}, status=400)
    repo = DynamoRepo()
    mapping = repo.get_latest_route_mapping(rid)
    if not mapping:
        return JsonResponse({"error": "no mapping found"}, status=404)
    return JsonResponse(mapping)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def passenger_predictions(request):
    from .prediction import load_historical_for_route
    rid = request.GET.get("route_id")
    if not rid:
        return JsonResponse({"error": "route_id required"}, status=400)
    
    df = load_historical_for_route(rid)
    recent = df.tail(60).to_dict('records')

    data = [{
        'timestamp': r['timestamp'].isoformat() if hasattr(r['timestamp'], 'isoformat') else str(r['timestamp']),
        'boarding': int(r.get('signal', 0)),
        'landing': int(r.get('landing', 0)),
        'loader': int(r.get('loader', 0))
    } for r in recent]
    
    return JsonResponse({"route_id": rid, "passenger_data": data})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def operator_push_routes(request):
    payload = request.data
    routes = payload.get("routes", {})
    now = datetime.now(timezone.utc).isoformat()
    repo = DynamoRepo()
    for rid, pair in routes.items():
        repo.append_history({
            "route_id": str(rid),
            "timestamp_iso": now,
            "origin": pair[0],
            "destination": pair[1],
        })
    return JsonResponse({"ok": True, "count": len(routes)})
