import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Simular dados do dashboard
    const stats = {
      totalUsers: 156,
      totalCompanies: 12,
      activeConnections: 89,
      totalCredits: 25000,
      systemStatus: "online",
      networkHealth: 98,
      topUsers: [
        {
          username: "João Silva",
          company: "Empresa Alpha",
          traffic: "2.5 GB",
          status: "online" as const,
        },
        {
          username: "Maria Santos",
          company: "Empresa Beta",
          traffic: "1.8 GB",
          status: "online" as const,
        },
        {
          username: "Pedro Costa",
          company: "Empresa Gamma",
          traffic: "3.2 GB",
          status: "offline" as const,
        },
      ],
      systemHealth: {
        cpu: 45,
        memory: 62,
        disk: 78,
        uptime: "15d 8h 32m",
      },
    }

    return NextResponse.json(stats)
  } catch (error) {
    console.error("Erro ao buscar estatísticas:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
