"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, XCircle, Clock, User } from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useAuth, withAuth } from "@/lib/auth-context"

interface PendingUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  project?: {
    id: number
    name: string
  }
  created_at: string
  status: string
}

function AdminUsersPage() {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const { user } = useAuth()

  useEffect(() => {
    if (user?.role === 'master') {
      loadPendingUsers()
    }
  }, [user])

  const loadPendingUsers = async () => {
    setIsLoading(true)
    try {
      const response = await apiClient.getPendingUsers()
      if (response.data) {
        setPendingUsers(response.data as PendingUser[])
      } else if (response.error) {
        setError(response.error)
      }
    } catch (error) {
      setError('Ошибка загрузки пользователей')
      console.error('Error loading pending users:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUserAction = async (userId: number, action: 'approve' | 'reject') => {
    try {
      const response = await apiClient.approveUser(userId, action)
      if (response.data) {
        // Refresh the list
        loadPendingUsers()
      } else if (response.error) {
        setError(response.error)
      }
    } catch (error) {
      setError(`Ошибка при ${action === 'approve' ? 'одобрении' : 'отклонении'} пользователя`)
      console.error('Error approving user:', error)
    }
  }

  if (user?.role !== 'master') {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <XCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Доступ запрещен</h3>
              <p className="text-gray-600">Эта страница доступна только для мастер-пользователей</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление пользователями</h1>
        <p className="text-gray-600 mt-2">Одобрение заявок на регистрацию</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
          {error}
        </div>
      )}

      <div className="mb-4">
        <Button onClick={loadPendingUsers} disabled={isLoading}>
          {isLoading ? "Загрузка..." : "Обновить"}
        </Button>
      </div>

      {pendingUsers.length === 0 && !isLoading && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Нет ожидающих заявок</h3>
              <p className="text-gray-600">Все заявки на регистрацию обработаны</p>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {pendingUsers.map((user) => (
          <Card key={user.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
                    <User className="h-5 w-5 text-gray-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">
                      {user.first_name} {user.last_name}
                    </CardTitle>
                    <p className="text-sm text-gray-600">@{user.username}</p>
                  </div>
                </div>
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Ожидает
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 mb-4">
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Проект:</strong> {user.project?.name || 'Не указан'}</p>
                <p><strong>Дата заявки:</strong> {new Date(user.created_at).toLocaleDateString('ru-RU')}</p>
              </div>
              <div className="flex space-x-2">
                <Button
                  onClick={() => handleUserAction(user.id, 'approve')}
                  className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="h-4 w-4" />
                  Одобрить
                </Button>
                <Button
                  onClick={() => handleUserAction(user.id, 'reject')}
                  variant="outline"
                  className="flex items-center gap-2 text-red-600 border-red-200 hover:bg-red-50"
                >
                  <XCircle className="h-4 w-4" />
                  Отклонить
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default withAuth(AdminUsersPage)