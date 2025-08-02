import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { verify } from "jsonwebtoken"

const JWT_SECRET = process.env.JWT_SECRET || "mikrotik-manager-super-secret-key"

// Rotas que não precisam de autenticação
const publicRoutes = ["/auth/login", "/auth/register", "/api/auth/login", "/api/auth/register", "/api/health"]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  console.log(`[MIDDLEWARE] Verificando rota: ${pathname}`)

  // Permitir arquivos estáticos
  if (pathname.startsWith("/_next") || pathname.startsWith("/favicon.ico") || pathname.startsWith("/placeholder")) {
    return NextResponse.next()
  }

  // Permitir acesso às rotas públicas
  if (publicRoutes.some((route) => pathname.startsWith(route))) {
    console.log(`[MIDDLEWARE] Rota pública permitida: ${pathname}`)
    return NextResponse.next()
  }

  // Verificar token de autenticação
  const token = request.cookies.get("auth-token")?.value

  if (!token) {
    console.log(`[MIDDLEWARE] Token não encontrado, redirecionando para login`)
    return NextResponse.redirect(new URL("/auth/login", request.url))
  }

  try {
    const decoded = verify(token, JWT_SECRET)
    console.log(`[MIDDLEWARE] Token válido para usuário:`, decoded)

    // Se está tentando acessar a raiz, redirecionar para dashboard
    if (pathname === "/") {
      console.log(`[MIDDLEWARE] Redirecionando raiz para dashboard`)
      return NextResponse.redirect(new URL("/dashboard", request.url))
    }

    return NextResponse.next()
  } catch (error) {
    console.log(`[MIDDLEWARE] Token inválido:`, error)
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
