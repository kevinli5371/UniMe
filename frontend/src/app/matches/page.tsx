"use client";

import response from '../test.json';
import './matches.css';
import { useState } from 'react';

interface Match {
    school: string;
    program: string;
    overall: string;
    academic: string;
    social: string;
    campus: string;
}

export default function Matches() {
    const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);

    function handleClick(match: Match) {
        console.log("Match clicked");
        setSelectedMatch(match);
    }

    return (
        <div className="matches-container">
            <div className="match-list">
                {response.data.map((match: Match, index: number) => (
                    <div key={index + 1} className="match" onClick={() => handleClick(match)}>
                        <p>{match.school}</p>
                        <p>{match.program}</p>
                        <p>Overall: {match.overall}</p>
                    </div>
                ))}
            </div>

            {selectedMatch && (
                <div className="popup">
                    <p>Academic: {selectedMatch.academic}</p>
                    <p>Social: {selectedMatch.social}</p>
                    <p>Campus: {selectedMatch.campus}</p>
                </div>
            )}
        </div>
    );
}