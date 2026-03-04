import './Header.css'

// O componente recebe funções (callbacks) e uma condição (boolean) via props
export default function Header({ onNew, showBack, onBack }) {
  return (
    <header className="header">
      <div className="header-inner">
        
        {/* Seção da Logo e Título do Hub */}
        <div className="header-brand">
          <div className="header-logo">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="var(--accent)" />
              <path d="M7 14L14 7L21 14L14 21L7 14Z" fill="var(--bg-0)" />
              <circle cx="14" cy="14" r="3" fill="var(--accent)" />
            </svg>
          </div>
          <div>
            <span className="header-title">Hub Educacional</span>
            <span className="header-subtitle">Recursos Inteligentes</span>
          </div>
        </div>

        {/* Lógica Condicional: Se 'showBack' for true, mostra "Voltar", senão mostra "Novo Recurso" */}
        <div className="header-actions">
          {showBack ? (
            <button className="btn btn-ghost" onClick={onBack}>
              {/* Ícone de Seta para Esquerda */}
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M10 3L5 8L10 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Voltar
            </button>
          ) : (
            <button className="btn btn-primary" onClick={onNew}>
              {/* Ícone de Plus (+) para Criar */}
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 3V13M3 8H13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
              </svg>
              Novo Recurso
            </button>
          )}
        </div>

      </div>
    </header>
  )
}