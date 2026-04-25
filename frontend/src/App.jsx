import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="App" style={{ textAlign: 'center', padding: '50px', fontFamily: 'sans-serif' }}>
        <Routes>
          <Route path="/" element={<h1>Mock Interviewer — Coming Soon</h1>} />
          <Route path="/login" element={<h2>Login Page Placeholder</h2>} />
          <Route path="/signup" element={<h2>Signup Page Placeholder</h2>} />
          <Route path="/dashboard" element={<h2>Dashboard Page Placeholder</h2>} />
          <Route path="/interview" element={<h2>Interview Session Placeholder</h2>} />
          <Route path="/history" element={<h2>Interview History Placeholder</h2>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;