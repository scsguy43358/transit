import React, { useEffect, useMemo, useState } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { getRoutes, getPredictions, getSchedule, getRouteMapping, getETA, pushRouteMapping, getPassengerData } from '../api';

function OperatorDashboard({ token }) {
  const [routes, setRoutes] = useState([]);
  const [routeId, setRouteId] = useState('');
  const [pred, setPred] = useState([]);
  const [sched, setSched] = useState(null);
  const [mapInfo, setMapInfo] = useState(null);
  const [eta, setEta] = useState(null);
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [msg, setMsg] = useState('');
  const [passengers, setPassengers] = useState([]);

  useEffect(() => {
    getRoutes(token).then(d => {
      const list = d?.routes || [];
      setRoutes(list);
      if (list.length) setRouteId(list[0]);
    }).catch(() => {});
  }, [token]);

  useEffect(() => {
    if (!routeId) return;
    (async () => {
      setMsg('');
      try {
        const [p, s] = await Promise.all([
          getPredictions(routeId, token).catch(()=>null),
          getSchedule(routeId, token).catch(()=>null)
        ]);
        const sorted = (p?.predictions || []).slice().sort((a,b)=>new Date(a.timestamp_iso)-new Date(b.timestamp_iso));
        setPred(sorted);
        setSched(s && !s.error ? s : null);
      } catch {}
      const passengerData = await getPassengerData(routeId, token).catch(()=>null);
      if (passengerData?.passenger_data) setPassengers(passengerData.passenger_data);
      try {
        const mi = await getRouteMapping(routeId, token);
        setMapInfo(mi);
        setOrigin(mi.origin || '');
        setDestination(mi.destination || '');
        if (mi.origin && mi.destination) {
          const e = await getETA(mi.origin, mi.destination, token);
          setEta(e);
        } else setEta(null);
      } catch {
        setMapInfo(null);
        setEta(null);
      }
    })();
  }, [routeId, token]);

  const updateMapping = async (e) => {
    e.preventDefault();
    if (!origin || !destination) return;
    try {
      await pushRouteMapping(routeId, origin, destination, token);
      setMsg('Route updated.');
      const mi = await getRouteMapping(routeId, token).catch(()=>null);
      setMapInfo(mi);
      if (mi?.origin && mi?.destination) {
        const e = await getETA(mi.origin, mi.destination, token).catch(()=>null);
        setEta(e);
      }
    } catch (err) {
      setMsg('Failed to update route.');
    }
  };

  const chartData = useMemo(() => {
    return pred.map((it, i)=>({ x: i, delay: Number(it.predicted_delay_sec||0) }));
  }, [pred]);

  return (
    <div className="page">
      <h2>Operator Dashboard</h2>

      <div className="card mb">
        <div className="row">
          <div style={{minWidth: 200}}>
            <label className="label">Select Route</label>
            <select className="select" value={routeId} onChange={e=>setRouteId(e.target.value)}>
              {routes.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          {mapInfo && eta && (
            <div>
              <div className="small"><b>Route:</b> {mapInfo.origin} → {mapInfo.destination}</div>
              <div className="small"><b>Distance:</b> {(eta.distance_m/1000).toFixed(1)} km</div>
              <div className="small"><b>Normal:</b> {Math.round(eta.duration_s/60)} min &nbsp; | &nbsp;
                <b>Now:</b> {Math.round(eta.duration_in_traffic_s/60)} min
              </div>
            </div>
          )}
        </div>

        <form onSubmit={updateMapping} className="mt">
          <div className="row">
            <div style={{flex:1}}>
              <label className="label">Origin</label>
              <input className="input" value={origin} onChange={e=>setOrigin(e.target.value)} placeholder="Origin address" />
            </div>
            <div style={{flex:1}}>
              <label className="label">Destination</label>
              <input className="input" value={destination} onChange={e=>setDestination(e.target.value)} placeholder="Destination address" />
            </div>
          </div>
          <button className="btn mt" type="submit">Save Mapping</button>
          {msg && <div className="small mt" style={{color: msg.includes('Fail')?'crimson':'#16a34a'}}>{msg}</div>}
        </form>
      </div>

     <div className="grid grid-3">
  <div className="card">
    <h3 style={{marginTop:0}}>Delay Predictions (next 60 min)</h3>
    {chartData.length ? (
      <div style={{width: '100%', height: 320}}>
        <ResponsiveContainer>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="x" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="delay" stroke="#2563eb" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    ) : <div className="small">No prediction data.</div>}
  </div>

  <div className="card">
    <h3 style={{marginTop:0}}>Optimized Schedule</h3>
    {sched ? (
      <>
        <div className="small">Generated: {new Date(sched.timestamp_iso).toLocaleString()}</div>
        <div className="small mt"><b>Fitness:</b> {sched.fitness}</div>
        <div className="mt">
          <b>Departures (minutes from generation):</b>
          <ul>
            {(sched.departures_minutes||[]).map((m,i)=><li key={i}>Bus {i+1}: {m} min</li>)}
          </ul>
        </div>
      </>
    ) : <div className="small">No schedule available.</div>}
  </div>

  <div className="card">
    <h3 style={{marginTop:0}}>Passenger Flow Analysis</h3>
    {passengers.length ? (
      <div style={{width: '100%', height: 320}}>
        <ResponsiveContainer>
          <LineChart data={passengers.slice(-20)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" tick={false} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="boarding" stroke="#16a34a" name="Boarding" />
            <Line type="monotone" dataKey="landing" stroke="#dc2626" name="Alighting" />
            <Line type="monotone" dataKey="loader" stroke="#f59e0b" name="Bus Load" />
          </LineChart>
        </ResponsiveContainer>
        <div className="small mt center">
          <span style={{color:'#16a34a'}}>● Boarding</span> &nbsp;
          <span style={{color:'#dc2626'}}>● Alighting</span> &nbsp;
          <span style={{color:'#f59e0b'}}>● Bus Load</span>
        </div>
      </div>
    ) : <div className="small">No passenger data.</div>}
  </div>
</div>
    </div>
  );
}

export default OperatorDashboard;
