import { type NextRequest, NextResponse } from "next/server"

// Dados simulados de créditos
const userCredits = [
  {
    id: "1",
    hotspotUserId: "1",
    hotspotUsername: "user001",
    companyName: "Empresa Alpha",
    creditType: "data" as const,
    initialAmount: 1024 * 1024 * 1024 * 5, // 5 GB
    currentAmount: 1024 * 1024 * 1024 * 2, // 2 GB restante
    unit: "bytes" as const,
    validFrom: "2024-01-01T00:00:00Z",
    validUntil: "2024-12-31T23:59:59Z",
    autoReset: true,
    resetPeriod: "monthly" as const,
    accumulative: false,
    createdAt: "2024-01-15T10:00:00Z",
    usagePercentage: 60,
    isExpired: false,
    isLowCredit: false,
  },
  {
    id: "2",
    hotspotUserId: "2",
    hotspotUsername: "user002",
    companyName: "Empresa Alpha",
    creditType: "time" as const,
    initialAmount: 1440, // 24 horas em minutos
    currentAmount: 180, // 3 horas restantes
    unit: "minutes" as const,
    validFrom: "2024-01-01T00:00:00Z",
    validUntil: "2024-06-30T23:59:59Z",
    autoReset: false,
    resetPeriod: null,
    accumulative: true,
    createdAt: "2024-01-20T14:30:00Z",
    usagePercentage: 87.5,
    isExpired: false,
    isLowCredit: true,
  },
  {
    id: "3",
    hotspotUserId: "3",
    hotspotUsername: "user003",
    companyName: "Empresa Beta",
    creditType: "unlimited" as const,
    initialAmount: 30, // 30 dias
    currentAmount: 15, // 15 dias restantes
    unit: "days" as const,
    validFrom: "2024-01-01T00:00:00Z",
    validUntil: "2024-01-31T23:59:59Z",
    autoReset: false,
    resetPeriod: null,
    accumulative: false,
    createdAt: "2024-02-01T09:15:00Z",
    usagePercentage: 50,
    isExpired: true,
    isLowCredit: false,
  },
]

export async function GET() {
  try {
    return NextResponse.json(userCredits)
  } catch (error) {
    console.error("Erro ao buscar créditos:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json()

    const newCredit = {
      id: Date.now().toString(),
      ...data,
      hotspotUsername: "user_test", // Em produção, buscar do banco
      companyName: "Empresa Teste", // Em produção, buscar do banco
      currentAmount: data.initialAmount,
      createdAt: new Date().toISOString(),
      usagePercentage: 0,
      isExpired: false,
      isLowCredit: false,
    }

    userCredits.push(newCredit)

    return NextResponse.json(newCredit, { status: 201 })
  } catch (error) {
    console.error("Erro ao criar crédito:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
