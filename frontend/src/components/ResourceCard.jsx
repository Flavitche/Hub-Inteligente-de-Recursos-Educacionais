import { useState } from 'react'
import ViewModal from './ViewModal'
import './ResourceCard.css'

// Configurações visuais 
const TYPE_CONFIG = {
  Video: { icon: '▶', color: 'var(--red)',   bg: 'var(--red-dim)'  },
  PDF:   { icon: '⬡', color: 'var(--blue)',  bg: 'var(--blue-dim)' },
  Link:  { icon: '◈', color: 'var(--green)', bg: 'var(--green-dim)'},
}

export default function ResourceCard({ resource, onEdit, onDelete, style }) {
  // Estado para controlar se o modal de detalhes está aberto
  const [viewing, setViewing] = useState(false)
  
  // Define qual configuração usar (se não achar o tipo, usa 'Link' como padrão)
  const cfg = TYPE_CONFIG[resource.type] || TYPE_CONFIG.Link

  // Função simples para formatar a data (ex: 04 mar. 2026)
  const formatDate = (iso) =>
    new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })

  // Lógica para abrir o modal apenas se o usuário não clicar nos botões de ação
  const handleCardClick = (e) => {
    if (e.target.closest('.card-actions') || e.target.closest('.card-link')) return
    setViewing(true)
  }

  return (
    <>
      <article
        className="resource-card animate-fade"
        style={style}
        onClick={handleCardClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setViewing(true)} // Acessibilidade: abrir com Enter
      >
        {/* Cabeçalho: Tipo do recurso e data de criação */}
        <div className="card-header">
          <span className="card-type-badge" style={{ color: cfg.color, background: cfg.bg }}>
            {cfg.icon} {resource.type}
          </span>
          <time className="card-date">{formatDate(resource.created_at)}</time>
        </div>

        <h3 className="card-title">{resource.title}</h3>

        {/* Descrição: Só aparece se existir uma */}
        {resource.description && (
          <p className="card-description">{resource.description}</p>
        )}

        {/* Tags: Faz um loop para mostrar cada tag do recurso */}
        {resource.tags?.length > 0 && (
          <div className="card-tags">
            {resource.tags.map((tag) => (
              <span key={tag} className="tag">{tag}</span>
            ))}
          </div>
        )}

        <div className="card-footer">
          {/* Link externo: stopPropagation impede que o modal abra ao clicar aqui */}
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="card-link"
            onClick={(e) => e.stopPropagation()}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M5.5 2.5H2.5C1.95 2.5 1.5 2.95 1.5 3.5V11.5C1.5 12.05 1.95 12.5 2.5 12.5H10.5C11.05 12.5 11.5 12.05 11.5 11.5V8.5M8.5 1.5H12.5M12.5 1.5V5.5M12.5 1.5L6.5 7.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Acessar
          </a>

          {/* Botões de Editar e Excluir */}
          <div className="card-actions">
            <button
              className="btn btn-ghost btn-sm"
              onClick={(e) => { e.stopPropagation(); onEdit(resource) }}
            >
              Editar
            </button>
            <button
              className="btn btn-danger btn-sm"
              onClick={(e) => { e.stopPropagation(); onDelete(resource.id) }}
            >
              Excluir
            </button>
          </div>
        </div>

        <div className="card-hint">clique para ver detalhes</div>
      </article>

      {/* Se 'viewing' for true, renderiza o Modal de visualização */}
      {viewing && (
        <ViewModal resource={resource} onClose={() => setViewing(false)} />
      )}
    </>
  )
}