import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const response = await apiClient.post('/token/', {
                username: username,
                password: password,
            });
            localStorage.setItem('accessToken', response.data.access);
            navigate('/home'); // Navigate to home page on success
        } catch (err) {
            setError('Login failed. Please check your credentials.');
            console.error(err);
        }
    };

    return (
        <header className="App-header">
            <h1 className="arizonia-regular">Music Book</h1>
            <form onSubmit={handleSubmit}>
                <h2>Login</h2>
                {error && <p style={{ color: 'red' }}>{error}</p>}
                <div>
                    <label>Username:</label>
                    <input type="text" value={username} onChange={e => setUsername(e.target.value)} />
                </div>
                <div>
                    <label>Password:</label>
                    <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
                </div>
                <button type="submit">Login</button>
            </form>
        </header>
    );
}

export default Login;