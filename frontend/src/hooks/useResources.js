import { useState, useCallback } from 'react'
import { resourcesApi, aiApi } from '../services/api'

export function useResources() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const fetchResources = useCallback(async (params = {}) => {
    setLoading(true)
    setError(null)
    try {
      const result = await resourcesApi.list(params)
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, fetchResources }
}

export function useResourceMutation() {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const createResource = useCallback(async (payload) => {
    setLoading(true)
    setError(null)
    try {
      const result = await resourcesApi.create(payload)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const updateResource = useCallback(async (id, payload) => {
    setLoading(true)
    setError(null)
    try {
      const result = await resourcesApi.update(id, payload)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const deleteResource = useCallback(async (id) => {
    setLoading(true)
    setError(null)
    try {
      await resourcesApi.delete(id)
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { loading, error, createResource, updateResource, deleteResource }
}

export function useAIGenerate() {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const generate = useCallback(async (title, type) => {
    setLoading(true)
    setError(null)
    try {
      const result = await aiApi.generate({ title, type })
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { loading, error, generate }
}
