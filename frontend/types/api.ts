// API Response Types
export interface ApiResponse<T = unknown> {
  data?: T
  error?: string
  message?: string
}

// Authentication Types
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    username: string
    email: string
    role: string
    first_name: string
    last_name: string
    project: string | null
  }
  message: string
}

export interface Project {
  id: number
  name: string
  description: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  project_id: number
}

export interface User {
  username: string
  role: string
  loginTime: string
}

// Data Types
export interface Well {
  id: number
  well_name?: string
  x?: number
  y?: number
  lat?: number
  lon?: number
  kb?: number
  td?: number
  completion_date?: string
  status?: string
}

export interface Production {
  id: number
  Date?: string
  well?: string
  Qo_ton?: number
  Qw_m3?: number
  Ql_m3?: number
  Obv_percent?: number
}

export interface PVT {
  id: number
  pressure?: number
  rs?: number
  bo?: number
  mu_o?: number
  rho_o?: number
}

export interface Tops {
  id: number
  well_name?: string
  formation?: string
  top_depth?: number
  bottom_depth?: number
}

export interface FaultData {
  x: number
  y: number
  fault_type?: string
}

export interface BoundaryData {
  x: number
  y: number
  boundary_type?: string
}

export interface GanttData {
  task: string
  start_date: string
  end_date: string
  well?: string
}