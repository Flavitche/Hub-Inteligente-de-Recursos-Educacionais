import { useState, useEffect, useCallback } from 'react'
import { useResources, useResourceMutation } from '../hooks/useResources'
import ResourceCard from '../components/ResourceCard'
import Pagination from '../components/Pagination'
import Toast from '../components/Toast'
import './ResourceList.css'

const TYPES = ['', 'Video', 'PDF', 'Link']

export default function ResourceList({ onEdit, onNew }) {
  const { data, loading, error, fetchResources } = useResources()
  const { deleteResource }                        = useResourceMutation()

  const [page, setPage]         = useState(1)
  const [search, setSearch]     = useState('')
  const [typeFilter, setType]   = useState('')
  const [toast, setToast]       = useState(null)

  const load = useCallback(() => {
    const params = { page, page_size: 9 }
    if (typeFilter) params.type = typeFilter
    if (search.trim().length >= 2) params.search = search.trim()
    fetchResources(params)
  }, [page, search, typeFilter, fetchResources])

  useEffect(() => { load() }, [load])

  // Debounce search
  useEffect(() => {
    if (search.length === 0 || search.length >= 2) {
      const t = setTimeout(() => { setPage(1); load() }, 400)
      return () => clearTimeout(t)
    }
  }, [search])

  const handleDelete = async (id) => {
    if (!confirm('Tem certeza que deseja excluir este recurso?')) return
    try {
      await deleteResource(id)
      setToast({ message: 'Recurso excluído com sucesso!', type: 'success' })
      load()
    } catch (err) {
      setToast({ message: err.message, type: 'error' })
    }
  }

  const handleTypeChange = (t) => {
    setType(t)
    setPage(1)
  }

  return (
    <div className="list-page">
      {/* ── Header ── */}
      <div className="list-header">
        <div>
          <h1 className="list-title">Recursos Educacionais</h1>
          <p className="list-subtitle">
            {data ? `${data.total} recurso${data.total !== 1 ? 's' : ''} encontrado${data.total !== 1 ? 's' : ''}` : 'Carregando...'}
          </p>
        </div>
        <button className="btn btn-primary" onClick={onNew}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3V13M3 8H13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
          </svg>
          Novo
        </button>
      </div>

      {/* ── Filters ── */}
      <div className="list-filters">
        <div className="search-wrap">
          <svg className="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M11 11L14 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <input
            type="text"
            className="search-input"
            placeholder="Buscar recursos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button className="search-clear" onClick={() => setSearch('')}>×</button>
          )}
        </div>

        <div className="type-filters">
          {TYPES.map((t) => (
            <button
              key={t || 'all'}
              className={`type-btn ${typeFilter === t ? 'active' : ''}`}
              onClick={() => handleTypeChange(t)}
            >
              {t || 'Todos'}
            </button>
          ))}
        </div>
      </div>

      {/* ── Content ── */}
      {loading && (
        <div className="list-skeleton">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton-card" style={{ animationDelay: `${i * 0.05}s` }} />
          ))}
        </div>
      )}

      {error && !loading && (
        <div className="list-error">
          <span className="error-icon">⚠</span>
          <p>{error}</p>
          <button className="btn btn-ghost" onClick={load}>Tentar novamente</button>
        </div>
      )}

      {!loading && !error && data?.items?.length === 0 && (
        <div className="list-empty">
          <div className="empty-icon">◈</div>
          <h3>Nenhum recurso encontrado</h3>
          <p>Tente ajustar os filtros ou crie um novo recurso.</p>
          <button className="btn btn-primary" onClick={onNew}>Criar primeiro recurso</button>
        </div>
      )}

      {!loading && !error && data?.items?.length > 0 && (
        <>
          <div className="resources-grid">
            {data.items.map((r, i) => (
              <ResourceCard
                key={r.id}
                resource={r}
                onEdit={onEdit}
                onDelete={handleDelete}
                style={{ animationDelay: `${i * 0.04}s` }}
              />
            ))}
          </div>
          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            onChange={setPage}
          />
        </>
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  )
}
