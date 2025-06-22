"use client";
import Link from 'next/link';
import { useState } from 'react';
import quizData from './questions.json';
import './likert.css'; // Import the CSS file
import './quiz.css'; // Import the CSS file for general styles

interface QuizOption {
  id: string;
  label: string;
  value: string | number;
}

interface QuizQuestion {
  id: number;
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
    dependsOn: number;
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
    const [answers, setAnswers] = useState<Record<number, string[] | string | number>>({});

    const handleCheckboxChange = (questionId: number, optionValue: string, maxSelections: number) => {
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
    const handleRadioChange = (questionId: number, optionValue: string) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: optionValue
        }));
    };

    // Handle number input questions
    const handleNumberChange = (questionId: number, value: number) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: value
        }));
    };

    // Check if checkbox option should be disabled
    const isCheckboxDisabled = (questionId: number, optionValue: string, maxSelections: number) => {
        const currentSelections = (answers[questionId] as string[]) || [];
        return currentSelections.length >= maxSelections && !currentSelections.includes(optionValue);
    };

    // Get selection count for checkboxes
    const getSelectionCount = (questionId: number) => {
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

    // Render checkbox question
    const renderCheckboxQuestion = (question: QuizQuestion) => (
        <div key={question.id} style={{ marginBottom: '30px' }}>
            <h3 style={{ marginBottom: '10px', color: '#333' }}>
                {question.id}. {question.question}
            </h3>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '15px' }}>
                Select up to {question.maxSelections} option{(question.maxSelections || 0) > 1 ? 's' : ''} 
                ({getSelectionCount(question.id)}/{question.maxSelections} selected)
            </p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
                {question.options.map((option) => {
                    const isSelected = ((answers[question.id] as string[]) || []).includes(String(option.value));
                    const isDisabled = isCheckboxDisabled(question.id, String(option.value), question.maxSelections || 1);
                    
                    return (
                        <label
                            key={option.id}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                padding: '12px',
                                border: '2px solid',
                                borderColor: isSelected ? '#70B1D9' : '#ddd',
                                borderRadius: '6px',
                                backgroundColor: isSelected ? '#e8f4fd' : 'white',
                                cursor: isDisabled ? 'not-allowed' : 'pointer',
                                opacity: isDisabled ? 0.6 : 1,
                                transition: 'all 0.2s ease'
                            }}
                        >
                            <input
                                type="checkbox"
                                checked={isSelected}
                                disabled={isDisabled}
                                onChange={() => handleCheckboxChange(question.id, String(option.value), question.maxSelections || 1)}
                                style={{ marginRight: '10px', transform: 'scale(1.2)' }}
                            />
                            <span style={{ fontWeight: isSelected ? 'bold' : 'normal' }}>
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
        <div key={question.id} style={{ marginBottom: '30px' }}>
            <h3 style={{ marginBottom: '15px', color: '#333' }}>
                {question.id}. {question.question}
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {question.options.map((option) => {
                    const isSelected = answers[question.id] === String(option.value);
                    
                    return (
                        <label
                            key={option.id}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                padding: '12px',
                                border: '2px solid',
                                borderColor: isSelected ? '#28a745' : '#ddd',
                                borderRadius: '6px',
                                backgroundColor: isSelected ? '#e8f5e8' : 'white',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease'
                            }}
                        >
                            <input
                                type="radio"
                                name={`question_${question.id}`}
                                value={String(option.value)}
                                checked={isSelected}
                                onChange={() => handleRadioChange(question.id, String(option.value))}
                                style={{ marginRight: '10px', transform: 'scale(1.2)' }}
                            />
                            <span style={{ fontWeight: isSelected ? 'bold' : 'normal' }}>
                                {option.label}
                            </span>
                        </label>
                    );
                })}
            </div>
        </div>
    );

    const renderLikertQuestion = (question: QuizQuestion) => (
        <div key={question.id} className="likert-container">
            <h3 className="likert-question">
                {/* {question.id}.*/} {question.question}
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
                            <div className="likert-button">
                                {index + 1}
                            </div>
                        </label>
                    );
                })}
                <p>{question.rightLabel}</p>
            </div>
        </div>
    );

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
                            <p>Be yourself and answer honestly to find out your personality type.</p>
                        </div>
                    </div>
                    <div className="info-circle-3">
                        <div className="circle-text">
                            <h2>Connect With a Current Student</h2>
                            <p>Be yourself and answer honestly to find out your personality type.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="all-questions">
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
                <Link href="/matches">
                    <button
                        disabled={!isQuizComplete()}
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
                        onClick={() => console.log("Answers:", answers)}
                    >
                        Submit Quiz
                    </button>
                </Link>
                
                {!isQuizComplete() && (
                    <p style={{ marginTop: '10px', color: '#666', fontSize: '14px' }}>
                        Please answer all questions to submit
                    </p>
                )}
            </div>
            {/* Debug section */}
            <div style={{ 
                marginTop: '40px', 
                padding: '15px', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '6px',
                fontSize: '12px'
            }}>
                <h4>Current Answers (Debug):</h4>
                <pre style={{ overflow: 'auto' }}>{JSON.stringify(answers, null, 2)}</pre>
            </div>
        </div>
    );
}