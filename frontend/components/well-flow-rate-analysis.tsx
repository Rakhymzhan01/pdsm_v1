"use client"

import React, { useEffect, useRef, useState } from 'react'
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

interface WellFlowRateData {
  date: string
  wells: Record<string, {
    oilRate: number
    waterRate: number
    totalRate: number
    wellCount: number
  }>
}

export function WellFlowRateAnalysis() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 })
  const [selectedWells, setSelectedWells] = useState<string[]>([])
  const { data: productionData, loading, error } = useProductionData()

  // Process production data to show flow rate dynamics
  const processFlowRateData = (data: ProductionRecord[]): WellFlowRateData[] => {
    if (!data || data.length === 0) return []

    // Group by month and well
    const grouped = data.reduce((acc, record) => {
      const date = new Date(record.Date)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      
      if (!acc[monthKey]) {
        acc[monthKey] = {}
      }
      
      if (!acc[monthKey][record.Well]) {
        acc[monthKey][record.Well] = {
          oilRates: [],
          waterRates: [],
          totalRates: []
        }
      }
      
      acc[monthKey][record.Well].oilRates.push(record.Qo_ton || 0)
      acc[monthKey][record.Well].waterRates.push(record.Qw_m3 || 0)
      acc[monthKey][record.Well].totalRates.push((record.Qo_ton || 0) + (record.Qw_m3 || 0))
      
      return acc
    }, {} as Record<string, Record<string, {
      oilRates: number[]
      waterRates: number[]
      totalRates: number[]
    }>>)

    // Calculate monthly averages
    const result = Object.entries(grouped)
      .map(([monthKey, wells]) => {
        const [year, month] = monthKey.split('-')
        const displayDate = new Date(parseInt(year), parseInt(month) - 1, 15)
        
        const wellsData: Record<string, { oilRate: number; waterRate: number; totalRate: number; wellCount: number }> = {}
        Object.entries(wells).forEach(([well, rates]) => {
          wellsData[well] = {
            oilRate: rates.oilRates.reduce((sum, rate) => sum + rate, 0) / rates.oilRates.length,
            waterRate: rates.waterRates.reduce((sum, rate) => sum + rate, 0) / rates.waterRates.length,
            totalRate: rates.totalRates.reduce((sum, rate) => sum + rate, 0) / rates.totalRates.length,
            wellCount: 1
          }
        })
        
        return {
          date: displayDate.toISOString().split('T')[0],
          wells: wellsData
        }
      })
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

    return result
  }

  // Get top producing wells for initial selection
  const getTopWells = (data: ProductionRecord[], count: number = 8): string[] => {
    const wellTotals = data.reduce((acc, record) => {
      if (!acc[record.Well]) acc[record.Well] = 0
      acc[record.Well] += record.Qo_ton || 0
      return acc
    }, {} as Record<string, number>)

    return Object.entries(wellTotals)
      .sort(([, a], [, b]) => b - a)
      .slice(0, count)
      .map(([well]) => well)
  }

  useEffect(() => {
    if (productionData && selectedWells.length === 0) {
      const topWells = getTopWells(productionData)
      setSelectedWells(topWells)
    }
  }, [productionData, selectedWells.length])

  useEffect(() => {
    const handleResize = () => {
      if (svgRef.current?.parentElement) {
        const parentWidth = svgRef.current.parentElement.clientWidth
        const isMobile = window.innerWidth < 768
        const isTablet = window.innerWidth < 1024
        
        setDimensions({
          width: Math.max(parentWidth - 40, isMobile ? 350 : 600),
          height: isMobile ? 300 : isTablet ? 350 : 400
        })
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    if (!productionData || loading || !svgRef.current || selectedWells.length === 0) return

    const flowRateData = processFlowRateData(productionData)
    if (flowRateData.length === 0) return

    // Clear previous chart
    d3.select(svgRef.current).selectAll("*").remove()

    const margin = { top: 30, right: 120, bottom: 60, left: 80 }
    const width = dimensions.width - margin.left - margin.right
    const height = dimensions.height - margin.top - margin.bottom

    const svg = d3.select(svgRef.current)
      .attr('width', dimensions.width)
      .attr('height', dimensions.height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Color scale for wells
    const colorScale = d3.scaleOrdinal<string>()
      .domain(selectedWells)
      .range(d3.schemeCategory10.concat(d3.schemeDark2))

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(flowRateData, d => new Date(d.date)) as [Date, Date])
      .range([0, width])

    const maxRate = d3.max(flowRateData, d => 
      Math.max(...selectedWells.map(well => d.wells[well]?.oilRate || 0))
    ) || 50

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

    // Create lines for each selected well
    selectedWells.forEach((well, index) => {
      // Filter data for this well
      const wellData = flowRateData
        .map(d => ({
          date: d.date,
          oilRate: d.wells[well]?.oilRate || 0,
          waterRate: d.wells[well]?.waterRate || 0,
          totalRate: d.wells[well]?.totalRate || 0
        }))
        .filter(d => d.oilRate > 0)

      if (wellData.length === 0) return

      // Line generator
      const line = d3.line<{date: string, oilRate: number, waterRate: number, totalRate: number}>()
        .x(d => xScale(new Date(d.date)))
        .y(d => yScale(d.oilRate))
        .curve(d3.curveMonotoneX)

      // Add line
      const linePath = g.append('path')
        .datum(wellData)
        .attr('fill', 'none')
        .attr('stroke', colorScale(well))
        .attr('stroke-width', 2.5)
        .attr('d', line)
        .style('opacity', 0.8)

      // Animate line
      const totalLength = (linePath.node() as SVGPathElement).getTotalLength()
      linePath
        .attr('stroke-dasharray', totalLength + ' ' + totalLength)
        .attr('stroke-dashoffset', totalLength)
        .transition()
        .duration(1000)
        .delay(index * 100)
        .ease(d3.easeQuadOut)
        .attr('stroke-dashoffset', 0)

      // Add dots
      const dots = g.selectAll(`.dots-${index}`)
        .data(wellData)
        .enter().append('circle')
        .attr('class', `dots-${index} well-${well}`)
        .attr('cx', d => xScale(new Date(d.date)))
        .attr('cy', d => yScale(d.oilRate))
        .attr('r', 0)
        .attr('fill', colorScale(well))
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')

      dots.transition()
        .delay(index * 100 + 800)
        .duration(300)
        .ease(d3.easeBounceOut)
        .attr('r', 4)

      // Tooltip
      const tooltip = d3.select(document.body)
        .append('div')
        .attr('class', `tooltip-well-${well}`)
        .style('position', 'absolute')
        .style('background', 'rgba(0,0,0,0.85)')
        .style('color', 'white')
        .style('padding', '10px 14px')
        .style('border-radius', '8px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('opacity', 0)
        .style('z-index', '1000')
        .style('box-shadow', '0 4px 20px rgba(0,0,0,0.3)')

      dots.on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', 6)

        // Highlight the well line
        g.selectAll('path')
          .style('opacity', 0.3)
        
        g.selectAll('path')
          .filter(function() {
            return d3.select(this).datum() === wellData
          })
          .style('opacity', 1)
          .style('stroke-width', 4)

        tooltip.html(`
          <div style="border-bottom: 1px solid ${colorScale(well)}; margin-bottom: 8px; padding-bottom: 6px;">
            <strong style="color: ${colorScale(well)}; font-size: 14px;">🛢️ Скважина ${well}</strong>
          </div>
          <div style="display: grid; gap: 4px;">
            <div>📅 ${new Date(d.date).toLocaleDateString('ru-RU', {month: 'long', year: 'numeric'})}</div>
            <div><span style="color: #ff6b35;">🛢️ Дебит нефти:</span> <strong>${d.oilRate.toFixed(1)} тн/сут</strong></div>
            <div><span style="color: #3b82f6;">💧 Дебит воды:</span> <strong>${d.waterRate.toFixed(1)} м³/сут</strong></div>
            <div><span style="color: #10b981;">📊 Общий дебит:</span> <strong>${d.totalRate.toFixed(1)} м³/сут</strong></div>
            <div><span style="color: #f59e0b;">💯 Обводненность:</span> <strong>${((d.waterRate / (d.oilRate * 0.8 + d.waterRate)) * 100).toFixed(1)}%</strong></div>
          </div>
        `)
        .style('opacity', 1)
        .style('left', (event.pageX + 15) + 'px')
        .style('top', (event.pageY - 10) + 'px')
      })
      .on('mouseout', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', 4)

        // Restore all lines
        g.selectAll('path')
          .style('opacity', 0.8)
          .style('stroke-width', 2.5)

        tooltip.style('opacity', 0)
      })
    })

    // Legend with performance indicators
    const legend = svg.append('g')
      .attr('transform', `translate(${width + margin.left + 20}, ${margin.top + 20})`)

    // Calculate performance metrics for legend
    const performanceData = selectedWells.map(well => {
      const wellFlowRates = flowRateData
        .map(d => d.wells[well]?.oilRate || 0)
        .filter(rate => rate > 0)
      
      const avgRate = wellFlowRates.reduce((sum, rate) => sum + rate, 0) / wellFlowRates.length
      const trend = wellFlowRates.length > 1 ? 
        (wellFlowRates[wellFlowRates.length - 1] - wellFlowRates[0]) / wellFlowRates[0] * 100 : 0
      
      return {
        well,
        avgRate,
        trend,
        performance: avgRate > maxRate * 0.7 ? 'high' : avgRate > maxRate * 0.4 ? 'medium' : 'low'
      }
    }).sort((a, b) => b.avgRate - a.avgRate)

    const legendItems = legend.selectAll('.legend-item')
      .data(performanceData)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => `translate(0, ${i * 28})`)

    legendItems.append('rect')
      .attr('width', 90)
      .attr('height', 24)
      .attr('rx', 4)
      .style('fill', 'rgba(255, 255, 255, 0.95)')
      .style('stroke', d => colorScale(d.well))
      .style('stroke-width', 2)

    legendItems.append('line')
      .attr('x1', 6)
      .attr('y1', 12)
      .attr('x2', 20)
      .attr('y2', 12)
      .style('stroke', d => colorScale(d.well))
      .style('stroke-width', 3)

    legendItems.append('text')
      .attr('x', 25)
      .attr('y', 10)
      .style('font-size', '10px')
      .style('font-weight', 'bold')
      .style('fill', '#374151')
      .text(d => d.well)

    legendItems.append('text')
      .attr('x', 25)
      .attr('y', 20)
      .style('font-size', '8px')
      .style('fill', d => d.performance === 'high' ? '#059669' : d.performance === 'medium' ? '#d97706' : '#dc2626')
      .text(d => {
        const trendIcon = d.trend > 5 ? '↗' : d.trend < -5 ? '↘' : '→'
        return `${d.avgRate.toFixed(1)} ${trendIcon}`
      })

    // Axes
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d => d3.timeFormat('%m.%Y')(d as Date))
        .ticks(6))

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
      .text('📅 Период')

    // Title
    svg.append('text')
      .attr('x', dimensions.width / 2)
      .attr('y', 20)
      .style('text-anchor', 'middle')
      .style('font-size', '15px')
      .style('font-weight', 'bold')
      .style('fill', '#1f2937')
      .text('Сравнительный анализ дебитов скважин')

  }, [productionData, loading, dimensions, selectedWells])

  if (loading) {
    return (
      <div className="h-[350px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-200 border-t-orange-600 mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground animate-pulse">Загрузка данных по скважинам...</p>
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

  return (
    <div className="w-full bg-gradient-to-br from-gray-50 to-white p-4 rounded-lg">
      <svg ref={svgRef} className="w-full drop-shadow-sm"></svg>
    </div>
  )
}