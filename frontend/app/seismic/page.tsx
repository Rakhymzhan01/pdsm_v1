import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Activity, 
  Navigation, 
  ZoomIn,
  ZoomOut,
  RotateCw,
  Download,
  Settings
} from "lucide-react"

export default function SeismicPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Сейсмика</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">3D сейсмика</Badge>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Настройки
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {/* Seismic Controls */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Управление</CardTitle>
            <CardDescription>Навигация по сейсмическим данным</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Navigation Controls */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Навигация</h4>
              
              <div className="grid grid-cols-3 gap-2">
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

            {/* Profile Selection */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Профили</h4>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Inline:</span>
                  <span className="font-medium text-sm">1250</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Xline:</span>
                  <span className="font-medium text-sm">2890</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Time:</span>
                  <span className="font-medium text-sm">1.2 с</span>
                </div>
              </div>
            </div>

            {/* Display Settings */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Отображение</h4>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Масштаб:</span>
                  <span className="font-medium text-sm">1:5000</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Контраст:</span>
                  <span className="font-medium text-sm">75%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Яркость:</span>
                  <span className="font-medium text-sm">100%</span>
                </div>
              </div>
            </div>

            {/* Horizon Picking */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Отбивка горизонтов</h4>
              
              <div className="grid gap-2">
                <Button variant="outline" size="sm" className="justify-start">
                  <div className="w-3 h-3 bg-red-500 rounded mr-2"></div>
                  Нижняя Юра
                </Button>
                <Button variant="outline" size="sm" className="justify-start">
                  <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                  Пермо-Триасс
                </Button>
                <Button variant="outline" size="sm" className="justify-start">
                  <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
                  Фундамент
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Seismic Display */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Сейсмические профили</CardTitle>
            <CardDescription>Inline 1250 / Xline 2890 - месторождение Каратюбе</CardDescription>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Navigation className="h-4 w-4 mr-2" />
                Переключить профиль
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Экспорт
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[600px] bg-muted rounded-lg flex items-center justify-center relative">
              <div className="text-center">
                <Activity className="h-20 w-20 mx-auto mb-6 text-muted-foreground" />
                <p className="text-xl font-medium text-muted-foreground mb-2">
                  Сейсмические данные
                </p>
                <p className="text-sm text-muted-foreground max-w-md">
                  Здесь будут отображаться 3D сейсмические данные 
                  по Inline и Xline профилям с отмеченными горизонтами
                </p>
              </div>

              {/* Simulated seismic traces */}
              <div className="absolute bottom-4 left-4 opacity-30">
                <div className="flex space-x-1">
                  {Array.from({length: 20}).map((_, i) => (
                    <div key={i} className="w-1 bg-gradient-to-t from-gray-600 to-gray-300" style={{height: Math.random() * 200 + 50}}></div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Seismic Interpretation Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Объем 3D съемки</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">85 км²</div>
            <p className="text-xs text-muted-foreground">площадь покрытия</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Частота дискретизации</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2 мс</div>
            <p className="text-xs text-muted-foreground">по времени</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Количество горизонтов</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">отбито</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Макс. время регистрации</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3.0 с</div>
            <p className="text-xs text-muted-foreground">TWT</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}