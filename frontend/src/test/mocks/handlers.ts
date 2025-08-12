import { http, HttpResponse } from "msw"

export const handlers = [
  // Mock authentication endpoints
  http.post("/api/auth/login", () => {
    return HttpResponse.json({
      access_token: "mock-token",
      token_type: "bearer",
    })
  }),

  http.get("/api/auth/me", () => {
    return HttpResponse.json({
      id: 1,
      email: "test@example.com",
      full_name: "Test User",
      is_active: true,
      is_superuser: false,
    })
  }),

  // Mock other API endpoints as needed
  http.get("/api/*", () => {
    return HttpResponse.json({ message: "Mock response" })
  }),
]