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

interface AggregatedData {
  date: string
  totalOil: number
  totalWater: number
  totalLiquid: number
  avgWaterCut: number
  wellCount: number
}

export function EnhancedProductionChart() {
  const svgRef = useRef<SVGSVGElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 })
  const { data: productionData, loading, error } = useProductionData()

  // Aggregate production data by month for clearer trend visualization
  const aggregateData = (data: ProductionRecord[]): AggregatedData[] => {
    if (!data || data.length === 0) return []

    // Group by month-year
    const grouped = data.reduce((acc, record) => {
      const date = new Date(record.Date)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      
      if (!acc[monthKey]) {
        acc[monthKey] = {
          totalOil: 0,
          totalWater: 0,
          totalLiquid: 0,
          waterCuts: [],
          wells: new Set(),
          dates: []
        }
      }
      
      acc[monthKey].totalOil += record.Qo_ton || 0
      acc[monthKey].totalWater += record.Qw_m3 || 0
      acc[monthKey].totalLiquid += record.Ql_m3 || 0
      acc[monthKey].wells.add(record.Well)
      acc[monthKey].dates.push(date)
      
      // Calculate water cut percentage
      const oilRate = record.Qo_ton || 0
      const waterRate = record.Qw_m3 || 0
      if (oilRate > 0 || waterRate > 0) {
        const waterCut = (waterRate / (oilRate * 0.8 + waterRate)) * 100
        acc[monthKey].waterCuts.push(waterCut)
      }
      
      return acc
    }, {} as Record<string, any>)

    // Convert to monthly aggregated data
    const monthlyData = Object.entries(grouped)
      .map(([monthKey, values]) => {
        // Use middle of month for display
        const [year, month] = monthKey.split('-')
        const displayDate = new Date(parseInt(year), parseInt(month) - 1, 15)
        
        return {
          date: displayDate.toISOString().split('T')[0],
          totalOil: values.totalOil,
          totalWater: values.totalWater, 
          totalLiquid: values.totalLiquid,
          wellCount: values.wells.size,
          avgWaterCut: values.waterCuts.length > 0 
            ? values.waterCuts.reduce((sum: number, val: number) => sum + val, 0) / values.waterCuts.length
            : 0
        }
      })
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

    return monthlyData
  }

  useEffect(() => {
    const handleResize = () => {
      if (svgRef.current?.parentElement) {
        const parentWidth = svgRef.current.parentElement.clientWidth
        setDimensions({
          width: Math.max(parentWidth - 40, 500),
          height: 350
        })
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    if (!productionData || loading || !svgRef.current) return

    const aggregatedData = aggregateData(productionData)
    if (aggregatedData.length === 0) return

    // Debug: log the data
    console.log('Production data length:', productionData.length)
    console.log('Aggregated data length:', aggregatedData.length)
    console.log('First 5 aggregated points:', aggregatedData.slice(0, 5))
    console.log('Last 5 aggregated points:', aggregatedData.slice(-5))
    console.log('Oil production range:', {
      min: Math.min(...aggregatedData.map(d => d.totalOil)),
      max: Math.max(...aggregatedData.map(d => d.totalOil))
    })
    console.log('Date range:', {
      first: aggregatedData[0]?.date,
      last: aggregatedData[aggregatedData.length - 1]?.date
    })

    // Clear previous chart
    d3.select(svgRef.current).selectAll("*").remove()

    const margin = { top: 30, right: 100, bottom: 50, left: 80 }
    const width = dimensions.width - margin.left - margin.right
    const height = dimensions.height - margin.top - margin.bottom

    const svg = d3.select(svgRef.current)
      .attr('width', dimensions.width)
      .attr('height', dimensions.height)

    // Background with subtle pattern
    const defs = svg.append('defs')
    
    // Create filter for glow effect
    const filter = defs.append('filter')
      .attr('id', 'glow')
    
    filter.append('feGaussianBlur')
      .attr('stdDeviation', '3')
      .attr('result', 'coloredBlur')
    
    const feMerge = filter.append('feMerge')
    feMerge.append('feMergeNode')
      .attr('in', 'coloredBlur')
    feMerge.append('feMergeNode')
      .attr('in', 'SourceGraphic')

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(aggregatedData, d => new Date(d.date)) as [Date, Date])
      .range([0, width])

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(aggregatedData, d => d.totalOil) || 100])
      .nice()
      .range([height, 0])

    // Create gradients
    const oilGradient = defs.append('linearGradient')
      .attr('id', 'oil-gradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', height)
      .attr('x2', 0).attr('y2', 0)

    oilGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#ff6b35')
      .attr('stop-opacity', 0.1)

    oilGradient.append('stop')
      .attr('offset', '50%')
      .attr('stop-color', '#ff6b35')
      .attr('stop-opacity', 0.4)

    oilGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#ff8c42')
      .attr('stop-opacity', 0.8)

    // Line generator with minimal smoothing
    const line = d3.line<AggregatedData>()
      .x(d => xScale(new Date(d.date)))
      .y(d => yScale(d.totalOil))
      .curve(d3.curveMonotoneX) // Less aggressive smoothing

    // Area generator
    const area = d3.area<AggregatedData>()
      .x(d => xScale(new Date(d.date)))
      .y0(height)
      .y1(d => yScale(d.totalOil))
      .curve(d3.curveMonotoneX) // Same curve as line

    // Add subtle grid
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

    // Add area with animation
    const areaPath = g.append('path')
      .datum(aggregatedData)
      .attr('fill', 'url(#oil-gradient)')
      .attr('d', area)
      .style('opacity', 0)

    areaPath.transition()
      .duration(1500)
      .ease(d3.easeQuadOut)
      .style('opacity', 1)

    // Add main line with glow
    const mainLine = g.append('path')
      .datum(aggregatedData)
      .attr('fill', 'none')
      .attr('stroke', '#ff6b35')
      .attr('stroke-width', 3)
      .attr('filter', 'url(#glow)')
      .attr('d', line)
      .style('stroke-dasharray', function() {
        const length = (this as SVGPathElement).getTotalLength()
        return `${length} ${length}`
      })
      .style('stroke-dashoffset', function() {
        return (this as SVGPathElement).getTotalLength()
      })

    mainLine.transition()
      .duration(2000)
      .ease(d3.easeQuadOut)
      .style('stroke-dashoffset', 0)

    // Add dots with animation
    const dots = g.selectAll('.dot')
      .data(aggregatedData)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(new Date(d.date)))
      .attr('cy', d => yScale(d.totalOil))
      .attr('r', 0)
      .attr('fill', '#fff')
      .attr('stroke', '#ff6b35')
      .attr('stroke-width', 3)
      .style('filter', 'url(#glow)')
      .style('cursor', 'pointer')

    dots.transition()
      .delay((d, i) => i * 50)
      .duration(500)
      .ease(d3.easeBounceOut)
      .attr('r', d => {
        // Make dot size proportional to production for better visibility
        const maxOil = Math.max(...aggregatedData.map(item => item.totalOil))
        const minSize = 3
        const maxSize = 8
        return minSize + (d.totalOil / maxOil) * (maxSize - minSize)
      })

    // Enhanced tooltip
    const tooltip = d3.select(document.body)
      .append('div')
      .attr('class', 'production-tooltip')
      .style('position', 'absolute')
      .style('background', 'linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(30,30,30,0.9) 100%)')
      .style('color', 'white')
      .style('padding', '12px 16px')
      .style('border-radius', '8px')
      .style('font-size', '13px')
      .style('font-family', 'system-ui, sans-serif')
      .style('pointer-events', 'none')
      .style('box-shadow', '0 10px 25px rgba(0,0,0,0.3)')
      .style('border', '1px solid #ff6b35')
      .style('backdrop-filter', 'blur(10px)')
      .style('z-index', '1000')
      .style('opacity', 0)
      .style('transform', 'translateY(-10px)')

    // Enhanced interactions
    dots.on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', 8)
          .style('stroke-width', 4)

        tooltip.html(`
          <div style="border-bottom: 1px solid #ff6b35; margin-bottom: 8px; padding-bottom: 6px;">
            <strong style="color: #ff6b35; font-size: 14px;">📅 ${new Date(d.date).toLocaleDateString('ru-RU')}</strong>
          </div>
          <div style="display: grid; gap: 4px;">
            <div><span style="color: #ff6b35;">🛢️ Нефть:</span> <strong>${d.totalOil.toFixed(1)} тн</strong></div>
            <div><span style="color: #60a5fa;">💧 Вода:</span> <strong>${d.totalWater.toFixed(1)} м³</strong></div>
            <div><span style="color: #10b981;">📊 Обводненность:</span> <strong>${d.avgWaterCut.toFixed(1)}%</strong></div>
            <div><span style="color: #f59e0b;">⚡ Скважин:</span> <strong>${d.wellCount}</strong></div>
          </div>
        `)
        .style('opacity', 1)
        .style('transform', 'translateY(0)')
        .style('left', (event.pageX + 15) + 'px')
        .style('top', (event.pageY - 10) + 'px')
      })
      .on('mouseout', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', 6)
          .style('stroke-width', 3)

        tooltip
          .style('opacity', 0)
          .style('transform', 'translateY(-10px)')
      })

    // Axes with custom styling
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d3.timeFormat('%m.%Y') as any)
        .ticks(Math.min(aggregatedData.length, 6)))

    xAxis.selectAll('text')
      .style('font-size', '12px')
      .style('fill', '#6b7280')
      .style('font-weight', '500')

    xAxis.selectAll('line, path')
      .style('stroke', '#d1d5db')
      .style('stroke-width', 1)

    const yAxis = g.append('g')
      .call(d3.axisLeft(yScale)
        .tickFormat(d => `${d} тн`)
        .ticks(6))

    yAxis.selectAll('text')
      .style('font-size', '12px')
      .style('fill', '#6b7280')
      .style('font-weight', '500')

    yAxis.selectAll('line, path')
      .style('stroke', '#d1d5db')
      .style('stroke-width', 1)

    // Axis labels with icons
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left + 20)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#374151')
      .text('🛢️ Добыча нефти (тн/сут)')

    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 5})`)
      .style('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#374151')
      .text('📅 Период')

    // Statistics panel
    if (aggregatedData.length > 0) {
      const totalProduction = aggregatedData.reduce((sum, d) => sum + d.totalOil, 0)
      const avgDaily = totalProduction / aggregatedData.length
      const maxDaily = Math.max(...aggregatedData.map(d => d.totalOil))

      const statsPanel = svg.append('g')
        .attr('transform', `translate(${width + margin.left - 90}, ${margin.top + 10})`)

      const statsBox = statsPanel.append('rect')
        .attr('width', 85)
        .attr('height', 75)
        .attr('rx', 6)
        .style('fill', 'rgba(255, 255, 255, 0.95)')
        .style('stroke', '#e5e7eb')
        .style('stroke-width', 1)

      statsPanel.append('text')
        .attr('x', 5)
        .attr('y', 15)
        .style('font-size', '10px')
        .style('font-weight', '600')
        .style('fill', '#9ca3af')
        .text('СТАТИСТИКА')

      statsPanel.append('text')
        .attr('x', 5)
        .attr('y', 30)
        .style('font-size', '11px')
        .style('fill', '#6b7280')
        .text(`Всего: ${totalProduction.toFixed(0)} тн`)

      statsPanel.append('text')
        .attr('x', 5)
        .attr('y', 45)
        .style('font-size', '11px')
        .style('fill', '#6b7280')
        .text(`Средн: ${avgDaily.toFixed(1)} тн`)

      statsPanel.append('text')
        .attr('x', 5)
        .attr('y', 60)
        .style('font-size', '11px')
        .style('fill', '#6b7280')
        .text(`Макс: ${maxDaily.toFixed(1)} тн`)
    }

    return () => {
      tooltip.remove()
    }

  }, [productionData, loading, dimensions])

  if (loading) {
    return (
      <div className="h-[350px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-200 border-t-orange-600 mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground animate-pulse">Загрузка данных добычи...</p>
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
      <div ref={tooltipRef}></div>
    </div>
  )
}