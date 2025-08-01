import { type NextRequest, NextResponse } from "next/server"

// Dados simulados de usuários do sistema
const systemUsers = [
  {
    id: "1",
    email: "admin@demo.com",
    name: "Administrador",
    role: "admin" as const,
    active: true,
    createdAt: "2024-01-15T10:00:00Z",
    lastLogin: "2024-01-31T08:30:00Z",
    loginAttempts: 0,
    lockedUntil: null,
    companies: [
      { id: "1", name: "Empresa Alpha", role: "admin" },
      { id: "2", name: "Empresa Beta", role: "admin" },
    ],
  },
  {
    id: "2",
    email: "manager@demo.com",
    name: "Gerente Silva",
    role: "manager" as const,
    active: true,
    createdAt: "2024-01-20T14:30:00Z",
    lastLogin: "2024-01-30T16:45:00Z",
    loginAttempts: 0,
    lockedUntil: null,
    companies: [{ id: "1", name: "Empresa Alpha", role: "manager" }],
  },
  {
    id: "3",
    email: "user@demo.com",
    name: "Usuário Comum",
    role: "user" as const,
    active: false,
    createdAt: "2024-02-01T09:15:00Z",
    lastLogin: null,
    loginAttempts: 2,
    lockedUntil: null,
    companies: [{ id: "2", name: "Empresa Beta", role: "user" }],
  },
]

export async function GET() {
  try {
    return NextResponse.json(systemUsers)
  } catch (error) {
    console.error("Erro ao buscar usuários:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json()

    const newUser = {
      id: Date.now().toString(),
      ...data,
      createdAt: new Date().toISOString(),
      lastLogin: null,
      loginAttempts: 0,
      lockedUntil: null,
      companies:
        data.companyIds?.map((id: string) => ({
          id,
          name: `Empresa ${id}`,
          role: "user",
        })) || [],
    }

    systemUsers.push(newUser)

    return NextResponse.json(newUser, { status: 201 })
  } catch (error) {
    console.error("Erro ao criar usuário:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
