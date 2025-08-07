// API Client for FastAPI Backend Integration
import type { 
  ApiResponse, 
  LoginResponse, 
  Well, 
  Production, 
  PVT, 
  Tops,
  FaultData,
  BoundaryData,
  GanttData
} from '@/types/api'
import { logger } from './logger'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_BASE_PATH = process.env.NEXT_PUBLIC_API_BASE_PATH || '/api/v1'

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${API_BASE_URL}${API_BASE_PATH}`
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`
    const method = options.method || 'GET'
    
    try {
      logger.apiRequest(endpoint, method)
      
      // Get auth token from localStorage
      const token = localStorage.getItem('authToken')
      
      const response = await fetch(url, {
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorText = await response.text()
        const errorMessage = `HTTP ${response.status}: ${errorText}`
        logger.apiError(endpoint, errorMessage)
        throw new Error(errorMessage)
      }

      const data = await response.json()
      logger.apiResponse(endpoint, response.status, data)
      return { data }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Network connection failed'
      logger.apiError(endpoint, error)
      return { error: errorMessage }
    }
  }

  // Authentication
  async login(username: string, password: string): Promise<ApiResponse<LoginResponse>> {
    return this.request('/auth/login_nextjs', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  }

  // Wells data
  async getWells(): Promise<ApiResponse<Well[]>> {
    return this.request('/karatobe/wells')
  }

  // Production data
  async getProductionData(): Promise<ApiResponse<Production[]>> {
    return this.request('/karatobe/production')
  }

  // Faults data
  async getFaults(): Promise<ApiResponse<FaultData[]>> {
    return this.request('/karatobe/faults')
  }

  // Boundaries data  
  async getBoundaries(): Promise<ApiResponse<BoundaryData[]>> {
    return this.request('/karatobe/boundaries')
  }

  // Gantt data
  async getGanttData(): Promise<ApiResponse<GanttData[]>> {
    return this.request('/karatobe/gantt')
  }

  // PVT data
  async getPvtData(): Promise<ApiResponse<PVT[]>> {
    return this.request('/karatobe/pvt')
  }

  // Tops data
  async getTopsData(): Promise<ApiResponse<Tops[]>> {
    return this.request('/karatobe/tops')
  }

  // Relative Permeability Table
  async getRelativePermeabilityTable(): Promise<ApiResponse<unknown[]>> {
    return this.request('/karatobe/relative_permeability_table')
  }

  // Relative Permeability Summary
  async getRelativePermeabilitySummary(): Promise<ApiResponse<unknown[]>> {
    return this.request('/karatobe/relative_permeability_summary')
  }

  // XPT data for specific well
  async getXptData(wellName: string): Promise<ApiResponse<unknown[]>> {
    return this.request(`/karatobe/xpt_data/${wellName}`)
  }

  // Well log data
  async getWellLogData(wellName: string): Promise<ApiResponse<unknown[]>> {
    return this.request(`/karatobe/logs/${wellName}`)
  }
}

export const apiClient = new ApiClient()
export type { ApiResponse }