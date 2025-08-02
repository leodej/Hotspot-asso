import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const startDate = searchParams.get("startDate")
    const endDate = searchParams.get("endDate")
    const company = searchParams.get("company")
    const type = searchParams.get("type")

    // Dados simulados de relatórios
    const reportData = {
      daily: [
        {
          date: "2024-01-25",
          totalUsers: 45,
          activeUsers: 32,
          totalTraffic: 1024 * 1024 * 1024 * 2.5, // 2.5 GB
          downloadTraffic: 1024 * 1024 * 1024 * 2, // 2 GB
          uploadTraffic: 1024 * 1024 * 512, // 512 MB
          avgSessionTime: 125,
        },
        {
          date: "2024-01-26",
          totalUsers: 52,
          activeUsers: 38,
          totalTraffic: 1024 * 1024 * 1024 * 3.2, // 3.2 GB
          downloadTraffic: 1024 * 1024 * 1024 * 2.5, // 2.5 GB
          uploadTraffic: 1024 * 1024 * 700, // 700 MB
          avgSessionTime: 142,
        },
        {
          date: "2024-01-27",
          totalUsers: 48,
          activeUsers: 35,
          totalTraffic: 1024 * 1024 * 1024 * 2.8, // 2.8 GB
          downloadTraffic: 1024 * 1024 * 1024 * 2.2, // 2.2 GB
          uploadTraffic: 1024 * 1024 * 600, // 600 MB
          avgSessionTime: 138,
        },
      ],
      topUsers: [
        {
          username: "user001",
          company: "Empresa Alpha",
          totalTraffic: 1024 * 1024 * 1024 * 1.5, // 1.5 GB
          sessionCount: 15,
          avgSessionTime: 180,
        },
        {
          username: "user045",
          company: "Empresa Beta",
          totalTraffic: 1024 * 1024 * 1024 * 1.2, // 1.2 GB
          sessionCount: 12,
          avgSessionTime: 165,
        },
        {
          username: "user123",
          company: "Empresa Alpha",
          totalTraffic: 1024 * 1024 * 1024 * 1.0, // 1.0 GB
          sessionCount: 18,
          avgSessionTime: 145,
        },
      ],
      companies: [
        {
          name: "Empresa Alpha",
          activeUsers: 25,
          totalTraffic: 1024 * 1024 * 1024 * 5.2, // 5.2 GB
          avgSpeed: 15.5,
        },
        {
          name: "Empresa Beta",
          activeUsers: 18,
          totalTraffic: 1024 * 1024 * 1024 * 3.8, // 3.8 GB
          avgSpeed: 12.3,
        },
        {
          name: "Empresa Gamma",
          activeUsers: 8,
          totalTraffic: 1024 * 1024 * 1024 * 1.5, // 1.5 GB
          avgSpeed: 8.7,
        },
      ],
      summary: {
        totalSessions: 156,
        totalTraffic: 1024 * 1024 * 1024 * 10.5, // 10.5 GB
        avgSessionTime: 142,
        peakHour: "20:00",
        topCompany: "Empresa Alpha",
      },
    }

    return NextResponse.json(reportData)
  } catch (error) {
    console.error("Erro ao buscar relatórios:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
