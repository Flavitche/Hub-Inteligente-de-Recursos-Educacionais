import { useState } from 'react'
import Header from './components/Header'
import ResourceList from './pages/ResourceList'
import ResourceForm from './pages/ResourceForm'
import './App.css'

export default function App() {
  const [view, setView]           = useState('list')   // 'list' | 'create' | 'edit'
  const [editingResource, setEditingResource] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const goToCreate = () => {
    setEditingResource(null)
    setView('create')
  }

  const goToEdit = (resource) => {
    setEditingResource(resource)
    setView('edit')
  }

  const goToList = (refresh = false) => {
    setView('list')
    if (refresh) setRefreshKey((k) => k + 1)
  }

  return (
    <div className="app-shell">
      <Header onNew={goToCreate} showBack={view !== 'list'} onBack={() => goToList()} />

      <main className="app-main">
        {view === 'list' && (
          <ResourceList
            key={refreshKey}
            onEdit={goToEdit}
            onNew={goToCreate}
          />
        )}
        {(view === 'create' || view === 'edit') && (
          <ResourceForm
            resource={editingResource}
            onSuccess={() => goToList(true)}
            onCancel={() => goToList()}
          />
        )}
      </main>
    </div>
  )
}
