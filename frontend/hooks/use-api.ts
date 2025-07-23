"use client"

import { useState, useEffect } from 'react'
import { apiClient, type ApiResponse } from '@/lib/api-client'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => void
}

// Simplified hooks to avoid dependency issues
export function useWells(): UseApiState<any[]> {
  const [data, setData] = useState<any[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getWells()
      
      if (response.error) {
        setError(response.error)
        // Fallback to demo data if server error
        setData([])
      } else {
        setData(response.data || [])
        setError(null)
      }
    } catch (err) {
      console.warn('Wells API failed, using fallback data:', err)
      setError('Backend disconnected - using demo data')
      // Fallback data when backend is not available
      setData([
        { id: 1, name: "301", status: "active" },
        { id: 2, name: "302", status: "active" },
        { id: 3, name: "303", status: "active" }
      ])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, []) // Empty dependency array - only run once

  return {
    data,
    loading,
    error,
    refetch: fetchData
  }
}

export function useProductionData(): UseApiState<any[]> {
  const [data, setData] = useState<any[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getProductionData()
      
      if (response.error) {
        setError(response.error)
        // Fallback to demo data
        setData([])
      } else {
        setData(response.data || [])
        setError(null)
      }
    } catch (err) {
      console.warn('Production API failed, using fallback data:', err)
      setError('Backend disconnected - using demo data')
      // Fallback production data
      setData([
        { Qo_ton: 15.2, Obv_percent: 25.0, well: "301", Date: "2025-07-21" },
        { Qo_ton: 18.5, Obv_percent: 18.5, well: "302", Date: "2025-07-21" },
        { Qo_ton: 12.1, Obv_percent: 35.2, well: "303", Date: "2025-07-21" }
      ])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, []) // Empty dependency array - only run once

  return {
    data,
    loading,
    error,
    refetch: fetchData
  }
}

export function useGanttData(): UseApiState<any[]> {
  const [data, setData] = useState<any[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getGanttData()
      
      if (response.error) {
        setError(response.error)
        setData(null)
      } else {
        setData(response.data || null)
        setError(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect to server')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, []) // Empty dependency array - only run once

  return {
    data,
    loading,
    error,
    refetch: fetchData
  }
}

export function usePvtData(): UseApiState<any[]> {
  const [data, setData] = useState<any[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getPvtData()
      
      if (response.error) {
        setError(response.error)
        setData(null)
      } else {
        setData(response.data || null)
        setError(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect to server')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, []) // Empty dependency array - only run once

  return {
    data,
    loading,
    error,
    refetch: fetchData
  }
}