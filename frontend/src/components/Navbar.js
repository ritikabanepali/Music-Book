import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Navbar() {
    const navigate = useNavigate();

    const handleLogout = () => {
        // Clear the token from storage
        localStorage.removeItem('accessToken');
        // Navigate back to the login page
        navigate('/login');
    };

    return (
        <nav style={{ padding: '10px', background: '#f0f0f0', marginBottom: '20px' }}>
            <Link to="/home" style={{ marginRight: '15px' }}>Home (Search)</Link>
            <Link to="/my-reviews" style={{ marginRight: '15px' }}>My Reviews</Link>
            <button onClick={handleLogout}>Logout</button>
        </nav>
    );
}

export default Navbar;