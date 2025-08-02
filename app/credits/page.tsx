"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import {
  Plus,
  Edit,
  Trash2,
  CreditCard,
  Clock,
  Database,
  Infinity,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
} from "lucide-react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

interface UserCredit {
  id: string
  hotspotUserId: string
  hotspotUsername: string
  companyName: string
  creditType: "data" | "time" | "unlimited" | "accumulative"
  initialAmount: number
  currentAmount: number
  unit: "bytes" | "minutes" | "days"
  validFrom: string
  validUntil?: string
  autoReset: boolean
  resetPeriod?: "daily" | "weekly" | "monthly"
  accumulative: boolean
  createdAt: string
  usagePercentage: number
  isExpired: boolean
  isLowCredit: boolean
}

export default function CreditsPage() {
  const [credits, setCredits] = useState<UserCredit[]>([])
  const [hotspotUsers, setHotspotUsers] = useState<Array<{ id: string; username: string; companyName: string }>>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingCredit, setEditingCredit] = useState<UserCredit | null>(null)
  const [formData, setFormData] = useState({
    hotspotUserId: "",
    creditType: "data" as const,
    initialAmount: 1000,
    unit: "bytes" as const,
    validFrom: new Date().toISOString().split("T")[0],
    validUntil: "",
    autoReset: false,
    resetPeriod: "daily" as const,
    accumulative: false,
  })

  const [selectedCompany, setSelectedCompany] = useState<string>("all")
  const [selectedMonth, setSelectedMonth] = useState<string>("all")

  useEffect(() => {
    fetchCredits()
    fetchHotspotUsers()
  }, [])

  const fetchCredits = async () => {
    try {
      const response = await fetch("/api/credits")
      const data = await response.json()
      setCredits(data)
    } catch (error) {
      console.error("Erro ao carregar créditos:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchHotspotUsers = async () => {
    try {
      const response = await fetch("/api/hotspot-users")
      const data = await response.json()
      setHotspotUsers(
        data.map((u: any) => ({
          id: u.id,
          username: u.username,
          companyName: u.companyName,
        })),
      )
    } catch (error) {
      console.error("Erro ao carregar usuários hotspot:", error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const url = editingCredit ? `/api/credits/${editingCredit.id}` : "/api/credits"
      const method = editingCredit ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await fetchCredits()
        setDialogOpen(false)
        resetForm()
      }
    } catch (error) {
      console.error("Erro ao salvar crédito:", error)
    }
  }

  const handleEdit = (credit: UserCredit) => {
    setEditingCredit(credit)
    setFormData({
      hotspotUserId: credit.hotspotUserId,
      creditType: credit.creditType,
      initialAmount: credit.initialAmount,
      unit: credit.unit,
      validFrom: credit.validFrom.split("T")[0],
      validUntil: credit.validUntil ? credit.validUntil.split("T")[0] : "",
      autoReset: credit.autoReset,
      resetPeriod: credit.resetPeriod || "daily",
      accumulative: credit.accumulative,
    })
    setDialogOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm("Tem certeza que deseja excluir este crédito?")) {
      try {
        await fetch(`/api/credits/${id}`, { method: "DELETE" })
        await fetchCredits()
      } catch (error) {
        console.error("Erro ao excluir crédito:", error)
      }
    }
  }

  const resetCredit = async (id: string) => {
    try {
      await fetch(`/api/credits/${id}/reset`, {
        method: "POST",
      })
      await fetchCredits()
    } catch (error) {
      console.error("Erro ao resetar crédito:", error)
    }
  }

  const resetForm = () => {
    setEditingCredit(null)
    setFormData({
      hotspotUserId: "",
      creditType: "data",
      initialAmount: 1000,
      unit: "bytes",
      validFrom: new Date().toISOString().split("T")[0],
      validUntil: "",
      autoReset: false,
      resetPeriod: "daily",
      accumulative: false,
    })
  }

  const formatAmount = (amount: number, unit: string, creditType: string) => {
    if (creditType === "unlimited") return "Ilimitado"

    switch (unit) {
      case "bytes":
        if (amount >= 1024 * 1024 * 1024) {
          return `${(amount / (1024 * 1024 * 1024)).toFixed(2)} GB`
        } else if (amount >= 1024 * 1024) {
          return `${(amount / (1024 * 1024)).toFixed(2)} MB`
        } else if (amount >= 1024) {
          return `${(amount / 1024).toFixed(2)} KB`
        }
        return `${amount} B`
      case "minutes":
        if (amount >= 1440) {
          return `${Math.floor(amount / 1440)}d ${Math.floor((amount % 1440) / 60)}h ${amount % 60}m`
        } else if (amount >= 60) {
          return `${Math.floor(amount / 60)}h ${amount % 60}m`
        }
        return `${amount}m`
      case "days":
        return `${amount} dias`
      default:
        return amount.toString()
    }
  }

  const getCreditTypeIcon = (type: string) => {
    switch (type) {
      case "data":
        return <Database className="h-4 w-4" />
      case "time":
        return <Clock className="h-4 w-4" />
      case "unlimited":
        return <Infinity className="h-4 w-4" />
      case "accumulative":
        return <TrendingUp className="h-4 w-4" />
      default:
        return <CreditCard className="h-4 w-4" />
    }
  }

  const getCreditTypeBadge = (type: string) => {
    const variants = {
      data: "default",
      time: "secondary",
      unlimited: "outline",
      accumulative: "destructive",
    } as const
    return <Badge variant={variants[type as keyof typeof variants]}>{type.toUpperCase()}</Badge>
  }

  const getUnitOptions = () => {
    switch (formData.creditType) {
      case "data":
        return [{ value: "bytes", label: "Bytes" }]
      case "time":
        return [{ value: "minutes", label: "Minutos" }]
      case "unlimited":
        return [{ value: "days", label: "Dias" }]
      case "accumulative":
        return [
          { value: "bytes", label: "Bytes" },
          { value: "minutes", label: "Minutos" },
        ]
      default:
        return []
    }
  }

  const getUniqueCompanies = () => {
    const companies = [...new Set(credits.map((credit) => credit.companyName))]
    return companies.sort()
  }

  const getAvailableMonths = () => {
    const months = [
      ...new Set(
        credits.map((credit) => {
          const date = new Date(credit.createdAt)
          return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`
        }),
      ),
    ]
    return months.sort().reverse()
  }

  const getFilteredCredits = () => {
    return credits.filter((credit) => {
      const companyMatch = selectedCompany === "all" || credit.companyName === selectedCompany

      const creditDate = new Date(credit.createdAt)
      const creditMonth = `${creditDate.getFullYear()}-${String(creditDate.getMonth() + 1).padStart(2, "0")}`
      const monthMatch = selectedMonth === "all" || creditMonth === selectedMonth

      return companyMatch && monthMatch
    })
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

  const filteredCredits = getFilteredCredits()

  return (
    <DashboardLayout>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Sistema de Créditos</h1>
            <p className="text-muted-foreground">Gerencie créditos de dados, tempo e acesso dos usuários</p>
          </div>

          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <Plus className="mr-2 h-4 w-4" />
                Novo Crédito
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{editingCredit ? "Editar Crédito" : "Novo Crédito"}</DialogTitle>
                <DialogDescription>Configure os créditos para o usuário hotspot</DialogDescription>
              </DialogHeader>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="hotspotUserId">Usuário Hotspot</Label>
                    <Select
                      value={formData.hotspotUserId}
                      onValueChange={(value) => setFormData((prev) => ({ ...prev, hotspotUserId: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione um usuário" />
                      </SelectTrigger>
                      <SelectContent>
                        {hotspotUsers.map((user) => (
                          <SelectItem key={user.id} value={user.id}>
                            {user.username} - {user.companyName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="creditType">Tipo de Crédito</Label>
                    <Select
                      value={formData.creditType}
                      onValueChange={(value: any) =>
                        setFormData((prev) => ({
                          ...prev,
                          creditType: value,
                          unit: value === "data" ? "bytes" : value === "time" ? "minutes" : "days",
                        }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="data">Dados</SelectItem>
                        <SelectItem value="time">Tempo</SelectItem>
                        <SelectItem value="unlimited">Ilimitado</SelectItem>
                        <SelectItem value="accumulative">Acumulativo</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="initialAmount">Quantidade Inicial</Label>
                    <Input
                      id="initialAmount"
                      type="number"
                      value={formData.initialAmount}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, initialAmount: Number.parseInt(e.target.value) }))
                      }
                      required
                      disabled={formData.creditType === "unlimited"}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="unit">Unidade</Label>
                    <Select
                      value={formData.unit}
                      onValueChange={(value: any) => setFormData((prev) => ({ ...prev, unit: value }))}
                      disabled={formData.creditType === "unlimited"}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {getUnitOptions().map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="validFrom">Válido de</Label>
                    <Input
                      id="validFrom"
                      type="date"
                      value={formData.validFrom}
                      onChange={(e) => setFormData((prev) => ({ ...prev, validFrom: e.target.value }))}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="validUntil">Válido até</Label>
                    <Input
                      id="validUntil"
                      type="date"
                      value={formData.validUntil}
                      onChange={(e) => setFormData((prev) => ({ ...prev, validUntil: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="autoReset"
                      checked={formData.autoReset}
                      onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, autoReset: checked }))}
                    />
                    <Label htmlFor="autoReset">Reset Automático</Label>
                  </div>

                  {formData.autoReset && (
                    <div className="space-y-2">
                      <Label htmlFor="resetPeriod">Período de Reset</Label>
                      <Select
                        value={formData.resetPeriod}
                        onValueChange={(value: any) => setFormData((prev) => ({ ...prev, resetPeriod: value }))}
                      >
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
                  )}

                  <div className="flex items-center space-x-2">
                    <Switch
                      id="accumulative"
                      checked={formData.accumulative}
                      onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, accumulative: checked }))}
                    />
                    <Label htmlFor="accumulative">Acumulativo (sobras são mantidas)</Label>
                  </div>
                </div>

                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancelar
                  </Button>
                  <Button type="submit">{editingCredit ? "Atualizar" : "Criar"}</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Filtros */}
        <div className="flex gap-4">
          <div className="space-y-2">
            <Label htmlFor="company-filter">Filtrar por Empresa</Label>
            <Select value={selectedCompany} onValueChange={setSelectedCompany}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Todas as empresas" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas as empresas</SelectItem>
                {getUniqueCompanies().map((company) => (
                  <SelectItem key={company} value={company}>
                    {company}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="month-filter">Filtrar por Mês</Label>
            <Select value={selectedMonth} onValueChange={setSelectedMonth}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Todos os meses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os meses</SelectItem>
                {getAvailableMonths().map((month) => {
                  const [year, monthNum] = month.split("-")
                  const monthName = new Date(Number.parseInt(year), Number.parseInt(monthNum) - 1).toLocaleDateString(
                    "pt-BR",
                    {
                      month: "long",
                      year: "numeric",
                    },
                  )
                  return (
                    <SelectItem key={month} value={month}>
                      {monthName}
                    </SelectItem>
                  )
                })}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Estatísticas */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Créditos</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{filteredCredits.length}</div>
              <p className="text-xs text-muted-foreground">Créditos ativos</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Créditos Baixos</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{filteredCredits.filter((c) => c.isLowCredit).length}</div>
              <p className="text-xs text-muted-foreground">Abaixo de 20%</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Expirados</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{filteredCredits.filter((c) => c.isExpired).length}</div>
              <p className="text-xs text-muted-foreground">Créditos vencidos</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Auto Reset</CardTitle>
              <RefreshCw className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{filteredCredits.filter((c) => c.autoReset).length}</div>
              <p className="text-xs text-muted-foreground">Com reset automático</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Lista de Créditos</CardTitle>
            <CardDescription>{filteredCredits.length} crédito(s) encontrado(s)</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Usuário</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Crédito Atual</TableHead>
                  <TableHead>Uso</TableHead>
                  <TableHead>Validade</TableHead>
                  <TableHead>Configurações</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCredits.map((credit) => (
                  <TableRow key={credit.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{credit.hotspotUsername}</div>
                        <div className="text-sm text-muted-foreground">{credit.companyName}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {getCreditTypeIcon(credit.creditType)}
                        {getCreditTypeBadge(credit.creditType)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">
                          {formatAmount(credit.currentAmount, credit.unit, credit.creditType)}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          de {formatAmount(credit.initialAmount, credit.unit, credit.creditType)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-2">
                        <Progress value={credit.usagePercentage} className="h-2" />
                        <div className="text-sm text-muted-foreground">{credit.usagePercentage.toFixed(1)}% usado</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {credit.validUntil ? (
                          <div>
                            <div>Até: {new Date(credit.validUntil).toLocaleDateString("pt-BR")}</div>
                            {credit.isExpired && (
                              <Badge variant="destructive" className="text-xs mt-1">
                                Expirado
                              </Badge>
                            )}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">Sem expiração</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {credit.autoReset && (
                          <Badge variant="outline" className="text-xs">
                            Reset {credit.resetPeriod}
                          </Badge>
                        )}
                        {credit.accumulative && (
                          <Badge variant="outline" className="text-xs">
                            Acumulativo
                          </Badge>
                        )}
                        {credit.isLowCredit && (
                          <Badge variant="destructive" className="text-xs">
                            Crédito baixo
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => resetCredit(credit.id)}
                          title="Resetar crédito"
                        >
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleEdit(credit)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleDelete(credit.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
