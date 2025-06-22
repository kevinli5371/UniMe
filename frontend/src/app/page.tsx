"use client";
import { useEffect, useRef } from 'react';
import Link from 'next/link';
import './home.css';

export default function Home() {
  const landingRef = useRef<HTMLDivElement>(null);
  const matchmeRef = useRef<HTMLDivElement>(null);
  const chancemeRef = useRef<HTMLDivElement>(null);

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
          </div>
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