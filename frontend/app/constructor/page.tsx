import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Settings, 
  Layers, 
  PlusCircle,
  Edit3,
  Save,
  Upload,
  Download,
  Eye,
  EyeOff
} from "lucide-react"

export default function ConstructorPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Конструктор графиков</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">Инструменты визуализации</Badge>
          <Button variant="outline" size="sm">
            <Save className="h-4 w-4 mr-2" />
            Сохранить
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {/* Tools Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Панель инструментов</CardTitle>
            <CardDescription>Конструктор дашбордов</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Chart Types */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Типы графиков</h4>
              
              <div className="grid gap-2">
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Линейный график
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Гистограмма
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Круговая диаграмма
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Тепловая карта
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Таблица
                </Button>
              </div>
            </div>

            {/* Data Sources */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Источники данных</h4>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Добыча нефти</span>
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <Eye className="h-4 w-4 text-green-500" />
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Обводненность</span>
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <Eye className="h-4 w-4 text-green-500" />
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Пластовое давление</span>
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Газовый фактор</span>
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Template Actions */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Шаблоны</h4>
              
              <div className="grid gap-2">
                <Button variant="outline" size="sm">
                  <Upload className="h-4 w-4 mr-2" />
                  Загрузить
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Сохранить
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Constructor Canvas */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Область конструирования</CardTitle>
            <CardDescription>Перетаскивайте компоненты с панели инструментов</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[600px] border-2 border-dashed border-muted-foreground/25 rounded-lg flex items-center justify-center relative bg-muted/20">
              <div className="text-center">
                <Layers className="h-20 w-20 mx-auto mb-6 text-muted-foreground" />
                <p className="text-xl font-medium text-muted-foreground mb-2">
                  Область конструирования
                </p>
                <p className="text-sm text-muted-foreground max-w-md">
                  Перетащите элементы с панели слева для создания 
                  пользовательского дашборда
                </p>
              </div>

              {/* Grid overlay */}
              <div className="absolute inset-0 opacity-10">
                <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="1"/>
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#grid)" />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chart Properties Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Свойства выбранного элемента</CardTitle>
          <CardDescription>Настройки и параметры графиков</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <Edit3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Выберите элемент для редактирования</p>
            <p className="text-sm">Здесь будут отображаться настройки выбранного компонента</p>
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Компонентов на сцене</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">элементов</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Активные слои</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1</div>
            <p className="text-xs text-muted-foreground">слоев</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Последние изменения</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">-</div>
            <p className="text-xs text-muted-foreground">не сохранено</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Размер файла</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0 KB</div>
            <p className="text-xs text-muted-foreground">конфигурация</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}