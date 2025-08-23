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

interface FieldProductionData {
  date: string
  fields: Record<string, {
    totalOil: number
    totalWater: number
    wellCount: number
  }>
}

export function FieldProductionHistoryChart() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 })
  const { data: productionData, loading, error } = useProductionData()

  // Group production data by field/horizon
  const aggregateDataByField = (data: ProductionRecord[]): FieldProductionData[] => {
    if (!data || data.length === 0) return []

    // Group by month-year and field
    const grouped = data.reduce((acc, record) => {
      const date = new Date(record.Date)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      const field = record.Horizon || 'Прочие'
      
      if (!acc[monthKey]) {
        acc[monthKey] = {}
      }
      
      if (!acc[monthKey][field]) {
        acc[monthKey][field] = {
          totalOil: 0,
          totalWater: 0,
          wells: new Set()
        }
      }
      
      acc[monthKey][field].totalOil += record.Qo_ton || 0
      acc[monthKey][field].totalWater += record.Qw_m3 || 0
      acc[monthKey][field].wells.add(record.Well)
      
      return acc
    }, {} as Record<string, Record<string, {
      totalOil: number
      totalWater: number
      wells: Set<string>
    }>>)

    // Convert to array format
    const result = Object.entries(grouped)
      .map(([monthKey, fields]) => {
        const [year, month] = monthKey.split('-')
        const displayDate = new Date(parseInt(year), parseInt(month) - 1, 15)
        
        const fieldsData: Record<string, { totalOil: number; totalWater: number; wellCount: number }> = {}
        Object.entries(fields).forEach(([field, data]) => {
          fieldsData[field] = {
            totalOil: data.totalOil,
            totalWater: data.totalWater,
            wellCount: data.wells.size
          }
        })
        
        return {
          date: displayDate.toISOString().split('T')[0],
          fields: fieldsData
        }
      })
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

    return result
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

    const aggregatedData = aggregateDataByField(productionData)
    if (aggregatedData.length === 0) return

    // Get all unique fields
    const allFields = Array.from(new Set(
      aggregatedData.flatMap(d => Object.keys(d.fields))
    )).sort()

    // Clear previous chart
    d3.select(svgRef.current).selectAll("*").remove()

    const margin = { top: 30, right: 120, bottom: 50, left: 80 }
    const width = dimensions.width - margin.left - margin.right
    const height = dimensions.height - margin.top - margin.bottom

    const svg = d3.select(svgRef.current)
      .attr('width', dimensions.width)
      .attr('height', dimensions.height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Color scale for different fields
    const colorScale = d3.scaleOrdinal<string>()
      .domain(allFields)
      .range(['#ff6b35', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16'])

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(aggregatedData, d => new Date(d.date)) as [Date, Date])
      .range([0, width])

    const maxProduction = d3.max(aggregatedData, d => 
      Math.max(...Object.values(d.fields).map(field => field.totalOil))
    ) || 100

    const yScale = d3.scaleLinear()
      .domain([0, maxProduction])
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

    // Create lines for each field
    allFields.forEach((field, index) => {
      // Filter data for this field
      const fieldData = aggregatedData
        .map(d => ({
          date: d.date,
          value: d.fields[field]?.totalOil || 0
        }))
        .filter(d => d.value > 0)

      if (fieldData.length === 0) return

      // Line generator
      const line = d3.line<{date: string, value: number}>()
        .x(d => xScale(new Date(d.date)))
        .y(d => yScale(d.value))
        .curve(d3.curveMonotoneX)

      // Add area
      const area = d3.area<{date: string, value: number}>()
        .x(d => xScale(new Date(d.date)))
        .y0(height)
        .y1(d => yScale(d.value))
        .curve(d3.curveMonotoneX)

      // Area with low opacity
      g.append('path')
        .datum(fieldData)
        .attr('fill', colorScale(field))
        .attr('fill-opacity', 0.2)
        .attr('d', area)

      // Line
      const linePath = g.append('path')
        .datum(fieldData)
        .attr('fill', 'none')
        .attr('stroke', colorScale(field))
        .attr('stroke-width', 2.5)
        .attr('d', line)

      // Animate line
      const totalLength = (linePath.node() as SVGPathElement).getTotalLength()
      linePath
        .attr('stroke-dasharray', totalLength + ' ' + totalLength)
        .attr('stroke-dashoffset', totalLength)
        .transition()
        .duration(1500)
        .delay(index * 200)
        .ease(d3.easeQuadOut)
        .attr('stroke-dashoffset', 0)

      // Add dots
      const dots = g.selectAll(`.dots-${index}`)
        .data(fieldData)
        .enter().append('circle')
        .attr('class', `dots-${index}`)
        .attr('cx', d => xScale(new Date(d.date)))
        .attr('cy', d => yScale(d.value))
        .attr('r', 0)
        .attr('fill', colorScale(field))
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')

      dots.transition()
        .delay((d, i) => index * 200 + i * 50)
        .duration(300)
        .ease(d3.easeBounceOut)
        .attr('r', 3)

      // Tooltip
      const tooltip = d3.select(document.body)
        .append('div')
        .attr('class', `tooltip-${field}`)
        .style('position', 'absolute')
        .style('background', 'rgba(0,0,0,0.8)')
        .style('color', 'white')
        .style('padding', '8px 12px')
        .style('border-radius', '6px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('opacity', 0)
        .style('z-index', '1000')

      dots.on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', 5)

        const fieldInfo = aggregatedData.find(item => item.date === d.date)?.fields[field]

        tooltip.html(`
          <div style="margin-bottom: 4px;"><strong>${field}</strong></div>
          <div>📅 ${new Date(d.date).toLocaleDateString('ru-RU', {month: 'long', year: 'numeric'})}</div>
          <div>🛢️ Нефть: <strong>${d.value.toFixed(1)} тн</strong></div>
          <div>💧 Вода: <strong>${fieldInfo?.totalWater.toFixed(1) || 0} м³</strong></div>
          <div>⚡ Скважин: <strong>${fieldInfo?.wellCount || 0}</strong></div>
        `)
        .style('opacity', 1)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
      })
      .on('mouseout', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', 3)

        tooltip.style('opacity', 0)
      })
    })

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width + margin.left + 20}, ${margin.top + 20})`)

    const legendItems = legend.selectAll('.legend-item')
      .data(allFields)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => `translate(0, ${i * 25})`)

    legendItems.append('rect')
      .attr('width', 90)
      .attr('height', 20)
      .attr('rx', 3)
      .style('fill', 'rgba(255, 255, 255, 0.9)')
      .style('stroke', '#e5e7eb')
      .style('stroke-width', 1)

    legendItems.append('line')
      .attr('x1', 5)
      .attr('y1', 10)
      .attr('x2', 20)
      .attr('y2', 10)
      .style('stroke', d => colorScale(d))
      .style('stroke-width', 3)

    legendItems.append('text')
      .attr('x', 25)
      .attr('y', 14)
      .style('font-size', '11px')
      .style('font-weight', '500')
      .style('fill', '#374151')
      .text(d => d.length > 8 ? d.substring(0, 8) + '...' : d)

    // Axes
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d => d3.timeFormat('%m.%Y')(d as Date))
        .ticks(6))

    xAxis.selectAll('text')
      .style('font-size', '12px')
      .style('fill', '#6b7280')

    const yAxis = g.append('g')
      .call(d3.axisLeft(yScale)
        .tickFormat(d => `${d} тн`)
        .ticks(6))

    yAxis.selectAll('text')
      .style('font-size', '12px')
      .style('fill', '#6b7280')

    // Axis labels
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left + 20)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#374151')
      .text('🛢️ Добыча нефти (тн)')

    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 10})`)
      .style('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#374151')
      .text('📅 Период')

    // Title
    svg.append('text')
      .attr('x', dimensions.width / 2)
      .attr('y', 20)
      .style('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .style('fill', '#333')
      .text('История добычи по месторождениям')

  }, [productionData, loading, dimensions])

  if (loading) {
    return (
      <div className="h-[350px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-200 border-t-orange-600 mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground animate-pulse">Загрузка данных по месторождениям...</p>
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