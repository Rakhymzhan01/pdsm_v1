import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Calendar } from "lucide-react"

const ganttData = [
  {
    task: "Получение экологического разрешения на воздействие по проекту ГПП на строительства 44 скважин",
    type: "environmental",
    start: "2022-07",
    end: "2022-11",
    progress: 100,
  },
  {
    task: "Получения экологического разрешения на воздействие по проекту ГПП на строительства 8 скважин",
    type: "environmental",
    start: "2022-09",
    end: "2022-12",
    progress: 100,
  },
  {
    task: "Строительство эксплуатационных скважин",
    type: "construction",
    start: "2022-11",
    end: "2024-06",
    progress: 85,
  },
  {
    task: "ПИР нефтепровод 75 км ННТ НМ",
    type: "design",
    start: "2023-01",
    end: "2024-12",
    progress: 70,
  },
  {
    task: "СМР нефтепровод 75 км ННТ НМ",
    type: "construction",
    start: "2023-07",
    end: "2024-12",
    progress: 60,
  },
]

export default function GanttPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">План график планируемых работ по месторождению</h2>
        <Calendar className="h-8 w-8 text-muted-foreground" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Диаграмма Ганта - Планирование работ</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-12 gap-2 text-xs font-medium text-muted-foreground border-b pb-2">
              <div className="col-span-6">Задача</div>
              <div className="col-span-1">Тип</div>
              <div className="col-span-5">Временная шкала (2022-2024)</div>
            </div>

            {ganttData.map((item, index) => (
              <div key={index} className="grid grid-cols-12 gap-2 items-center py-2 border-b">
                <div className="col-span-6 text-sm">{item.task}</div>
                <div className="col-span-1">
                  <Badge
                    variant={
                      item.type === "environmental"
                        ? "default"
                        : item.type === "construction"
                          ? "destructive"
                          : "secondary"
                    }
                    className="text-xs"
                  >
                    {item.type === "environmental" ? "Эко" : item.type === "construction" ? "Стр" : "Пр"}
                  </Badge>
                </div>
                <div className="col-span-5">
                  <div className="relative h-6 bg-muted rounded">
                    <div
                      className={`absolute left-0 top-0 h-full rounded ${
                        item.type === "environmental"
                          ? "bg-blue-500"
                          : item.type === "construction"
                            ? "bg-red-500"
                            : "bg-green-500"
                      }`}
                      style={{ width: `${item.progress}%` }}
                    />
                    <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
                      {item.progress}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span className="text-sm">Экологические разрешения</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span className="text-sm">Строительство</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span className="text-sm">Проектирование</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
