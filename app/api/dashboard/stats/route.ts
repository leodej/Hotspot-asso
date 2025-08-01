import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Simular dados do dashboard (em produção, buscar do banco de dados)
    const stats = {
      totalUsers: 1247,
      totalCompanies: 23,
      activeConnections: 892,
      totalCredits: 45230,
      systemStatus: "online",
      networkHealth: 98,
      topUsers: [
        {
          username: "joao.silva",
          company: "Empresa Alpha",
          traffic: "2.5 GB",
          status: "online" as const,
        },
        {
          username: "maria.santos",
          company: "Empresa Beta",
          traffic: "1.8 GB",
          status: "online" as const,
        },
        {
          username: "pedro.costa",
          company: "Empresa Gamma",
          traffic: "1.2 GB",
          status: "offline" as const,
        },
      ],
      systemHealth: {
        cpu: 45,
        memory: 62,
        disk: 38,
        uptime: "15d 8h 23m",
      },
    }

    return NextResponse.json(stats)
  } catch (error) {
    console.error("Erro ao buscar estatísticas:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
