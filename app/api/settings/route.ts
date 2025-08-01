import { type NextRequest, NextResponse } from "next/server"

// Configurações simuladas do sistema
const systemSettings = {
  general: {
    timezone: "America/Sao_Paulo",
    sessionTimeout: 3600,
    maxUploadSize: 100,
    cacheEnabled: true,
    debugMode: false,
  },
  mikrotik: {
    defaultPort: 8728,
    connectionTimeout: 10,
    sslEnabled: false,
    maxConnections: 50,
    retryAttempts: 3,
  },
  monitoring: {
    collectionInterval: 300,
    alertsEnabled: true,
    retentionDays: 90,
    emailAlerts: true,
  },
  email: {
    smtpHost: "smtp.gmail.com",
    smtpPort: 587,
    smtpUser: "",
    smtpPassword: "",
    fromEmail: "noreply@mikrotik-manager.com",
    sslEnabled: true,
  },
  backup: {
    autoBackup: true,
    backupTime: "02:00",
    retentionDays: 30,
    backupPath: "/app/backups",
    compressionEnabled: true,
  },
}

export async function GET() {
  try {
    return NextResponse.json(systemSettings)
  } catch (error) {
    console.error("Erro ao buscar configurações:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const data = await request.json()

    // Em produção, salvar no banco de dados
    Object.assign(systemSettings, data)

    return NextResponse.json({ message: "Configurações salvas com sucesso" })
  } catch (error) {
    console.error("Erro ao salvar configurações:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
