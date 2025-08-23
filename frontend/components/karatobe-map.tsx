"use client"

import React, { useRef, useEffect, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { useWells } from '@/hooks/use-api'

// Set your Mapbox access token
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN || 'pk.eyJ1IjoicmFraHltemhhbiIsImEiOiJjbWRmenk0ZDkwaG1iMm9zZWJkZmxzZzZuIn0.i1JY2PZZTILJqv7Dno64Yw'

interface WellData {
  Well: string
  X: string  
  Y: string
  Lat: string
  Lon: string
  Object: string
  Year: string
}

export function KaratobeMap() {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [lng] = useState(56.54) // Longitude for Karatobe field
  const [lat] = useState(47.91) // Latitude for Karatobe field  
  const [zoom] = useState(11)
  
  const { data: wellsData, loading: wellsLoading, error: wellsError } = useWells()

  useEffect(() => {
    if (map.current) return // Initialize map only once
    
    if (!mapContainer.current) return

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-v9', // Satellite imagery
      center: [lng, lat],
      zoom: zoom,
      pitch: 45, // Add 3D tilt
      bearing: 0
    })

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')

    // Add scale control
    map.current.addControl(new mapboxgl.ScaleControl(), 'bottom-left')

    return () => {
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [lng, lat, zoom])

  useEffect(() => {
    if (!map.current || !wellsData || wellsLoading) return

    // Wait for map to load
    const addWellMarkers = () => {
      // Remove existing layers and sources if they exist
      if (map.current?.getLayer('well-labels')) {
        map.current.removeLayer('well-labels')
      }
      if (map.current?.getLayer('wells')) {
        map.current.removeLayer('wells')
      }
      if (map.current?.getSource('wells')) {
        map.current.removeSource('wells')
      }

      // Create GeoJSON data from wells
      const geojsonData = {
        type: 'FeatureCollection' as const,
        features: wellsData
          .filter((well: WellData) => well.Lat && well.Lon)
          .map((well: WellData) => ({
            type: 'Feature' as const,
            properties: {
              name: well.Well,
              object: well.Object,
              year: well.Year,
              x: well.X,
              y: well.Y
            },
            geometry: {
              type: 'Point' as const,
              coordinates: [parseFloat(well.Lon), parseFloat(well.Lat)]
            }
          }))
      }

      // Add wells as a source (only if it doesn't exist)
      if (!map.current?.getSource('wells')) {
        map.current?.addSource('wells', {
          type: 'geojson',
          data: geojsonData
        })
      } else {
        // Update existing source data
        const source = map.current.getSource('wells') as mapboxgl.GeoJSONSource
        source.setData(geojsonData)
      }

      // Add wells layer with different colors based on object type (only if it doesn't exist)
      if (!map.current?.getLayer('wells')) {
        map.current?.addLayer({
          id: 'wells',
          type: 'circle',
          source: 'wells',
          paint: {
            'circle-radius': [
              'interpolate',
              ['linear'],
              ['zoom'],
              8, 4,
              14, 8
            ],
            'circle-color': [
              'match',
              ['get', 'object'],
              'P&T', '#ff6b35', // Orange for P&T
              'Консв', '#4a90e2', // Blue for Conservation
              '#ffd700' // Default yellow
            ],
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
            'circle-opacity': 0.8
          }
        })
      }

      // Add well labels (only if it doesn't exist)
      if (!map.current?.getLayer('well-labels')) {
        map.current?.addLayer({
          id: 'well-labels',
          type: 'symbol',
          source: 'wells',
          layout: {
            'text-field': ['get', 'name'],
            'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
            'text-offset': [0, 1.5],
            'text-anchor': 'top',
            'text-size': 12
          },
          paint: {
            'text-color': '#ffffff',
            'text-halo-color': '#000000',
            'text-halo-width': 1
          }
        })
      }

      // Remove existing layers if they exist
      if (map.current?.getLayer('wells-labels')) {
        map.current.removeLayer('wells-labels')
      }
      if (map.current?.getLayer('wells')) {
        map.current.removeLayer('wells')
      }
      if (map.current?.getSource('wells')) {
        map.current.removeSource('wells')
      }

      // Add click event for well popups
      map.current?.on('click', 'wells', (e) => {
        if (!e.features?.[0]) return
        
        const properties = e.features[0].properties
        const geometry = e.features[0].geometry as GeoJSON.Point
        const coordinates: [number, number] = [geometry.coordinates[0], geometry.coordinates[1]]

        // Create popup content
        const popupContent = `
          <div class="p-2">
            <h3 class="font-semibold text-lg mb-2">Скважина ${properties?.name}</h3>
            <div class="space-y-1 text-sm">
              <div><span class="font-medium">Объект:</span> ${properties?.object}</div>
              <div><span class="font-medium">Год:</span> ${properties?.year}</div>
              <div><span class="font-medium">X:</span> ${properties?.x}</div>
              <div><span class="font-medium">Y:</span> ${properties?.y}</div>
            </div>
          </div>
        `

        new mapboxgl.Popup({ offset: 15 })
          .setLngLat(coordinates)
          .setHTML(popupContent)
          .addTo(map.current!)
      })

      // Change cursor on hover
      map.current?.on('mouseenter', 'wells', () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = 'pointer'
        }
      })

      map.current?.on('mouseleave', 'wells', () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = ''
        }
      })
    }

    if (map.current.isStyleLoaded()) {
      addWellMarkers()
    } else {
      map.current.on('load', addWellMarkers)
    }
  }, [wellsData, wellsLoading])

  if (wellsError) {
    return (
      <div className="h-[350px] bg-muted rounded-lg flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500">Ошибка загрузки данных скважин</p>
          <p className="text-sm text-muted-foreground mt-2">{wellsError}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-[350px] rounded-lg overflow-hidden">
      <div ref={mapContainer} className="w-full h-full" />
      
      {/* Legend */}
      <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg">
        <h4 className="font-semibold text-sm mb-2">Типы объектов:</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ff6b35]"></div>
            <span>P&T</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#4a90e2]"></div>
            <span>Консервация</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ffd700]"></div>
            <span>Другие</span>
          </div>
        </div>
      </div>

      {/* Loading overlay */}
      {wellsLoading && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
          <div className="text-white text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
            <p>Загрузка скважин...</p>
          </div>
        </div>
      )}

      {/* Wells count */}
      {wellsData && !wellsLoading && (
        <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg">
          <p className="text-sm font-medium">Скважин: {wellsData.length}</p>
        </div>
      )}
    </div>
  )
}