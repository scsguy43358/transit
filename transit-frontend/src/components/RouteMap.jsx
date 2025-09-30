import React, { useEffect, useRef } from 'react';

function RouteMap({ origin, destination }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!origin || !destination || !window.google) return;

    const map = new window.google.maps.Map(ref.current, {
      center: { lat: 0, lng: 0 }, zoom: 12
    });
    const svc = new window.google.maps.DirectionsService();
    const rend = new window.google.maps.DirectionsRenderer();
    rend.setMap(map);

    svc.route(
      { origin, destination, travelMode: window.google.maps.TravelMode.DRIVING },
      (result, status) => {
        if (status === 'OK' && result) {
          rend.setDirections(result);
          const leg = result.routes?.[0]?.legs?.[0];
          const steps = leg?.steps || [];
          if (steps.length) {
            const mid = steps[Math.floor(steps.length/2)];
            new window.google.maps.Marker({
              map, position: mid.end_location, title: 'Bus (approx)'
            });
          }
        } else {
          // eslint-disable-next-line no-console
          console.error('Directions failed:', status);
        }
      }
    );
  }, [origin, destination]);

  return <div ref={ref} style={{ width:'100%', height: 360, background:'#e5e7eb' }} />;
}

export default RouteMap;
