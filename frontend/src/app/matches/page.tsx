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
        if (data) setMatches(JSON.parse(data));
    }, []);

    function handleClick(match: Match) {
        setSelectedMatch(match);
    }

    return (
        <div className="matches-container">
            <div className="match-list">
                {matches.map((match, index) => (
                    <div key={index} className="match" onClick={() => handleClick(match)}>
                        <p>{match.school}</p>
                        <p>{match.program}</p>
                        <p>Overall: {match.overall.toFixed(3)}</p>
                    </div>
                ))}
            </div>
            {selectedMatch && (
                <div className="popup">
                    <p>Academic: {selectedMatch.academic.toFixed(3)}</p>
                    <p>Social: {selectedMatch.social.toFixed(3)}</p>
                    <p>Campus: {selectedMatch.campus.toFixed(3)}</p>
                </div>
            )}
        </div>
    );
}