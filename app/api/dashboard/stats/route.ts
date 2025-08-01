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
      networkHealth: 98.5,
      recentActivity: [
        {
          id: 1,
          type: "user_created",
          message: "Novo usuário cadastrado",
          details: "João Silva",
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        },
        {
          id: 2,
          type: "router_connected",
          message: "Roteador conectado",
          details: "192.168.1.1",
          timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
        },
        {
          id: 3,
          type: "backup_completed",
          message: "Backup realizado",
          details: "Sistema",
          timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        },
      ],
    }

    return NextResponse.json(stats)
  } catch (error) {
    console.error("Erro ao buscar estatísticas:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
