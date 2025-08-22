"use client"

import React, { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { useProductionData } from '@/hooks/use-api'

interface ProductionRecord {
  Date: string
  well: string
  Qo_ton: number
  Qw_m3: number  
  Ql_m3: number
  Obv_percent: number
}

interface AggregatedData {
  date: string
  totalOil: number
  totalWater: number
  totalLiquid: number
  avgWaterCut: number
  wellCount: number
}

export function ProductionHistoryChart() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 })
  const { data: productionData, loading, error } = useProductionData()

  // Aggregate production data by date
  const aggregateData = (data: ProductionRecord[]): AggregatedData[] => {
    if (!data || data.length === 0) return []

    const grouped = data.reduce((acc, record) => {
      const date = record.Date
      if (!acc[date]) {
        acc[date] = {
          totalOil: 0,
          totalWater: 0,
          totalLiquid: 0,
          waterCuts: [],
          wells: new Set()
        }
      }
      
      acc[date].totalOil += record.Qo_ton || 0
      acc[date].totalWater += record.Qw_m3 || 0
      acc[date].totalLiquid += record.Ql_m3 || 0
      acc[date].wells.add(record.well)
      if (record.Obv_percent) {
        acc[date].waterCuts.push(record.Obv_percent)
      }
      
      return acc
    }, {} as Record<string, any>)

    return Object.entries(grouped)
      .map(([date, values]) => ({
        date,
        totalOil: values.totalOil,
        totalWater: values.totalWater, 
        totalLiquid: values.totalLiquid,
        wellCount: values.wells.size,
        avgWaterCut: values.waterCuts.length > 0 
          ? values.waterCuts.reduce((sum: number, val: number) => sum + val, 0) / values.waterCuts.length
          : 0
      }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
  }

  useEffect(() => {
    const handleResize = () => {
      if (svgRef.current?.parentElement) {
        const parentWidth = svgRef.current.parentElement.clientWidth
        setDimensions({
          width: Math.max(parentWidth - 40, 400),
          height: 300
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

    // Clear previous chart
    d3.select(svgRef.current).selectAll("*").remove()

    const margin = { top: 20, right: 80, bottom: 40, left: 60 }
    const width = dimensions.width - margin.left - margin.right
    const height = dimensions.height - margin.top - margin.bottom

    const svg = d3.select(svgRef.current)
      .attr('width', dimensions.width)
      .attr('height', dimensions.height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(aggregatedData, d => new Date(d.date)) as [Date, Date])
      .range([0, width])

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(aggregatedData, d => d.totalOil) || 100])
      .range([height, 0])

    // Line generator
    const line = d3.line<AggregatedData>()
      .x(d => xScale(new Date(d.date)))
      .y(d => yScale(d.totalOil))
      .curve(d3.curveMonotoneX)

    // Add gradient for area
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', 'oil-gradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', height)
      .attr('x2', 0).attr('y2', 0)

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#ff6b35')
      .attr('stop-opacity', 0.1)

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#ff6b35')
      .attr('stop-opacity', 0.8)

    // Add area
    const area = d3.area<AggregatedData>()
      .x(d => xScale(new Date(d.date)))
      .y0(height)
      .y1(d => yScale(d.totalOil))
      .curve(d3.curveMonotoneX)

    g.append('path')
      .datum(aggregatedData)
      .attr('fill', 'url(#oil-gradient)')
      .attr('d', area)

    // Add line
    g.append('path')
      .datum(aggregatedData)
      .attr('fill', 'none')
      .attr('stroke', '#ff6b35')
      .attr('stroke-width', 3)
      .attr('d', line)

    // Add dots
    g.selectAll('.dot')
      .data(aggregatedData)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(new Date(d.date)))
      .attr('cy', d => yScale(d.totalOil))
      .attr('r', 4)
      .attr('fill', '#ff6b35')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('opacity', 0.8)
      .on('mouseover', function(event, d) {
        // Tooltip
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'rgba(0,0,0,0.8)')
          .style('color', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('font-size', '12px')
          .style('pointer-events', 'none')
          .style('z-index', '1000')

        tooltip.html(`
          <div><strong>Дата:</strong> ${d.date}</div>
          <div><strong>Добыча нефти:</strong> ${d.totalOil.toFixed(1)} тн</div>
          <div><strong>Обводненность:</strong> ${d.avgWaterCut.toFixed(1)}%</div>
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
        .style('opacity', 1)

        d3.select(this).attr('r', 6).style('opacity', 1)
      })
      .on('mouseout', function() {
        d3.selectAll('.tooltip').remove()
        d3.select(this).attr('r', 4).style('opacity', 0.8)
      })

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d3.timeFormat('%d.%m') as any)
        .ticks(6))
      .selectAll('text')
      .style('font-size', '12px')

    // Y axis
    g.append('g')
      .call(d3.axisLeft(yScale)
        .tickFormat(d => `${d} тн`))
      .selectAll('text')
      .style('font-size', '12px')

    // Grid lines
    g.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickSize(-height)
        .tickFormat(() => '')
      )
      .style('stroke-dasharray', '2,2')
      .style('opacity', 0.3)

    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisLeft(yScale)
        .tickSize(-width)
        .tickFormat(() => '')
      )
      .style('stroke-dasharray', '2,2')
      .style('opacity', 0.3)

    // Axis labels
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('fill', '#666')
      .text('Добыча нефти (тн/сут)')

    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom})`)
      .style('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('fill', '#666')
      .text('Дата')

    // Title
    svg.append('text')
      .attr('x', dimensions.width / 2)
      .attr('y', 15)
      .style('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .style('fill', '#333')
      .text('История добычи нефти в Каратюбе')

  }, [productionData, loading, dimensions])

  if (loading) {
    return (
      <div className="h-[300px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">Загрузка данных добычи...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[300px] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500">Ошибка загрузки данных</p>
          <p className="text-sm text-muted-foreground mt-1">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <svg ref={svgRef} className="w-full"></svg>
    </div>
  )
}