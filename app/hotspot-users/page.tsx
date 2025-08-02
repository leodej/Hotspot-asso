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
import { Textarea } from "@/components/ui/textarea"
import {
  Plus,
  Edit,
  Trash2,
  UserCheck,
  UserX,
  Shield,
  ShieldOff,
  FolderSyncIcon as Sync,
  Clock,
  Download,
  Upload,
  Wifi,
} from "lucide-react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

interface HotspotUser {
  id: string
  companyId: string
  companyName: string
  profileId: string
  profileName: string
  username: string
  password: string
  email?: string
  fullName?: string
  phone?: string
  macAddress?: string
  ipAddress?: string
  active: boolean
  blocked: boolean
  blockReason?: string
  createdAt: string
  lastLogin?: string
  expiresAt?: string
  isOnline: boolean
  currentSession?: {
    sessionId: string
    startTime: string
    bytesIn: number
    bytesOut: number
    ipAddress: string
  }
}

export default function HotspotUsersPage() {
  const [users, setUsers] = useState<HotspotUser[]>([])
  const [companies, setCompanies] = useState<Array<{ id: string; name: string }>>([])
  const [profiles, setProfiles] = useState<Array<{ id: string; name: string; companyId: string }>>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [blockDialogOpen, setBlockDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<HotspotUser | null>(null)
  const [blockingUser, setBlockingUser] = useState<HotspotUser | null>(null)
  const [blockReason, setBlockReason] = useState("")
  const [formData, setFormData] = useState({
    companyId: "",
    profileId: "",
    username: "",
    password: "",
    email: "",
    fullName: "",
    phone: "",
    macAddress: "",
    ipAddress: "",
    active: true,
    expiresAt: "",
  })

  useEffect(() => {
    fetchUsers()
    fetchCompanies()
    fetchProfiles()

    // Atualizar status online a cada 30 segundos
    const interval = setInterval(fetchUsers, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await fetch("/api/hotspot-users")
      const data = await response.json()
      setUsers(data)
    } catch (error) {
      console.error("Erro ao carregar usuários hotspot:", error)
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

  const fetchProfiles = async () => {
    try {
      const response = await fetch("/api/profiles")
      const data = await response.json()
      setProfiles(data.filter((p: any) => p.active))
    } catch (error) {
      console.error("Erro ao carregar perfis:", error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const url = editingUser ? `/api/hotspot-users/${editingUser.id}` : "/api/hotspot-users"
      const method = editingUser ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await fetchUsers()
        setDialogOpen(false)
        resetForm()
      }
    } catch (error) {
      console.error("Erro ao salvar usuário hotspot:", error)
    }
  }

  const handleEdit = (user: HotspotUser) => {
    setEditingUser(user)
    setFormData({
      companyId: user.companyId,
      profileId: user.profileId,
      username: user.username,
      password: user.password,
      email: user.email || "",
      fullName: user.fullName || "",
      phone: user.phone || "",
      macAddress: user.macAddress || "",
      ipAddress: user.ipAddress || "",
      active: user.active,
      expiresAt: user.expiresAt ? user.expiresAt.split("T")[0] : "",
    })
    setDialogOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm("Tem certeza que deseja excluir este usuário? Esta ação também removerá o usuário do MikroTik.")) {
      try {
        await fetch(`/api/hotspot-users/${id}`, { method: "DELETE" })
        await fetchUsers()
      } catch (error) {
        console.error("Erro ao excluir usuário:", error)
      }
    }
  }

  const handleBlock = async () => {
    if (!blockingUser) return

    try {
      await fetch(`/api/hotspot-users/${blockingUser.id}/block`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          blocked: !blockingUser.blocked,
          reason: blockReason,
        }),
      })
      await fetchUsers()
      setBlockDialogOpen(false)
      setBlockingUser(null)
      setBlockReason("")
    } catch (error) {
      console.error("Erro ao bloquear/desbloquear usuário:", error)
    }
  }

  const syncWithMikrotik = async (companyId: string) => {
    try {
      await fetch(`/api/companies/${companyId}/sync-users`, {
        method: "POST",
      })
      await fetchUsers()
    } catch (error) {
      console.error("Erro ao sincronizar com MikroTik:", error)
    }
  }

  const disconnectUser = async (userId: string) => {
    try {
      await fetch(`/api/hotspot-users/${userId}/disconnect`, {
        method: "POST",
      })
      await fetchUsers()
    } catch (error) {
      console.error("Erro ao desconectar usuário:", error)
    }
  }

  const resetForm = () => {
    setEditingUser(null)
    setFormData({
      companyId: "",
      profileId: "",
      username: "",
      password: "",
      email: "",
      fullName: "",
      phone: "",
      macAddress: "",
      ipAddress: "",
      active: true,
      expiresAt: "",
    })
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B"
    const k = 1024
    const sizes = ["B", "KB", "MB", "GB", "TB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }

  const getFilteredProfiles = () => {
    return profiles.filter((p) => p.companyId === formData.companyId)
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
            <h1 className="text-3xl font-bold tracking-tight">Usuários Hotspot</h1>
            <p className="text-muted-foreground">Gerencie usuários hotspot integrados com MikroTik</p>
          </div>

          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => syncWithMikrotik("")}>
              <Sync className="mr-2 h-4 w-4" />
              Sincronizar Todos
            </Button>

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={resetForm}>
                  <Plus className="mr-2 h-4 w-4" />
                  Novo Usuário
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-3xl">
                <DialogHeader>
                  <DialogTitle>{editingUser ? "Editar Usuário Hotspot" : "Novo Usuário Hotspot"}</DialogTitle>
                  <DialogDescription>Configure os dados do usuário hotspot</DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="companyId">Empresa</Label>
                      <Select
                        value={formData.companyId}
                        onValueChange={(value) => setFormData((prev) => ({ ...prev, companyId: value, profileId: "" }))}
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
                      <Label htmlFor="profileId">Perfil</Label>
                      <Select
                        value={formData.profileId}
                        onValueChange={(value) => setFormData((prev) => ({ ...prev, profileId: value }))}
                        disabled={!formData.companyId}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione um perfil" />
                        </SelectTrigger>
                        <SelectContent>
                          {getFilteredProfiles().map((profile) => (
                            <SelectItem key={profile.id} value={profile.id}>
                              {profile.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="username">Nome de Usuário</Label>
                      <Input
                        id="username"
                        value={formData.username}
                        onChange={(e) => setFormData((prev) => ({ ...prev, username: e.target.value }))}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="password">Senha</Label>
                      <Input
                        id="password"
                        type="password"
                        value={formData.password}
                        onChange={(e) => setFormData((prev) => ({ ...prev, password: e.target.value }))}
                        required={!editingUser}
                        placeholder={editingUser ? "Deixe vazio para manter" : ""}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="fullName">Nome Completo</Label>
                      <Input
                        id="fullName"
                        value={formData.fullName}
                        onChange={(e) => setFormData((prev) => ({ ...prev, fullName: e.target.value }))}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="phone">Telefone</Label>
                      <Input
                        id="phone"
                        value={formData.phone}
                        onChange={(e) => setFormData((prev) => ({ ...prev, phone: e.target.value }))}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="macAddress">MAC Address</Label>
                      <Input
                        id="macAddress"
                        value={formData.macAddress}
                        onChange={(e) => setFormData((prev) => ({ ...prev, macAddress: e.target.value }))}
                        placeholder="00:00:00:00:00:00"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="ipAddress">IP Fixo</Label>
                      <Input
                        id="ipAddress"
                        value={formData.ipAddress}
                        onChange={(e) => setFormData((prev) => ({ ...prev, ipAddress: e.target.value }))}
                        placeholder="192.168.1.100"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="expiresAt">Data de Expiração</Label>
                      <Input
                        id="expiresAt"
                        type="date"
                        value={formData.expiresAt}
                        onChange={(e) => setFormData((prev) => ({ ...prev, expiresAt: e.target.value }))}
                      />
                    </div>

                    <div className="flex items-center space-x-2 pt-6">
                      <Switch
                        id="active"
                        checked={formData.active}
                        onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, active: checked }))}
                      />
                      <Label htmlFor="active">Usuário Ativo</Label>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-2">
                    <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                      Cancelar
                    </Button>
                    <Button type="submit">{editingUser ? "Atualizar" : "Criar"}</Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Estatísticas */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Usuários</CardTitle>
              <UserCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.length}</div>
              <p className="text-xs text-muted-foreground">{users.filter((u) => u.active).length} ativos</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Online Agora</CardTitle>
              <Wifi className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.filter((u) => u.isOnline).length}</div>
              <p className="text-xs text-muted-foreground">Conectados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Bloqueados</CardTitle>
              <ShieldOff className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.filter((u) => u.blocked).length}</div>
              <p className="text-xs text-muted-foreground">Usuários bloqueados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Expirando</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {
                  users.filter(
                    (u) => u.expiresAt && new Date(u.expiresAt) <= new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
                  ).length
                }
              </div>
              <p className="text-xs text-muted-foreground">Próximos 7 dias</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Lista de Usuários Hotspot</CardTitle>
            <CardDescription>{users.length} usuário(s) cadastrado(s)</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Usuário</TableHead>
                  <TableHead>Empresa</TableHead>
                  <TableHead>Perfil</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Sessão Atual</TableHead>
                  <TableHead>Tráfego</TableHead>
                  <TableHead>Expira</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{user.username}</div>
                        {user.fullName && <div className="text-sm text-muted-foreground">{user.fullName}</div>}
                      </div>
                    </TableCell>
                    <TableCell>{user.companyName}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{user.profileName}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col space-y-1">
                        <div className="flex items-center space-x-2">
                          {user.isOnline ? (
                            <Wifi className="h-4 w-4 text-green-500" />
                          ) : (
                            <Wifi className="h-4 w-4 text-gray-400" />
                          )}
                          <Badge variant={user.isOnline ? "secondary" : "outline"}>
                            {user.isOnline ? "Online" : "Offline"}
                          </Badge>
                        </div>
                        {user.blocked && (
                          <Badge variant="destructive" className="text-xs">
                            Bloqueado
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {user.currentSession ? (
                        <div className="text-sm">
                          <div>IP: {user.currentSession.ipAddress}</div>
                          <div className="text-muted-foreground">
                            {new Date(user.currentSession.startTime).toLocaleTimeString("pt-BR")}
                          </div>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {user.currentSession ? (
                        <div className="text-sm">
                          <div className="flex items-center space-x-1">
                            <Download className="h-3 w-3 text-green-500" />
                            <span>{formatBytes(user.currentSession.bytesIn)}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Upload className="h-3 w-3 text-blue-500" />
                            <span>{formatBytes(user.currentSession.bytesOut)}</span>
                          </div>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {user.expiresAt ? (
                        <div className="text-sm">{new Date(user.expiresAt).toLocaleDateString("pt-BR")}</div>
                      ) : (
                        <span className="text-muted-foreground">Nunca</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {user.isOnline && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => disconnectUser(user.id)}
                            title="Desconectar"
                          >
                            <UserX className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setBlockingUser(user)
                            setBlockDialogOpen(true)
                          }}
                          title={user.blocked ? "Desbloquear" : "Bloquear"}
                        >
                          {user.blocked ? <Shield className="h-4 w-4" /> : <ShieldOff className="h-4 w-4" />}
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleEdit(user)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleDelete(user.id)}>
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

        {/* Dialog de Bloqueio */}
        <Dialog open={blockDialogOpen} onOpenChange={setBlockDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{blockingUser?.blocked ? "Desbloquear Usuário" : "Bloquear Usuário"}</DialogTitle>
              <DialogDescription>
                {blockingUser?.blocked
                  ? `Desbloquear o usuário ${blockingUser?.username}?`
                  : `Bloquear o usuário ${blockingUser?.username}?`}
              </DialogDescription>
            </DialogHeader>

            {!blockingUser?.blocked && (
              <div className="space-y-2">
                <Label htmlFor="blockReason">Motivo do Bloqueio</Label>
                <Textarea
                  id="blockReason"
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                  placeholder="Descreva o motivo do bloqueio..."
                  required
                />
              </div>
            )}

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setBlockDialogOpen(false)}>
                Cancelar
              </Button>
              <Button variant={blockingUser?.blocked ? "default" : "destructive"} onClick={handleBlock}>
                {blockingUser?.blocked ? "Desbloquear" : "Bloquear"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
