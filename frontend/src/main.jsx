import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import BlindReviewPortal from './components/BlindReviewPortal.jsx';
import BlindReviewAnalysisPortal from './components/BlindReviewAnalysisPortal.jsx';
import './styles.css';

const searchParams = new URLSearchParams(window.location.search);
const mode = searchParams.get('mode');
const blindReviewMode = mode === 'blind-review';
const reviewAnalysisMode = mode === 'review-analysis';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {blindReviewMode ? (
      <BlindReviewPortal />
    ) : reviewAnalysisMode ? (
      <BlindReviewAnalysisPortal />
    ) : (
      <App />
    )}
  </React.StrictMode>,
);
