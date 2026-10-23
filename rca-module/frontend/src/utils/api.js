import axios from 'axios'

const api = axios.create({
  baseURL: '', // proxied by Vite in dev
  timeout: 120000, // LLM calls can take time
})

export default api
