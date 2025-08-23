"use client"

import React, { useEffect, useRef, useState, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

interface CumulativeProductionData {
  well_name: string
  latitude: number
  longitude: number
  object_type: string
  horizon: string
  cumulative_oil: number
  cumulative_water: number
  cumulative_liquid: number
  production_days: number
  avg_daily_oil: number
}

// Set your Mapbox access token
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN || 'pk.eyJ1Ijoia2FyYXRvYmUiLCJhIjoiY2x6c2hsZ2NjMGRrZzJxc2pvNjZ1bmN5dCJ9.yL5zS6fBGXFhAZzVnS_hzg'

export function CumulativeProductionMap() {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [lng, setLng] = useState(76.6219)
  const [lat, setLat] = useState(50.4547)
  const [zoom, setZoom] = useState(11)
  const [data, setData] = useState<CumulativeProductionData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mapBounds, setMapBounds] = useState<mapboxgl.LngLatBounds | null>(null)
  const [hasInitialized, setHasInitialized] = useState(false)

  // Fetch cumulative production data
  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching cumulative production data...')
        const response = await fetch('http://localhost:8000/api/v1/karatobe/cumulative-production')
        console.log('Response status:', response.status)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const result = await response.json()
        console.log('Fetched data:', result.length, 'wells')
        setData(result)
        
        // Calculate initial bounds from data
        if (result.length > 0) {
          const coordinates = result.map((well: CumulativeProductionData) => [well.longitude, well.latitude] as [number, number])
          const bounds = new mapboxgl.LngLatBounds()
          coordinates.forEach(coord => bounds.extend(coord))
          setMapBounds(bounds)
        }
      } catch (err) {
        console.error('Error fetching cumulative production data:', err)
        setError(err instanceof Error ? err.message : 'Unknown error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const addWellsLayer = useCallback(() => {
    if (!map.current || !data.length) return

    // Calculate min and max cumulative oil for color scaling
    const cumulativeOilValues = data.map(d => d.cumulative_oil).filter(v => v > 0)
    const minOil = Math.min(...cumulativeOilValues)
    const maxOil = Math.max(...cumulativeOilValues)

    console.log('Cumulative oil range:', { minOil, maxOil })

    // Create GeoJSON features
    const geojsonData = {
      type: 'FeatureCollection' as const,
      features: data.map(well => ({
        type: 'Feature' as const,
        properties: {
          well_name: well.well_name,
          object_type: well.object_type,
          horizon: well.horizon,
          cumulative_oil: well.cumulative_oil,
          cumulative_water: well.cumulative_water,
          cumulative_liquid: well.cumulative_liquid,
          production_days: well.production_days,
          avg_daily_oil: well.avg_daily_oil
        },
        geometry: {
          type: 'Point' as const,
          coordinates: [well.longitude, well.latitude]
        }
      }))
    }

    // Add source
    map.current.addSource('cumulative-wells', {
      type: 'geojson',
      data: geojsonData
    })

    // Add circle layer with color based on cumulative production
    map.current.addLayer({
      id: 'wells-circles',
      type: 'circle',
      source: 'cumulative-wells',
      paint: {
        'circle-radius': [
          'interpolate',
          ['linear'],
          ['get', 'cumulative_oil'],
          0, 8,
          maxOil / 4, 12,
          maxOil / 2, 16,
          maxOil, 20
        ],
        'circle-color': [
          'interpolate',
          ['linear'],
          ['get', 'cumulative_oil'],
          0, '#313131',        // Black for no production
          minOil, '#2563eb',   // Blue for low production  
          maxOil / 4, '#10b981', // Green for medium-low
          maxOil / 2, '#f59e0b', // Yellow for medium-high
          maxOil, '#dc2626'      // Red for high production
        ],
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 2,
        'circle-opacity': 0.8,
        'circle-stroke-opacity': 1
      }
    })

    // Add well labels
    map.current.addLayer({
      id: 'wells-labels',
      type: 'symbol',
      source: 'cumulative-wells',
      layout: {
        'text-field': ['get', 'well_name'],
        'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
        'text-size': 11,
        'text-offset': [0, 2],
        'text-anchor': 'top'
      },
      paint: {
        'text-color': '#ffffff',
        'text-halo-color': '#000000',
        'text-halo-width': 1
      }
    })

    // Add click popup
    map.current.on('click', 'wells-circles', (e) => {
      if (e.features && e.features[0]) {
        const feature = e.features[0]
        const props = feature.properties

        new mapboxgl.Popup({ closeOnClick: true })
          .setLngLat([props!.longitude, props!.latitude])
          .setHTML(`
            <div style="font-family: system-ui; font-size: 13px; line-height: 1.4;">
              <div style="font-weight: 600; font-size: 14px; color: #1f2937; margin-bottom: 8px;">
                🛢️ Скважина ${props!.well_name}
              </div>
              <div style="display: grid; gap: 4px;">
                <div><span style="color: #6b7280;">Объект:</span> <strong>${props!.object_type}</strong></div>
                <div><span style="color: #6b7280;">Горизонт:</span> <strong>${props!.horizon}</strong></div>
                <div><span style="color: #dc2626;">🛢️ Накопленная нефть:</span> <strong>${(props!.cumulative_oil).toFixed(1)} тн</strong></div>
                <div><span style="color: #2563eb;">💧 Накопленная вода:</span> <strong>${(props!.cumulative_water).toFixed(1)} м³</strong></div>
                <div><span style="color: #10b981;">📊 Средний дебит:</span> <strong>${(props!.avg_daily_oil).toFixed(1)} тн/сут</strong></div>
                <div><span style="color: #f59e0b;">📅 Дней в работе:</span> <strong>${props!.production_days}</strong></div>
              </div>
            </div>
          `)
          .addTo(map.current!)
      }
    })

    // Change cursor on hover
    map.current.on('mouseenter', 'wells-circles', () => {
      if (map.current) {
        map.current.getCanvas().style.cursor = 'pointer'
      }
    })

    map.current.on('mouseleave', 'wells-circles', () => {
      if (map.current) {
        map.current.getCanvas().style.cursor = ''
      }
    })
  }, [data])

  const fitMapToWells = useCallback(() => {
    if (!map.current || !data.length) {
      console.log('Cannot fit to wells - missing map or data')
      return
    }

    console.log('Fitting map to', data.length, 'wells')
    
    // Get coordinates of all wells
    const coordinates = data.map(well => [well.longitude, well.latitude] as [number, number])
    console.log('First few coordinates:', coordinates.slice(0, 3))
    
    // Create bounds from coordinates
    const bounds = new mapboxgl.LngLatBounds()
    coordinates.forEach(coord => bounds.extend(coord))

    console.log('Bounds:', bounds.getNorthEast(), bounds.getSouthWest())

    // Fit map to bounds with padding
    map.current.fitBounds(bounds, {
      padding: { top: 50, bottom: 50, left: 50, right: 50 },
      duration: hasInitialized ? 1000 : 0, // No animation on first load
      maxZoom: 13 // Don't zoom in too much
    })
  }, [data, hasInitialized])

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current || loading || !data.length) return

    console.log('Initializing map...')

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [lng, lat],
      zoom: zoom,
      pitch: 0,
      bearing: 0
    })

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')
    map.current.addControl(new mapboxgl.FullscreenControl(), 'top-right')

    map.current.on('move', () => {
      if (map.current) {
        setLng(parseFloat(map.current.getCenter().lng.toFixed(4)))
        setLat(parseFloat(map.current.getCenter().lat.toFixed(4)))
        setZoom(parseFloat(map.current.getZoom().toFixed(2)))
      }
    })

    map.current.on('load', () => {
      console.log('Map loaded, adding wells layer...')
      addWellsLayer()
      
      // Fit to wells immediately after layer is added
      if (!hasInitialized) {
        fitMapToWells()
        setHasInitialized(true)
      }
    })

    return () => {
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [data, loading, addWellsLayer, fitMapToWells, lng, lat, zoom, hasInitialized])

  if (loading) {
    return (
      <div className="h-[400px] flex items-center justify-center bg-muted rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-200 border-t-orange-600 mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground animate-pulse">Загрузка данных накопленной добычи...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[400px] flex items-center justify-center bg-red-50 rounded-lg border border-red-200">
        <div className="text-center p-6">
          <div className="text-red-500 text-4xl mb-2">⚠️</div>
          <p className="text-red-700 font-medium">Ошибка загрузки карты</p>
          <p className="text-sm text-red-600 mt-1">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-[400px] w-full rounded-lg overflow-hidden">
      <div ref={mapContainer} className="h-full w-full" />
      
      {/* Color Legend */}
      <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm p-3 rounded-lg shadow-lg border pointer-events-none">
        <div className="text-xs font-semibold mb-2 text-gray-700">Накопленная добыча (тн)</div>
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gray-800 border border-white"></div>
            <span className="text-xs">Нет добычи</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-600 border border-white"></div>
            <span className="text-xs">Низкая (&lt; 25%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500 border border-white"></div>
            <span className="text-xs">Средняя (25-50%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500 border border-white"></div>
            <span className="text-xs">Высокая (50-75%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-600 border border-white"></div>
            <span className="text-xs">Очень высокая (&gt; 75%)</span>
          </div>
        </div>
      </div>

      {/* Statistics Panel */}
      <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm p-3 rounded-lg shadow-lg border pointer-events-none">
        <div className="text-xs font-semibold mb-2 text-gray-700">СТАТИСТИКА</div>
        <div className="text-xs text-gray-600 space-y-1">
          <div>Скважин: {data.length}</div>
          <div>Общая добыча: {data.reduce((sum, well) => sum + well.cumulative_oil, 0).toFixed(0)} тн</div>
          <div>Средний дебит: {(data.reduce((sum, well) => sum + well.avg_daily_oil, 0) / data.length).toFixed(1)} тн/сут</div>
        </div>
      </div>

      {/* Fit to Wells Button */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2">
        <button
          onClick={fitMapToWells}
          className="bg-white/95 backdrop-blur-sm px-3 py-1 rounded-lg shadow-lg border text-xs font-medium text-gray-700 hover:bg-white hover:text-blue-600 transition-colors"
          title="Показать все скважины"
        >
          📍 Показать все скважины
        </button>
      </div>
    </div>
  )
}