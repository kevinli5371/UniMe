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

export default function Matches() {
    const [matches, setMatches] = useState<Match[]>([]);
    const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);

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

    const getMockProgramInfo = (school: string, program: string) => {
        return {
            acceptanceRate: "65%",
            avgGrade: "87%",
            classSize: "120",
            programSite: "#",
            uniSite: "#",
            description: "Basic info about this program and what makes it unique. This program focuses on innovative approaches to solving complex problems.",
            mentors: [
                {
                    name: "Anna Wei",
                    avatar: "https://via.placeholder.com/80x80/9282b7/ffffff?text=AW"
                },
                {
                    name: "Anna Wei", 
                    details: `University of Waterloo, First Year Systems Design Engineering`,
                    avatar: "https://via.placeholder.com/80x80/9282b7/ffffff?text=AW"
                }
            ]
        };
    };

    return (
        <div className="matches-container">
            <div className="match-list">
                {matches.map((match, index) => (
                    <div 
                        key={index} 
                        className={`match ${selectedMatch === match ? 'selected' : ''}`}
                        onClick={() => handleClick(match)}
                    >
                        <h3>{match.school}</h3>
                        <p className="program-name">{match.program}</p>
                        <p className="overall-score">Overall: {formatPercentage(match.overall)}</p>
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
                    
                    <div className="links-section">
                        <a href={getMockProgramInfo(selectedMatch.school, selectedMatch.program).programSite} className="program-link">
                            Link to program site
                        </a>
                        <a href={getMockProgramInfo(selectedMatch.school, selectedMatch.program).uniSite} className="program-link">
                            Link to uni site
                        </a>
                    </div>
                    
                    <div className="mentors-section">
                        <div className="mentors-grid">
                            {getMockProgramInfo(selectedMatch.school, selectedMatch.program).mentors.map((mentor, index) => (
                                <div key={index} className="mentor-card">
                                    <h4>{mentor.name}</h4>
                                    <p className="mentor-details">{mentor.details}</p>
                                    <div 
                                        className="mentor-avatar"
                                        style={{ backgroundImage: `url(${mentor.avatar})` }}
                                    ></div>
                                    <button className="mentor-button">MentorMe!</button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}