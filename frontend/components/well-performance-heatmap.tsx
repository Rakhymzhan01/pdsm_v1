"use client"

import React, { useEffect, useState } from 'react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface WellPerformanceData {
  well_name: string
  object_type: string
  horizon: string
  cumulative_oil: number
  cumulative_water: number
  avg_daily_oil: number
  production_days: number
  efficiency_score: number
}

export function WellPerformanceHeatmap() {
  const [data, setData] = useState<WellPerformanceData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'name' | 'performance' | 'object'>('performance')

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching well performance data...')
        const response = await fetch('http://localhost:8000/api/v1/karatobe/cumulative-production')
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const result = await response.json()
        
        // Calculate efficiency score for each well
        const processedData = result.map((well: {well_name: string; object_type: string; horizon: string; cumulative_oil: number; cumulative_water: number; avg_daily_oil: number; production_days: number}) => {
          // Efficiency score based on avg daily production, production days, and cumulative oil
          const dailyScore = Math.min(well.avg_daily_oil / 30, 1) // Normalize to 30 tons/day max
          const daysScore = Math.min(well.production_days / 1000, 1) // Normalize to 1000 days max
          const cumulativeScore = Math.min(well.cumulative_oil / 30000, 1) // Normalize to 30000 tons max
          
          const efficiency_score = (dailyScore * 0.5 + daysScore * 0.2 + cumulativeScore * 0.3) * 100
          
          return {
            well_name: well.well_name,
            object_type: well.object_type,
            horizon: well.horizon,
            cumulative_oil: well.cumulative_oil,
            cumulative_water: well.cumulative_water,
            avg_daily_oil: well.avg_daily_oil,
            production_days: well.production_days,
            efficiency_score: Math.round(efficiency_score)
          }
        })
        
        setData(processedData)
      } catch (err) {
        console.error('Error fetching well performance data:', err)
        setError(err instanceof Error ? err.message : 'Unknown error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const getSortedData = () => {
    const filtered = data.filter(well => well.avg_daily_oil > 0) // Only active wells
    
    switch (sortBy) {
      case 'name':
        return [...filtered].sort((a, b) => a.well_name.localeCompare(b.well_name))
      case 'performance':
        return [...filtered].sort((a, b) => b.efficiency_score - a.efficiency_score)
      case 'object':
        return [...filtered].sort((a, b) => {
          if (a.object_type !== b.object_type) {
            return a.object_type.localeCompare(b.object_type)
          }
          return b.efficiency_score - a.efficiency_score
        })
      default:
        return filtered
    }
  }

  const getPerformanceColor = (score: number) => {
    if (score >= 80) return 'bg-red-600'      // Excellent
    if (score >= 60) return 'bg-orange-500'  // Good
    if (score >= 40) return 'bg-yellow-500'  // Average
    if (score >= 20) return 'bg-blue-500'    // Below average
    return 'bg-gray-400'                      // Poor
  }


  if (loading) {
    return (
      <div className="h-[400px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-orange-200 border-t-orange-600 mx-auto mb-3"></div>
          <p className="text-sm text-muted-foreground">Загрузка данных производительности...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[400px] flex items-center justify-center">
        <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
          <div className="text-red-500 text-2xl mb-2">⚠️</div>
          <p className="text-red-700 font-medium text-sm">Ошибка загрузки данных</p>
          <p className="text-xs text-red-600 mt-1">{error}</p>
        </div>
      </div>
    )
  }

  const sortedData = getSortedData()
  const maxScore = Math.max(...sortedData.map(w => w.efficiency_score))
  const avgScore = sortedData.reduce((sum, w) => sum + w.efficiency_score, 0) / sortedData.length

  return (
    <div className="h-[400px] p-3 bg-gradient-to-br from-gray-50 to-white rounded-lg overflow-hidden">
      {/* Header with controls */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-800">Тепловая карта</h3>
          <p className="text-xs text-gray-600">{sortedData.length} активных скважин</p>
        </div>
        
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'name' | 'performance' | 'object')}
          className="text-xs border rounded px-2 py-1 bg-white"
        >
          <option value="performance">По эффективности</option>
          <option value="name">По названию</option>
          <option value="object">По объекту</option>
        </select>
      </div>

      {/* Statistics in compact row */}
      <div className="flex justify-between mb-3 text-xs bg-white/60 rounded-lg p-2">
        <div className="text-center">
          <div className="font-semibold text-red-600">{maxScore}%</div>
          <div className="text-gray-600">Макс</div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-orange-600">{avgScore.toFixed(1)}%</div>
          <div className="text-gray-600">Средн</div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-blue-600">{sortedData.length}</div>
          <div className="text-gray-600">Скважин</div>
        </div>
      </div>

      {/* Scrollable Heatmap Grid */}
      <div 
        className="h-[230px] overflow-y-auto overflow-x-hidden border border-gray-200 rounded-lg bg-gray-50/50 p-2"
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: '#9ca3af #e5e7eb'
        }}
      >
        <div className="grid grid-cols-10 gap-1">
          <TooltipProvider>
            {sortedData.map((well) => ( // Show all wells with scroll
              <Tooltip key={well.well_name}>
                <TooltipTrigger asChild>
                  <div
                    className={`
                      w-6 h-6 rounded cursor-pointer transition-all duration-200 hover:scale-125 hover:z-10 
                      flex items-center justify-center text-white text-[7px] font-bold shadow-sm hover:shadow-lg
                      ${getPerformanceColor(well.efficiency_score)}
                    `}
                    style={{
                      opacity: 0.8 + (well.efficiency_score / 100) * 0.2
                    }}
                  >
                    {well.well_name.replace(/[^0-9]/g, '').slice(-2) || well.well_name.slice(-1)}
                  </div>
                </TooltipTrigger>
                <TooltipContent className="p-3 max-w-xs">
                  <div className="space-y-2">
                    <div className="font-semibold text-sm border-b pb-1 text-gray-800">
                      🛢️ Скважина {well.well_name}
                    </div>
                    
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-600">Эффективность:</span>
                        <span className={`font-bold ${
                          well.efficiency_score >= 60 ? 'text-green-600' : 
                          well.efficiency_score >= 40 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {well.efficiency_score}%
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-600">Дебит:</span>
                        <span className="font-medium">{well.avg_daily_oil.toFixed(1)} тн/сут</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-600">Накоплено:</span>
                        <span className="font-medium">{(well.cumulative_oil/1000).toFixed(1)}к тн</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-600">Объект:</span>
                        <span className="font-medium">{well.object_type}</span>
                      </div>
                    </div>
                  </div>
                </TooltipContent>
              </Tooltip>
            ))}
          </TooltipProvider>
        </div>

      </div>

      {/* Compact Legend */}
      <div className="mt-2 pt-2 border-t border-gray-200">
        <div className="flex items-center justify-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-red-600 rounded"></div>
            <span>80%+</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-orange-500 rounded"></div>
            <span>60%</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-yellow-500 rounded"></div>
            <span>40%</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-blue-500 rounded"></div>
            <span>20%</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-gray-400 rounded"></div>
            <span>&lt;20%</span>
          </div>
        </div>
      </div>
    </div>
  )
}