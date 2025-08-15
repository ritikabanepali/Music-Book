import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import Navbar from './Navbar';

const ProtectedRoute = () => {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // This div will provide a consistent layout for all protected pages
    return (
        <div className="App-main-layout"> 
            <Navbar />
            <main>
                <Outlet />
            </main>
        </div>
    );
};

export default ProtectedRoute;