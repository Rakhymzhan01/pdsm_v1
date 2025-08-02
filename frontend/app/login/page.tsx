"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { MapPin, User, Lock, AlertCircle } from "lucide-react"
import { apiClient } from "@/lib/api-client"

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")
    
    try {
      if (!username || !password) {
        setError('Пожалуйста, введите имя пользователя и пароль')
        return
      }

      // Call Flask API for authentication
      const response = await apiClient.login(username, password)
      
      if (response.error) {
        setError('Ошибка сервера: ' + response.error)
        return
      }

      if (response.data) {
        // Store authentication data
        localStorage.setItem('authToken', 'authenticated-' + Date.now())
        localStorage.setItem('userData', JSON.stringify({
          username: username,
          role: 'administrator',
          loginTime: new Date().toISOString()
        }))
        
        // Redirect to main dashboard
        window.location.href = '/'
      } else {
        setError('Неверное имя пользователя или пароль')
      }
    } catch (error) {
      console.error('Login error:', error)
      setError('Ошибка подключения к серверу. Проверьте настройки сети.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <MapPin className="h-6 w-6" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">Авторизация</CardTitle>
          <CardDescription>Войдите в систему анализа месторождения Каратюбе</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="username">Пользователь</Label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="username"
                  type="text"
                  placeholder="Введите имя пользователя"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="pl-10"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Пароль</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="Введите ваш пароль"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-orange-600 hover:bg-orange-700"
              disabled={isLoading}
            >
              {isLoading ? "Вход..." : "Войти"}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            © 2025 Аман Жумекешов
            <br />
            <span className="text-xs opacity-75">
              Для тестирования: username=&quot;test&quot;, password=&quot;test&quot;
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
