"use client";
import { useState } from 'react';
import './chance.css';

interface ChanceMeFormData {
    school: string;
    program: string;
    top6: string;
    ecs: string;
}

export default function ChanceMe() {
    const [formData, setFormData] = useState<ChanceMeFormData>({
        school: '',
        program: '',
        top6: '',
        ecs: ''
    });
    
    const [result, setResult] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleInputChange = (field: keyof ChanceMeFormData, value: string) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const isFormValid = () => {
        return formData.school.trim() !== '' && 
               formData.program.trim() !== '' && 
               formData.top6.trim() !== '' &&
               !isNaN(Number(formData.top6)) &&
               Number(formData.top6) >= 0 &&
               Number(formData.top6) <= 100;
    };

    const handleSubmit = async () => {
        if (!isFormValid()) {
            setError('Please fill in all required fields with valid data');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch("http://localhost:5001/api/chance-me", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (data.success) {
                setResult(data.prediction);
            } else {
                setError(data.error || 'An error occurred');
            }
        } catch (err) {
            setError('Failed to connect to server. Please make sure the backend is running.');
            console.error('Submit error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setFormData({
            school: '',
            program: '',
            top6: '',
            ecs: ''
        });
        setResult(null);
        setError(null);
    };

    return (
        <div className="chance-container">
            <div className="header">
                <h1>calculate your chances</h1>
                <p className="subtext">Find your admission chances based on real admissions data. These results do not guarantee your acceptance.</p>
            </div>

            <div className="chance-me-content">
                <div className="form-container">
                    <div className="input-group">
                        <label htmlFor="school">University/School *</label>
                        <input
                            id="school"
                            type="text"
                            placeholder="e.g., Waterloo"
                            value={formData.school}
                            onChange={(e) => handleInputChange('school', e.target.value)}
                            className="form-input"
                        />
                    </div>

                    <div className="input-group">
                        <label>Program *</label>
                        <input
                            id="program"
                            type="text"
                            placeholder="e.g., Software Engineering"
                            value={formData.program}
                            onChange={(e) => handleInputChange('program', e.target.value)}
                            className="form-input"
                        />
                    </div>

                    <div className="input-group">
                        <label htmlFor="top6">Top 6 Average (%) *</label>
                        <input
                            id="top6"
                            type="number"
                            min="0"
                            max="100"
                            step="0.1"
                            placeholder="e.g., 95.5"
                            value={formData.top6}
                            onChange={(e) => handleInputChange('top6', e.target.value)}
                            className="form-input"
                        />
                    </div>

                    <div className="input-group">
                        <label htmlFor="ecs">Extracurriculars (optional)</label>
                        <input
                            id="ecs"
                            type="text"
                            placeholder="e.g., robotics, student council, volunteering"
                            value={formData.ecs}
                            onChange={(e) => handleInputChange('ecs', e.target.value)}
                            className="form-input"
                        />
                        <small className="input-help">Separate multiple activities with commas</small>
                    </div>

                    <div className="button-group">
                        <button
                            onClick={handleSubmit}
                            disabled={!isFormValid() || loading}
                            className={`submit-button ${!isFormValid() || loading ? 'disabled' : ''}`}
                        >
                            {loading ? 'Calculating...' : 'Calculate My Chances'}
                        </button>
                        
                        <button
                            onClick={handleReset}
                            className="reset-button"
                            disabled={loading}
                        >
                            Reset Form
                        </button>
                    </div>

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
                        </div>
                    )}
                </div>

                {result && (
                    <div className="result-container">
                        <h3>Your Admission Prediction</h3>
                        <div className="result-content">
                            <pre>{result}</pre>
                        </div>
                        <div className="disclaimer">
                            <p>
                                <strong>Disclaimer:</strong> This prediction is based on historical data and should be used as a general guide only. 
                                Actual admission decisions depend on many factors including essays, interviews, and current competition levels.
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}