import { useEffect } from 'react'
import './ViewModal.css'

// Reaproveita as cores e ícones baseados no tipo do recurso
const TYPE_CONFIG = {
  Video: { icon: '▶', color: 'var(--red)',   bg: 'var(--red-dim)'  },
  PDF:   { icon: '⬡', color: 'var(--blue)',  bg: 'var(--blue-dim)' },
  Link:  { icon: '◈', color: 'var(--green)', bg: 'var(--green-dim)'},
}

export default function ViewModal({ resource, onClose }) {
  const cfg = TYPE_CONFIG[resource.type] || TYPE_CONFIG.Link

  // useEffect: Controla comportamentos que "saem" do React e vão para o navegador
  useEffect(() => {
    // 1. Fecha o modal se o usuário apertar a tecla 'Esc'
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    
    // 2. Trava o scroll da página ao fundo enquanto o modal está aberto
    document.body.style.overflow = 'hidden'
    
    // Função de limpeza (cleanup): desfaz tudo quando o modal fecha
    return () => {
      document.removeEventListener('keydown', handler)
      document.body.style.overflow = ''
    }
  }, [onClose])

  // Formata a data de um jeito mais amigável (ex: 04 de março de 2026)
  const formatDate = (iso) =>
    new Date(iso).toLocaleDateString('pt-BR', {
      day: '2-digit', month: 'long', year: 'numeric'
    })

  return (
    /* Overlay: o fundo escuro. Se clicar nele, o modal fecha */
    <div className="view-overlay" onClick={onClose}>
      
      {/* Box: a janela branca. stopPropagation impede que clicar aqui dentro feche o modal */}
      <div className="view-box" onClick={(e) => e.stopPropagation()}>

        {/* Cabeçalho com Badge e botão de fechar (X) */}
        <div className="view-header">
          <span className="view-type-badge" style={{ color: cfg.color, background: cfg.bg }}>
            {cfg.icon} {resource.type}
          </span>
          <button className="view-close" onClick={onClose} aria-label="Fechar">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M4 4L14 14M14 4L4 14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        <h2 className="view-title">{resource.title}</h2>

        {/* Seção de Descrição */}
        {resource.description && (
          <div className="view-section">
            <span className="view-label">Descrição</span>
            <p className="view-description">{resource.description}</p>
          </div>
        )}

        {/* Lista de Tags mapeada */}
        {resource.tags?.length > 0 && (
          <div className="view-section">
            <span className="view-label">Tags</span>
            <div className="view-tags">
              {resource.tags.map((tag) => (
                <span key={tag} className="tag">{tag}</span>
              ))}
            </div>
          </div>
        )}

        {/* Datas de criação e atualização */}
        <div className="view-meta">
          <div className="view-meta-item">
            <span className="view-label">Criado em</span>
            <span className="view-meta-value">{formatDate(resource.created_at)}</span>
          </div>
          <div className="view-meta-item">
            <span className="view-label">Atualizado em</span>
            <span className="view-meta-value">{formatDate(resource.updated_at)}</span>
          </div>
        </div>

        {/* Botão de ação principal para abrir o link externo */}
        <a
          href={resource.url}
          target="_blank"
          rel="noopener noreferrer"
          className="view-link-btn"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M5.5 2.5H2.5C1.95 2.5 1.5 2.95 1.5 3.5V11.5C1.5 12.05 1.95 12.5 2.5 12.5H10.5C11.05 12.5 11.5 12.05 11.5 11.5V8.5M8.5 1.5H12.5M12.5 1.5V5.5M12.5 1.5L6.5 7.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Acessar recurso
        </a>

      </div>
    </div>
  )
}