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
import { Plus, Edit, Trash2, TestTube, CheckCircle, XCircle } from "lucide-react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

interface Company {
  id: string
  name: string
  mikrotikIp: string
  mikrotikPort: number
  mikrotikUser: string
  mikrotikPassword: string
  defaultDownload: number
  defaultUpload: number
  defaultTime: number
  active: boolean
  connectionStatus: "connected" | "disconnected" | "testing"
  createdAt: string
}

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingCompany, setEditingCompany] = useState<Company | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    mikrotikIp: "",
    mikrotikPort: 8728,
    mikrotikUser: "",
    mikrotikPassword: "",
    defaultDownload: 10,
    defaultUpload: 5,
    defaultTime: 60,
    active: true,
  })

  useEffect(() => {
    fetchCompanies()
  }, [])

  const fetchCompanies = async () => {
    try {
      const response = await fetch("/api/companies")
      const data = await response.json()
      setCompanies(data)
    } catch (error) {
      console.error("Erro ao carregar empresas:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const url = editingCompany ? `/api/companies/${editingCompany.id}` : "/api/companies"
      const method = editingCompany ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await fetchCompanies()
        setDialogOpen(false)
        resetForm()
      }
    } catch (error) {
      console.error("Erro ao salvar empresa:", error)
    }
  }

  const handleEdit = (company: Company) => {
    setEditingCompany(company)
    setFormData({
      name: company.name,
      mikrotikIp: company.mikrotikIp,
      mikrotikPort: company.mikrotikPort,
      mikrotikUser: company.mikrotikUser,
      mikrotikPassword: company.mikrotikPassword,
      defaultDownload: company.defaultDownload,
      defaultUpload: company.defaultUpload,
      defaultTime: company.defaultTime,
      active: company.active,
    })
    setDialogOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm("Tem certeza que deseja excluir esta empresa?")) {
      try {
        await fetch(`/api/companies/${id}`, { method: "DELETE" })
        await fetchCompanies()
      } catch (error) {
        console.error("Erro ao excluir empresa:", error)
      }
    }
  }

  const testConnection = async (id: string) => {
    try {
      setCompanies((prev) => prev.map((c) => (c.id === id ? { ...c, connectionStatus: "testing" } : c)))

      const response = await fetch(`/api/companies/${id}/test-connection`, {
        method: "POST",
      })

      const result = await response.json()

      setCompanies((prev) =>
        prev.map((c) =>
          c.id === id
            ? {
                ...c,
                connectionStatus: result.success ? "connected" : "disconnected",
              }
            : c,
        ),
      )
    } catch (error) {
      console.error("Erro ao testar conexão:", error)
      setCompanies((prev) => prev.map((c) => (c.id === id ? { ...c, connectionStatus: "disconnected" } : c)))
    }
  }

  const resetForm = () => {
    setEditingCompany(null)
    setFormData({
      name: "",
      mikrotikIp: "",
      mikrotikPort: 8728,
      mikrotikUser: "",
      mikrotikPassword: "",
      defaultDownload: 10,
      defaultUpload: 5,
      defaultTime: 60,
      active: true,
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

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Empresas</h1>
            <p className="text-muted-foreground">Gerencie as empresas e suas configurações MikroTik</p>
          </div>

          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <Plus className="mr-2 h-4 w-4" />
                Nova Empresa
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{editingCompany ? "Editar Empresa" : "Nova Empresa"}</DialogTitle>
                <DialogDescription>Configure os dados da empresa e conexão com MikroTik</DialogDescription>
              </DialogHeader>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Nome da Empresa</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="mikrotikIp">IP do MikroTik</Label>
                    <Input
                      id="mikrotikIp"
                      value={formData.mikrotikIp}
                      onChange={(e) => setFormData((prev) => ({ ...prev, mikrotikIp: e.target.value }))}
                      placeholder="192.168.1.1"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="mikrotikPort">Porta</Label>
                    <Input
                      id="mikrotikPort"
                      type="number"
                      value={formData.mikrotikPort}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, mikrotikPort: Number.parseInt(e.target.value) }))
                      }
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="mikrotikUser">Usuário</Label>
                    <Input
                      id="mikrotikUser"
                      value={formData.mikrotikUser}
                      onChange={(e) => setFormData((prev) => ({ ...prev, mikrotikUser: e.target.value }))}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="mikrotikPassword">Senha</Label>
                    <Input
                      id="mikrotikPassword"
                      type="password"
                      value={formData.mikrotikPassword}
                      onChange={(e) => setFormData((prev) => ({ ...prev, mikrotikPassword: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="defaultDownload">Download Padrão (Mbps)</Label>
                    <Input
                      id="defaultDownload"
                      type="number"
                      value={formData.defaultDownload}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, defaultDownload: Number.parseInt(e.target.value) }))
                      }
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="defaultUpload">Upload Padrão (Mbps)</Label>
                    <Input
                      id="defaultUpload"
                      type="number"
                      value={formData.defaultUpload}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, defaultUpload: Number.parseInt(e.target.value) }))
                      }
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="defaultTime">Tempo Padrão (min)</Label>
                    <Input
                      id="defaultTime"
                      type="number"
                      value={formData.defaultTime}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, defaultTime: Number.parseInt(e.target.value) }))
                      }
                      required
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="active"
                    checked={formData.active}
                    onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, active: checked }))}
                  />
                  <Label htmlFor="active">Empresa Ativa</Label>
                </div>

                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancelar
                  </Button>
                  <Button type="submit">{editingCompany ? "Atualizar" : "Criar"}</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Lista de Empresas</CardTitle>
            <CardDescription>{companies.length} empresa(s) cadastrada(s)</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>IP MikroTik</TableHead>
                  <TableHead>Limites Padrão</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Conexão</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {companies.map((company) => (
                  <TableRow key={company.id}>
                    <TableCell className="font-medium">{company.name}</TableCell>
                    <TableCell>
                      {company.mikrotikIp}:{company.mikrotikPort}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>↓ {company.defaultDownload} Mbps</div>
                        <div>↑ {company.defaultUpload} Mbps</div>
                        <div>⏱ {company.defaultTime} min</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={company.active ? "secondary" : "outline"}>
                        {company.active ? "Ativa" : "Inativa"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {company.connectionStatus === "connected" && <CheckCircle className="h-4 w-4 text-green-500" />}
                        {company.connectionStatus === "disconnected" && <XCircle className="h-4 w-4 text-red-500" />}
                        {company.connectionStatus === "testing" && (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        )}
                        <Badge
                          variant={
                            company.connectionStatus === "connected"
                              ? "secondary"
                              : company.connectionStatus === "testing"
                                ? "outline"
                                : "destructive"
                          }
                        >
                          {company.connectionStatus === "connected"
                            ? "Conectado"
                            : company.connectionStatus === "testing"
                              ? "Testando"
                              : "Desconectado"}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => testConnection(company.id)}
                          disabled={company.connectionStatus === "testing"}
                        >
                          <TestTube className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleEdit(company)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleDelete(company.id)}>
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
