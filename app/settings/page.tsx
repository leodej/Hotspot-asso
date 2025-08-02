"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import {
  Settings,
  Server,
  Mail,
  Shield,
  Database,
  Clock,
  HardDrive,
  Cpu,
  MemoryStick,
  Save,
  RefreshCw,
  Download,
  CheckCircle,
} from "lucide-react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

interface SystemSettings {
  general: {
    timezone: string
    sessionTimeout: number
    maxUploadSize: number
    cacheEnabled: boolean
    debugMode: boolean
  }
  mikrotik: {
    defaultPort: number
    connectionTimeout: number
    sslEnabled: boolean
    maxConnections: number
    retryAttempts: number
  }
  monitoring: {
    collectionInterval: number
    alertsEnabled: boolean
    retentionDays: number
    emailAlerts: boolean
  }
  email: {
    smtpHost: string
    smtpPort: number
    smtpUser: string
    smtpPassword: string
    fromEmail: string
    sslEnabled: boolean
  }
  backup: {
    autoBackup: boolean
    backupTime: string
    retentionDays: number
    backupPath: string
    compressionEnabled: boolean
  }
}

interface SystemStatus {
  cpu: number
  memory: number
  disk: number
  uptime: string
  version: string
  lastBackup: string
  activeConnections: number
  queuedJobs: number
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettings | null>(null)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testingEmail, setTestingEmail] = useState(false)
  const [testingBackup, setTestingBackup] = useState(false)

  const [logoFile, setLogoFile] = useState<File | null>(null)
  const [logoPreview, setLogoPreview] = useState<string>("")
  const [systemName, setSystemName] = useState<string>("MikroTik Manager")

  useEffect(() => {
    fetchSettings()
    fetchSystemStatus()

    // Atualizar status do sistema a cada 30 segundos
    const interval = setInterval(fetchSystemStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await fetch("/api/settings")
      const data = await response.json()
      setSettings(data)
    } catch (error) {
      console.error("Erro ao carregar configurações:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch("/api/system/status")
      const data = await response.json()
      setSystemStatus(data)
    } catch (error) {
      console.error("Erro ao carregar status do sistema:", error)
    }
  }

  const saveSettings = async () => {
    if (!settings) return

    try {
      setSaving(true)
      const response = await fetch("/api/settings", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(settings),
      })

      if (response.ok) {
        // Mostrar sucesso
        console.log("Configurações salvas com sucesso")
      }
    } catch (error) {
      console.error("Erro ao salvar configurações:", error)
    } finally {
      setSaving(false)
    }
  }

  const testEmailSettings = async () => {
    try {
      setTestingEmail(true)
      const response = await fetch("/api/settings/test-email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(settings?.email),
      })

      const result = await response.json()
      console.log("Teste de email:", result.success ? "Sucesso" : "Falha")
    } catch (error) {
      console.error("Erro ao testar email:", error)
    } finally {
      setTestingEmail(false)
    }
  }

  const createBackup = async () => {
    try {
      setTestingBackup(true)
      const response = await fetch("/api/backup/create", {
        method: "POST",
      })

      if (response.ok) {
        await fetchSystemStatus()
        console.log("Backup criado com sucesso")
      }
    } catch (error) {
      console.error("Erro ao criar backup:", error)
    } finally {
      setTestingBackup(false)
    }
  }

  const updateSettings = (section: keyof SystemSettings, key: string, value: any) => {
    if (!settings) return

    setSettings((prev) => ({
      ...prev!,
      [section]: {
        ...prev![section],
        [key]: value,
      },
    }))
  }

  const handleLogoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setLogoFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setLogoPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const saveSystemBranding = async () => {
    try {
      const formData = new FormData()
      if (logoFile) {
        formData.append("logo", logoFile)
      }
      formData.append("systemName", systemName)

      const response = await fetch("/api/settings/branding", {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        console.log("Configurações de marca salvas com sucesso")
      }
    } catch (error) {
      console.error("Erro ao salvar configurações de marca:", error)
    }
  }

  const getStatusColor = (percentage: number) => {
    if (percentage < 50) return "text-green-500"
    if (percentage < 80) return "text-yellow-500"
    return "text-red-500"
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
            <h1 className="text-3xl font-bold tracking-tight">Configurações</h1>
            <p className="text-muted-foreground">Gerencie as configurações do sistema</p>
          </div>

          <Button onClick={saveSettings} disabled={saving}>
            <Save className="mr-2 h-4 w-4" />
            {saving ? "Salvando..." : "Salvar Configurações"}
          </Button>
        </div>

        <Tabs defaultValue="general" className="space-y-4">
          <TabsList className="grid w-full grid-cols-7">
            <TabsTrigger value="general">Geral</TabsTrigger>
            <TabsTrigger value="mikrotik">MikroTik</TabsTrigger>
            <TabsTrigger value="monitoring">Monitoramento</TabsTrigger>
            <TabsTrigger value="email">Email</TabsTrigger>
            <TabsTrigger value="backup">Backup</TabsTrigger>
            <TabsTrigger value="system">Sistema</TabsTrigger>
            <TabsTrigger value="branding">Marca</TabsTrigger>
          </TabsList>

          <TabsContent value="general" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>Configurações Gerais</span>
                </CardTitle>
                <CardDescription>Configurações básicas do sistema</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="timezone">Timezone</Label>
                    <Select
                      value={settings?.general.timezone}
                      onValueChange={(value) => updateSettings("general", "timezone", value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="America/Sao_Paulo">America/São_Paulo</SelectItem>
                        <SelectItem value="America/New_York">America/New_York</SelectItem>
                        <SelectItem value="Europe/London">Europe/London</SelectItem>
                        <SelectItem value="UTC">UTC</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="sessionTimeout">Timeout de Sessão (segundos)</Label>
                    <Input
                      id="sessionTimeout"
                      type="number"
                      value={settings?.general.sessionTimeout}
                      onChange={(e) => updateSettings("general", "sessionTimeout", Number.parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="maxUploadSize">Tamanho Máximo de Upload (MB)</Label>
                    <Input
                      id="maxUploadSize"
                      type="number"
                      value={settings?.general.maxUploadSize}
                      onChange={(e) => updateSettings("general", "maxUploadSize", Number.parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="cacheEnabled"
                        checked={settings?.general.cacheEnabled}
                        onCheckedChange={(checked) => updateSettings("general", "cacheEnabled", checked)}
                      />
                      <Label htmlFor="cacheEnabled">Cache Habilitado</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Switch
                        id="debugMode"
                        checked={settings?.general.debugMode}
                        onCheckedChange={(checked) => updateSettings("general", "debugMode", checked)}
                      />
                      <Label htmlFor="debugMode">Modo Debug</Label>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="mikrotik" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Server className="h-5 w-5" />
                  <span>Configurações MikroTik</span>
                </CardTitle>
                <CardDescription>Configurações de conexão com roteadores MikroTik</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="defaultPort">Porta Padrão</Label>
                    <Input
                      id="defaultPort"
                      type="number"
                      value={settings?.mikrotik.defaultPort}
                      onChange={(e) => updateSettings("mikrotik", "defaultPort", Number.parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="connectionTimeout">Timeout de Conexão (seg)</Label>
                    <Input
                      id="connectionTimeout"
                      type="number"
                      value={settings?.mikrotik.connectionTimeout}
                      onChange={(e) => updateSettings("mikrotik", "connectionTimeout", Number.parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="maxConnections">Máximo de Conexões</Label>
                    <Input
                      id="maxConnections"
                      type="number"
                      value={settings?.mikrotik.maxConnections}
                      onChange={(e) => updateSettings("mikrotik", "maxConnections", Number.parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="retryAttempts">Tentativas de Reconexão</Label>
                    <Input
                      id="retryAttempts"
                      type="number"
                      value={settings?.mikrotik.retryAttempts}
                      onChange={(e) => updateSettings("mikrotik", "retryAttempts", Number.parseInt(e.target.value))}
                    />
                  </div>

                  <div className="flex items-center space-x-2 pt-6">
                    <Switch
                      id="sslEnabled"
                      checked={settings?.mikrotik.sslEnabled}
                      onCheckedChange={(checked) => updateSettings("mikrotik", "sslEnabled", checked)}
                    />
                    <Label htmlFor="sslEnabled">SSL Habilitado</Label>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="monitoring" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>Monitoramento</span>
                </CardTitle>
                <CardDescription>Configurações de coleta de dados e alertas</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="collectionInterval">Intervalo de Coleta (segundos)</Label>
                    <Input
                      id="collectionInterval"
                      type="number"
                      value={settings?.monitoring.collectionInterval}
                      onChange={(e) =>
                        updateSettings("monitoring", "collectionInterval", Number.parseInt(e.target.value))
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="retentionDays">Retenção de Dados (dias)</Label>
                    <Input
                      id="retentionDays"
                      type="number"
                      value={settings?.monitoring.retentionDays}
                      onChange={(e) => updateSettings("monitoring", "retentionDays", Number.parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="alertsEnabled"
                      checked={settings?.monitoring.alertsEnabled}
                      onCheckedChange={(checked) => updateSettings("monitoring", "alertsEnabled", checked)}
                    />
                    <Label htmlFor="alertsEnabled">Alertas Habilitados</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch
                      id="emailAlerts"
                      checked={settings?.monitoring.emailAlerts}
                      onCheckedChange={(checked) => updateSettings("monitoring", "emailAlerts", checked)}
                    />
                    <Label htmlFor="emailAlerts">Alertas por Email</Label>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="email" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Mail className="h-5 w-5" />
                  <span>Configurações de Email</span>
                </CardTitle>
                <CardDescription>Configurações SMTP para envio de emails</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="smtpHost">Servidor SMTP</Label>
                    <Input
                      id="smtpHost"
                      value={settings?.email.smtpHost}
                      onChange={(e) => updateSettings("email", "smtpHost", e.target.value)}
                      placeholder="smtp.gmail.com"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="smtpPort">Porta SMTP</Label>
                    <Input
                      id="smtpPort"
                      type="number"
                      value={settings?.email.smtpPort}
                      onChange={(e) => updateSettings("email", "smtpPort", Number.parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="smtpUser">Usuário SMTP</Label>
                    <Input
                      id="smtpUser"
                      value={settings?.email.smtpUser}
                      onChange={(e) => updateSettings("email", "smtpUser", e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="smtpPassword">Senha SMTP</Label>
                    <Input
                      id="smtpPassword"
                      type="password"
                      value={settings?.email.smtpPassword}
                      onChange={(e) => updateSettings("email", "smtpPassword", e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="fromEmail">Email Remetente</Label>
                    <Input
                      id="fromEmail"
                      type="email"
                      value={settings?.email.fromEmail}
                      onChange={(e) => updateSettings("email", "fromEmail", e.target.value)}
                    />
                  </div>

                  <div className="flex items-center space-x-2 pt-6">
                    <Switch
                      id="emailSslEnabled"
                      checked={settings?.email.sslEnabled}
                      onCheckedChange={(checked) => updateSettings("email", "sslEnabled", checked)}
                    />
                    <Label htmlFor="emailSslEnabled">SSL Habilitado</Label>
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button variant="outline" onClick={testEmailSettings} disabled={testingEmail}>
                    <Mail className="mr-2 h-4 w-4" />
                    {testingEmail ? "Testando..." : "Testar Email"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="backup" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="h-5 w-5" />
                  <span>Backup e Restauração</span>
                </CardTitle>
                <CardDescription>Configurações de backup automático</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="backupTime">Horário do Backup</Label>
                    <Input
                      id="backupTime"
                      type="time"
                      value={settings?.backup.backupTime}
                      onChange={(e) => updateSettings("backup", "backupTime", e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="backupRetentionDays">Retenção de Backups (dias)</Label>
                    <Input
                      id="backupRetentionDays"
                      type="number"
                      value={settings?.backup.retentionDays}
                      onChange={(e) => updateSettings("backup", "retentionDays", Number.parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="backupPath">Caminho dos Backups</Label>
                  <Input
                    id="backupPath"
                    value={settings?.backup.backupPath}
                    onChange={(e) => updateSettings("backup", "backupPath", e.target.value)}
                    placeholder="/app/backups"
                  />
                </div>

                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="autoBackup"
                      checked={settings?.backup.autoBackup}
                      onCheckedChange={(checked) => updateSettings("backup", "autoBackup", checked)}
                    />
                    <Label htmlFor="autoBackup">Backup Automático</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch
                      id="compressionEnabled"
                      checked={settings?.backup.compressionEnabled}
                      onCheckedChange={(checked) => updateSettings("backup", "compressionEnabled", checked)}
                    />
                    <Label htmlFor="compressionEnabled">Compressão Habilitada</Label>
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button variant="outline" onClick={createBackup} disabled={testingBackup}>
                    <Download className="mr-2 h-4 w-4" />
                    {testingBackup ? "Criando..." : "Criar Backup Agora"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Server className="h-5 w-5" />
                    <span>Status do Sistema</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Cpu className="h-4 w-4" />
                        <span className="text-sm">CPU</span>
                      </div>
                      <span className={`text-sm font-medium ${getStatusColor(systemStatus?.cpu || 0)}`}>
                        {systemStatus?.cpu || 0}%
                      </span>
                    </div>
                    <Progress value={systemStatus?.cpu || 0} className="h-2" />
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <MemoryStick className="h-4 w-4" />
                        <span className="text-sm">Memória</span>
                      </div>
                      <span className={`text-sm font-medium ${getStatusColor(systemStatus?.memory || 0)}`}>
                        {systemStatus?.memory || 0}%
                      </span>
                    </div>
                    <Progress value={systemStatus?.memory || 0} className="h-2" />
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <HardDrive className="h-4 w-4" />
                        <span className="text-sm">Disco</span>
                      </div>
                      <span className={`text-sm font-medium ${getStatusColor(systemStatus?.disk || 0)}`}>
                        {systemStatus?.disk || 0}%
                      </span>
                    </div>
                    <Progress value={systemStatus?.disk || 0} className="h-2" />
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t">
                    <span className="text-sm font-medium">Uptime</span>
                    <span className="text-sm text-muted-foreground">{systemStatus?.uptime || "0d 0h 0m"}</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Shield className="h-5 w-5" />
                    <span>Informações do Sistema</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Versão</span>
                      <Badge variant="outline">{systemStatus?.version || "1.0.0"}</Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Último Backup</span>
                      <span className="text-sm text-muted-foreground">
                        {systemStatus?.lastBackup
                          ? new Date(systemStatus.lastBackup).toLocaleDateString("pt-BR")
                          : "Nunca"}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Conexões Ativas</span>
                      <Badge variant="secondary">{systemStatus?.activeConnections || 0}</Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Jobs na Fila</span>
                      <Badge variant={systemStatus?.queuedJobs ? "destructive" : "outline"}>
                        {systemStatus?.queuedJobs || 0}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Status Geral</span>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <Badge variant="secondary">Operacional</Badge>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <Button variant="outline" className="w-full bg-transparent" onClick={fetchSystemStatus}>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Atualizar Status
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="branding" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>Identidade Visual</span>
                </CardTitle>
                <CardDescription>Configure o logo e nome do sistema</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="systemName">Nome do Sistema</Label>
                    <Input
                      id="systemName"
                      value={systemName}
                      onChange={(e) => setSystemName(e.target.value)}
                      placeholder="MikroTik Manager"
                    />
                  </div>

                  <div className="space-y-4">
                    <Label htmlFor="logoUpload">Logo do Sistema</Label>
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        {logoPreview ? (
                          <img
                            src={logoPreview || "/placeholder.svg"}
                            alt="Preview do logo"
                            className="w-16 h-16 object-contain border rounded-lg"
                          />
                        ) : (
                          <div className="w-16 h-16 bg-gray-100 border rounded-lg flex items-center justify-center">
                            <Settings className="h-8 w-8 text-gray-400" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1">
                        <Input
                          id="logoUpload"
                          type="file"
                          accept="image/*"
                          onChange={handleLogoUpload}
                          className="cursor-pointer"
                        />
                        <p className="text-sm text-muted-foreground mt-1">
                          Formatos aceitos: PNG, JPG, SVG. Será redimensionado automaticamente para 64x64px.
                        </p>
                      </div>
                    </div>
                  </div>

                  <Button onClick={saveSystemBranding} className="w-full">
                    <Save className="mr-2 h-4 w-4" />
                    Salvar Configurações de Marca
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
