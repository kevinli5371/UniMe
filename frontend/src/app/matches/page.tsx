"use client";
import { useState, useEffect } from 'react';
import './matches.css';

interface Match {
    school: string;
    program: string;
    overall: number;
    academic: number;
    campus: number;
    social: number;
}

interface Mentor {
    id: string;
    name: string;
    school: string;
    program: string;
    year: string;
    details: string;
    bio: string;
    avatar: string;
    linkedin: string;
}

export default function Matches() {
    const [matches, setMatches] = useState<Match[]>([]);
    const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
    const [isDownloading, setIsDownloading] = useState(false);
    const [programMentors, setProgramMentors] = useState<Mentor[]>([]);

    useEffect(() => {
        const data = localStorage.getItem("matches");
        if (data) {
            const parsedData = JSON.parse(data);
            // Handle both possible response formats
            const matchesArray = parsedData.matches || parsedData;
            setMatches(matchesArray);
        }
    }, []);

    function handleClick(match: Match) {
        setSelectedMatch(match);
    }

    const formatPercentage = (value: number) => {
        return `${Math.round(value * 100)}%`;
    };

    const fetchMentors = async (school: string, program: string) => {
        try {
            const programKey = `${school}_${program}`;
            console.log("Fetching mentors for:", programKey);
            
            const response = await fetch(`http://localhost:5001/api/program-mentors/${encodeURIComponent(programKey)}`);
            console.log("Response status:", response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log("Mentor data received:", data);
                setProgramMentors(data);
            } else {
                console.error("API returned error:", await response.text());
                setProgramMentors([]); // Empty if not found
            }
        } catch (error) {
            console.error("Error fetching mentors:", error);
            setProgramMentors([]);
        }
    };

    useEffect(() => {
        if (selectedMatch) {
            fetchMentors(selectedMatch.school, selectedMatch.program);
        }
    }, [selectedMatch]);

    const downloadPDF = async () => {
        try {
          setIsDownloading(true);
          
          // Get weights from localStorage
          const preferences = JSON.parse(localStorage.getItem("preferences") || "{}");
          const weights = {
            wa: preferences.wa || 0.6,
            wc: preferences.wc || 0.2,
            wso: preferences.wso || 0.2
          };
          
          // Get answers from localStorage
          const answers = JSON.parse(localStorage.getItem("answers") || "{}");
          
          // Make a separate API call to get all 100 matches
          const fullMatchesResponse = await fetch('http://localhost:5001/api/full-matches', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(answers)
          });
          
          if (!fullMatchesResponse.ok) {
            throw new Error('Failed to fetch full matches data');
          }
          
          const fullMatchesData = await fullMatchesResponse.json();
          
          // Format all 100 matches for the PDF
          interface FullMatch {
            overall: number;
            academic: number;
            campus: number;
            social: number;
            school: string;
            program: string;
          }

          const allMatches: [number, number, number, number, string, string][] = fullMatchesData.matches.map((match: FullMatch) => [
            match.overall,
            match.academic,
            match.campus, 
            match.social,
            match.school,
            match.program
          ]);
          
          // Download the PDF with all 100 matches
          const response = await fetch('http://localhost:5001/api/download-pdf', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              results: allMatches,
              weights: weights
            })
          });
          
          // Rest of the function remains the same...
          if (!response.ok) {
            throw new Error('Failed to download PDF');
          }
          
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `LinkU_matches_${new Date().toISOString().split('T')[0]}.pdf`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          
        } catch (error) {
          console.error('Error downloading PDF:', error);
          alert('Failed to download results. Please try again.');
        } finally {
          setIsDownloading(false);
        }
      };

    return (
        <div className="matches-container">
            <div className="matches-content">
                <div className="matches-header">
                    <p className="recommendations-label">Recommendations</p>
                    <h1 className="matches-title">Your Top Uni Matches</h1>
                    <p className="matches-subtitle">
                        Based on your answers, here are the university programs that 
                        best match your interests and goals. Click on one to learn more!
                    </p>
                </div>
            <button 
                onClick={downloadPDF} 
                disabled={isDownloading}
                className="fixed-download-button"
            >
                {isDownloading ? (
                    'Downloading...'
                ) : (
                    <>
                        <svg 
                            xmlns="http://www.w3.org/2000/svg" 
                            width="20" 
                            height="20" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="2" 
                            strokeLinecap="round" 
                            strokeLinejoin="round" 
                            style={{ marginRight: '8px' }}
                        >
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                        </svg>
                        Download PDF Report
                    </>
                )}
            </button>

                <div className="matches-main">
                    <div className="match-list">
                        {matches.map((match, index) => (
                            <div 
                                key={index} 
                                className={`match ${selectedMatch === match ? 'selected' : ''}`}
                                onClick={() => handleClick(match)}
                            >
                                <h3 className="match-school">{match.school}</h3>
                                <p className="match-program">{match.program}</p>
                                <p className="match-score">Overall: {formatPercentage(match.overall)}</p>
                            </div>
                        ))}
                    </div>
                    
                    {selectedMatch && (
                        <div className="popup">
                            <div className="popup-header">
                                <h2>{selectedMatch.school}</h2>
                                <p className="program-subtitle">{selectedMatch.program}</p>
                            </div>
                            
                            <div className="match-stats">
                                <h3>Your match statistics:</h3>
                                <div className="stats-grid">
                                    <span className="stat-item">Academics: {formatPercentage(selectedMatch.academic)}</span>
                                    <span className="stat-item">Social: {formatPercentage(selectedMatch.social)}</span>
                                    <span className="stat-item">Campus: {formatPercentage(selectedMatch.campus)}</span>
                                </div>
                            </div>
                            
                            <div className="program-info">
                                <p>Basic info about this program and what makes it unique. This program focuses on innovative approaches to solving complex problems.</p>
                            </div>
                         
                            
                            <div className="mentors-section">
                                <h3>Connect with Student Mentors</h3>
                                <div className="mentors-grid">
                                    {programMentors.length > 0 ? (
                                        programMentors.map((mentor, index) => (
                                            <div key={index} className="mentor-card">
                                                <h4>{mentor.name}</h4>
                                                <p className="mentor-details">{mentor.details}</p>
                                                <div 
                                                    className="mentor-avatar"
                                                    style={{ backgroundImage: `url(${mentor.avatar})` }}
                                                ></div>
                                                <a 
                                                    href={mentor.linkedin} 
                                                    target="_blank" 
                                                    rel="noopener noreferrer" 
                                                    className="mentor-button"
                                                >
                                                    MentorMe!
                                                </a>
                                            </div>
                                        ))
                                    ) : (
                                        <p>No mentors available for this program. Check back soon!</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}