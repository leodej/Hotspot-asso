"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function HomePage() {
  const router = useRouter()

  useEffect(() => {
    // Verificar se há token de autenticação
    const cookies = document.cookie.split(";")
    const authToken = cookies.find((cookie) => cookie.trim().startsWith("auth-token="))

    if (authToken) {
      // Se autenticado, redirecionar para dashboard
      router.push("/dashboard")
    } else {
      // Se não autenticado, redirecionar para login
      router.push("/auth/login")
    }
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
  )
}
