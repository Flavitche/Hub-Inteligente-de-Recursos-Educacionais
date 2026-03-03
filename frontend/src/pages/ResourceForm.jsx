import { useState, useEffect } from 'react'
import { useResourceMutation, useAIGenerate } from '../hooks/useResources'
import Toast from '../components/Toast'
import './ResourceForm.css'

const TYPES = ['Video', 'PDF', 'Link']

const EMPTY = { title: '', description: '', type: 'Video', url: '', tags: [] }

export default function ResourceForm({ resource, onSuccess, onCancel }) {
  const isEditing = !!resource
  const { loading: saving, createResource, updateResource } = useResourceMutation()
  const { loading: aiLoading, generate }                    = useAIGenerate()

  const [form, setForm]     = useState(EMPTY)
  const [tagInput, setTagInput] = useState('')
  const [toast, setToast]   = useState(null)
  const [errors, setErrors] = useState({})
  const [aiGlow, setAiGlow] = useState(false)

  useEffect(() => {
    if (resource) {
      setForm({
        title:       resource.title       || '',
        description: resource.description || '',
        type:        resource.type        || 'Video',
        url:         resource.url         || '',
        tags:        resource.tags        || [],
      })
    }
  }, [resource])

  const set = (field, value) => {
    setForm((f) => ({ ...f, [field]: value }))
    setErrors((e) => ({ ...e, [field]: null }))
  }

  // ── Tags ──────────────────────────────────────────────────────────────────
  const addTag = (raw) => {
    const tag = raw.trim().toLowerCase()
    if (!tag || form.tags.includes(tag) || form.tags.length >= 10) return
    set('tags', [...form.tags, tag])
    setTagInput('')
  }

  const removeTag = (tag) => set('tags', form.tags.filter((t) => t !== tag))

  const handleTagKey = (e) => {
    if (['Enter', ',', ' '].includes(e.key)) {
      e.preventDefault()
      addTag(tagInput)
    }
    if (e.key === 'Backspace' && !tagInput && form.tags.length) {
      removeTag(form.tags[form.tags.length - 1])
    }
  }

  // ── Validation ────────────────────────────────────────────────────────────
  const validate = () => {
    const e = {}
    if (!form.title.trim() || form.title.length < 3)
      e.title = 'Título deve ter pelo menos 3 caracteres'
    if (!form.url.trim())
      e.url = 'URL é obrigatória'
    else if (!/^https?:\/\/.+/.test(form.url))
      e.url = 'URL deve começar com http:// ou https://'
    return e
  }

  // ── AI Generate ───────────────────────────────────────────────────────────
  const handleGenerate = async () => {
    if (!form.title.trim()) {
      setErrors({ title: 'Preencha o título antes de gerar com IA' })
      return
    }
    try {
      const result = await generate(form.title, form.type)
      setAiGlow(true)
      setTimeout(() => setAiGlow(false), 1500)
      set('description', result.description)
      set('tags', result.tags)
      setToast({ message: '✨ Descrição e tags geradas com IA!', type: 'success' })
    } catch (err) {
      setToast({ message: `Erro na IA: ${err.message}`, type: 'error' })
    }
  }

  // ── Submit ────────────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    const e = validate()
    if (Object.keys(e).length) { setErrors(e); return }

    try {
      if (isEditing) {
        await updateResource(resource.id, form)
        setToast({ message: 'Recurso atualizado!', type: 'success' })
      } else {
        await createResource(form)
        setToast({ message: 'Recurso criado com sucesso!', type: 'success' })
      }
      setTimeout(() => onSuccess(), 800)
    } catch (err) {
      setToast({ message: err.message, type: 'error' })
    }
  }

  return (
    <div className="form-page animate-fade">
      <div className="form-header">
        <h1 className="form-title">
          {isEditing ? 'Editar Recurso' : 'Novo Recurso'}
        </h1>
        <p className="form-subtitle">
          {isEditing
            ? 'Atualize as informações do recurso educacional'
            : 'Preencha os dados ou use a IA para gerar automaticamente'}
        </p>
      </div>

      <div className="form-card">
        {/* ── Title ── */}
        <div className={`field ${errors.title ? 'field-error' : ''}`}>
          <label className="label">Título <span className="required">*</span></label>
          <input
            className="input"
            type="text"
            placeholder="Ex: Python para Iniciantes — Curso Completo"
            value={form.title}
            onChange={(e) => set('title', e.target.value)}
            maxLength={255}
          />
          {errors.title && <span className="field-msg">{errors.title}</span>}
        </div>

        {/* ── Type + URL ── */}
        <div className="field-row">
          <div className="field">
            <label className="label">Tipo <span className="required">*</span></label>
            <div className="type-selector">
              {TYPES.map((t) => (
                <button
                  key={t}
                  type="button"
                  className={`type-option ${form.type === t ? 'selected' : ''}`}
                  onClick={() => set('type', t)}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className={`field field-grow ${errors.url ? 'field-error' : ''}`}>
            <label className="label">URL <span className="required">*</span></label>
            <input
              className="input"
              type="url"
              placeholder="https://..."
              value={form.url}
              onChange={(e) => set('url', e.target.value)}
            />
            {errors.url && <span className="field-msg">{errors.url}</span>}
          </div>
        </div>

        {/* ── AI Button ── */}
        <div className="ai-section">
          <div className="ai-divider">
            <span>ou gere automaticamente com IA</span>
          </div>
          <button
            type="button"
            className={`btn btn-ai btn-lg ai-generate-btn ${aiLoading ? 'loading' : ''}`}
            onClick={handleGenerate}
            disabled={aiLoading || saving}
          >
            {aiLoading ? (
              <>
                <span className="spinner" />
                Gerando com IA...
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M9 1L11.5 6.5L17 9L11.5 11.5L9 17L6.5 11.5L1 9L6.5 6.5L9 1Z" fill="currentColor" opacity="0.9"/>
                </svg>
                Gerar Descrição e Tags com IA
              </>
            )}
          </button>
        </div>

        {/* ── Description ── */}
        <div className={`field ${aiGlow ? 'field-glow' : ''}`}>
          <label className="label">
            Descrição
            {aiGlow && <span className="ai-badge">✨ Gerado por IA</span>}
          </label>
          <textarea
            className="textarea"
            placeholder="Descreva o conteúdo do recurso educacional..."
            value={form.description}
            onChange={(e) => set('description', e.target.value)}
            rows={5}
            maxLength={5000}
          />
          <span className="char-count">{form.description.length}/5000</span>
        </div>

        {/* ── Tags ── */}
        <div className={`field ${aiGlow ? 'field-glow' : ''}`}>
          <label className="label">
            Tags
            {form.tags.length > 0 && (
              <span className="tag-count">{form.tags.length}/10</span>
            )}
          </label>
          <div className="tags-input-wrap">
            {form.tags.map((tag) => (
              <span key={tag} className="tag tag-removable">
                {tag}
                <button
                  type="button"
                  className="tag-remove"
                  onClick={() => removeTag(tag)}
                  aria-label={`Remover tag ${tag}`}
                >×</button>
              </span>
            ))}
            <input
              className="tags-input"
              type="text"
              placeholder={form.tags.length < 10 ? 'Adicionar tag...' : 'Máximo atingido'}
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagKey}
              onBlur={() => tagInput && addTag(tagInput)}
              disabled={form.tags.length >= 10}
            />
          </div>
          <span className="field-hint">Enter, vírgula ou espaço para adicionar</span>
        </div>

        {/* ── Actions ── */}
        <div className="form-actions">
          <button type="button" className="btn btn-ghost btn-lg" onClick={onCancel}>
            Cancelar
          </button>
          <button
            type="button"
            className="btn btn-primary btn-lg"
            onClick={handleSubmit}
            disabled={saving}
          >
            {saving ? (
              <><span className="spinner spinner-dark" /> Salvando...</>
            ) : (
              isEditing ? 'Salvar alterações' : 'Criar recurso'
            )}
          </button>
        </div>
      </div>

      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
      )}
    </div>
  )
}
