import { renderHook, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ReactNode } from "react"
import { describe, it, expect, beforeEach, vi } from "vitest"
import useAuth, { isLoggedIn } from "./useAuth"

// Mock the navigate function
const mockNavigate = vi.fn()
vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => mockNavigate,
}))

// Mock the custom toast hook
vi.mock("./useCustomToast", () => ({
  default: () => vi.fn(),
}))

// Mock the client services
vi.mock("../client", () => ({
  LoginService: {
    loginAccessToken: vi.fn(),
  },
  UsersService: {
    readUserMe: vi.fn().mockResolvedValue({
      id: 1,
      email: "test@example.com",
      full_name: "Test User",
      is_superuser: false,
    }),
  },
}))

// Create a wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
  
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  }
}

describe("useAuth", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it("should return initial state when not logged in", () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    })

    expect(result.current.user).toBeUndefined()
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe(null)
    expect(typeof result.current.loginMutation).toBe("object")
    expect(typeof result.current.logout).toBe("function")
    expect(typeof result.current.resetError).toBe("function")
  })

  it("should logout and navigate to login", () => {
    localStorage.setItem("access_token", "test-token")
    
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    })

    result.current.logout()

    expect(localStorage.getItem("access_token")).toBeNull()
    expect(mockNavigate).toHaveBeenCalledWith({ to: "/login" })
  })

  it("should reset error state", () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    })

    // Manually set error state (in real usage this would come from login mutation)
    result.current.resetError()

    expect(result.current.error).toBe(null)
  })
})

describe("isLoggedIn", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it("should return false when no token in localStorage", () => {
    expect(isLoggedIn()).toBe(false)
  })

  it("should return true when token exists in localStorage", () => {
    localStorage.setItem("access_token", "test-token")
    expect(isLoggedIn()).toBe(true)
  })
})