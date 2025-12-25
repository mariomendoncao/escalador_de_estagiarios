import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'https://api.escala-estagiarios.mmendol.com',
    timeout: 120000, // 120 seconds for large imports
});

export default api;
