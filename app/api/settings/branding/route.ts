import { type NextRequest, NextResponse } from "next/server"
import { writeFile, mkdir } from "fs/promises"
import { join } from "path"
import sharp from "sharp"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const logoFile = formData.get("logo") as File
    const systemName = formData.get("systemName") as string

    let logoPath = null

    if (logoFile) {
      // Criar diretório se não existir
      const uploadsDir = join(process.cwd(), "public", "uploads")
      try {
        await mkdir(uploadsDir, { recursive: true })
      } catch (error) {
        // Diretório já existe
      }

      // Processar e redimensionar a imagem
      const bytes = await logoFile.arrayBuffer()
      const buffer = Buffer.from(bytes)

      // Redimensionar para 64x64px mantendo proporção
      const resizedBuffer = await sharp(buffer)
        .resize(64, 64, {
          fit: "contain",
          background: { r: 255, g: 255, b: 255, alpha: 0 },
        })
        .png()
        .toBuffer()

      // Salvar arquivo
      const filename = `logo-${Date.now()}.png`
      logoPath = join(uploadsDir, filename)
      await writeFile(logoPath, resizedBuffer)
      logoPath = `/uploads/${filename}`
    }

    // Em produção, salvar no banco de dados
    // Por enquanto, apenas simular o salvamento
    const brandingSettings = {
      systemName: systemName || "MikroTik Manager",
      logoPath: logoPath,
    }

    console.log("Configurações de marca salvas:", brandingSettings)

    return NextResponse.json({
      message: "Configurações de marca salvas com sucesso",
      data: brandingSettings,
    })
  } catch (error) {
    console.error("Erro ao salvar configurações de marca:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}

export async function GET() {
  try {
    // Em produção, buscar do banco de dados
    const brandingSettings = {
      systemName: "MikroTik Manager",
      logoPath: null,
    }

    return NextResponse.json(brandingSettings)
  } catch (error) {
    console.error("Erro ao buscar configurações de marca:", error)
    return NextResponse.json({ message: "Erro interno do servidor" }, { status: 500 })
  }
}
