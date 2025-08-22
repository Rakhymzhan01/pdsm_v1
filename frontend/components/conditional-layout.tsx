"use client"

import type React from "react"
import { usePathname } from "next/navigation"
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { useAuth } from "@/lib/auth-context"

interface ConditionalLayoutProps {
  children: React.ReactNode
}

export function ConditionalLayout({ children }: ConditionalLayoutProps) {
  const pathname = usePathname()
  const { isAuthenticated, isLoading } = useAuth()
  
  // Pages where sidebar should not be shown
  const authPages = ['/login', '/register']
  const shouldHideSidebar = authPages.includes(pathname) || !isAuthenticated
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Загрузка...</p>
        </div>
      </div>
    )
  }

  if (shouldHideSidebar) {
    // Render without sidebar for auth pages or unauthenticated users
    return (
      <main className="min-h-screen">
        {children}
      </main>
    )
  }

  // Render with sidebar for authenticated users
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}