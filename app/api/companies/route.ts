import { type NextRequest, NextResponse } from "next/server"

// Dados simulados (em produção, usar banco de dados)
const companies = [
  {
    id: "1",
    name: "Empresa Alpha",
    mikrotikIp: "192.168.1.1",
    mikrotikPort: 8728,
    mikrotikUser: "admin",
    mikrotikPassword: "password123",
    defaultDownload: 10,
    defaultUpload: 5,
    defaultTime: 60,
    active: true,
    connectionStatus: "connected" as const,
    createdAt: "2024-01-15T10:00:00Z",
  },
  {
    id: "2",
    name: "Empresa Beta",
    mikrotikIp: "192.168.2.1",
    mikrotikPort: 8728,
    mikrotikUser: "admin",
    mikrotikPassword: "password456",
    defaultDownload: 20,
    defaultUpload: 10,
    defaultTime: 120,
    active: true,
    connectionStatus: "connected" as const,
    createdAt: "2024-01-20T14:30:00Z",
  },
  {
    id: "3",
    name: "Empresa Gamma",
    mikrotikIp: "192.168.3.1",
    mikrotikPort: 8728,
    mikrotikUser: "admin",
    mikrotikPassword: "password789",
    defaultDownload: 15,
    defaultUpload: 8,
    defaultTime: 90,
    active: false,
    connectionStatus: "disconnected" as const,
    createdAt: "2024-02-01T09:15:00Z",
  },
]

export async function GET() {
  try {
    return NextResponse.json(companies)
  } catch (error) {
    console.error("Erro ao buscar empresas:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json()

    const newCompany = {
      id: Date.now().toString(),
      ...data,
      connectionStatus: "disconnected" as const,
      createdAt: new Date().toISOString(),
    }

    companies.push(newCompany)

    return NextResponse.json(newCompany, { status: 201 })
  } catch (error) {
    console.error("Erro ao criar empresa:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
