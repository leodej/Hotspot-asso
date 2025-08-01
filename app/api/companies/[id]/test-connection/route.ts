import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params

    // Get company data from database/API
    const companiesResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"}/api/companies`)
    const companies = await companiesResponse.json()
    const company = companies.find((c: any) => c.id === id)

    if (!company) {
      return NextResponse.json({
        success: false,
        message: "Empresa não encontrada",
        error: "Company not found",
      })
    }

    // Test MikroTik connection
    try {
      const testResponse = await fetch(`http://${company.mikrotikIp}:${company.mikrotikPort}/rest/system/identity`, {
        method: "GET",
        headers: {
          Authorization: `Basic ${Buffer.from(`${company.mikrotikUser}:${company.mikrotikPassword}`).toString("base64")}`,
        },
        signal: AbortSignal.timeout(5000), // 5 second timeout
      })

      if (testResponse.ok) {
        const routerData = await testResponse.json()
        return NextResponse.json({
          success: true,
          message: "Conexão estabelecida com sucesso",
          routerInfo: {
            identity: routerData.name || "MikroTik-Router",
            version: routerData.version || "Unknown",
            uptime: routerData.uptime || "Unknown",
          },
        })
      } else {
        return NextResponse.json({
          success: false,
          message: "Falha na autenticação - Verifique usuário e senha",
          error: "Authentication failed",
        })
      }
    } catch (connectionError) {
      return NextResponse.json({
        success: false,
        message: "Falha na conexão - Verifique IP e porta",
        error: connectionError instanceof Error ? connectionError.message : "Connection failed",
      })
    }
  } catch (error) {
    console.error("Erro ao testar conexão:", error)
    return NextResponse.json({
      success: false,
      message: "Erro interno do servidor",
      error: error instanceof Error ? error.message : "Unknown error",
    })
  }
}
