import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import Login from './components/Login';
import OperatorDashboard from './components/OperatorDashboard';
import CommuterDashboard from './components/CommuterDashboard';

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('accessToken'));
  const navigate = useNavigate();

  useEffect(() => {
    if (token) localStorage.setItem('accessToken', token);
    else localStorage.removeItem('accessToken');
  }, [token]);

  const logout = () => { setToken(null); navigate('/login'); };

  return (
    <>
      {token && (
        <div className="nav">
          <div>
            <Link to="/operator">Operator Dashboard</Link>
            <Link to="/commuter">Commuter Dashboard</Link>
          </div>
          <button className="btn" onClick={logout}>Logout</button>
        </div>
      )}

      <div className="page">
        <Routes>
          <Route path="/" element={token ? <Navigate to="/commuter" /> : <Navigate to="/login" />} />
          <Route path="/login" element={<Login setToken={setToken} />} />
          <Route path="/operator" element={token ? <OperatorDashboard token={token} /> : <Navigate to="/login" />} />
          <Route path="/commuter" element={token ? <CommuterDashboard token={token} /> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
