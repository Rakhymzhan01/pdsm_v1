'use client'

import React, { useState, useRef } from 'react'
import Map, { Marker, Popup, Layer, Source } from 'react-map-gl/mapbox'
import type { MapRef } from 'react-map-gl/mapbox'
import * as d3 from 'd3'
import 'mapbox-gl/dist/mapbox-gl.css'

interface Well {
  id: string
  name: string
  longitude: number
  latitude: number
  status: 'active' | 'repair' | 'stopped'
  production: number
  waterCut: number
  depth: number
}

interface MapComponentProps {
  wells?: Well[]
  showFaults?: boolean
  showBoundaries?: boolean
}

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN

const defaultWells: Well[] = [
  { id: '301', name: '301', longitude: 57.7, latitude: 50.1, status: 'active', production: 45, waterCut: 23, depth: 1850 },
  { id: '302', name: '302', longitude: 57.72, latitude: 50.12, status: 'active', production: 38, waterCut: 31, depth: 1820 },
  { id: '303', name: '303', longitude: 57.74, latitude: 50.14, status: 'repair', production: 0, waterCut: 0, depth: 1890 },
  { id: '304', name: '304', longitude: 57.76, latitude: 50.16, status: 'active', production: 52, waterCut: 18, depth: 1775 },
  { id: '305', name: '305', longitude: 57.78, latitude: 50.18, status: 'stopped', production: 0, waterCut: 0, depth: 1945 },
]

export default function MapComponent({ 
  wells = defaultWells, 
  showFaults = false, 
  showBoundaries = true
}: MapComponentProps) {
  const [viewState, setViewState] = useState({
    longitude: 57.75,
    latitude: 50.15,
    zoom: 12
  })
  
  const [popupInfo, setPopupInfo] = useState<Well | null>(null)
  const mapRef = useRef<MapRef | null>(null)

  const getWellColor = (status: string) => {
    switch (status) {
      case 'active': return '#10b981'
      case 'repair': return '#f59e0b'
      case 'stopped': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getWellSize = (production: number) => {
    const scale = d3.scaleLinear()
      .domain([0, 100])
      .range([8, 20])
    return scale(production)
  }

  // Boundary data for Karatobe field
  const boundaryData = {
    type: 'Feature' as const,
    properties: {},
    geometry: {
      type: 'Polygon' as const,
      coordinates: [[
        [57.65, 50.08],
        [57.85, 50.08],
        [57.85, 50.22],
        [57.65, 50.22],
        [57.65, 50.08]
      ]]
    }
  }

  // Fault lines data
  const faultData = {
    type: 'FeatureCollection' as const,
    features: [
      {
        type: 'Feature' as const,
        properties: {},
        geometry: {
          type: 'LineString' as const,
          coordinates: [
            [57.68, 50.09],
            [57.72, 50.15],
            [57.76, 50.19]
          ]
        }
      },
      {
        type: 'Feature' as const,
        properties: {},
        geometry: {
          type: 'LineString' as const,
          coordinates: [
            [57.71, 50.10],
            [57.75, 50.14],
            [57.79, 50.18]
          ]
        }
      }
    ]
  }

  return (
    <div className="h-full w-full relative">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/satellite-v9"
        terrain={{ source: 'mapbox-dem', exaggeration: 1.5 }}
      >
        {/* Boundary Layer */}
        {showBoundaries && (
          <Source id="boundary" type="geojson" data={boundaryData}>
            <Layer
              id="boundary-fill"
              type="fill"
              paint={{
                'fill-color': '#3b82f6',
                'fill-opacity': 0.1
              }}
            />
            <Layer
              id="boundary-line"
              type="line"
              paint={{
                'line-color': '#3b82f6',
                'line-width': 2,
                'line-dasharray': [2, 2]
              }}
            />
          </Source>
        )}

        {/* Fault Lines Layer */}
        {showFaults && (
          <Source id="faults" type="geojson" data={faultData}>
            <Layer
              id="fault-lines"
              type="line"
              paint={{
                'line-color': '#dc2626',
                'line-width': 3,
                'line-opacity': 0.8
              }}
            />
          </Source>
        )}

        {/* Well Markers */}
        {wells.map((well) => (
          <Marker
            key={well.id}
            longitude={well.longitude}
            latitude={well.latitude}
            anchor="center"
            onClick={() => setPopupInfo(well)}
          >
            <div
              className="cursor-pointer flex items-center justify-center rounded-full border-2 border-white shadow-lg font-bold text-white text-xs"
              style={{
                backgroundColor: getWellColor(well.status),
                width: getWellSize(well.production),
                height: getWellSize(well.production),
                fontSize: getWellSize(well.production) > 12 ? '10px' : '8px'
              }}
              title={`Скважина ${well.name}`}
            >
              {well.name}
            </div>
          </Marker>
        ))}

        {/* Well Info Popup */}
        {popupInfo && (
          <Popup
            anchor="top"
            longitude={popupInfo.longitude}
            latitude={popupInfo.latitude}
            onClose={() => setPopupInfo(null)}
            className="well-popup"
          >
            <div className="p-3 min-w-[200px]">
              <h3 className="font-bold text-lg mb-2">Скважина {popupInfo.name}</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Статус:</span>
                  <span className={`font-medium ${
                    popupInfo.status === 'active' ? 'text-green-600' :
                    popupInfo.status === 'repair' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {popupInfo.status === 'active' ? 'Действующая' :
                     popupInfo.status === 'repair' ? 'В ремонте' : 'Остановлена'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Дебит нефти:</span>
                  <span className="font-medium">{popupInfo.production} т/сут</span>
                </div>
                <div className="flex justify-between">
                  <span>Обводненность:</span>
                  <span className="font-medium">{popupInfo.waterCut}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Глубина:</span>
                  <span className="font-medium">{popupInfo.depth} м</span>
                </div>
              </div>
            </div>
          </Popup>
        )}
      </Map>

      {/* Map Controls */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-2">
        <div className="flex flex-col gap-2">
          <button
            onClick={() => {
              const map = mapRef.current?.getMap()
              if (map) map.zoomIn()
            }}
            className="p-2 hover:bg-gray-100 rounded"
            title="Увеличить"
          >
            +
          </button>
          <button
            onClick={() => {
              const map = mapRef.current?.getMap()
              if (map) map.zoomOut()
            }}
            className="p-2 hover:bg-gray-100 rounded"
            title="Уменьшить"
          >
            -
          </button>
        </div>
      </div>

      {/* Scale and North Arrow */}
      <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-3">
        <div className="text-center text-xs">
          <div className="font-bold">N ↑</div>
          <div className="text-gray-500 mt-1">Масштаб 1:{Math.round(10000 / Math.pow(2, viewState.zoom - 12))}</div>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3">
        <h4 className="font-medium text-sm mb-2">Условные обозначения</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Действующие скважины</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span>В ремонте</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>Остановленные</span>
          </div>
          {showBoundaries && (
            <div className="flex items-center gap-2">
              <div className="w-4 h-0.5 bg-blue-500 border-dashed"></div>
              <span>Границы участка</span>
            </div>
          )}
          {showFaults && (
            <div className="flex items-center gap-2">
              <div className="w-4 h-0.5 bg-red-600"></div>
              <span>Разломы</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}