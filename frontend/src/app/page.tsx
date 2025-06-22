import Link from 'next/link';
import './home.css';

export default function Home() {
  return (
    <div className="home">
      <div className="content">

        <div className="landing">
          <div className="text">
            <p>Match, Chance, Connect, </p>
            <h1>UniMe</h1>
          </div>
          <div className="button-container">
            <Link href="/quiz">
              <button className="button">MatchMe</button>
            </Link>
            <Link href="/matches">
              <button className="button">ChanceMe</button>
            </Link>
          </div>
        </div>

        <div className="matchme">
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

        <div className="chanceme">
          <div className="text">
            <h1>ChanceMe</h1>
            <p>Only 3 minutes, estimate your chances of getting into your dream university program</p>
          </div>
          <div className="button-container">
            <Link href="/quiz">
              <button className="button">Take the test  →  </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
