// Simple logging utility for development and production
type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LogEntry {
  level: LogLevel
  message: string
  timestamp: string
  data?: unknown
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development'

  private createLogEntry(level: LogLevel, message: string, data?: unknown): LogEntry {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      data
    }
  }

  private log(entry: LogEntry) {
    if (this.isDevelopment) {
      const logMethod = entry.level === 'error' ? console.error : 
                      entry.level === 'warn' ? console.warn : 
                      console.log

      logMethod(`[${entry.timestamp}] ${entry.level.toUpperCase()}: ${entry.message}`, entry.data || '')
    }
  }

  debug(message: string, data?: unknown) {
    this.log(this.createLogEntry('debug', message, data))
  }

  info(message: string, data?: unknown) {
    this.log(this.createLogEntry('info', message, data))
  }

  warn(message: string, data?: unknown) {
    this.log(this.createLogEntry('warn', message, data))
  }

  error(message: string, error?: unknown) {
    this.log(this.createLogEntry('error', message, error))
  }

  // API specific logging
  apiRequest(endpoint: string, method: string = 'GET') {
    this.info(`API Request: ${method} ${endpoint}`)
  }

  apiResponse(endpoint: string, status: number, data?: unknown) {
    this.info(`API Response: ${endpoint} - Status: ${status}`, data)
  }

  apiError(endpoint: string, error: unknown) {
    this.error(`API Error: ${endpoint}`, error)
  }
}

export const logger = new Logger()