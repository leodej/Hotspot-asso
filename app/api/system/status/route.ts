import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Simular dados de status do sistema
    const systemStatus = {
      cpu: Math.floor(Math.random() * 80) + 10, // 10-90%
      memory: Math.floor(Math.random() * 70) + 20, // 20-90%
      disk: Math.floor(Math.random() * 60) + 15, // 15-75%
      uptime: "15d 8h 32m",
      version: "1.0.0",
      lastBackup: "2024-01-30T02:00:00Z",
      activeConnections: Math.floor(Math.random() * 100) + 50, // 50-150
      queuedJobs: Math.floor(Math.random() * 5), // 0-5
    }

    return NextResponse.json(systemStatus)
  } catch (error) {
    console.error("Erro ao buscar status do sistema:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
