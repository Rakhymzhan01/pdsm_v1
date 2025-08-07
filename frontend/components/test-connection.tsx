"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'

export function TestConnection() {
  const [isTestingWells, setIsTestingWells] = useState(false)
  const [isTestingProduction, setIsTestingProduction] = useState(false)
  const [wellsResult, setWellsResult] = useState<string | null>(null)
  const [productionResult, setProductionResult] = useState<string | null>(null)

  const testWellsConnection = async () => {
    setIsTestingWells(true)
    setWellsResult(null)
    
    try {
      const response = await apiClient.getWells()
      if (response.error) {
        setWellsResult(`Error: ${response.error}`)
      } else if (response.data) {
        setWellsResult(`Success: Retrieved ${response.data.length} wells`)
      }
    } catch (error) {
      setWellsResult(`Error: ${error}`)
    } finally {
      setIsTestingWells(false)
    }
  }

  const testProductionConnection = async () => {
    setIsTestingProduction(true)
    setProductionResult(null)
    
    try {
      const response = await apiClient.getProductionData()
      if (response.error) {
        setProductionResult(`Error: ${response.error}`)
      } else if (response.data) {
        setProductionResult(`Success: Retrieved ${response.data.length} production records`)
      }
    } catch (error) {
      setProductionResult(`Error: ${error}`)
    } finally {
      setIsTestingProduction(false)
    }
  }

  const getResultIcon = (result: string | null) => {
    if (!result) return null
    if (result.startsWith('Success')) return <CheckCircle className="h-4 w-4 text-green-500" />
    return <XCircle className="h-4 w-4 text-red-500" />
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>FastAPI Connection Test</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Button
            onClick={testWellsConnection}
            disabled={isTestingWells}
            className="w-full"
          >
            {isTestingWells ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing Wells...
              </>
            ) : (
              'Test Wells API'
            )}
          </Button>
          {wellsResult && (
            <div className="flex items-center gap-2 text-sm">
              {getResultIcon(wellsResult)}
              <span>{wellsResult}</span>
            </div>
          )}
        </div>

        <div className="space-y-2">
          <Button
            onClick={testProductionConnection}
            disabled={isTestingProduction}
            className="w-full"
          >
            {isTestingProduction ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing Production...
              </>
            ) : (
              'Test Production API'
            )}
          </Button>
          {productionResult && (
            <div className="flex items-center gap-2 text-sm">
              {getResultIcon(productionResult)}
              <span>{productionResult}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}