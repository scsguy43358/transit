from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from .google_maps_client import GoogleMapsClient
from .dynamo_repo import DynamoRepo
from .ga import optimize_schedule
from .prediction import train_and_predict_for_window, get_route_ids

scheduler = BackgroundScheduler()

def traffic_job():
    repo = DynamoRepo()
    gm = GoogleMapsClient()
    route_ids = get_route_ids()
    now = datetime.now(timezone.utc)
    window = 60
    for rid in route_ids:
        mapping = repo.get_latest_route_mapping(rid)
        if mapping and mapping.get("origin") and mapping.get("destination"):
            eta = gm.get_route_eta(mapping["origin"], mapping["destination"])
            if eta:
                repo.put_snapshot({
                    "route_id": str(rid),
                    "timestamp_iso": now.isoformat(),
                    "distance_m": eta.distance_meters or 0,
                    "duration_s": eta.duration_seconds or 0,
                    "duration_in_traffic_s": eta.duration_in_traffic_seconds or 0,
                    "source": "google_maps",
                })
    for rid in route_ids:
        preds = train_and_predict_for_window(rid, now, window)
        for i, delay in enumerate(preds):
            repo.put_prediction({
                "route_id": str(rid),
                "timestamp_iso": (now + timedelta(minutes=i)).isoformat(),
                "predicted_delay_sec": int(delay),
                "model_version": "rf_v1",
            })
        ga = optimize_schedule(num_buses=6, window_minutes=window, predicted_delays=preds)
        repo.put_schedule({
            "route_id": str(rid),
            "timestamp_iso": now.isoformat(),
            "departures_minutes": ga["departures_minutes"],
            "fitness": ga["fitness"],
        })

def start_scheduler():
    try:
        scheduler.add_job(traffic_job, "interval", minutes=5, id="traffic_job", replace_existing=True)
        scheduler.start()
    except Exception:
        pass
