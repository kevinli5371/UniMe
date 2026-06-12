"use client";
import Link from 'next/link';
import { useState, useMemo, useRef, useEffect, useCallback } from 'react';
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
    const [hasStarted, setHasStarted] = useState(false);
    const [focusedIndex, setFocusedIndex] = useState<number | null>(null);
    const [confirmedCheckboxIds, setConfirmedCheckboxIds] = useState<string[]>([]);
    const questionRefs = useRef<(HTMLDivElement | null)[]>([]);
    const router = useRouter();

    const allQuestions = useMemo(
        () => typedQuizData.sections.flatMap(section => section.questions),
        []
    );

    const isQuestionAnswered = useCallback((question: QuizQuestion) => {
        const answer = answers[question.id];
        if (question.type === 'checkbox') {
            return Array.isArray(answer) && answer.length > 0;
        } else if (question.type === 'number') {
            return typeof answer === 'number' && !isNaN(answer);
        } else {
            return typeof answer === 'string' && answer !== '';
        }
    }, [answers]);

    const isQuestionComplete = useCallback((question: QuizQuestion) => {
        if (question.type === 'checkbox') {
            return confirmedCheckboxIds.includes(question.id) && isQuestionAnswered(question);
        }
        return isQuestionAnswered(question);
    }, [answers, isQuestionAnswered, confirmedCheckboxIds]);

    const currentQuestionIndex = useMemo(() => {
        if (focusedIndex !== null) return focusedIndex;
        const firstIncomplete = allQuestions.findIndex(q => !isQuestionComplete(q));
        return firstIncomplete === -1 ? allQuestions.length - 1 : firstIncomplete;
    }, [allQuestions, isQuestionComplete, focusedIndex]);

    const answeredCount = useMemo(
        () => allQuestions.filter(q => isQuestionComplete(q)).length,
        [allQuestions, isQuestionComplete]
    );

    const progress = (answeredCount / allQuestions.length) * 100;

    const scrollToQuestion = useCallback((index: number) => {
        const el = questionRefs.current[index];
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }, []);

    const advanceToNext = useCallback((currentIndex: number) => {
        if (!hasStarted) setHasStarted(true);
        setFocusedIndex(null);

        const nextIndex = currentIndex + 1;
        if (nextIndex < allQuestions.length) {
            setTimeout(() => scrollToQuestion(nextIndex), 350);
        }
    }, [allQuestions.length, hasStarted, scrollToQuestion]);

    useEffect(() => {
        document.documentElement.classList.add('quiz-scroll');
        return () => document.documentElement.classList.remove('quiz-scroll');
    }, []);

    const getQuestionClass = (index: number) => {
        if (!hasStarted) {
            return index === 0 ? 'question-active' : 'question-future';
        }
        if (index === currentQuestionIndex) return 'question-active';
        if (isQuestionComplete(allQuestions[index])) return 'question-past';
        return 'question-future';
    };

    const handleCheckboxChange = (questionId: string, optionValue: string, maxSelections: number) => {
        setAnswers((prevAnswers) => {
            const currentSelections = (prevAnswers[questionId] as string[]) || [];
            let newSelections: string[];

            if (currentSelections.includes(optionValue)) {
                newSelections = currentSelections.filter((value) => value !== optionValue);
            } else if (currentSelections.length < maxSelections) {
                newSelections = [...currentSelections, optionValue];
            } else {
                return prevAnswers;
            }

            if (newSelections.length === 0) {
                setConfirmedCheckboxIds(prev => prev.filter(id => id !== questionId));
            }

            return { ...prevAnswers, [questionId]: newSelections };
        });
    };

    const handleCheckboxContinue = (questionId: string, questionIndex: number) => {
        if (getSelectionCount(questionId) === 0) return;
        setConfirmedCheckboxIds(prev =>
            prev.includes(questionId) ? prev : [...prev, questionId]
        );
        advanceToNext(questionIndex);
    };

    const handleRadioChange = (questionId: string, optionValue: string, questionIndex: number) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: optionValue
        }));
        advanceToNext(questionIndex);
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

    const isQuizComplete = () => {
        return allQuestions.every(question => isQuestionComplete(question));
    };

    // Submit handler
    const handleSubmit = async () => {
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'}/api/match`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(answers),
            });

            if (!res.ok) {
                throw new Error(`Server error: ${res.status}`);
            }

            const matches = await res.json();
            localStorage.setItem("matches", JSON.stringify(matches));
            router.push("/matches");
        } catch (error) {
            console.error("Quiz submit error:", error);
            alert("Failed to submit quiz. Please try again later.");
        }
    };

    // Render checkbox question
    const renderCheckboxQuestion = (question: QuizQuestion, questionIndex: number) => {
        const selectionCount = getSelectionCount(question.id);
        const showContinue = selectionCount > 0 && !confirmedCheckboxIds.includes(question.id);

        return (
        <div key={question.id} className="checkbox-container">
            <h3 className="checkbox-question">
                {question.question}
            </h3>

            <p className="checkbox-selection-info">
                Select up to {question.maxSelections} option{(question.maxSelections || 0) > 1 ? 's' : ''}
                ({selectionCount}/{question.maxSelections} selected)
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

            {showContinue && (
                <button
                    type="button"
                    className="checkbox-continue"
                    onClick={() => handleCheckboxContinue(question.id, questionIndex)}
                >
                    Continue →
                </button>
            )}
        </div>
        );
    };

    // Render radio question
    const renderRadioQuestion = (question: QuizQuestion, questionIndex: number) => (
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
                                onChange={() => handleRadioChange(question.id, String(option.value), questionIndex)}
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

    const renderLikertQuestion = (question: QuizQuestion, questionIndex: number) => {
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
                                    onChange={() => handleRadioChange(question.id, String(option.value), questionIndex)}
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

    const renderQuestion = (question: QuizQuestion, questionIndex: number) => {
        switch (question.type) {
            case 'checkbox':
                return renderCheckboxQuestion(question, questionIndex);
            case 'radio':
                return renderRadioQuestion(question, questionIndex);
            case 'likert':
                return renderLikertQuestion(question, questionIndex);
            default:
                return null;
        }
    };

    return (
        <div className={`quiz-container ${hasStarted ? 'quiz-started' : 'quiz-not-started'}`}>
            <div className="quiz-progress-bar">
                <div className="quiz-progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <Link href="/" className="back-button">
                ← Back to Home
            </Link>
            <div className="header">
                <h1>Discover Your Perfect Program</h1>
                <p className="subtext">Based on Ontario University Data</p>
                <div className="circle-container">
                    <div className="info-circle-1">
                        <div className="circle-text">
                            <h2>Complete the 3 minute test</h2>
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
                            const questionIndex = allQuestions.findIndex(q => q.id === question.id);
                            return (
                                <div
                                    key={question.id}
                                    ref={(el) => { questionRefs.current[questionIndex] = el; }}
                                    data-index={questionIndex}
                                    className={`quiz-question-item ${getQuestionClass(questionIndex)}`}
                                    onClick={() => {
                                        if (hasStarted) setFocusedIndex(questionIndex);
                                    }}
                                >
                                    {renderQuestion(question, questionIndex)}
                                </div>
                            );
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