import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import BlindReviewPortal from './components/BlindReviewPortal.jsx';
import './styles.css';

const searchParams = new URLSearchParams(window.location.search);
const blindReviewMode = searchParams.get('mode') === 'blind-review';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {blindReviewMode ? <BlindReviewPortal /> : <App />}
  </React.StrictMode>,
);
