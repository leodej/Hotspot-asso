"use client"

import type React from "react"

import { useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import {
  Menu,
  Home,
  Users,
  Building2,
  Wifi,
  CreditCard,
  BarChart3,
  Settings,
  LogOut,
  Router,
  UserCheck,
  Shield,
} from "lucide-react"
import Link from "next/link"

interface DashboardLayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Usuários do Sistema", href: "/users", icon: Users },
  { name: "Empresas", href: "/companies", icon: Building2 },
  { name: "Perfis Hotspot", href: "/profiles", icon: Wifi },
  { name: "Usuários Hotspot", href: "/hotspot-users", icon: UserCheck },
  { name: "Créditos", href: "/credits", icon: CreditCard },
  { name: "Relatórios", href: "/reports", icon: BarChart3 },
  { name: "Configurações", href: "/settings", icon: Settings },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  const handleLogout = () => {
    document.cookie = "auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;"
    router.push("/auth/login")
  }

  const Sidebar = ({ mobile = false }) => (
    <div className="flex h-full flex-col">
      <div className="flex h-16 shrink-0 items-center px-4">
        <div className="flex items-center space-x-2">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Router className="h-6 w-6 text-white" />
          </div>
          <span className="text-lg font-bold">MikroTik Manager</span>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-2 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                isActive ? "bg-blue-100 text-blue-900" : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
              onClick={() => mobile && setSidebarOpen(false)}
            >
              <item.icon
                className={`mr-3 h-5 w-5 flex-shrink-0 ${
                  isActive ? "text-blue-500" : "text-gray-400 group-hover:text-gray-500"
                }`}
              />
              {item.name}
            </Link>
          )
        })}
      </nav>

      <div className="flex-shrink-0 p-4">
        <Button variant="outline" className="w-full justify-start bg-transparent" onClick={handleLogout}>
          <LogOut className="mr-2 h-4 w-4" />
          Sair
        </Button>
      </div>
    </div>
  )

  return (
    <div className="h-screen flex">
      {/* Sidebar Desktop */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 border-r border-gray-200 bg-white">
          <Sidebar />
        </div>
      </div>

      {/* Mobile sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 w-64">
          <Sidebar mobile />
        </SheetContent>
      </Sheet>

      {/* Main content */}
      <div className="flex flex-col flex-1 md:pl-64">
        <div className="sticky top-0 z-10 flex-shrink-0 flex h-16 bg-white shadow">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden ml-4" onClick={() => setSidebarOpen(true)}>
                <Menu className="h-6 w-6" />
              </Button>
            </SheetTrigger>
          </Sheet>

          <div className="flex-1 px-4 flex justify-between items-center">
            <div className="flex-1" />
            <div className="ml-4 flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-green-500" />
                <span className="text-sm text-muted-foreground">Admin</span>
              </div>
            </div>
          </div>
        </div>

        <main className="flex-1 overflow-y-auto">
          <div className="py-6 px-4 sm:px-6 lg:px-8">{children}</div>
        </main>
      </div>
    </div>
  )
}
