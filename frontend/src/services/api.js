import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// ── Interceptors ──────────────────────────────────────────────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Erro desconhecido'
    return Promise.reject(new Error(message))
  }
)

// ── Resources ─────────────────────────────────────────────────────────────────
export const resourcesApi = {
  list: (params) =>
    api.get('/resources/', { params }).then((r) => r.data),

  getById: (id) =>
    api.get(`/resources/${id}`).then((r) => r.data),

  create: (data) =>
    api.post('/resources/', data).then((r) => r.data),

  update: (id, data) =>
    api.patch(`/resources/${id}`, data).then((r) => r.data),

  delete: (id) =>
    api.delete(`/resources/${id}`),
}

// ── AI ────────────────────────────────────────────────────────────────────────
export const aiApi = {
  generate: (data) =>
    api.post('/ai/generate', data).then((r) => r.data),
}

// ── Health ────────────────────────────────────────────────────────────────────
export const healthApi = {
  check: () =>
    api.get('/health').then((r) => r.data),
}

export default api
