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
import { Checkbox } from "@/components/ui/checkbox"
import { Plus, Edit, Trash2, UserCheck, UserX, History } from "lucide-react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

interface SystemUser {
  id: string
  email: string
  name: string
  role: "admin" | "manager" | "user"
  active: boolean
  createdAt: string
  lastLogin?: string
  loginAttempts: number
  lockedUntil?: string
  companies: Array<{
    id: string
    name: string
    role: string
  }>
}

export default function UsersPage() {
  const [users, setUsers] = useState<SystemUser[]>([])
  const [companies, setCompanies] = useState<Array<{ id: string; name: string }>>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<SystemUser | null>(null)
  const [formData, setFormData] = useState({
    email: "",
    name: "",
    password: "",
    role: "user" as const,
    active: true,
    companyIds: [] as string[],
  })

  useEffect(() => {
    fetchUsers()
    fetchCompanies()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await fetch("/api/users")
      const data = await response.json()
      setUsers(data)
    } catch (error) {
      console.error("Erro ao carregar usuários:", error)
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const url = editingUser ? `/api/users/${editingUser.id}` : "/api/users"
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
      console.error("Erro ao salvar usuário:", error)
    }
  }

  const handleEdit = (user: SystemUser) => {
    setEditingUser(user)
    setFormData({
      email: user.email,
      name: user.name,
      password: "",
      role: user.role,
      active: user.active,
      companyIds: user.companies.map((c) => c.id),
    })
    setDialogOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm("Tem certeza que deseja excluir este usuário?")) {
      try {
        await fetch(`/api/users/${id}`, { method: "DELETE" })
        await fetchUsers()
      } catch (error) {
        console.error("Erro ao excluir usuário:", error)
      }
    }
  }

  const toggleUserStatus = async (id: string, active: boolean) => {
    try {
      await fetch(`/api/users/${id}/toggle-status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active }),
      })
      await fetchUsers()
    } catch (error) {
      console.error("Erro ao alterar status:", error)
    }
  }

  const resetForm = () => {
    setEditingUser(null)
    setFormData({
      email: "",
      name: "",
      password: "",
      role: "user",
      active: true,
      companyIds: [],
    })
  }

  const getRoleBadge = (role: string) => {
    const variants = {
      admin: "destructive",
      manager: "default",
      user: "secondary",
    } as const
    return <Badge variant={variants[role as keyof typeof variants]}>{role.toUpperCase()}</Badge>
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
            <h1 className="text-3xl font-bold tracking-tight">Usuários do Sistema</h1>
            <p className="text-muted-foreground">Gerencie usuários e suas permissões</p>
          </div>

          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <Plus className="mr-2 h-4 w-4" />
                Novo Usuário
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{editingUser ? "Editar Usuário" : "Novo Usuário"}</DialogTitle>
                <DialogDescription>Configure os dados do usuário e suas permissões</DialogDescription>
              </DialogHeader>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Nome Completo</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="password">Senha {editingUser && "(deixe vazio para manter)"}</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData((prev) => ({ ...prev, password: e.target.value }))}
                      required={!editingUser}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="role">Função</Label>
                    <Select
                      value={formData.role}
                      onValueChange={(value: any) => setFormData((prev) => ({ ...prev, role: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="user">Usuário</SelectItem>
                        <SelectItem value="manager">Gerente</SelectItem>
                        <SelectItem value="admin">Administrador</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Empresas Associadas</Label>
                  <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto border rounded p-2">
                    {companies.map((company) => (
                      <div key={company.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={company.id}
                          checked={formData.companyIds.includes(company.id)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setFormData((prev) => ({
                                ...prev,
                                companyIds: [...prev.companyIds, company.id],
                              }))
                            } else {
                              setFormData((prev) => ({
                                ...prev,
                                companyIds: prev.companyIds.filter((id) => id !== company.id),
                              }))
                            }
                          }}
                        />
                        <Label htmlFor={company.id} className="text-sm">
                          {company.name}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="active"
                    checked={formData.active}
                    onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, active: checked }))}
                  />
                  <Label htmlFor="active">Usuário Ativo</Label>
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

        <Card>
          <CardHeader>
            <CardTitle>Lista de Usuários</CardTitle>
            <CardDescription>{users.length} usuário(s) cadastrado(s)</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Função</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Último Login</TableHead>
                  <TableHead>Empresas</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{getRoleBadge(user.role)}</TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {user.active ? (
                          <UserCheck className="h-4 w-4 text-green-500" />
                        ) : (
                          <UserX className="h-4 w-4 text-red-500" />
                        )}
                        <Badge variant={user.active ? "secondary" : "outline"}>
                          {user.active ? "Ativo" : "Inativo"}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>
                      {user.lastLogin ? new Date(user.lastLogin).toLocaleDateString("pt-BR") : "Nunca"}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {user.companies.slice(0, 2).map((company) => (
                          <Badge key={company.id} variant="outline" className="text-xs">
                            {company.name}
                          </Badge>
                        ))}
                        {user.companies.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{user.companies.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm" onClick={() => toggleUserStatus(user.id, !user.active)}>
                          {user.active ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleEdit(user)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <History className="h-4 w-4" />
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
      </div>
    </DashboardLayout>
  )
}
