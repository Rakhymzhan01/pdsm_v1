import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  FileText, 
  Calculator, 
  BarChart3,
  TrendingUp,
  Download,
  Edit,
  Eye,
  MapPin
} from "lucide-react"

export default function CalculationPlanPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Подсчетный план</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">Оценка запасов</Badge>
          <Button variant="outline" size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Редактировать
          </Button>
        </div>
      </div>

      {/* Reserve Categories */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-green-600" />
              Категория A
            </CardTitle>
            <CardDescription>Доказанные запасы</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="text-3xl font-bold text-green-600">2,450</div>
              <p className="text-sm text-muted-foreground">тыс. тонн нефти</p>
              <div className="flex justify-between text-sm">
                <span>Нижняя Юра:</span>
                <span className="font-medium">2,180</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Пермо-Триасс:</span>
                <span className="font-medium">270</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-yellow-600" />
              Категория B
            </CardTitle>
            <CardDescription>Вероятные запасы</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="text-3xl font-bold text-yellow-600">890</div>
              <p className="text-sm text-muted-foreground">тыс. тонн нефти</p>
              <div className="flex justify-between text-sm">
                <span>Нижняя Юра:</span>
                <span className="font-medium">730</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Пермо-Триасс:</span>
                <span className="font-medium">160</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5 text-blue-600" />
              Категория C
            </CardTitle>
            <CardDescription>Возможные запасы</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="text-3xl font-bold text-blue-600">1,235</div>
              <p className="text-sm text-muted-foreground">тыс. тонн нефти</p>
              <div className="flex justify-between text-sm">
                <span>Нижняя Юра:</span>
                <span className="font-medium">980</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Пермо-Триасс:</span>
                <span className="font-medium">255</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Reserve Calculation Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Параметры подсчета запасов</CardTitle>
          <CardDescription>Основные параметры для оценки ресурсов</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <h4 className="font-medium">Нижняя Юра (J1)</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Площадь нефтеносности:</span>
                  <span className="font-medium">18.2 км²</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Средняя эфф. мощность:</span>
                  <span className="font-medium">14.5 м</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Пористость:</span>
                  <span className="font-medium">16.8%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Нефтенасыщенность:</span>
                  <span className="font-medium">0.72</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">КИН:</span>
                  <span className="font-medium">0.31</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Плотность нефти:</span>
                  <span className="font-medium">875 кг/м³</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">Пермо-Триасс (P-T)</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Площадь нефтеносности:</span>
                  <span className="font-medium">8.9 км²</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Средняя эфф. мощность:</span>
                  <span className="font-medium">8.3 м</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Пористость:</span>
                  <span className="font-medium">12.5%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Нефтенасыщенность:</span>
                  <span className="font-medium">0.68</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">КИН:</span>
                  <span className="font-medium">0.28</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Плотность нефти:</span>
                  <span className="font-medium">882 кг/м³</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reserve Distribution Map */}
      <Card>
        <CardHeader>
          <CardTitle>Карта распределения запасов</CardTitle>
          <CardDescription>Пространственное распределение запасов по категориям</CardDescription>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Eye className="h-4 w-4 mr-2" />
              Полный экран
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Экспорт
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] bg-muted rounded-lg flex items-center justify-center">
            <div className="text-center">
              <MapPin className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium text-muted-foreground">Карта распределения запасов</p>
              <p className="text-sm text-muted-foreground mt-2">
                Цветовое кодирование по категориям запасов A, B, C
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Общая статистика</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center pb-2 border-b">
              <span className="font-medium">Общие запасы (A+B+C):</span>
              <span className="text-lg font-bold">4,575 тыс. т</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Нижняя Юра:</span>
              <span className="font-medium">3,890 тыс. т (85%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Пермо-Триасс:</span>
              <span className="font-medium">685 тыс. т (15%)</span>
            </div>
            <div className="flex justify-between pt-2 border-t">
              <span className="text-sm font-medium">Доказанные запасы (A):</span>
              <span className="font-bold">54%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Прогноз разработки</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm">Планируемый КИН:</span>
              <span className="font-medium">30.5%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Извлекаемые запасы:</span>
              <span className="font-medium">1,395 тыс. т</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Продолжительность:</span>
              <span className="font-medium">25 лет</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Макс. годовая добыча:</span>
              <span className="font-medium">95 тыс. т/год</span>
            </div>
            <div className="flex justify-between pt-2 border-t">
              <span className="text-sm font-medium">Остаточные запасы:</span>
              <span className="font-bold">3,180 тыс. т</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Export Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Экспорт отчетов</CardTitle>
          <CardDescription>Генерация отчетов по подсчету запасов</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button variant="outline" className="h-20 flex-col">
              <FileText className="h-6 w-6 mb-2" />
              <span className="text-sm">Отчет по запасам</span>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col">
              <Calculator className="h-6 w-6 mb-2" />
              <span className="text-sm">Параметры подсчета</span>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col">
              <Download className="h-6 w-6 mb-2" />
              <span className="text-sm">Полный отчет</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}