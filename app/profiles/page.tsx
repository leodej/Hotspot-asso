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
import { Plus, Edit, Trash2, Wifi, Clock, Download, Upload, Star } from "lucide-react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

interface HotspotProfile {
  id: string
  companyId: string
  companyName: string
  name: string
  downloadLimit: number
  uploadLimit: number
  timeLimit?: number
  idleTimeout: number
  sessionTimeout?: number
  keepaliveTimeout: number
  active: boolean
  isDefault: boolean
  createdAt: string
  usersCount: number
}

export default function ProfilesPage() {
  const [profiles, setProfiles] = useState<HotspotProfile[]>([])
  const [companies, setCompanies] = useState<Array<{ id: string; name: string }>>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingProfile, setEditingProfile] = useState<HotspotProfile | null>(null)
  const [formData, setFormData] = useState({
    companyId: "",
    name: "",
    downloadLimit: 10,
    uploadLimit: 5,
    timeLimit: 0,
    idleTimeout: 300,
    sessionTimeout: 0,
    keepaliveTimeout: 120,
    active: true,
    isDefault: false,
  })

  useEffect(() => {
    fetchProfiles()
    fetchCompanies()
  }, [])

  const fetchProfiles = async () => {
    try {
      const response = await fetch("/api/profiles")
      const data = await response.json()
      setProfiles(data)
    } catch (error) {
      console.error("Erro ao carregar perfis:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCompanies = async () => {
    try {
      const response = await fetch("/api/companies")
      const data = await response.json()
      setCompanies(data.filter((c: any) => c.active))
    } catch (error) {
      console.error("Erro ao carregar empresas:", error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const url = editingProfile ? `/api/profiles/${editingProfile.id}` : "/api/profiles"
      const method = editingProfile ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await fetchProfiles()
        setDialogOpen(false)
        resetForm()
      }
    } catch (error) {
      console.error("Erro ao salvar perfil:", error)
    }
  }

  const handleEdit = (profile: HotspotProfile) => {
    setEditingProfile(profile)
    setFormData({
      companyId: profile.companyId,
      name: profile.name,
      downloadLimit: profile.downloadLimit,
      uploadLimit: profile.uploadLimit,
      timeLimit: profile.timeLimit || 0,
      idleTimeout: profile.idleTimeout,
      sessionTimeout: profile.sessionTimeout || 0,
      keepaliveTimeout: profile.keepaliveTimeout,
      active: profile.active,
      isDefault: profile.isDefault,
    })
    setDialogOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm("Tem certeza que deseja excluir este perfil?")) {
      try {
        await fetch(`/api/profiles/${id}`, { method: "DELETE" })
        await fetchProfiles()
      } catch (error) {
        console.error("Erro ao excluir perfil:", error)
      }
    }
  }

  const setAsDefault = async (id: string, companyId: string) => {
    try {
      await fetch(`/api/profiles/${id}/set-default`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ companyId }),
      })
      await fetchProfiles()
    } catch (error) {
      console.error("Erro ao definir perfil padrão:", error)
    }
  }

  const resetForm = () => {
    setEditingProfile(null)
    setFormData({
      companyId: "",
      name: "",
      downloadLimit: 10,
      uploadLimit: 5,
      timeLimit: 0,
      idleTimeout: 300,
      sessionTimeout: 0,
      keepaliveTimeout: 120,
      active: true,
      isDefault: false,
    })
  }

  const formatSpeed = (mbps: number) => {
    if (mbps >= 1000) {
      return `${(mbps / 1000).toFixed(1)} Gbps`
    }
    return `${mbps} Mbps`
  }

  const formatTime = (minutes: number) => {
    if (minutes === 0) return "Ilimitado"
    if (minutes >= 1440) return `${Math.floor(minutes / 1440)}d`
    if (minutes >= 60) return `${Math.floor(minutes / 60)}h ${minutes % 60}m`
    return `${minutes}m`
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
            <h1 className="text-3xl font-bold tracking-tight">Perfis Hotspot</h1>
            <p className="text-muted-foreground">Gerencie perfis de acesso e limites por empresa</p>
          </div>

          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <Plus className="mr-2 h-4 w-4" />
                Novo Perfil
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{editingProfile ? "Editar Perfil" : "Novo Perfil"}</DialogTitle>
                <DialogDescription>Configure os limites e timeouts do perfil hotspot</DialogDescription>
              </DialogHeader>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="companyId">Empresa</Label>
                    <Select
                      value={formData.companyId}
                      onValueChange={(value) => setFormData((prev) => ({ ...prev, companyId: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma empresa" />
                      </SelectTrigger>
                      <SelectContent>
                        {companies.map((company) => (
                          <SelectItem key={company.id} value={company.id}>
                            {company.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="name">Nome do Perfil</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                      placeholder="Ex: Plano Básico"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="downloadLimit">Limite Download (Mbps)</Label>
                    <Input
                      id="downloadLimit"
                      type="number"
                      value={formData.downloadLimit}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, downloadLimit: Number.parseInt(e.target.value) }))
                      }
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="uploadLimit">Limite Upload (Mbps)</Label>
                    <Input
                      id="uploadLimit"
                      type="number"
                      value={formData.uploadLimit}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, uploadLimit: Number.parseInt(e.target.value) }))
                      }
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="timeLimit">Limite de Tempo (min)</Label>
                    <Input
                      id="timeLimit"
                      type="number"
                      value={formData.timeLimit}
                      onChange={(e) => setFormData((prev) => ({ ...prev, timeLimit: Number.parseInt(e.target.value) }))}
                      placeholder="0 = ilimitado"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="idleTimeout">Idle Timeout (seg)</Label>
                    <Input
                      id="idleTimeout"
                      type="number"
                      value={formData.idleTimeout}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, idleTimeout: Number.parseInt(e.target.value) }))
                      }
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="sessionTimeout">Session Timeout (min)</Label>
                    <Input
                      id="sessionTimeout"
                      type="number"
                      value={formData.sessionTimeout}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, sessionTimeout: Number.parseInt(e.target.value) }))
                      }
                      placeholder="0 = ilimitado"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="keepaliveTimeout">Keepalive Timeout (seg)</Label>
                  <Input
                    id="keepaliveTimeout"
                    type="number"
                    value={formData.keepaliveTimeout}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, keepaliveTimeout: Number.parseInt(e.target.value) }))
                    }
                    required
                  />
                </div>

                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="active"
                      checked={formData.active}
                      onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, active: checked }))}
                    />
                    <Label htmlFor="active">Perfil Ativo</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch
                      id="isDefault"
                      checked={formData.isDefault}
                      onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, isDefault: checked }))}
                    />
                    <Label htmlFor="isDefault">Perfil Padrão</Label>
                  </div>
                </div>

                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancelar
                  </Button>
                  <Button type="submit">{editingProfile ? "Atualizar" : "Criar"}</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Perfis</CardTitle>
              <Wifi className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{profiles.length}</div>
              <p className="text-xs text-muted-foreground">{profiles.filter((p) => p.active).length} ativos</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Perfis Padrão</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{profiles.filter((p) => p.isDefault).length}</div>
              <p className="text-xs text-muted-foreground">Por empresa</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Usuários Ativos</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{profiles.reduce((sum, p) => sum + p.usersCount, 0)}</div>
              <p className="text-xs text-muted-foreground">Usando perfis</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Velocidade Média</CardTitle>
              <Download className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {profiles.length > 0
                  ? Math.round(profiles.reduce((sum, p) => sum + p.downloadLimit, 0) / profiles.length)
                  : 0}{" "}
                Mbps
              </div>
              <p className="text-xs text-muted-foreground">Download médio</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Lista de Perfis</CardTitle>
            <CardDescription>{profiles.length} perfil(s) cadastrado(s)</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Empresa</TableHead>
                  <TableHead>Velocidade</TableHead>
                  <TableHead>Tempo</TableHead>
                  <TableHead>Timeouts</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Usuários</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {profiles.map((profile) => (
                  <TableRow key={profile.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center space-x-2">
                        {profile.isDefault && <Star className="h-4 w-4 text-yellow-500" />}
                        <span>{profile.name}</span>
                      </div>
                    </TableCell>
                    <TableCell>{profile.companyName}</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div className="flex items-center space-x-1">
                          <Download className="h-3 w-3 text-green-500" />
                          <span>{formatSpeed(profile.downloadLimit)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Upload className="h-3 w-3 text-blue-500" />
                          <span>{formatSpeed(profile.uploadLimit)}</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>Sessão: {formatTime(profile.timeLimit || 0)}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-xs text-muted-foreground">
                        <div>Idle: {profile.idleTimeout}s</div>
                        <div>Keep: {profile.keepaliveTimeout}s</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={profile.active ? "secondary" : "outline"}>
                        {profile.active ? "Ativo" : "Inativo"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{profile.usersCount}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {!profile.isDefault && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setAsDefault(profile.id, profile.companyId)}
                            title="Definir como padrão"
                          >
                            <Star className="h-4 w-4" />
                          </Button>
                        )}
                        <Button variant="outline" size="sm" onClick={() => handleEdit(profile)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleDelete(profile.id)}>
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
