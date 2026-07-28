import axios from 'axios';

// Lida em tempo de build (NEXT_PUBLIC_*). Precisa ser a URL que o navegador
// do usuário alcança — definida em frontend/.env.local.
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 180000, // triagem em CPU pode demorar bastante
  headers: { 'Content-Type': 'application/json' },
});

export default api;
