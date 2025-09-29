import os
import glob
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def _csv_by_prefix(prefix):
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
    for f in files:
        name = os.path.basename(f).lower()
        if name.startswith(prefix):
            return f
    return None

def _paths():
    b = _csv_by_prefix("boarding")
    l = _csv_by_prefix("landing")
    d = _csv_by_prefix("loader")
    if not b or not l or not d:
        raise FileNotFoundError("boarding/landing/loader CSVs not found in traffic/data/")
    return b, l, d

def _read_csvs():
    b, l, d = _paths()
    b = pd.read_csv(b)
    l = pd.read_csv(l)
    d = pd.read_csv(d)
    for df in (b, l, d):
        first = df.columns[0]
        if first != "timestamp":
            df.rename(columns={first: "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return b, l, d

def get_route_ids():
    b, _, _ = _read_csvs()
    cols = [c for c in b.columns if c != "timestamp"]
    ids = [c for c in cols if str(c).isdigit() and 5 <= len(str(c)) <= 6]
    if not ids:
        ids = cols
    return [str(x) for x in ids]

def load_historical_for_route(route_id):
    b, l, d = _read_csvs()
    r = str(route_id)
    if r not in b.columns:
        ids = get_route_ids()
        if not ids:
            raise ValueError("no route ids detected")
        r = ids[0]
    df = b[["timestamp", r]].rename(columns={r: "signal"})
    l2 = l[["timestamp", r]].rename(columns={r: "landing"}) if r in l.columns else l.rename(columns={l.columns[1]: "landing"})[["timestamp", "landing"]]
    d2 = d[["timestamp", r]].rename(columns={r: "loader"}) if r in d.columns else d.rename(columns={d.columns[1]: "loader"})[["timestamp", "loader"]]
    df = df.merge(l2, on="timestamp", how="left").merge(d2, on="timestamp", how="left")
    df = df.sort_values("timestamp").reset_index(drop=True)
    df = df.fillna(0)
    return df

def _features(df):
    X = df.copy()
    X["hour"] = X["timestamp"].dt.hour
    X["weekday"] = X["timestamp"].dt.weekday
    X["month"] = X["timestamp"].dt.month
    X["signal_lag1"] = X["signal"].shift(1).fillna(0)
    X["signal_lag2"] = X["signal"].shift(2).fillna(0)
    X["signal_roll3"] = X["signal"].rolling(3).mean().fillna(0)
    X["mix"] = (X["signal_roll3"] + 0.5 * X["landing"] + 0.3 * X["loader"]).fillna(0)
    X = X.fillna(0)
    return X

def train_and_predict_for_window(route_id, start_ts, window_minutes):
    df = load_historical_for_route(route_id)
    X = _features(df)
    y = (X["mix"] * 10.0).values
    feats = ["hour", "weekday", "month", "signal_lag1", "signal_lag2", "signal_roll3", "landing", "loader"]
    model = RandomForestRegressor(n_estimators=140, random_state=42)
    model.fit(X[feats].values, y)
    last = X.iloc[-1]
    preds = []
    hour = float(last["hour"])
    weekday = float(last["weekday"])
    month = float(last["month"])
    lag1 = float(last["signal_lag1"])
    lag2 = float(last["signal_lag2"])
    roll = float(last["signal_roll3"])
    landing = float(last["landing"])
    loader = float(last["loader"])
    for _ in range(int(window_minutes)):
        f = np.array([[hour, weekday, month, lag1, lag2, roll, landing, loader]])
        yhat = float(model.predict(f)[0])
        preds.append(max(0.0, yhat))
        lag2, lag1 = lag1, roll
        roll = (roll * 2 + yhat / 10.0) / 3.0
        hour = (hour + 1 / 60.0) % 24
        landing = max(0.0, landing * 0.95)
        loader = max(0.0, loader * 0.95)
    return np.array(preds)
