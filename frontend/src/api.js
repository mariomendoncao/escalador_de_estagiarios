import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 120000, // 120 seconds for large imports
});

export default api;
