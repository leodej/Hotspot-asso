"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Users, Building2, Activity, Download, Upload, Clock, Wifi, AlertTriangle, CheckCircle } from "lucide-react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

interface DashboardStats {
  totalUsers: number
  activeUsers: number
  totalCompanies: number
  activeCompanies: number
  totalTraffic: {
    download: string
    upload: string
  }
  topUsers: Array<{
    username: string
    company: string
    traffic: string
    status: "online" | "offline"
  }>
  systemHealth: {
    cpu: number
    memory: number
    disk: number
    uptime: string
  }
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Atualiza a cada 30s
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch("/api/dashboard/stats")
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error("Erro ao carregar dados do dashboard:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Visão geral do sistema MikroTik Manager</p>
        </div>

        {/* Cards de Estatísticas */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Usuários Ativos</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.activeUsers || 0}</div>
              <p className="text-xs text-muted-foreground">de {stats?.totalUsers || 0} usuários totais</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Empresas Ativas</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.activeCompanies || 0}</div>
              <p className="text-xs text-muted-foreground">de {stats?.totalCompanies || 0} empresas totais</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Download Total</CardTitle>
              <Download className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totalTraffic.download || "0 GB"}</div>
              <p className="text-xs text-muted-foreground">Tráfego de download hoje</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Upload Total</CardTitle>
              <Upload className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totalTraffic.upload || "0 GB"}</div>
              <p className="text-xs text-muted-foreground">Tráfego de upload hoje</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Visão Geral</TabsTrigger>
            <TabsTrigger value="users">Top Usuários</TabsTrigger>
            <TabsTrigger value="system">Sistema</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Atividade em Tempo Real</CardTitle>
                  <CardDescription>Monitoramento de conexões ativas</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Wifi className="h-4 w-4 text-green-500" />
                        <span className="text-sm">Conexões Ativas</span>
                      </div>
                      <Badge variant="secondary">{stats?.activeUsers || 0}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Activity className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">Taxa de Transferência</span>
                      </div>
                      <Badge variant="outline">125 Mbps</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-orange-500" />
                        <span className="text-sm">Tempo Médio de Sessão</span>
                      </div>
                      <Badge variant="outline">2h 15m</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Status das Empresas</CardTitle>
                  <CardDescription>Conectividade com roteadores MikroTik</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Empresa Alpha</span>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <Badge variant="secondary">Online</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Empresa Beta</span>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <Badge variant="secondary">Online</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Empresa Gamma</span>
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                        <Badge variant="destructive">Offline</Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Top Usuários por Tráfego</CardTitle>
                <CardDescription>Usuários com maior consumo de dados hoje</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {stats?.topUsers?.map((user, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-blue-600">{index + 1}</span>
                        </div>
                        <div>
                          <p className="text-sm font-medium">{user.username}</p>
                          <p className="text-xs text-muted-foreground">{user.company}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={user.status === "online" ? "secondary" : "outline"}>
                          {user.status === "online" ? "Online" : "Offline"}
                        </Badge>
                        <span className="text-sm font-medium">{user.traffic}</span>
                      </div>
                    </div>
                  )) || <p className="text-center text-muted-foreground py-4">Nenhum dado disponível</p>}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Saúde do Sistema</CardTitle>
                <CardDescription>Monitoramento de recursos do servidor</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">CPU</span>
                      <span className="text-sm text-muted-foreground">{stats?.systemHealth.cpu || 0}%</span>
                    </div>
                    <Progress value={stats?.systemHealth.cpu || 0} className="h-2" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Memória</span>
                      <span className="text-sm text-muted-foreground">{stats?.systemHealth.memory || 0}%</span>
                    </div>
                    <Progress value={stats?.systemHealth.memory || 0} className="h-2" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Disco</span>
                      <span className="text-sm text-muted-foreground">{stats?.systemHealth.disk || 0}%</span>
                    </div>
                    <Progress value={stats?.systemHealth.disk || 0} className="h-2" />
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t">
                    <span className="text-sm font-medium">Uptime</span>
                    <span className="text-sm text-muted-foreground">{stats?.systemHealth.uptime || "0d 0h 0m"}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
