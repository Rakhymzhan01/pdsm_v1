"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BarChart3, TrendingUp, MapPin, Activity, Database, AlertCircle } from "lucide-react"
import { useWells, useProductionData } from "@/hooks/use-api"
import { withAuth } from "@/lib/auth-context"

function HomePage() {
  const { data: wellsData, loading: wellsLoading, error: wellsError } = useWells()
  const { data: productionData, loading: productionLoading, error: productionError } = useProductionData()

  // Calculate statistics from real data
  const activeWells = wellsData?.length || 0
  const totalOilProduction = productionData?.reduce((sum: number, record: any) => {
    return sum + (parseFloat(record.Qo_ton) || 0)
  }, 0) || 0

  const averageWaterCut = productionData && productionData.length > 0 
    ? productionData.reduce((sum: number, record: any) => sum + (parseFloat(record.Obv_percent) || 0), 0) / productionData.length
    : 0
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Добро пожаловать!</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">Активы</Badge>
          <Badge variant="outline">Аккаунт</Badge>
        </div>
      </div>

      {/* Error display */}
      {(wellsError || productionError) && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">
                Ошибка загрузки данных: {wellsError || productionError}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Общий объем нефти</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {productionLoading ? (
              <div className="text-2xl font-bold animate-pulse">Loading...</div>
            ) : (
              <div className="text-2xl font-bold">
                {totalOilProduction.toLocaleString('ru-RU', { maximumFractionDigits: 0 })}
              </div>
            )}
            <p className="text-xs text-muted-foreground">тн за последний период</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего скважин</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {wellsLoading ? (
              <div className="text-2xl font-bold animate-pulse">Loading...</div>
            ) : (
              <div className="text-2xl font-bold">{activeWells}</div>
            )}
            <p className="text-xs text-muted-foreground">в базе данных</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Цена нефти Brent</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$68.50</div>
            <p className="text-xs text-muted-foreground">+2.1% за день</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Средняя обводненность</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {productionLoading ? (
              <div className="text-2xl font-bold animate-pulse">Loading...</div>
            ) : (
              <div className="text-2xl font-bold">
                {averageWaterCut.toFixed(1)}%
              </div>
            )}
            <p className="text-xs text-muted-foreground">по активным скважинам</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Карта текущих отборов на 10 июля 2025</CardTitle>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-[350px] bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <MapPin className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Интерактивная карта месторождения</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Здесь будет отображаться карта с расположением скважин
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Таблица сводных метрик по добыче</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-blue-600">Количество дней с начала эксплуатации</span>
                <span className="font-medium">1,087</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-blue-600">Общее количество скважин</span>
                <span className="font-medium">64</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-blue-600">Общий объем нефти (тн)</span>
                <span className="font-medium">428,113</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-blue-600">Общий объем нефти из Нижней Юры (тн)</span>
                <span className="font-medium">392,960</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-blue-600">Общий объем нефти из Пермо-Триасса (тн)</span>
                <span className="font-medium">33,608</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-red-600">Количество дней с начала года</span>
                <span className="font-medium">191</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-red-600">Общее количество действующих скважин</span>
                <span className="font-medium">57</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>История Добычи м. Каратюбе</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] bg-muted rounded-lg flex items-center justify-center">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">График истории добычи</p>
              <p className="text-sm text-muted-foreground mt-2">Временной ряд показателей добычи нефти</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Разделы</CardTitle>
            <CardDescription>Данный сайт предназначен для анализа данных месторождения Каратюбе.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Дом:</h4>
              <p className="text-sm text-muted-foreground">Текущая домашняя страница.</p>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Сводка:</h4>
              <p className="text-sm text-muted-foreground">
                Сводная информация по всему месторождению с тремя графиками:
              </p>
              <ul className="text-sm text-muted-foreground mt-1 ml-4 list-disc">
                <li>Карта Накопленных отборов</li>
                <li>Тепловая карта скважин</li>
                <li>История Добычи</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Анализ:</h4>
              <p className="text-sm text-muted-foreground">Информационная панель для анализа по скважинам.</p>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Корреляция:</h4>
              <p className="text-sm text-muted-foreground">Корреляция разрезов скважин.</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Нужна помощь?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Сейсмика:</h4>
              <p className="text-sm text-muted-foreground">Сейсмические профили по Inline / Xline.</p>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Карта:</h4>
              <p className="text-sm text-muted-foreground">
                Географическое положение месторождения с пробуренными скважинами.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Гант:</h4>
              <p className="text-sm text-muted-foreground">
                Диаграмма Ганта — это популярный тип столбчатых диаграмм для иллюстрации плана, графика работ по
                проекту.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-2">База:</h4>
              <p className="text-sm text-muted-foreground">Производственная база данных по:</p>
              <ul className="text-sm text-muted-foreground mt-1 ml-4 list-disc">
                <li>Добыче продукции</li>
                <li>Истории геолого-технических мероприятий</li>
                <li>Интервалов перфораций</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default withAuth(HomePage)
