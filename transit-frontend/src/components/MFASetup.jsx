import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

function MFASetup({ token }) {
  const [qrUri, setQrUri] = useState('');
  const [secret, setSecret] = useState('');
  const [code, setCode] = useState('');
  const [msg, setMsg] = useState('');
  const [enabled, setEnabled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    enrollMFA();
  }, []);

  const enrollMFA = async () => {
    const res = await fetch(`${API_BASE}/api/auth/mfa/enroll/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    if (data.enabled) {
      setEnabled(true);
      setMsg('MFA already enabled');
    } else {
      setQrUri(data.otpauth_uri);
      setSecret(data.secret);
    }
  };

  const confirm = async (e) => {
    e.preventDefault();
    const res = await fetch(`${API_BASE}/api/auth/mfa/confirm/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ totp_code: code })
    });
    const data = await res.json();
    if (data.enabled) {
      setMsg('MFA enabled successfully!');
      setEnabled(true);
      setTimeout(() => navigate('/commuter'), 2000);
    } else {
      setMsg(data.error || 'Invalid code');
    }
  };

  const skip = () => navigate('/commuter');

  if (enabled) {
    return (
      <div className="page" style={{maxWidth: 500}}>
        <div className="card center">
          <h2>MFA Enabled</h2>
          <p>Your account is now protected with Multi-Factor Authentication.</p>
          <button className="btn mt" onClick={skip}>Continue to Dashboard</button>
        </div>
      </div>
    );
  }

  return (
    <div className="page" style={{maxWidth: 600}}>
      <div className="card">
        <h2 style={{marginTop:0}}>Setup Multi-Factor Authentication (MFA)</h2>
        <p className="small">Scan this QR code with Google Authenticator or Authy:</p>
        
        {qrUri && (
          <div className="center mt mb">
            <img 
              src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrUri)}`}
              alt="QR Code"
            />
            <div className="small mt">Or enter manually: <code>{secret}</code></div>
          </div>
        )}

        <form onSubmit={confirm}>
          <label className="label">Enter 6-digit code from app:</label>
          <input 
            className="input mb" 
            placeholder="123456" 
            value={code} 
            onChange={e=>setCode(e.target.value)}
            maxLength="6"
            required 
          />
          {msg && <div className="small mb" style={{color: msg.includes('Invalid')?'crimson':'#16a34a'}}>{msg}</div>}
          <div className="row">
            <button className="btn" type="submit">Verify & Enable MFA</button>
            <button className="btn" type="button" onClick={skip} style={{background:'#6b7280'}}>Skip for Now</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default MFASetup;