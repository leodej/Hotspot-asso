import { type NextRequest, NextResponse } from "next/server"

// Dados simulados de usuários hotspot
const hotspotUsers = [
  {
    id: "1",
    companyId: "1",
    companyName: "Empresa Alpha",
    profileId: "1",
    profileName: "Plano Básico",
    username: "user001",
    password: "pass123",
    email: "user001@email.com",
    fullName: "João Silva",
    phone: "(11) 99999-0001",
    macAddress: "00:11:22:33:44:55",
    ipAddress: "192.168.1.100",
    active: true,
    blocked: false,
    blockReason: null,
    createdAt: "2024-01-15T10:00:00Z",
    lastLogin: "2024-01-31T08:30:00Z",
    expiresAt: "2024-12-31T23:59:59Z",
    isOnline: true,
    currentSession: {
      sessionId: "sess_001",
      startTime: "2024-01-31T08:30:00Z",
      bytesIn: 1024 * 1024 * 150, // 150 MB
      bytesOut: 1024 * 1024 * 50, // 50 MB
      ipAddress: "192.168.1.100",
    },
  },
  {
    id: "2",
    companyId: "1",
    companyName: "Empresa Alpha",
    profileId: "2",
    profileName: "Plano Premium",
    username: "user002",
    password: "pass456",
    email: "user002@email.com",
    fullName: "Maria Santos",
    phone: "(11) 99999-0002",
    macAddress: "00:11:22:33:44:66",
    ipAddress: "192.168.1.101",
    active: true,
    blocked: false,
    blockReason: null,
    createdAt: "2024-01-20T14:30:00Z",
    lastLogin: "2024-01-30T16:45:00Z",
    expiresAt: null,
    isOnline: false,
    currentSession: null,
  },
  {
    id: "3",
    companyId: "2",
    companyName: "Empresa Beta",
    profileId: "3",
    profileName: "Acesso Limitado",
    username: "user003",
    password: "pass789",
    email: "user003@email.com",
    fullName: "Pedro Costa",
    phone: "(11) 99999-0003",
    macAddress: "00:11:22:33:44:77",
    ipAddress: null,
    active: true,
    blocked: true,
    blockReason: "Uso excessivo de banda",
    createdAt: "2024-02-01T09:15:00Z",
    lastLogin: "2024-01-29T12:00:00Z",
    expiresAt: "2024-06-30T23:59:59Z",
    isOnline: false,
    currentSession: null,
  },
]

export async function GET() {
  try {
    return NextResponse.json(hotspotUsers)
  } catch (error) {
    console.error("Erro ao buscar usuários hotspot:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json()

    const newUser = {
      id: Date.now().toString(),
      ...data,
      companyName: "Empresa Teste", // Em produção, buscar do banco
      profileName: "Perfil Teste", // Em produção, buscar do banco
      blocked: false,
      blockReason: null,
      createdAt: new Date().toISOString(),
      lastLogin: null,
      isOnline: false,
      currentSession: null,
    }

    hotspotUsers.push(newUser)

    return NextResponse.json(newUser, { status: 201 })
  } catch (error) {
    console.error("Erro ao criar usuário hotspot:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
