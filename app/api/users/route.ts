import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Simular dados de usuários (em produção, buscar do banco de dados)
    const users = [
      {
        id: "1",
        name: "João Silva",
        email: "joao.silva@email.com",
        company: "Empresa Alpha",
        status: "active" as const,
        createdAt: "2024-01-15",
      },
      {
        id: "2",
        name: "Maria Santos",
        email: "maria.santos@email.com",
        company: "Empresa Beta",
        status: "active" as const,
        createdAt: "2024-01-20",
      },
      {
        id: "3",
        name: "Pedro Costa",
        email: "pedro.costa@email.com",
        company: "Empresa Gamma",
        status: "inactive" as const,
        createdAt: "2024-01-25",
      },
    ]

    return NextResponse.json(users)
  } catch (error) {
    console.error("Erro ao buscar usuários:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
