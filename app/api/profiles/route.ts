import { type NextRequest, NextResponse } from "next/server"

// Dados simulados de perfis hotspot
const hotspotProfiles = [
  {
    id: "1",
    companyId: "1",
    companyName: "Empresa Alpha",
    name: "Plano Básico",
    downloadLimit: 10,
    uploadLimit: 5,
    timeLimit: 60,
    idleTimeout: 300,
    sessionTimeout: 3600,
    keepaliveTimeout: 120,
    active: true,
    isDefault: true,
    createdAt: "2024-01-15T10:00:00Z",
    usersCount: 25,
  },
  {
    id: "2",
    companyId: "1",
    companyName: "Empresa Alpha",
    name: "Plano Premium",
    downloadLimit: 50,
    uploadLimit: 25,
    timeLimit: 0,
    idleTimeout: 600,
    sessionTimeout: 0,
    keepaliveTimeout: 300,
    active: true,
    isDefault: false,
    createdAt: "2024-01-20T14:30:00Z",
    usersCount: 12,
  },
  {
    id: "3",
    companyId: "2",
    companyName: "Empresa Beta",
    name: "Acesso Limitado",
    downloadLimit: 5,
    uploadLimit: 2,
    timeLimit: 30,
    idleTimeout: 180,
    sessionTimeout: 1800,
    keepaliveTimeout: 60,
    active: true,
    isDefault: true,
    createdAt: "2024-02-01T09:15:00Z",
    usersCount: 8,
  },
]

export async function GET() {
  try {
    return NextResponse.json(hotspotProfiles)
  } catch (error) {
    console.error("Erro ao buscar perfis:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json()

    const newProfile = {
      id: Date.now().toString(),
      ...data,
      companyName: "Empresa Teste", // Em produção, buscar do banco
      createdAt: new Date().toISOString(),
      usersCount: 0,
    }

    hotspotProfiles.push(newProfile)

    return NextResponse.json(newProfile, { status: 201 })
  } catch (error) {
    console.error("Erro ao criar perfil:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
