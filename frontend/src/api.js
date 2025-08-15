import axios from 'axios'; // makes HTTP requests from browser to API

// axios.get('http://127.0.0.1:8000/api/reviews') to => apiClient.get('/reviews')
const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
});

// automatically adds the Authorization header to every request
apiClient.interceptors.request.use(config => { // request inceptor before a request is sent
    const token = localStorage.getItem('accessToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

export default apiClient;