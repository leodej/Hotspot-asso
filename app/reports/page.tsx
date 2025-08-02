"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  BarChart3,
  Download,
  Upload,
  Calendar,
  Users,
  Building2,
  TrendingUp,
  TrendingDown,
  FileText,
  Filter,
} from "lucide-react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

interface ReportData {
  daily: Array<{
    date: string
    totalUsers: number
    activeUsers: number
    totalTraffic: number
    downloadTraffic: number
    uploadTraffic: number
    avgSessionTime: number
  }>
  topUsers: Array<{
    username: string
    company: string
    totalTraffic: number
    sessionCount: number
    avgSessionTime: number
  }>
  companies: Array<{
    name: string
    activeUsers: number
    totalTraffic: number
    avgSpeed: number
  }>
  summary: {
    totalSessions: number
    totalTraffic: number
    avgSessionTime: number
    peakHour: string
    topCompany: string
  }
}

export default function ReportsPage() {
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
    endDate: new Date().toISOString().split("T")[0],
  })
  const [selectedCompany, setSelectedCompany] = useState("all")
  const [reportType, setReportType] = useState("daily")
  const [companies, setCompanies] = useState<Array<{ id: string; name: string }>>([])

  useEffect(() => {
    fetchReportData()
    fetchCompanies()
  }, [dateRange, selectedCompany, reportType])

  const fetchReportData = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        company: selectedCompany,
        type: reportType,
      })

      const response = await fetch(`/api/reports?${params}`)
      const data = await response.json()
      setReportData(data)
    } catch (error) {
      console.error("Erro ao carregar relatórios:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCompanies = async () => {
    try {
      const response = await fetch("/api/companies")
      const data = await response.json()
      setCompanies(data)
    } catch (error) {
      console.error("Erro ao carregar empresas:", error)
    }
  }

  const exportReport = async (format: "csv" | "json") => {
    try {
      const params = new URLSearchParams({
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        company: selectedCompany,
        type: reportType,
        format,
      })

      const response = await fetch(`/api/reports/export?${params}`)
      const blob = await response.blob()

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `relatorio-${reportType}-${dateRange.startDate}-${dateRange.endDate}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error("Erro ao exportar relatório:", error)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B"
    const k = 1024
    const sizes = ["B", "KB", "MB", "GB", "TB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}h ${mins}m`
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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Relatórios</h1>
            <p className="text-muted-foreground">Análise detalhada de uso e tráfego</p>
          </div>

          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => exportReport("csv")}>
              <Download className="mr-2 h-4 w-4" />
              Exportar CSV
            </Button>
            <Button variant="outline" onClick={() => exportReport("json")}>
              <FileText className="mr-2 h-4 w-4" />
              Exportar JSON
            </Button>
          </div>
        </div>

        {/* Filtros */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Filter className="h-5 w-5" />
              <span>Filtros</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startDate">Data Inicial</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={dateRange.startDate}
                  onChange={(e) => setDateRange((prev) => ({ ...prev, startDate: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="endDate">Data Final</Label>
                <Input
                  id="endDate"
                  type="date"
                  value={dateRange.endDate}
                  onChange={(e) => setDateRange((prev) => ({ ...prev, endDate: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="company">Empresa</Label>
                <Select value={selectedCompany} onValueChange={setSelectedCompany}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas as Empresas</SelectItem>
                    {companies.map((company) => (
                      <SelectItem key={company.id} value={company.id}>
                        {company.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="reportType">Tipo de Relatório</Label>
                <Select value={reportType} onValueChange={setReportType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Diário</SelectItem>
                    <SelectItem value="weekly">Semanal</SelectItem>
                    <SelectItem value="monthly">Mensal</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Resumo */}
        {reportData && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total de Sessões</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reportData.summary.totalSessions}</div>
                <p className="text-xs text-muted-foreground">No período selecionado</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tráfego Total</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatBytes(reportData.summary.totalTraffic)}</div>
                <p className="text-xs text-muted-foreground">Download + Upload</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tempo Médio</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatTime(reportData.summary.avgSessionTime)}</div>
                <p className="text-xs text-muted-foreground">Por sessão</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Horário de Pico</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reportData.summary.peakHour}</div>
                <p className="text-xs text-muted-foreground">Maior atividade</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Top Empresa</CardTitle>
                <Building2 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-lg font-bold">{reportData.summary.topCompany}</div>
                <p className="text-xs text-muted-foreground">Maior tráfego</p>
              </CardContent>
            </Card>
          </div>
        )}

        <Tabs defaultValue="usage" className="space-y-4">
          <TabsList>
            <TabsTrigger value="usage">Uso Diário</TabsTrigger>
            <TabsTrigger value="users">Top Usuários</TabsTrigger>
            <TabsTrigger value="companies">Por Empresa</TabsTrigger>
          </TabsList>

          <TabsContent value="usage" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Uso Diário</CardTitle>
                <CardDescription>Estatísticas de uso por dia</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Data</TableHead>
                      <TableHead>Usuários Únicos</TableHead>
                      <TableHead>Usuários Ativos</TableHead>
                      <TableHead>Tráfego Total</TableHead>
                      <TableHead>Download</TableHead>
                      <TableHead>Upload</TableHead>
                      <TableHead>Tempo Médio</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reportData?.daily.map((day, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{new Date(day.date).toLocaleDateString("pt-BR")}</TableCell>
                        <TableCell>{day.totalUsers}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <span>{day.activeUsers}</span>
                            {day.activeUsers > (reportData.daily[index - 1]?.activeUsers || 0) ? (
                              <TrendingUp className="h-4 w-4 text-green-500" />
                            ) : (
                              <TrendingDown className="h-4 w-4 text-red-500" />
                            )}
                          </div>
                        </TableCell>
                        <TableCell>{formatBytes(day.totalTraffic)}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-1">
                            <Download className="h-3 w-3 text-green-500" />
                            <span>{formatBytes(day.downloadTraffic)}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-1">
                            <Upload className="h-3 w-3 text-blue-500" />
                            <span>{formatBytes(day.uploadTraffic)}</span>
                          </div>
                        </TableCell>
                        <TableCell>{formatTime(day.avgSessionTime)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Top Usuários por Tráfego</CardTitle>
                <CardDescription>Usuários com maior consumo no período</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Posição</TableHead>
                      <TableHead>Usuário</TableHead>
                      <TableHead>Empresa</TableHead>
                      <TableHead>Tráfego Total</TableHead>
                      <TableHead>Sessões</TableHead>
                      <TableHead>Tempo Médio</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reportData?.topUsers.map((user, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-medium text-blue-600">{index + 1}</span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="font-medium">{user.username}</TableCell>
                        <TableCell>{user.company}</TableCell>
                        <TableCell>
                          <div className="font-medium">{formatBytes(user.totalTraffic)}</div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{user.sessionCount}</Badge>
                        </TableCell>
                        <TableCell>{formatTime(user.avgSessionTime)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="companies" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Relatório por Empresa</CardTitle>
                <CardDescription>Estatísticas agrupadas por empresa</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Empresa</TableHead>
                      <TableHead>Usuários Ativos</TableHead>
                      <TableHead>Tráfego Total</TableHead>
                      <TableHead>Velocidade Média</TableHead>
                      <TableHead>Performance</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reportData?.companies.map((company, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{company.name}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">{company.activeUsers}</Badge>
                        </TableCell>
                        <TableCell>{formatBytes(company.totalTraffic)}</TableCell>
                        <TableCell>{company.avgSpeed.toFixed(1)} Mbps</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            {company.avgSpeed > 10 ? (
                              <Badge variant="secondary">Boa</Badge>
                            ) : company.avgSpeed > 5 ? (
                              <Badge variant="outline">Regular</Badge>
                            ) : (
                              <Badge variant="destructive">Baixa</Badge>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
