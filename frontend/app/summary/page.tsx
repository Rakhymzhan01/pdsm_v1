import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CumulativeProductionMap } from "@/components/cumulative-production-map"
import { WellPerformanceHeatmap } from "@/components/well-performance-heatmap"
import { FieldProductionHistoryChart } from "@/components/field-production-history-chart"

export default function SummaryPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Сводка по месторождению</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">Каратюбе</Badge>
          <Badge variant="secondary">Обновлено: 10.07.2025</Badge>
        </div>
      </div>

      {/* Main Summary Charts Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Cumulative Production Map */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Карта накопленных отборов</CardTitle>
            <CardDescription>Пространственное распределение добычи по скважинам</CardDescription>
          </CardHeader>
          <CardContent>
            <CumulativeProductionMap />
          </CardContent>
        </Card>

        {/* Well Performance Heatmap */}
        <Card>
          <CardHeader>
            <CardTitle>Тепловая карта скважин</CardTitle>
            <CardDescription>Производительность скважин по эффективности</CardDescription>
          </CardHeader>
          <CardContent>
            <WellPerformanceHeatmap />
          </CardContent>
        </Card>
      </div>

      {/* Production History Chart */}
      <Card>
        <CardHeader>
          <CardTitle>История добычи по месторождению</CardTitle>
          <CardDescription>Временной ряд показателей добычи нефти и воды</CardDescription>
        </CardHeader>
        <CardContent>
          <FieldProductionHistoryChart />
        </CardContent>
      </Card>

      {/* Summary Statistics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Общая добыча нефти</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">428,113 тн</div>
            <p className="text-xs text-muted-foreground">с начала эксплуатации</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Нижняя Юра</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">392,960 тн</div>
            <p className="text-xs text-muted-foreground">91.8% от общей добычи</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Пермо-Триасс</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">33,608 тн</div>
            <p className="text-xs text-muted-foreground">7.8% от общей добычи</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Средний дебит</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12.5 тн/сут</div>
            <p className="text-xs text-muted-foreground">по действующим скважинам</p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Breakdown */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Распределение по пластам</CardTitle>
            <CardDescription>Вклад различных продуктивных горизонтов</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">Нижняя Юра (J1)</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="w-[92%] h-full bg-blue-500" />
                </div>
                <span className="text-sm font-medium">91.8%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Пермо-Триасс (P-T)</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="w-[8%] h-full bg-green-500" />
                </div>
                <span className="text-sm font-medium">7.8%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Прочие</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="w-[1%] h-full bg-gray-500" />
                </div>
                <span className="text-sm font-medium">0.4%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Статус скважин</CardTitle>
            <CardDescription>Текущее состояние скважинного фонда</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-green-600">Действующие</span>
              <span className="font-medium">57 скважин</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-yellow-600">В ремонте</span>
              <span className="font-medium">3 скважины</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-red-600">Остановленные</span>
              <span className="font-medium">4 скважины</span>
            </div>
            <div className="flex items-center justify-between border-t pt-2">
              <span className="text-sm font-medium">Всего пробурено</span>
              <span className="font-bold">64 скважины</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}