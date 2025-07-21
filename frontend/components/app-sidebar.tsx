import type * as React from "react"
import {
  Home,
  Map,
  BarChart3,
  Settings,
  Database,
  FileText,
  Calendar,
  Activity,
  MapPin,
  TrendingUp,
  LogOut,
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"

const navigationItems = [
  {
    title: "Главное",
    items: [
      { title: "Дом", url: "/", icon: Home },
      { title: "Сводка", url: "/summary", icon: BarChart3 },
    ],
  },
  {
    title: "Анализ",
    items: [
      { title: "Анализ", url: "/analysis", icon: Activity },
      { title: "Конструктор", url: "/constructor", icon: Settings },
      { title: "Корреляция", url: "/correlation", icon: TrendingUp },
      { title: "Сейсмика", url: "/seismic", icon: Activity },
    ],
  },
  {
    title: "Планирование",
    items: [
      { title: "Подсчетный план", url: "/calculation-plan", icon: FileText },
      { title: "Гант", url: "/gantt", icon: Calendar },
    ],
  },
  {
    title: "Данные",
    items: [
      { title: "База", url: "/database", icon: Database },
      { title: "Карта", url: "/map", icon: Map },
    ],
  },
]

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <div className="flex items-center gap-2 px-4 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <MapPin className="h-4 w-4" />
          </div>
          <div className="grid flex-1 text-left text-sm leading-tight">
            <span className="truncate font-semibold">Каратюбе</span>
            <span className="truncate text-xs text-muted-foreground">Нефтегазовое месторождение</span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        {navigationItems.map((group) => (
          <SidebarGroup key={group.title}>
            <SidebarGroupLabel>{group.title}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {group.items.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild>
                      <a href={item.url}>
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <div className="flex items-center gap-2 px-2 py-1.5">
              <Avatar className="h-8 w-8">
                <AvatarFallback>АЖ</AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">Аман Жумекешов</span>
                <span className="truncate text-xs text-muted-foreground">Администратор</span>
              </div>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  )
}
