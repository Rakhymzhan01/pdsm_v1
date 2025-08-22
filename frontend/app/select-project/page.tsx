"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { MapPin, Building2, Database } from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useAuth } from "@/lib/auth-context"
import { useRouter } from "next/navigation"

interface Project {
  id: number
  name: string
  description: string
}

export default function SelectProjectPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { user } = useAuth()
  const router = useRouter()

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const response = await apiClient.getProjects()
      if (response.data) {
        // Показываем только основные 3 проекта
        const mainProjects = response.data.filter((p: Project) => 
          p.name === "Karatobe" || p.name === "Airankol" || p.name === "Crystal Management"
        )
        setProjects(mainProjects)
      }
    } catch (error) {
      console.error("Error loading projects:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleProjectSelect = (projectName: string) => {
    // Сохраняем выбранный проект в localStorage
    localStorage.setItem('selectedProject', projectName)
    
    // Перенаправляем на соответствующую страницу проекта
    switch (projectName) {
      case "Karatobe":
        router.push("/")
        break
      case "Airankol":
        router.push("/airankol")
        break
      case "Crystal Management":
        router.push("/crystal-management")
        break
      default:
        router.push("/")
    }
  }

  const getProjectIcon = (projectName: string) => {
    switch (projectName) {
      case "Karatobe":
        return <MapPin className="h-8 w-8 text-blue-600" />
      case "Airankol":
        return <Building2 className="h-8 w-8 text-green-600" />
      case "Crystal Management":
        return <Database className="h-8 w-8 text-purple-600" />
      default:
        return <MapPin className="h-8 w-8 text-gray-600" />
    }
  }

  const getProjectColor = (projectName: string) => {
    switch (projectName) {
      case "Karatobe":
        return "border-blue-200 hover:border-blue-400 hover:bg-blue-50"
      case "Airankol":
        return "border-green-200 hover:border-green-400 hover:bg-green-50"
      case "Crystal Management":
        return "border-purple-200 hover:border-purple-400 hover:bg-purple-50"
      default:
        return "border-gray-200 hover:border-gray-400 hover:bg-gray-50"
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Загрузка проектов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Выберите проект
          </h1>
          <p className="text-gray-600">
            Добро пожаловать, {user?.username}! Выберите проект для работы
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {projects.map((project) => (
            <Card 
              key={project.id}
              className={`cursor-pointer transition-all duration-200 ${getProjectColor(project.name)}`}
              onClick={() => handleProjectSelect(project.name)}
            >
              <CardHeader className="text-center">
                <div className="flex justify-center mb-4">
                  {getProjectIcon(project.name)}
                </div>
                <CardTitle className="text-xl">{project.name}</CardTitle>
                <CardDescription className="text-sm">
                  {project.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  className="w-full bg-orange-600 hover:bg-orange-700"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleProjectSelect(project.name)
                  }}
                >
                  Открыть проект
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            У вас есть доступ ко всем проектам. Выберите проект для начала работы.
          </p>
        </div>
      </div>
    </div>
  )
}