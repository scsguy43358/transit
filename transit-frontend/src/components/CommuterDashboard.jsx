import React, { useEffect, useState } from 'react';
import { getRoutes, getSchedule, getRouteMapping, getETA } from '../api';
import RouteMap from './RouteMap';

function CommuterDashboard({ token }) {
  const [routes, setRoutes] = useState([]);
  const [routeId, setRouteId] = useState('');
  const [sched, setSched] = useState(null);
  const [mapInfo, setMapInfo] = useState(null);
  const [eta, setEta] = useState(null);
  const [nextBusText, setNextBusText] = useState('');

  useEffect(() => {
    getRoutes(token).then(d => {
      const list = d?.routes || [];
      setRoutes(list);
      if (list.length) setRouteId(list[0]);
    }).catch(()=>{});
  }, [token]);

  useEffect(() => {
    if (!routeId) return;
    (async () => {
      const s = await getSchedule(routeId, token).catch(()=>null);
      setSched(s && !s.error ? s : null);
      // next bus text
      if (s && !s.error && Array.isArray(s.departures_minutes)) {
        const t0 = new Date(s.timestamp_iso);
        const now = new Date();
        const diffMin = (now - t0) / 60000;
        const upcoming = s.departures_minutes.filter(m => m >= diffMin);
        if (upcoming.length) {
          const off = upcoming[0];
          const when = new Date(t0.getTime() + off * 60000);
          const mins = Math.max(0, Math.round(off - diffMin));
          setNextBusText(`Next bus at ${when.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})} (in ~${mins} min)`);
        } else setNextBusText('No upcoming departures.');
      } else setNextBusText('No schedule available.');

      // mapping + ETA
      const mi = await getRouteMapping(routeId, token).catch(()=>null);
      setMapInfo(mi);
      if (mi?.origin && mi?.destination) {
        const e = await getETA(mi.origin, mi.destination, token).catch(()=>null);
        setEta(e);
      } else setEta(null);
    })();
  }, [routeId, token]);

  let status = '';
  if (eta) {
    const normal = eta.duration_s/60;
    const current = eta.duration_in_traffic_s/60;
    if (current > normal * 1.5) status = 'Major delays due to traffic';
    else if (current > normal * 1.2) status = 'Some delays (traffic slower than usual)';
    else status = 'On schedule';
  }

  const badgeClass =
    status.includes('Major') ? 'badge bad' :
    status.includes('Some')  ? 'badge warn' : 'badge good';

  return (
    <div className="page">
      <h2>Commuter Dashboard</h2>

      <div className="card mb">
        <div className="row">
          <div style={{minWidth: 200}}>
            <label className="label">Select Route</label>
            <select className="select" value={routeId} onChange={e=>setRouteId(e.target.value)}>
              {routes.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          {status && <div className={badgeClass} style={{alignSelf:'flex-end'}}>{status}</div>}
        </div>

        {mapInfo && (
          <div className="small mt">
            <b>Route:</b> {mapInfo.origin} → {mapInfo.destination}
            {eta && <>
              &nbsp; | &nbsp; <b>Distance:</b> {(eta.distance_m/1000).toFixed(1)} km
              &nbsp; | &nbsp; <b>Now:</b> {Math.round(eta.duration_in_traffic_s/60)} min
            </>}
          </div>
        )}

        <div className="mt"><b>{nextBusText}</b></div>
      </div>

      {mapInfo?.origin && mapInfo?.destination && (
        <div className="card">
          <h3 style={{marginTop:0}}>Route Map</h3>
          <RouteMap origin={mapInfo.origin} destination={mapInfo.destination} />
        </div>
      )}

      {!mapInfo && (
        <div className="small">Waiting for operator to set origin/destination for this route.</div>
      )}
    </div>
  );
}

export default CommuterDashboard;
