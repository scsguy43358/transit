import numpy as np

def optimize_schedule(num_buses: int, window_minutes: int, predicted_delays):
    n = max(1, int(num_buses))
    w = max(1, int(window_minutes))
    base = np.linspace(0, w - 1, n).astype(int).tolist()
    pd = np.array(predicted_delays, dtype=float)
    if pd.size == 0:
        return {"departures_minutes": base, "fitness": 0.0}
    risk = pd[:w]
    spacing = np.diff([0] + base + [w])
    fit = float(1.0 / (np.var(spacing) + 1e-6) * 0.5 + 1.0 / (np.mean(risk) + 1e-6) * 0.5)
    return {"departures_minutes": base, "fitness": round(fit, 5)}
