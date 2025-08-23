import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { WellFlowRateAnalysis } from "@/components/well-flow-rate-analysis"
import { 
  Activity, 
  TrendingUp, 
  Droplets, 
  Gauge, 
  Zap,
  Target,
  Settings
} from "lucide-react"

export default function AnalysisPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Анализ скважин</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">Информационная панель</Badge>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Настройки
          </Button>
        </div>
      </div>

      {/* Well Selection and Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Выбрано скважин</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">15</div>
            <p className="text-xs text-muted-foreground">для анализа</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Средний дебит</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">14.2</div>
            <p className="text-xs text-muted-foreground">тн/сут</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Обводненность</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">23%</div>
            <p className="text-xs text-muted-foreground">средняя</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">КИН</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0.31</div>
            <p className="text-xs text-muted-foreground">коэффициент извлечения</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Analysis Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Production Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Анализ добычи</CardTitle>
            <CardDescription>Динамика дебитов по скважинам</CardDescription>
          </CardHeader>
          <CardContent>
            <WellFlowRateAnalysis />
          </CardContent>
        </Card>

        {/* Decline Curve Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Кривые падения</CardTitle>
            <CardDescription>Прогноз добычи по характеристикам вытеснения</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Анализ падения дебита</p>
                <p className="text-xs text-muted-foreground mt-2">
                  Экспоненциальная и гиперболическая модели
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Well Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Показатели эффективности скважин</CardTitle>
          <CardDescription>Детальный анализ технологических параметров</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Activity className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="font-medium">Коэффициент продуктивности</p>
                  <p className="text-sm text-muted-foreground">3.2 м³/(сут·МПа)</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Droplets className="h-5 w-5 text-cyan-500" />
                <div>
                  <p className="font-medium">Скин-фактор</p>
                  <p className="text-sm text-muted-foreground">+2.1</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Gauge className="h-5 w-5 text-green-500" />
                <div>
                  <p className="font-medium">Пластовое давление</p>
                  <p className="text-sm text-muted-foreground">18.5 МПа</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Zap className="h-5 w-5 text-yellow-500" />
                <div>
                  <p className="font-medium">Газовый фактор</p>
                  <p className="text-sm text-muted-foreground">45 м³/м³</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Target className="h-5 w-5 text-red-500" />
                <div>
                  <p className="font-medium">Проницаемость</p>
                  <p className="text-sm text-muted-foreground">125 мД</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Activity className="h-5 w-5 text-purple-500" />
                <div>
                  <p className="font-medium">Пористость</p>
                  <p className="text-sm text-muted-foreground">16.8%</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Well List Table */}
      <Card>
        <CardHeader>
          <CardTitle>Список скважин для анализа</CardTitle>
          <CardDescription>Выберите скважины для детального изучения</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="grid grid-cols-6 gap-4 py-2 font-medium text-sm border-b">
              <span>Скважина</span>
              <span>Дебит, тн/сут</span>
              <span>Обводненность, %</span>
              <span>Статус</span>
              <span>Горизонт</span>
              <span>Действия</span>
            </div>
            
            {[
              { well: "301", rate: "12.5", water: "15", status: "Действует", horizon: "J1", active: true },
              { well: "302", rate: "18.3", water: "28", status: "Действует", horizon: "J1", active: true },
              { well: "303", rate: "9.7", water: "45", status: "Действует", horizon: "P-T", active: false },
              { well: "304", rate: "21.2", water: "12", status: "Действует", horizon: "J1", active: true },
              { well: "305", rate: "0.0", water: "0", status: "В ремонте", horizon: "J1", active: false },
            ].map((well, idx) => (
              <div key={idx} className={`grid grid-cols-6 gap-4 py-3 text-sm border-b hover:bg-muted/50 ${well.active ? 'bg-blue-50/50' : ''}`}>
                <span className="font-medium">{well.well}</span>
                <span>{well.rate}</span>
                <span>{well.water}</span>
                <span>
                  <Badge 
                    variant={well.status === "Действует" ? "default" : "secondary"}
                    className="text-xs"
                  >
                    {well.status}
                  </Badge>
                </span>
                <span>{well.horizon}</span>
                <Button variant="ghost" size="sm" className="h-8 px-2">
                  Выбрать
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}