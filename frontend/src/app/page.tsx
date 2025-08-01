"use client";
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { supabase } from '../../supabase/supabaseClient';
import './home.css';

export default function Home() {
  const landingRef = useRef<HTMLDivElement>(null);
  const matchmeRef = useRef<HTMLDivElement>(null);
  const chancemeRef = useRef<HTMLDivElement>(null);
  
  // Login state
  const [showLogin, setShowLogin] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const observerOptions = {
      threshold: 0.2,
      rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
        }
      });
    }, observerOptions);

    // Observe all sections
    if (landingRef.current) observer.observe(landingRef.current);
    if (matchmeRef.current) observer.observe(matchmeRef.current);
    if (chancemeRef.current) observer.observe(chancemeRef.current);

    return () => observer.disconnect();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password,
      });

      if (error) {
        setError(error.message);
        console.error('Login error:', error);
      } else {
        console.log('Login successful:', data);
        alert('Login successful!');
        setShowLogin(false);
        setEmail('');
        setPassword('');
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home">
      <div className="content">
        <div className="landing" ref={landingRef}>
          <div className="text">
            <h1>UniMe</h1>
            <p style={{ width: '100%' }}>Your personal digital guidance counselor</p>
          </div>
          <div className="button-container">
            <Link href="/quiz">
              <button className="button">MatchMe</button>
            </Link>
            <Link href="/chance">
              <button className="button">ChanceMe</button>
            </Link>
            <button 
              className="button login-btn" 
              onClick={() => setShowLogin(!showLogin)}
            >
              {showLogin ? 'Cancel' : 'Login'}
            </button>
          </div>

          {/* Simple Login Form */}
          {showLogin && (
            <div className="login-form">
              <form onSubmit={handleLogin}>
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                {error && <div className="error-message">{error}</div>}
                <button type="submit" disabled={loading}>
                  {loading ? 'Signing in...' : 'Sign In'}
                </button>
              </form>
            </div>
          )}
        </div>

        <div className="matchme" ref={matchmeRef}>
          <div className="text">
            <h1>MatchMe</h1>
            <p>Only 5 minutes, find a university and program that uniquely matches you and get connected with a current student</p>
          </div>
          <div className="button-container">
            <Link href="/quiz">
              <button className="button">Take the test  →  </button>
            </Link>
          </div>
        </div>

        <div className="chanceme" ref={chancemeRef}>
          <div className="text">
            <h1>ChanceMe</h1>
            <p>Only 3 minutes, estimate your chances of getting into your dream university program</p>
          </div>
          <div className="button-container">
            <Link href="/chance">
              <button className="button">Take the test  →  </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}