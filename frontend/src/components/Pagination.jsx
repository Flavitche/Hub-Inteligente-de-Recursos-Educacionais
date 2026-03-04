import './Pagination.css'

export default function Pagination({ page, totalPages, onChange }) {
  // Se só tiver uma página, não precisa mostrar a barra de navegação
  if (totalPages <= 1) return null

  // Cálculo para mostrar apenas algumas páginas vizinhas 
  const pages = []
  const start = Math.max(1, page - 2) // Garante que o início não seja menor que 1
  const end   = Math.min(totalPages, page + 2) // Garante que o fim não passe do total

  // Monta o array de números das páginas que vão aparecer no meio
  for (let i = start; i <= end; i++) pages.push(i)

  return (
    <nav className="pagination">
      {/* Botão Anterior: desativa se estivermos na primeira página */}
      <button
        className="page-btn"
        onClick={() => onChange(page - 1)}
        disabled={page === 1}
        aria-label="Página anterior"
      >
        ‹
      </button>

      {/* Se a primeira página não estiver no range, mostra o número 1 e reticências (...) */}
      {start > 1 && (
        <>
          <button className="page-btn" onClick={() => onChange(1)}>1</button>
          {start > 2 && <span className="page-ellipsis">…</span>}
        </>
      )}

      {/* Renderiza a lista de páginas próximas à atual */}
      {pages.map((p) => (
        <button
          key={p}
          className={`page-btn ${p === page ? 'active' : ''}`} // Destaca a página atual
          onClick={() => onChange(p)}
        >
          {p}
        </button>
      ))}

      {/* Se a última página não estiver no range, mostra reticências e o número total */}
      {end < totalPages && (
        <>
          {end < totalPages - 1 && <span className="page-ellipsis">…</span>}
          <button className="page-btn" onClick={() => onChange(totalPages)}>{totalPages}</button>
        </>
      )}

      {/* Botão Próximo: desativa se estivermos na última página */}
      <button
        className="page-btn"
        onClick={() => onChange(page + 1)}
        disabled={page === totalPages}
        aria-label="Próxima página"
      >
        ›
      </button>
    </nav>
  )
}