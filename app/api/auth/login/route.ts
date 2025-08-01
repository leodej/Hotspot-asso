import { type NextRequest, NextResponse } from "next/server"
import { sign } from "jsonwebtoken"

const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key"

// Usuários demo (em produção, usar banco de dados)
const users = [
  {
    id: "1",
    email: "admin@demo.com",
    password: "admin123", // Em produção, usar hash
    role: "admin",
    name: "Administrador",
  },
  {
    id: "2",
    email: "manager@demo.com",
    password: "manager123",
    role: "manager",
    name: "Gerente",
  },
]

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // Validar credenciais
    const user = users.find((u) => u.email === email && u.password === password)

    if (!user) {
      return NextResponse.json({ message: "Credenciais inválidas" }, { status: 401 })
    }

    // Gerar JWT token
    const token = sign(
      {
        userId: user.id,
        email: user.email,
        role: user.role,
        name: user.name,
      },
      JWT_SECRET,
      { expiresIn: "24h" },
    )

    // Log de auditoria
    console.log(`Login realizado: ${user.email} - ${new Date().toISOString()}`)

    return NextResponse.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        name: user.name,
      },
    })
  } catch (error) {
    console.error("Erro no login:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
