// API Client for Flask Backend Integration

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'
const API_BASE_PATH = process.env.NEXT_PUBLIC_API_BASE_PATH || '/api'

interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${API_BASE_URL}${API_BASE_PATH}`
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`
      console.log(`Making API request to: ${url}`)
      
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

      console.log(`API response status: ${response.status}`)

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log(`API response data:`, data)
      return { data }
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error)
      return { error: error instanceof Error ? error.message : 'Network connection failed' }
    }
  }

  // Authentication
  async login(username: string, password: string): Promise<ApiResponse<any>> {
    return this.request('/login_from_nextjs', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  }

  // Wells data
  async getWells(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/wells')
  }

  // Production data
  async getProductionData(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/production')
  }

  // Faults data
  async getFaults(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/faults')
  }

  // Boundaries data  
  async getBoundaries(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/boundaries')
  }

  // Gantt data
  async getGanttData(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/gantt')
  }

  // PVT data
  async getPvtData(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/pvt')
  }

  // Tops data
  async getTopsData(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/tops')
  }

  // Relative Permeability Table
  async getRelativePermeabilityTable(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/relative_permeability_table')
  }

  // Relative Permeability Summary
  async getRelativePermeabilitySummary(): Promise<ApiResponse<any[]>> {
    return this.request('/karatobe/relative_permeability_summary')
  }

  // XPT data for specific well
  async getXptData(wellName: string): Promise<ApiResponse<any[]>> {
    return this.request(`/karatobe/xpt_data/${wellName}`)
  }

  // Well log data
  async getWellLogData(wellName: string): Promise<ApiResponse<any[]>> {
    return this.request(`/karatobe/logs/${wellName}`)
  }
}

export const apiClient = new ApiClient()
export type { ApiResponse }