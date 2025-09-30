import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api';

function Login({ setToken }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [needsOtp, setNeedsOtp] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await login(email, password, needsOtp ? otp : null);
      if (res.mfaRequired) {
        setNeedsOtp(true);
        setError('MFA enabled. Enter the 6-digit OTP from your authenticator.');
        return;
      }
      setToken(res.access);
      navigate('/commuter');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page" style={{maxWidth: 420}}>
      <div className="card">
        <h2 className="center" style={{marginTop: 0}}>Transit System Login</h2>
        <form onSubmit={submit}>
          <label className="label">Email</label>
          <input className="input mb" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
          <label className="label">Password</label>
          <input className="input mb" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
          {needsOtp && (
            <>
              <label className="label">OTP Code</label>
              <input className="input mb" placeholder="123456" value={otp} onChange={e=>setOtp(e.target.value)} />
            </>
          )}
          {error && <div className="small" style={{color: 'crimson'}}>{error}</div>}
          <button className="btn mt" type="submit">{needsOtp ? 'Verify & Login' : 'Login'}</button>
        </form>
      </div>
    </div>
  );
}

export default Login;
