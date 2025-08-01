"use client";
import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import quizData from './questions.json';
import './styling/likert.css'; // Import the CSS file
import './styling/quiz.css'; // Import the CSS file for general styles
import './styling/checkbox.css'; // Import the CSS file for checkbox styles
import './styling/radio.css'; // Import the CSS file for radio styles

interface QuizOption {
  id: string;
  label: string;
  value: string | number;
}

interface QuizQuestion {
  id: string;
  question: string;
  type: string;
  options: QuizOption[];
  maxSelections?: number;
  scale?: number;
  leftLabel?: string;
  rightLabel?: string;
  min?: number;
  max?: number;
  defaultValue?: number;
  placeholder?: string;
  conditional?: {
    dependsOn: string;
    requiredValue: string;
  };
}

interface QuizSection {
  id: string;
  title: string;
  questions: QuizQuestion[];
}

interface QuizData {
  title: string;
  sections: QuizSection[];
}

// Type assertion to fix the import issue
const typedQuizData = quizData as QuizData;

export default function Quiz() {
    const [answers, setAnswers] = useState<Record<string, string[] | string | number>>({});
    const router = useRouter();

    const handleCheckboxChange = (questionId: string, optionValue: string, maxSelections: number) => {
        setAnswers((prevAnswers) => {
            const currentSelections = (prevAnswers[questionId] as string[]) || [];
            if (currentSelections.includes(optionValue)) {
                return {
                    ...prevAnswers,
                    [questionId]: currentSelections.filter((value) => value !== optionValue)
                };
            } else if (currentSelections.length < maxSelections) {
                return {
                    ...prevAnswers, 
                    [questionId]: [...currentSelections, optionValue]
                };
            }
            return prevAnswers;
        });
    };

    // Handle radio and likert questions
    const handleRadioChange = (questionId: string, optionValue: string) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: optionValue
        }));
    };

    // Handle number input questions
    const handleNumberChange = (questionId: string, value: number) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: value
        }));
    };

    // Check if checkbox option should be disabled
    const isCheckboxDisabled = (questionId: string, optionValue: string, maxSelections: number) => {
        const currentSelections = (answers[questionId] as string[]) || [];
        return currentSelections.length >= maxSelections && !currentSelections.includes(optionValue);
    };

    // Get selection count for checkboxes
    const getSelectionCount = (questionId: string) => {
        const selections = answers[questionId] as string[];
        return selections?.length || 0;
    };

    // Check if quiz is complete
    const isQuizComplete = () => {
        const allQuestions = typedQuizData.sections.flatMap(section => section.questions);
        return allQuestions.every(question => {
            const answer = answers[question.id];
            
            if (question.type === 'checkbox') {
                // For checkbox questions, answer should be an array with at least one item
                return Array.isArray(answer) && answer.length > 0;
            } else if (question.type === 'number') {
                // For number questions, answer should be a number
                return typeof answer === 'number' && !isNaN(answer);
            } else {
                // For radio/likert questions, answer should be a non-empty string
                return typeof answer === 'string' && answer !== '';
            }
        });
    };

    // Submit handler
    const handleSubmit = async () => {
        const res = await fetch("http://localhost:5001/api/match", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(answers),
        });
        const matches = await res.json();
        localStorage.setItem("matches", JSON.stringify(matches));
        router.push("/matches");
    };

    // Render checkbox question
    const renderCheckboxQuestion = (question: QuizQuestion) => (
        <div key={question.id} className="checkbox-container">
            <h3 className="checkbox-question">
                {question.question}
            </h3>
            
            <p className="checkbox-selection-info">
                Select up to {question.maxSelections} option{(question.maxSelections || 0) > 1 ? 's' : ''} 
                ({getSelectionCount(question.id)}/{question.maxSelections} selected)
            </p>
            
            <div className="checkbox-grid">
                {question.options.map((option) => {
                    const isSelected = ((answers[question.id] as string[]) || []).includes(String(option.value));
                    const isDisabled = isCheckboxDisabled(question.id, String(option.value), question.maxSelections || 1);
                    
                    return (
                        <label
                            key={option.id}
                            className="checkbox-option"
                        >
                            <input
                                type="checkbox"
                                checked={isSelected}
                                disabled={isDisabled}
                                onChange={() => handleCheckboxChange(question.id, String(option.value), question.maxSelections || 1)}
                            />
                            <div className="checkbox-custom"></div>
                            <span className="checkbox-label-text">
                                {option.label}
                            </span>
                        </label>
                    );
                })}
            </div>
        </div>
    );

    // Render radio question
    const renderRadioQuestion = (question: QuizQuestion) => (
        <div key={question.id} className="radio-container">
            <h3 className="radio-question">
                {question.question}
            </h3>
            
            <div className="radio-options">
                {question.options.map((option) => {
                    const isSelected = answers[question.id] === String(option.value);
                    
                    return (
                        <label
                            key={option.id}
                            className="radio-option"
                        >
                            <input
                                type="radio"
                                name={`question_${question.id}`}
                                value={String(option.value)}
                                checked={isSelected}
                                onChange={() => handleRadioChange(question.id, String(option.value))}
                            />
                            <div className="radio-custom"></div>
                            <span className="radio-label-text">
                                {option.label}
                            </span>
                        </label>
                    );
                })}
            </div>
        </div>
    );

    const renderLikertQuestion = (question: QuizQuestion) => {
        // Calculate the total number of options for dynamic CSS
        const totalOptions = question.options.length;
        
        return (
            <div 
                key={question.id} 
                className="likert-container"
                style={{ '--likert-total': totalOptions } as React.CSSProperties}
            >
                <h3 className="likert-question">
                    {question.question}
                </h3>
                
                <div className="likert-options">
                    <p>{question.leftLabel}</p>
                    {question.options.map((option, index) => {
                        const isSelected = answers[question.id] === String(option.value);
                        
                        return (
                            <label key={option.id} className="likert-option">
                                <input
                                    type="radio"
                                    name={`question_${question.id}`}
                                    value={String(option.value)}
                                    checked={isSelected}
                                    onChange={() => handleRadioChange(question.id, String(option.value))}
                                />
                                <div className="likert-button"></div>
                            </label>
                        );
                    })}
                    <p>{question.rightLabel}</p>
                </div>
            </div>
        );
    };

    return (
        <div className="quiz-container">
            <div className="header">
                <h1>get matched for free</h1>
                <p className="subtext">Based on Ontario University Data</p>
                <div className="circle-container">
                    <div className="info-circle-1">
                        <div className="circle-text">
                            <h2>Complete the Test</h2>
                            <p>Be yourself and answer honestly to find out your personality type.</p>
                        </div>
                    </div>
                    <div id="2" className="info-circle-2">
                        <div className="circle-text">
                            <h2>View Your Matches</h2>
                            <p>Discover which universities align with you the most.</p>
                        </div>
                    </div>
                    <div className="info-circle-3">
                        <div className="circle-text">
                            <h2>Connect With a Current Student</h2>
                            <p>Get connected with student mentors studying at one of your matched schools.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="all-questions" style={{ maxWidth: '900px', margin: '0 auto', padding: '0 20px' }}>
                {typedQuizData.sections.map(section => (
                    <div key={section.id} className="section-container">
                        {section.questions.map(question => {
                            switch (question.type) {
                                case 'checkbox':
                                    return renderCheckboxQuestion(question);
                                case 'radio':
                                    return renderRadioQuestion(question);
                                case 'likert':
                                    return renderLikertQuestion(question);
                                default:
                                    return null;
                            }
                        })}
                    </div>
                ))}
            </div>

            <div style={{ textAlign: 'center', marginTop: '40px' }}>
                <button
                    disabled={!isQuizComplete()}
                    onClick={handleSubmit}
                    style={{
                        padding: '15px 30px',
                        fontSize: '18px',
                        fontWeight: 'bold',
                        backgroundColor: isQuizComplete() ? '#28a745' : '#ccc',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: isQuizComplete() ? 'pointer' : 'not-allowed',
                        transition: 'background-color 0.2s ease'
                    }}
                >
                    Submit Quiz
                </button>
            {/* Debug section */}
            <div>
            {/* Add padding to the debug section */}
            <div style={{ padding: '40px' }}>
                {/* Debug info (optional): */}
                {/* <pre>{JSON.stringify(answers, null, 2)}</pre> */}
            </div>
            </div>
        </div>
    </div>
    );
}