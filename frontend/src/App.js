import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import all your pages and components
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import AlbumDetailPage from './pages/AlbumDetailPage';
import MyReviewsPage from './pages/MyReviewsPage';

import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public Login Route */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected Routes - All routes inside here require a login */}
          <Route element={<ProtectedRoute />}>
            <Route path="/home" element={<HomePage />} />
            <Route path="/album/:spotifyId" element={<AlbumDetailPage />} />
            <Route path="/my-reviews" element={<MyReviewsPage />} />
          </Route>

          {/* If a user tries any other path, redirect them to login */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;