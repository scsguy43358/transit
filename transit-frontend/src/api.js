const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

// ---- AUTH ----
export async function login(email, password, totpCode = null) {
  const res = await fetch(`${API_BASE}/api/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, totp_code: totpCode })
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && data && data.mfa_required) return { mfaRequired: true };
    throw new Error(data?.error || 'Login failed');
  }
  return data; // {access, refresh}
}

// ---- DATA ----
export async function getRoutes(token) {
  const res = await fetch(`${API_BASE}/api/routes/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch routes');
  return res.json(); // { routes: [...] }
}

export async function getPredictions(routeId, token) {
  const res = await fetch(`${API_BASE}/api/predictions/?route_id=${encodeURIComponent(routeId)}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch predictions');
  return res.json();
}

export async function getSchedule(routeId, token) {
  const res = await fetch(`${API_BASE}/api/schedule/?route_id=${encodeURIComponent(routeId)}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch schedule');
  return res.json();
}

export async function pushRouteMapping(routeId, origin, destination, token) {
  const payload = { routes: { [routeId]: [origin, destination] } };
  const res = await fetch(`${API_BASE}/api/operator/routes/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data?.error) throw new Error(data?.error || 'Failed to update route mapping');
  return data;
}

// Try two likely endpoints for mapping; if both fail, throw
export async function getRouteMapping(routeId, token) {
  const headers = { 'Authorization': `Bearer ${token}` };
  const try1 = await fetch(`${API_BASE}/api/routeMapping?route_id=${encodeURIComponent(routeId)}`, { headers });
  if (try1.ok) return try1.json();
  const try2 = await fetch(`${API_BASE}/api/route-mapping/?route_id=${encodeURIComponent(routeId)}`, { headers });
  if (try2.ok) return try2.json();
  throw new Error('No route mapping available');
}

export async function getETA(origin, destination, token) {
  const qs = new URLSearchParams({ origin, destination }).toString();
  const res = await fetch(`${API_BASE}/api/eta/?${qs}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch ETA');
  return res.json();
}
export async function getPassengerData(routeId, token) {
  const res = await fetch(`${API_BASE}/api/passengers/?route_id=${encodeURIComponent(routeId)}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch passenger data');
  return res.json();
}
