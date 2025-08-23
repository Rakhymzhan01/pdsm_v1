"use client"

import React, { useEffect, useRef, useState, useCallback } from 'react'
import * as d3 from 'd3'
import { useProductionData } from '@/hooks/use-api'

interface ProductionRecord {
  Date: string
  Well: string
  Qo_ton: number
  Qw_m3: number  
  Ql_m3: number
  Horizon?: string
}

interface WellDeclineData {
  well: string
  actualData: { time: number; rate: number; date: string }[]
  exponentialForecast: { time: number; rate: number }[]
  hyperbolicForecast: { time: number; rate: number }[]
  exponentialParams: { qi: number; di: number; r2: number }
  hyperbolicParams: { qi: number; di: number; b: number; r2: number }
}

export function DeclineCurveAnalysis() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 })
  const [selectedWell, setSelectedWell] = useState<string>('')
  const [wellOptions, setWellOptions] = useState<string[]>([])
  const { data: productionData, loading, error } = useProductionData()

  // Calculate decline curve parameters and forecasts
  const calculateDeclineCurves = useCallback((data: ProductionRecord[]): WellDeclineData[] => {
    if (!data || data.length === 0) return []

    // Group by well and calculate monthly averages
    const wellGroups = data.reduce((acc, record) => {
      if (!acc[record.Well]) acc[record.Well] = []
      acc[record.Well].push(record)
      return acc
    }, {} as Record<string, ProductionRecord[]>)

    const results: WellDeclineData[] = []

    Object.entries(wellGroups).forEach(([well, records]) => {
      // Sort by date and calculate monthly averages
      const sortedRecords = records.sort((a, b) => new Date(a.Date).getTime() - new Date(b.Date).getTime())
      
      // Group by month
      const monthlyData = sortedRecords.reduce((acc, record) => {
        const date = new Date(record.Date)
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
        
        if (!acc[monthKey]) {
          acc[monthKey] = { rates: [], date: monthKey }
        }
        acc[monthKey].rates.push(record.Qo_ton || 0)
        
        return acc
      }, {} as Record<string, { rates: number[]; date: string }>)

      const actualData = Object.values(monthlyData)
        .map((month, index) => ({
          time: index + 1, // Time in months from start
          rate: month.rates.reduce((sum, rate) => sum + rate, 0) / month.rates.length,
          date: month.date
        }))
        .filter(point => point.rate > 0)
        .slice(0, 24) // Use max 24 months for analysis

      if (actualData.length < 3) return // Need at least 3 data points

      // Calculate exponential decline parameters: q(t) = qi * exp(-di * t)
      const exponentialParams = calculateExponentialDecline(actualData)
      
      // Calculate hyperbolic decline parameters: q(t) = qi / (1 + b * di * t)^(1/b)
      const hyperbolicParams = calculateHyperbolicDecline(actualData)

      // Generate forecast data (extend to 60 months)
      const forecastMonths = Array.from({ length: 60 }, (_, i) => i + 1)
      
      const exponentialForecast = forecastMonths.map(t => ({
        time: t,
        rate: exponentialParams.qi * Math.exp(-exponentialParams.di * t)
      }))

      const hyperbolicForecast = forecastMonths.map(t => ({
        time: t,
        rate: hyperbolicParams.qi / Math.pow(1 + hyperbolicParams.b * hyperbolicParams.di * t, 1 / hyperbolicParams.b)
      }))

      results.push({
        well,
        actualData,
        exponentialForecast,
        hyperbolicForecast,
        exponentialParams,
        hyperbolicParams
      })
    })

    return results.filter(result => result.actualData.length >= 3)
  }, [])

  // Exponential decline curve fitting
  const calculateExponentialDecline = (data: { time: number; rate: number }[]) => {
    // Linear regression on log(rate) vs time
    const logData = data.map(d => ({ x: d.time, y: Math.log(Math.max(d.rate, 0.1)) }))
    
    const n = logData.length
    const sumX = logData.reduce((sum, d) => sum + d.x, 0)
    const sumY = logData.reduce((sum, d) => sum + d.y, 0)
    const sumXY = logData.reduce((sum, d) => sum + d.x * d.y, 0)
    const sumX2 = logData.reduce((sum, d) => sum + d.x * d.x, 0)
    
    const di = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
    const lnQi = (sumY - di * sumX) / n
    const qi = Math.exp(lnQi)
    
    // Calculate R²
    const yMean = sumY / n
    const ssRes = logData.reduce((sum, d) => {
      const predicted = lnQi + di * d.x
      return sum + Math.pow(d.y - predicted, 2)
    }, 0)
    const ssTot = logData.reduce((sum, d) => sum + Math.pow(d.y - yMean, 2), 0)
    const r2 = 1 - (ssRes / ssTot)
    
    return { qi: Math.abs(qi), di: Math.abs(di), r2 }
  }

  // Hyperbolic decline curve fitting (simplified approach)
  const calculateHyperbolicDecline = (data: { time: number; rate: number }[]) => {
    // Use Arps equation: q = qi / (1 + b * di * t)^(1/b)
    // Simplified fitting with b = 0.5 (common assumption)
    const b = 0.5
    
    // Transform data for linear regression: (q^-b - qi^-b) = b * di * t * qi^-b
    const qi = data[0].rate
    const transformedData = data.slice(1).map(d => ({
      x: d.time,
      y: Math.pow(qi / d.rate, b) - 1
    }))
    
    if (transformedData.length === 0) {
      return { qi, di: 0.1, b, r2: 0 }
    }
    
    const n = transformedData.length
    const sumX = transformedData.reduce((sum, d) => sum + d.x, 0)
    const sumY = transformedData.reduce((sum, d) => sum + d.y, 0)
    const sumXY = transformedData.reduce((sum, d) => sum + d.x * d.y, 0)
    const sumX2 = transformedData.reduce((sum, d) => sum + d.x * d.x, 0)
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
    const di = slope * b
    
    // Calculate R²
    const yMean = sumY / n
    const ssRes = transformedData.reduce((sum, d) => {
      const predicted = slope * d.x
      return sum + Math.pow(d.y - predicted, 2)
    }, 0)
    const ssTot = transformedData.reduce((sum, d) => sum + Math.pow(d.y - yMean, 2), 0)
    const r2 = ssTot > 0 ? 1 - (ssRes / ssTot) : 0
    
    return { qi, di: Math.abs(di), b, r2 }
  }

  useEffect(() => {
    if (productionData) {
      console.log('Production data length:', productionData.length)
      console.log('Sample production record:', productionData[0])
      
      const declineData = calculateDeclineCurves(productionData)
      console.log('Decline data calculated:', declineData.length, 'wells')
      
      const wells = declineData.map(d => d.well).sort()
      console.log('Available wells:', wells)
      setWellOptions(wells)
      
      if (wells.length > 0 && !selectedWell) {
        // Select the first well for simplicity
        setSelectedWell(wells[0])
        console.log('Selected first well:', wells[0])
      }
    }
  }, [productionData, calculateDeclineCurves])

  useEffect(() => {
    const handleResize = () => {
      if (svgRef.current?.parentElement) {
        const parentWidth = svgRef.current.parentElement.clientWidth
        const isMobile = window.innerWidth < 768
        const isTablet = window.innerWidth < 1024
        
        setDimensions({
          width: Math.max(parentWidth - 40, isMobile ? 350 : 600),
          height: isMobile ? 280 : isTablet ? 350 : 400
        })
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    if (!productionData || loading || !svgRef.current || !selectedWell) return

    const declineData = calculateDeclineCurves(productionData)
    const wellData = declineData.find(d => d.well === selectedWell)
    
    if (!wellData) return

    // Clear previous chart
    d3.select(svgRef.current).selectAll("*").remove()

    const isMobile = dimensions.width < 500
    const margin = { 
      top: 30, 
      right: isMobile ? 20 : 150, 
      bottom: isMobile ? 50 : 60, 
      left: isMobile ? 60 : 80 
    }
    const width = dimensions.width - margin.left - margin.right
    const height = dimensions.height - margin.top - margin.bottom

    const svgHeight = isMobile ? dimensions.height + 100 : dimensions.height // Extra space for legend on mobile
    const svg = d3.select(svgRef.current)
      .attr('width', dimensions.width)
      .attr('height', svgHeight)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const maxTime = Math.max(
      ...wellData.actualData.map(d => d.time),
      ...wellData.exponentialForecast.map(d => d.time)
    )
    
    const maxRate = Math.max(
      ...wellData.actualData.map(d => d.rate),
      wellData.exponentialParams.qi
    )

    const xScale = d3.scaleLinear()
      .domain([0, maxTime])
      .range([0, width])

    const yScale = d3.scaleLinear()
      .domain([0, maxRate * 1.1])
      .nice()
      .range([height, 0])

    // Add grid
    const gridLinesY = g.append('g')
      .attr('class', 'grid-y')
      .call(d3.axisLeft(yScale)
        .tickSize(-width)
        .tickFormat(() => '')
      )
    
    gridLinesY.selectAll('line')
      .style('stroke', '#e5e7eb')
      .style('stroke-width', 0.5)
      .style('stroke-dasharray', '2,2')

    const gridLinesX = g.append('g')
      .attr('class', 'grid-x')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickSize(-height)
        .tickFormat(() => '')
      )
    
    gridLinesX.selectAll('line')
      .style('stroke', '#e5e7eb')
      .style('stroke-width', 0.5)
      .style('stroke-dasharray', '2,2')

    // Line generators
    const line = d3.line<{ time: number; rate: number }>()
      .x(d => xScale(d.time))
      .y(d => yScale(d.rate))
      .curve(d3.curveMonotoneX)

    // Add actual data line and points
    g.append('path')
      .datum(wellData.actualData)
      .attr('fill', 'none')
      .attr('stroke', '#1f2937')
      .attr('stroke-width', 3)
      .attr('d', line)

    g.selectAll('.actual-dot')
      .data(wellData.actualData)
      .enter().append('circle')
      .attr('class', 'actual-dot')
      .attr('cx', d => xScale(d.time))
      .attr('cy', d => yScale(d.rate))
      .attr('r', 4)
      .attr('fill', '#1f2937')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)

    // Add exponential forecast line
    g.append('path')
      .datum(wellData.exponentialForecast)
      .attr('fill', 'none')
      .attr('stroke', '#dc2626')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')
      .attr('d', line)

    // Add hyperbolic forecast line
    g.append('path')
      .datum(wellData.hyperbolicForecast)
      .attr('fill', 'none')
      .attr('stroke', '#2563eb')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '3,7')
      .attr('d', line)

    // Add vertical line to separate actual from forecast
    const lastActualTime = Math.max(...wellData.actualData.map(d => d.time))
    g.append('line')
      .attr('x1', xScale(lastActualTime))
      .attr('x2', xScale(lastActualTime))
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', '#6b7280')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '2,2')

    // Add forecast label
    g.append('text')
      .attr('x', xScale(lastActualTime + 2))
      .attr('y', 20)
      .style('font-size', '11px')
      .style('font-weight', '500')
      .style('fill', '#6b7280')
      .text('Прогноз →')

    // Axes
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d => `${d} мес`)
        .ticks(8))

    xAxis.selectAll('text')
      .style('font-size', '11px')
      .style('fill', '#6b7280')

    const yAxis = g.append('g')
      .call(d3.axisLeft(yScale)
        .tickFormat(d => `${d} тн/сут`)
        .ticks(6))

    yAxis.selectAll('text')
      .style('font-size', '11px')
      .style('fill', '#6b7280')

    // Axis labels
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left + 20)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '13px')
      .style('font-weight', '600')
      .style('fill', '#374151')
      .text('🛢️ Дебит нефти (тн/сут)')

    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 15})`)
      .style('text-anchor', 'middle')
      .style('font-size', '13px')
      .style('font-weight', '600')
      .style('fill', '#374151')
      .text('⏰ Время эксплуатации (месяцы)')

    // Legend and parameters - adaptive positioning
    const legend = svg.append('g')
      .attr('transform', isMobile ? 
        `translate(20, ${height + margin.top + margin.bottom + 10})` : 
        `translate(${width + margin.left + 20}, ${margin.top + 20})`)

    const legendData = [
      { name: 'Фактические данные', color: '#1f2937', type: 'solid', params: null },
      { 
        name: 'Экспоненциальная', 
        color: '#dc2626', 
        type: 'dashed',
        params: wellData.exponentialParams
      },
      { 
        name: 'Гиперболическая', 
        color: '#2563eb', 
        type: 'dashed',
        params: wellData.hyperbolicParams
      }
    ]

    const legendItems = legend.selectAll('.legend-item')
      .data(legendData)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => 
        isMobile ? 
          `translate(${i * 130}, 0)` : // Horizontal layout for mobile
          `translate(0, ${i * 45})`     // Vertical layout for desktop
      )

    legendItems.append('rect')
      .attr('width', 120)
      .attr('height', 40)
      .attr('rx', 4)
      .style('fill', 'rgba(255, 255, 255, 0.95)')
      .style('stroke', '#e5e7eb')
      .style('stroke-width', 1)

    legendItems.append('line')
      .attr('x1', 8)
      .attr('y1', 12)
      .attr('x2', 28)
      .attr('y2', 12)
      .style('stroke', d => d.color)
      .style('stroke-width', d => d.name === 'Фактические данные' ? 3 : 2)
      .style('stroke-dasharray', d => d.type === 'dashed' ? '3,3' : 'none')

    legendItems.append('text')
      .attr('x', 32)
      .attr('y', 10)
      .style('font-size', '10px')
      .style('font-weight', 'bold')
      .style('fill', '#374151')
      .text(d => d.name)

    legendItems.append('text')
      .attr('x', 8)
      .attr('y', 25)
      .style('font-size', '8px')
      .style('fill', '#6b7280')
      .text(d => {
        if (!d.params) return ''
        if ('b' in d.params) {
          return `qi=${d.params.qi.toFixed(1)} di=${d.params.di.toFixed(3)} b=${d.params.b}`
        } else {
          return `qi=${d.params.qi.toFixed(1)} di=${d.params.di.toFixed(3)}`
        }
      })

    legendItems.append('text')
      .attr('x', 8)
      .attr('y', 35)
      .style('font-size', '8px')
      .style('fill', d => d.params && d.params.r2 > 0.7 ? '#059669' : '#dc2626')
      .text(d => d.params ? `R² = ${d.params.r2.toFixed(3)}` : '')

    // Title
    svg.append('text')
      .attr('x', dimensions.width / 2)
      .attr('y', 20)
      .style('text-anchor', 'middle')
      .style('font-size', '15px')
      .style('font-weight', 'bold')
      .style('fill', '#1f2937')
      .text(`Анализ кривых падения - Скважина ${selectedWell}`)

  }, [productionData, loading, dimensions, selectedWell, calculateDeclineCurves])

  if (loading) {
    return (
      <div className="h-[350px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-200 border-t-orange-600 mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground animate-pulse">Расчет кривых падения...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[350px] flex items-center justify-center">
        <div className="text-center p-6 bg-red-50 rounded-lg border border-red-200">
          <div className="text-red-500 text-4xl mb-2">⚠️</div>
          <p className="text-red-700 font-medium">Ошибка загрузки данных</p>
          <p className="text-sm text-red-600 mt-1">{error}</p>
        </div>
      </div>
    )
  }

  // Show info about data processing
  const debugInfo = productionData ? (
    <div className="mb-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
      <p>Загружено записей: {productionData.length}</p>
      <p>Доступно скважин для анализа: {wellOptions.length}</p>
      {wellOptions.length === 0 && (
        <p className="text-red-600 mt-1">
          Недостаточно данных для построения кривых падения. 
          Требуется минимум 3 точки данных на скважину.
        </p>
      )}
    </div>
  ) : null

  if (wellOptions.length === 0 && !loading) {
    return (
      <div className="w-full bg-gradient-to-br from-gray-50 to-white p-4 rounded-lg">
        {debugInfo}
        <div className="h-[300px] flex items-center justify-center">
          <div className="text-center p-6 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="text-yellow-500 text-4xl mb-2">📊</div>
            <p className="text-yellow-700 font-medium">Недостаточно данных</p>
            <p className="text-sm text-yellow-600 mt-1">
              Для построения кривых падения необходимо минимум 3 месяца данных по скважине
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full bg-gradient-to-br from-gray-50 to-white p-4 rounded-lg">
      {debugInfo}
      
      {/* Well selector */}
      <div className="mb-4">
        <label className="text-sm font-medium text-gray-700 mb-2 block">
          Выберите скважину для анализа ({wellOptions.length} доступно):
        </label>
        <select
          value={selectedWell}
          onChange={(e) => setSelectedWell(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white min-w-[200px]"
        >
          {wellOptions.length === 0 ? (
            <option value="">Нет доступных скважин</option>
          ) : (
            wellOptions.map(well => (
              <option key={well} value={well}>Скважина {well}</option>
            ))
          )}
        </select>
      </div>
      
      {selectedWell && (
        <svg ref={svgRef} className="w-full drop-shadow-sm"></svg>
      )}
    </div>
  )
}