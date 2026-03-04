import { useEffect } from 'react'
import './ConfirmModal.css'

export default function ConfirmModal({ title, message, onConfirm, onCancel }) {
  // Fecha com ESC
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onCancel() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onCancel])

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="modal-icon">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <circle cx="14" cy="14" r="13" stroke="var(--red)" strokeWidth="1.5" />
            <path d="M14 8V15" stroke="var(--red)" strokeWidth="2" strokeLinecap="round" />
            <circle cx="14" cy="19.5" r="1.2" fill="var(--red)" />
          </svg>
        </div>

        <div className="modal-content">
          <h3 className="modal-title">{title}</h3>
          <p className="modal-message">{message}</p>
        </div>

        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onCancel}>
            Cancelar
          </button>
          <button className="btn btn-danger-solid" onClick={onConfirm}>
            Sim, excluir
          </button>
        </div>
      </div>
    </div>
  )
}
