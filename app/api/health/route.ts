import { NextResponse } from "next/server"

export async function GET() {
  return NextResponse.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    service: "MIKROTIK MANAGER",
    version: "1.0.0",
    environment: process.env.NODE_ENV || "development",
    users_available: [
      { email: "admin@demo.com", password: "admin123", role: "admin" },
      { email: "admin@mikrotik-manager.com", password: "admin123", role: "admin" },
      { email: "manager@demo.com", password: "manager123", role: "manager" },
      { email: "user@demo.com", password: "user123", role: "user" },
    ],
  })
}
