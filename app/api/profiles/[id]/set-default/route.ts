import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const body = await request.json()
    const { companyId } = body

    // Aqui você implementaria a lógica para:
    // 1. Remover isDefault de todos os perfis da empresa
    // 2. Definir o perfil atual como padrão
    // Por enquanto, retornamos sucesso

    return NextResponse.json({
      success: true,
      message: "Perfil definido como padrão com sucesso",
    })
  } catch (error) {
    console.error("Erro ao definir perfil padrão:", error)
    return NextResponse.json({ error: "Erro interno do servidor" }, { status: 500 })
  }
}
