import { type NextRequest, NextResponse } from "next/server"

// Dados simulados (mesmo array da rota principal)
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

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params
    const data = await request.json()

    const companyIndex = companies.findIndex((c) => c.id === id)

    if (companyIndex === -1) {
      return NextResponse.json({ message: "Empresa não encontrada" }, { status: 404 })
    }

    companies[companyIndex] = {
      ...companies[companyIndex],
      ...data,
    }

    return NextResponse.json(companies[companyIndex])
  } catch (error) {
    console.error("Erro ao atualizar empresa:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params

    const companyIndex = companies.findIndex((c) => c.id === id)

    if (companyIndex === -1) {
      return NextResponse.json({ message: "Empresa não encontrada" }, { status: 404 })
    }

    companies.splice(companyIndex, 1)

    return NextResponse.json({ message: "Empresa excluída com sucesso" })
  } catch (error) {
    console.error("Erro ao excluir empresa:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
