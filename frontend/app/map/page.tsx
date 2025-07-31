"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  MapPin, 
  ZoomIn, 
  ZoomOut, 
  RotateCw,
  Download,
  Filter,
  Eye,
  EyeOff
} from "lucide-react"
import MapComponent from "@/components/map/MapComponent"
import { useState } from "react"

export default function MapPage() {
  const [showFaults, setShowFaults] = useState(false)
  const [showBoundaries, setShowBoundaries] = useState(true)
  const [showContours, setShowContours] = useState(true)
  const [showWells, setShowWells] = useState(true)
  const [showThickness, setShowThickness] = useState(false)

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Карта месторождения</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">Каратюбе</Badge>
          <Badge variant="secondary">64 скважины</Badge>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Экспорт
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {/* Map Controls Sidebar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Управление картой</CardTitle>
            <CardDescription>Настройки отображения</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Map Tools */}
            <div className="space-y-2">
              <h4 className="font-medium text-sm">Инструменты</h4>
              <div className="flex gap-2">
                <Button variant="outline" size="icon" className="h-8 w-8">
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" className="h-8 w-8">
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" className="h-8 w-8">
                  <RotateCw className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Layer Controls */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Слои карты</h4>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Скважины</span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6"
                    onClick={() => setShowWells(!showWells)}
                  >
                    {showWells ? 
                      <Eye className="h-4 w-4 text-green-500" /> : 
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    }
                  </Button>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Границы участка</span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6"
                    onClick={() => setShowBoundaries(!showBoundaries)}
                  >
                    {showBoundaries ? 
                      <Eye className="h-4 w-4 text-green-500" /> : 
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    }
                  </Button>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Разломы</span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6"
                    onClick={() => setShowFaults(!showFaults)}
                  >
                    {showFaults ? 
                      <Eye className="h-4 w-4 text-green-500" /> : 
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    }
                  </Button>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Изогипсы</span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6"
                    onClick={() => setShowContours(!showContours)}
                  >
                    {showContours ? 
                      <Eye className="h-4 w-4 text-green-500" /> : 
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    }
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm">Карты толщин</span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6"
                    onClick={() => setShowThickness(!showThickness)}
                  >
                    {showThickness ? 
                      <Eye className="h-4 w-4 text-green-500" /> : 
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    }
                  </Button>
                </div>
              </div>
            </div>

            {/* Well Filters */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Фильтры скважин</h4>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Действующие (57)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm">В ремонте (3)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm">Остановленные (4)</span>
                </div>
              </div>
            </div>

            {/* Production Filters */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Отображение данных</h4>
              
              <div className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Filter className="h-4 w-4 mr-2" />
                  Дебиты нефти
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Filter className="h-4 w-4 mr-2" />
                  Обводненность
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Filter className="h-4 w-4 mr-2" />
                  Накопленная добыча
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Map Area */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Географическое расположение скважин</CardTitle>
            <CardDescription>Интерактивная карта месторождения Каратюбе</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[600px] rounded-lg overflow-hidden">
              <MapComponent
                showFaults={showFaults}
                showBoundaries={showBoundaries}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Map Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Площадь участка</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24.7 км²</div>
            <p className="text-xs text-muted-foreground">лицензионный участок</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Плотность скважин</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.6</div>
            <p className="text-xs text-muted-foreground">скв/км²</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Средняя глубина</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,850 м</div>
            <p className="text-xs text-muted-foreground">забой скважин</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Координаты центра</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold">50.2°N</div>
            <div className="text-lg font-bold">57.8°E</div>
            <p className="text-xs text-muted-foreground">WGS84</p>
          </CardContent>
        </Card>
      </div>

      {/* Well Details Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Информация о выбранной скважине</CardTitle>
          <CardDescription>Нажмите на скважину на карте для просмотра детальной информации</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <MapPin className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Выберите скважину на карте</p>
            <p className="text-sm">Здесь будет отображаться детальная информация о скважине</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}