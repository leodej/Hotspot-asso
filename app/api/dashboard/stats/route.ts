import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Simular dados do dashboard (em produção, buscar do banco de dados)
    const stats = {
      totalUsers: 1250,
      activeUsers: 847,
      totalCompanies: 15,
      activeCompanies: 12,
      totalTraffic: {
        download: "2.5 TB",
        upload: "850 GB",
      },
      topUsers: [
        {
          username: "user001",
          company: "Empresa Alpha",
          traffic: "15.2 GB",
          status: "online" as const,
        },
        {
          username: "user045",
          company: "Empresa Beta",
          traffic: "12.8 GB",
          status: "online" as const,
        },
        {
          username: "user123",
          company: "Empresa Alpha",
          traffic: "10.5 GB",
          status: "offline" as const,
        },
        {
          username: "user089",
          company: "Empresa Gamma",
          traffic: "9.2 GB",
          status: "online" as const,
        },
        {
          username: "user156",
          company: "Empresa Beta",
          traffic: "8.7 GB",
          status: "offline" as const,
        },
      ],
      systemHealth: {
        cpu: 35,
        memory: 68,
        disk: 42,
        uptime: "15d 8h 32m",
      },
    }

    return NextResponse.json(stats)
  } catch (error) {
    console.error("Erro ao buscar estatísticas:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
