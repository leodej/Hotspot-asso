import { type NextRequest, NextResponse } from "next/server"
import { sign } from "jsonwebtoken"

const JWT_SECRET = process.env.JWT_SECRET || "mikrotik-manager-super-secret-key"

// Usuários demo para desenvolvimento
const users = [
  {
    id: "1",
    email: "admin@demo.com",
    password: "admin123",
    role: "admin",
    name: "Administrador Sistema",
  },
  {
    id: "2",
    email: "admin@mikrotik-manager.com",
    password: "admin123",
    role: "admin",
    name: "Admin Principal",
  },
  {
    id: "3",
    email: "manager@demo.com",
    password: "manager123",
    role: "manager",
    name: "Gerente",
  },
  {
    id: "4",
    email: "user@demo.com",
    password: "user123",
    role: "user",
    name: "Usuário Padrão",
  },
]

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    console.log(`Tentativa de login: ${email}`)

    // Validar se email e password foram fornecidos
    if (!email || !password) {
      return NextResponse.json({ message: "Email e senha são obrigatórios" }, { status: 400 })
    }

    // Buscar usuário
    const user = users.find((u) => u.email === email && u.password === password)

    if (!user) {
      console.log(`Login falhou para: ${email}`)
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

    console.log(`Login realizado com sucesso: ${user.email} - ${new Date().toISOString()}`)

    return NextResponse.json({
      success: true,
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
