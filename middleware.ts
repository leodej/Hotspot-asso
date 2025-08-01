import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { verify } from "jsonwebtoken"

const JWT_SECRET = process.env.JWT_SECRET || "mikrotik-manager-super-secret-key"

// Rotas que não precisam de autenticação
const publicRoutes = ["/auth/login", "/auth/register", "/api/auth/login", "/api/auth/register", "/api/health"]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Permitir acesso às rotas públicas
  if (publicRoutes.some((route) => pathname.startsWith(route))) {
    return NextResponse.next()
  }

  // Permitir arquivos estáticos
  if (pathname.startsWith("/_next") || pathname.startsWith("/favicon.ico")) {
    return NextResponse.next()
  }

  // Verificar token de autenticação
  const token = request.cookies.get("auth-token")?.value

  if (!token) {
    return NextResponse.redirect(new URL("/auth/login", request.url))
  }

  try {
    verify(token, JWT_SECRET)
    return NextResponse.next()
  } catch (error) {
    // Token inválido, redirecionar para login
    const response = NextResponse.redirect(new URL("/auth/login", request.url))
    response.cookies.delete("auth-token")
    return response
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
}
