import { useState, useEffect } from 'react'
import type { ApiResponse } from '@/types/api'

interface UseApiQueryOptions<T> {
  onSuccess?: (data: T) => void
  onError?: (error: string) => void
  enabled?: boolean
}

interface UseApiQueryResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function useApiQuery<T>(
  queryFn: () => Promise<ApiResponse<T>>,
  options: UseApiQueryOptions<T> = {}
): UseApiQueryResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await queryFn()
      
      if (response.error) {
        setError(response.error)
        options.onError?.(response.error)
      } else if (response.data) {
        setData(response.data)
        options.onSuccess?.(response.data)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMessage)
      options.onError?.(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (options.enabled !== false) {
      fetchData()
    }
  }, [options.enabled])

  return {
    data,
    loading,
    error,
    refetch: fetchData
  }
}

// Specific hooks for common data fetching
export const useWells = () => {
  const { apiClient } = require('@/lib/api-client')
  return useApiQuery(() => apiClient.getWells())
}

export const useProductionData = () => {
  const { apiClient } = require('@/lib/api-client')
  return useApiQuery(() => apiClient.getProductionData())
}

export const usePvtData = () => {
  const { apiClient } = require('@/lib/api-client')
  return useApiQuery(() => apiClient.getPvtData())
}