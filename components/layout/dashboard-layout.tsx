"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import {
  LayoutDashboard,
  Users,
  Building2,
  Wifi,
  CreditCard,
  FileText,
  Settings,
  LogOut,
  Router,
  UserCheck,
} from "lucide-react"

interface User {
  id: string
  name: string
  email: string
  role: string
}

interface DashboardLayoutProps {
  children: React.ReactNode
}

const menuItems = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Usuários",
    url: "/users",
    icon: Users,
  },
  {
    title: "Empresas",
    url: "/companies",
    icon: Building2,
  },
  {
    title: "Perfis Hotspot",
    url: "/profiles",
    icon: Wifi,
  },
  {
    title: "Usuários Hotspot",
    url: "/hotspot-users",
    icon: UserCheck,
  },
  {
    title: "Créditos",
    url: "/credits",
    icon: CreditCard,
  },
  {
    title: "Relatórios",
    url: "/reports",
    icon: FileText,
  },
  {
    title: "Configurações",
    url: "/settings",
    icon: Settings,
  },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [user, setUser] = useState<User | null>(null)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // Verificar se há dados do usuário no localStorage
    const userData = localStorage.getItem("user")
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [])

  const handleLogout = () => {
    // Limpar dados de autenticação
    document.cookie = "auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;"
    localStorage.removeItem("user")

    // Redirecionar para login
    router.push("/auth/login")
  }

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <Sidebar>
          <SidebarHeader>
            <div className="flex items-center space-x-2 px-4 py-2">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Router className="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">MikroTik Manager</h2>
                <p className="text-xs text-muted-foreground">Sistema de Gestão</p>
              </div>
            </div>
          </SidebarHeader>

          <SidebarContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <a href={item.url} className="flex items-center space-x-2">
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>

          <SidebarFooter>
            <div className="p-4">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="w-full justify-start">
                    <Avatar className="h-8 w-8 mr-2">
                      <AvatarImage src="/placeholder-user.jpg" />
                      <AvatarFallback>{user?.name?.charAt(0) || "U"}</AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col items-start">
                      <span className="text-sm font-medium">{user?.name || "Usuário"}</span>
                      <span className="text-xs text-muted-foreground">{user?.role || "admin"}</span>
                    </div>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>Minha Conta</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Configurações</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Sair</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </SidebarFooter>
        </Sidebar>

        <div className="flex-1 flex flex-col">
          <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-14 items-center px-4">
              <SidebarTrigger />
              <div className="ml-auto flex items-center space-x-4">
                <span className="text-sm text-muted-foreground">Bem-vindo, {user?.name || "Usuário"}</span>
              </div>
            </div>
          </header>

          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  )
}
