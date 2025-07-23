import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  TrendingUp, 
  Layers, 
  Eye,
  EyeOff,
  Maximize2,
  Download,
  Settings,
  BarChart3
} from "lucide-react"

export default function CorrelationPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Корреляция разрезов</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">Каратюбе</Badge>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Настройки
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {/* Well Selection Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Выбор скважин</CardTitle>
            <CardDescription>Для корреляции</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Active Wells */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Активные скважины</h4>
              
              <div className="space-y-2">
                {[
                  { well: "301", selected: true },
                  { well: "302", selected: true },
                  { well: "303", selected: false },
                  { well: "304", selected: true },
                  { well: "305", selected: false },
                  { well: "306", selected: false },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="text-sm">Скважина {item.well}</span>
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      {item.selected ? (
                        <Eye className="h-4 w-4 text-green-500" />
                      ) : (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      )}
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Correlation Settings */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Параметры корреляции</h4>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Масштаб</span>
                  <span className="text-xs font-medium">1:500</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Пласты</span>
                  <span className="text-xs font-medium">J1, P-T</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Каротаж</span>
                  <span className="text-xs font-medium">GR, SP, RT</span>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Легенда</h4>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-2 bg-yellow-500"></div>
                  <span className="text-xs">Нижняя Юра</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-2 bg-green-500"></div>
                  <span className="text-xs">Пермо-Триасс</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-2 bg-blue-500"></div>
                  <span className="text-xs">Нефтяной пласт</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-2 bg-red-500"></div>
                  <span className="text-xs">Водонасыщий</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Correlation Panel */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Корреляционная панель</CardTitle>
            <CardDescription>Корреляция разрезов скважин 301, 302, 304</CardDescription>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Maximize2 className="h-4 w-4 mr-2" />
                Полный экран
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Сохранить
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[600px] bg-muted rounded-lg flex items-center justify-center relative">
              <div className="text-center">
                <Layers className="h-20 w-20 mx-auto mb-6 text-muted-foreground" />
                <p className="text-xl font-medium text-muted-foreground mb-2">
                  Корреляционная панель
                </p>
                <p className="text-sm text-muted-foreground max-w-md">
                  Здесь будет отображаться корреляция геологических разрезов 
                  между выбранными скважинами с каротажными кривыми
                </p>
              </div>

              {/* Simulated Well Tracks */}
              <div className="absolute bottom-4 left-4 flex gap-4">
                <div className="text-center">
                  <div className="w-12 h-40 bg-yellow-200 border-2 border-yellow-400 rounded-t-lg mb-1"></div>
                  <span className="text-xs font-medium">Скв. 301</span>
                </div>
                <div className="text-center">
                  <div className="w-12 h-40 bg-yellow-200 border-2 border-yellow-400 rounded-t-lg mb-1"></div>
                  <span className="text-xs font-medium">Скв. 302</span>
                </div>
                <div className="text-center">
                  <div className="w-12 h-40 bg-yellow-200 border-2 border-yellow-400 rounded-t-lg mb-1"></div>
                  <span className="text-xs font-medium">Скв. 304</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Коэффициент корреляции</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0.87</div>
            <p className="text-xs text-muted-foreground">высокая корреляция</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Количество пластов</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">продуктивных пластов</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Средняя мощность</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18.5 м</div>
            <p className="text-xs text-muted-foreground">по продуктивным пластам</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Покрытие области</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">85%</div>
            <p className="text-xs text-muted-foreground">площади месторождения</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}