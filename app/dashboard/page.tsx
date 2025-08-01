"use client"

import { useEffect, useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Users,
  Building2,
  Wifi,
  CreditCard,
  Activity,
  AlertTriangle,
  CheckCircle,
  Router,
  Signal,
  Zap,
} from "lucide-react"

interface DashboardStats {
  totalUsers: number
  totalCompanies: number
  activeConnections: number
  totalCredits: number
  systemStatus: string
  networkHealth: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 156,
    totalCompanies: 12,
    activeConnections: 89,
    totalCredits: 25000,
    systemStatus: "online",
    networkHealth: 98,
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    console.log("[DASHBOARD] Página do dashboard carregada")

    const fetchStats = async () => {
      try {
        const response = await fetch("/api/dashboard/stats")
        if (response.ok) {
          const data = await response.json()
          setStats(data)
        }
      } catch (error) {
        console.error("Erro ao carregar estatísticas:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    // Atualizar a cada 30 segundos
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-green-500"
      case "warning":
        return "bg-yellow-500"
      case "error":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return <CheckCircle className="h-4 w-4" />
      case "warning":
        return <AlertTriangle className="h-4 w-4" />
      case "error":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">Visão geral do sistema MikroTik Manager</p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant={stats.systemStatus === "online" ? "default" : "destructive"}>
              {getStatusIcon(stats.systemStatus)}
              <span className="ml-1">
                {stats.systemStatus === "online" ? "Sistema Online" : "Sistema com Problemas"}
              </span>
            </Badge>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Usuários</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{loading ? "..." : stats.totalUsers}</div>
              <p className="text-xs text-muted-foreground">+12% em relação ao mês passado</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Empresas Ativas</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{loading ? "..." : stats.totalCompanies}</div>
              <p className="text-xs text-muted-foreground">+3 novas empresas este mês</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Conexões Ativas</CardTitle>
              <Wifi className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{loading ? "..." : stats.activeConnections}</div>
              <p className="text-xs text-muted-foreground">+8% desde ontem</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Créditos Totais</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R$ {loading ? "..." : stats.totalCredits.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">+15% em relação ao mês passado</p>
            </CardContent>
          </Card>
        </div>

        {/* System Status */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Router className="mr-2 h-5 w-5" />
                Status dos Roteadores
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Online</span>
                  <Badge variant="default">24</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Offline</span>
                  <Badge variant="destructive">2</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Manutenção</span>
                  <Badge variant="secondary">1</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Signal className="mr-2 h-5 w-5" />
                Saúde da Rede
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Latência Média</span>
                  <span className="text-sm font-medium">12ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Uptime</span>
                  <span className="text-sm font-medium">99.8%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Throughput</span>
                  <span className="text-sm font-medium">850 Mbps</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Zap className="mr-2 h-5 w-5" />
                Ações Rápidas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
                <Users className="mr-2 h-4 w-4" />
                Adicionar Usuário
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
                <Building2 className="mr-2 h-4 w-4" />
                Nova Empresa
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
                <Wifi className="mr-2 h-4 w-4" />
                Configurar Hotspot
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Atividade Recente</CardTitle>
            <CardDescription>Últimas ações realizadas no sistema</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Novo usuário cadastrado</p>
                  <p className="text-xs text-muted-foreground">João Silva - há 5 minutos</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Roteador conectado</p>
                  <p className="text-xs text-muted-foreground">192.168.1.1 - há 12 minutos</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Backup realizado</p>
                  <p className="text-xs text-muted-foreground">Sistema - há 1 hora</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
