import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Database, 
  Download, 
  Upload,
  Search,
  Filter,
  FileText,
  BarChart3,
  Calendar
} from "lucide-react"

export default function DatabasePage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">База данных</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">Производственные данные</Badge>
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Загрузить данные
          </Button>
        </div>
      </div>

      {/* Data Categories */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Добыча продукции
            </CardTitle>
            <CardDescription>Ежедневные данные по дебитам скважин</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Всего записей:</span>
                <span className="font-medium">15,847</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Последнее обновление:</span>
                <span className="font-medium">10.07.2025</span>
              </div>
              <Button variant="outline" size="sm" className="w-full">
                <Search className="h-4 w-4 mr-2" />
                Просмотр данных
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              История ГТМ
            </CardTitle>
            <CardDescription>Геолого-технические мероприятия</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Всего мероприятий:</span>
                <span className="font-medium">234</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">За текущий год:</span>
                <span className="font-medium">18</span>
              </div>
              <Button variant="outline" size="sm" className="w-full">
                <Search className="h-4 w-4 mr-2" />
                Просмотр истории
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Интервалы перфораций
            </CardTitle>
            <CardDescription>Данные по перфорации скважин</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Всего интервалов:</span>
                <span className="font-medium">1,456</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Активных:</span>
                <span className="font-medium">892</span>
              </div>
              <Button variant="outline" size="sm" className="w-full">
                <Search className="h-4 w-4 mr-2" />
                Просмотр данных
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Data Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Последние обновления базы данных</CardTitle>
          <CardDescription>Недавно загруженные или обновленные данные</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { date: "10.07.2025", type: "Добыча", description: "Загружены данные по добыче за июнь 2025", records: "186 записей" },
              { date: "08.07.2025", type: "ГТМ", description: "Обновление данных по ГРП скважины 345", records: "1 мероприятие" },
              { date: "05.07.2025", type: "Перфорации", description: "Новые интервалы перфорации скважин 362-363", records: "12 интервалов" },
              { date: "03.07.2025", type: "Добыча", description: "Корректировка данных по скважине 301", records: "30 записей" },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline" className="text-xs">{item.type}</Badge>
                    <span className="text-sm text-muted-foreground">{item.date}</span>
                  </div>
                  <p className="text-sm font-medium">{item.description}</p>
                  <p className="text-xs text-muted-foreground">{item.records}</p>
                </div>
                <Button variant="ghost" size="sm">
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Data Export/Import Tools */}
      <Card>
        <CardHeader>
          <CardTitle>Инструменты работы с данными</CardTitle>
          <CardDescription>Импорт, экспорт и управление базой данных</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Button variant="outline" className="h-20 flex-col">
              <Download className="h-6 w-6 mb-2" />
              <span className="text-sm">Экспорт данных</span>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col">
              <Upload className="h-6 w-6 mb-2" />
              <span className="text-sm">Импорт данных</span>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col">
              <Filter className="h-6 w-6 mb-2" />
              <span className="text-sm">Фильтры</span>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col">
              <Database className="h-6 w-6 mb-2" />
              <span className="text-sm">Резервное копирование</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}