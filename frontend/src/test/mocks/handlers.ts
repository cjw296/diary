import { http, HttpResponse } from "msw"

// In-memory user store for testing
let currentUser = {
  id: 1,
  email: "test@example.com",
  full_name: "John Doe",
  is_active: true,
  is_superuser: false,
}

export const handlers = [
  // Authentication endpoints
  http.post("/login/access-token", async ({ request }) => {
    const formData = await request.formData()
    const username = formData.get("username")
    const password = formData.get("password")
    
    // Simulate authentication logic
    if (username === "test@example.com" && password === "testpassword") {
      return HttpResponse.json({
        access_token: "mock-token",
        token_type: "bearer",
      })
    }
    
    return HttpResponse.json(
      { detail: "Incorrect email or password" },
      { status: 400 }
    )
  }),

  http.get("/users/me", ({ request }) => {
    const authHeader = request.headers.get("authorization")
    
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return HttpResponse.json(
        { detail: "Not authenticated" },
        { status: 401 }
      )
    }
    
    return HttpResponse.json(currentUser)
  }),

  http.patch("/users/me", async ({ request }) => {
    const authHeader = request.headers.get("authorization")
    
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return HttpResponse.json(
        { detail: "Not authenticated" },
        { status: 401 }
      )
    }
    
    try {
      const body = await request.json() as Partial<typeof currentUser>
      
      // Validate email format
      if (body.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email)) {
        return HttpResponse.json(
          { detail: "Invalid email format" },
          { status: 422 }
        )
      }
      
      // Simulate email already exists error
      if (body.email === "existing@example.com") {
        return HttpResponse.json(
          { detail: "Email already exists" },
          { status: 409 }
        )
      }
      
      // Update user data
      currentUser = { ...currentUser, ...body }
      
      return HttpResponse.json(currentUser)
    } catch (error) {
      return HttpResponse.json(
        { detail: "Invalid JSON" },
        { status: 400 }
      )
    }
  }),

  // Users management endpoints
  http.get("/users/", ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get("skip") || "0") / 20 + 1
    
    // Mock paginated users data
    const users = [
      currentUser,
      { id: 2, email: "admin@example.com", full_name: "Admin User", is_active: true, is_superuser: true },
      { id: 3, email: "user2@example.com", full_name: "Jane Smith", is_active: false, is_superuser: false },
    ]
    
    return HttpResponse.json({
      data: users,
      count: users.length,
    })
  }),

  http.post("/users/", async ({ request }) => {
    try {
      const body = await request.json()
      
      // Validate required fields
      if (!body.email || !body.password) {
        return HttpResponse.json(
          { detail: "Email and password are required" },
          { status: 422 }
        )
      }
      
      // Simulate creation of new user
      const newUser = {
        id: Math.floor(Math.random() * 1000),
        email: body.email,
        full_name: body.full_name || "",
        is_active: body.is_active ?? true,
        is_superuser: body.is_superuser ?? false,
      }
      
      return HttpResponse.json(newUser, { status: 201 })
    } catch (error) {
      return HttpResponse.json(
        { detail: "Invalid JSON" },
        { status: 400 }
      )
    }
  }),

  // Default fallback for unmatched API routes
  http.get("/api/*", () => {
    return HttpResponse.json({ message: "Mock response" })
  }),
]

// Helper to reset user data for tests
export const resetUserData = () => {
  currentUser = {
    id: 1,
    email: "test@example.com",
    full_name: "John Doe",
    is_active: true,
    is_superuser: false,
  }
}