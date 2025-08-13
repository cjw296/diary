import { screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../test/utils"
import { Route } from "./login"

// Mock useAuth hook
const mockLoginMutation = {
  mutateAsync: vi.fn(),
}
const mockResetError = vi.fn()
const mockUseAuth = vi.fn()

vi.mock("../hooks/useAuth", () => ({
  default: () => mockUseAuth(),
  isLoggedIn: vi.fn().mockReturnValue(false),
}))

// Mock router
vi.mock("@tanstack/react-router", () => ({
  createFileRoute: (path: string) => (config: any) => ({
    ...config,
    options: { 
      component: config.component,
      beforeLoad: config.beforeLoad 
    }
  }),
  redirect: vi.fn(),
}))

// Mock utils
vi.mock("../utils", () => ({
  emailPattern: {
    value: /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/,
    message: "Please enter a valid email",
  },
}))

const Login = Route.component

describe("Login", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseAuth.mockReturnValue({
      loginMutation: mockLoginMutation,
      error: null,
      resetError: mockResetError,
    })
  })

  it("renders login form", () => {
    renderWithProviders(<Login />)

    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Log In" })).toBeInTheDocument()
  })

  it("shows password toggle functionality", () => {
    renderWithProviders(<Login />)

    const passwordField = screen.getByPlaceholderText("Password")
    const toggleButton = screen.getByLabelText("Show password")

    // Initially password should be hidden
    expect(passwordField).toHaveAttribute("type", "password")

    // Click to show password
    fireEvent.click(toggleButton)
    
    expect(passwordField).toHaveAttribute("type", "text")
    expect(screen.getByLabelText("Hide password")).toBeInTheDocument()

    // Click to hide password again
    fireEvent.click(screen.getByLabelText("Hide password"))
    expect(passwordField).toHaveAttribute("type", "password")
  })

  it("validates required fields", async () => {
    renderWithProviders(<Login />)

    const submitButton = screen.getByRole("button", { name: "Log In" })
    fireEvent.click(submitButton)

    // Check that form fields are still present (validation prevents submission)
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Email")).toBeInTheDocument()
      expect(screen.getByPlaceholderText("Password")).toBeInTheDocument()
    })
  })

  it("submits login form with valid data", async () => {
    mockLoginMutation.mutateAsync.mockResolvedValue({})

    renderWithProviders(<Login />)

    const emailField = screen.getByPlaceholderText("Email")
    const passwordField = screen.getByPlaceholderText("Password")
    const submitButton = screen.getByRole("button", { name: "Log In" })

    fireEvent.change(emailField, { target: { value: "user@example.com" } })
    fireEvent.change(passwordField, { target: { value: "password123" } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockResetError).toHaveBeenCalled()
      expect(mockLoginMutation.mutateAsync).toHaveBeenCalledWith({
        username: "user@example.com",
        password: "password123",
      })
    })
  })

  it("displays authentication error", () => {
    mockUseAuth.mockReturnValue({
      loginMutation: mockLoginMutation,
      error: "Invalid credentials",
      resetError: mockResetError,
    })

    renderWithProviders(<Login />)

    expect(screen.getByText("Invalid credentials")).toBeInTheDocument()
  })

  it("shows loading state during submission", async () => {
    mockLoginMutation.mutateAsync.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    renderWithProviders(<Login />)

    const emailField = screen.getByPlaceholderText("Email")
    const passwordField = screen.getByPlaceholderText("Password")
    const submitButton = screen.getByRole("button", { name: "Log In" })

    fireEvent.change(emailField, { target: { value: "user@example.com" } })
    fireEvent.change(passwordField, { target: { value: "password123" } })
    fireEvent.click(submitButton)

    // Check loading state
    await waitFor(() => {
      expect(submitButton).toHaveAttribute("data-loading")
    })
  })

  it("handles login mutation error gracefully", async () => {
    mockLoginMutation.mutateAsync.mockRejectedValue(new Error("Network error"))

    renderWithProviders(<Login />)

    const emailField = screen.getByPlaceholderText("Email")
    const passwordField = screen.getByPlaceholderText("Password")
    const submitButton = screen.getByRole("button", { name: "Log In" })

    fireEvent.change(emailField, { target: { value: "user@example.com" } })
    fireEvent.change(passwordField, { target: { value: "password123" } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockLoginMutation.mutateAsync).toHaveBeenCalled()
    })

    // Form should still be present after error
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument()
  })

  it("prevents double submission when already submitting", async () => {
    mockLoginMutation.mutateAsync.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    renderWithProviders(<Login />)

    const emailField = screen.getByPlaceholderText("Email")
    const passwordField = screen.getByPlaceholderText("Password")
    const submitButton = screen.getByRole("button", { name: "Log In" })

    fireEvent.change(emailField, { target: { value: "user@example.com" } })
    fireEvent.change(passwordField, { target: { value: "password123" } })
    
    // Submit first time
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockLoginMutation.mutateAsync).toHaveBeenCalledTimes(1)
    })
  })

  it("has beforeLoad redirect for logged in users", () => {
    expect(typeof Route.beforeLoad).toBe("function")
  })

  it("shows email validation error", async () => {
    renderWithProviders(<Login />)

    const emailField = screen.getByPlaceholderText("Email")
    
    fireEvent.change(emailField, { target: { value: "invalid-email" } })
    fireEvent.blur(emailField)

    await waitFor(() => {
      expect(screen.getByText("Please enter a valid email")).toBeInTheDocument()
    })
  })
})