import os
import boto3
from boto3.dynamodb.conditions import Key

REGION = os.getenv("AWS_REGION", "us-east-1")
T_SNAP = os.getenv("DYNAMODB_TABLE_SNAPSHOTS", "TransitTrafficSnapshots")
T_PRED = os.getenv("DYNAMODB_TABLE_PREDICTIONS", "TransitPredictions")
T_SCHD = os.getenv("DYNAMODB_TABLE_SCHEDULES", "TransitSchedules")
T_HIST = os.getenv("DYNAMODB_TABLE_ROUTE_HISTORY", "TransitRouteHistory")

class DynamoRepo:
    def __init__(self, dynamo=None):
        self.d = dynamo or boto3.resource("dynamodb", region_name=REGION)
        self.t_snap = self.d.Table(T_SNAP)
        self.t_pred = self.d.Table(T_PRED)
        self.t_schd = self.d.Table(T_SCHD)
        self.t_hist = self.d.Table(T_HIST)

    def put_snapshot(self, item):
        self.t_snap.put_item(Item=item)

    def get_snapshots_by_route(self, route_id, limit=100):
        r = self.t_snap.query(KeyConditionExpression=Key("route_id").eq(route_id), Limit=limit, ScanIndexForward=False)
        return r.get("Items", [])

    def put_prediction(self, item):
        self.t_pred.put_item(Item=item)

    def get_predictions_by_route(self, route_id, limit=60):
        r = self.t_pred.query(KeyConditionExpression=Key("route_id").eq(route_id), Limit=limit, ScanIndexForward=False)
        return r.get("Items", [])

    def put_schedule(self, item):
        self.t_schd.put_item(Item=item)

    def get_latest_schedule(self, route_id):
        r = self.t_schd.query(KeyConditionExpression=Key("route_id").eq(route_id), Limit=1, ScanIndexForward=False)
        it = r.get("Items", [])
        return it[0] if it else None

    def append_history(self, item):
        self.t_hist.put_item(Item=item)

    def get_latest_route_mapping(self, route_id):
        r = self.t_hist.query(KeyConditionExpression=Key("route_id").eq(route_id), Limit=1, ScanIndexForward=False)
        it = r.get("Items", [])
        return it[0] if it else None
