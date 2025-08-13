import { screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"

// Mock the useAuth hook
const mockUseAuth = vi.fn()
vi.mock("../../hooks/useAuth", () => ({
  default: () => mockUseAuth(),
}))

// Import the component directly since we can't easily test the route
import { Route } from "./index"

// Get the Dashboard component from the route configuration
const Dashboard = Route.options.component as React.ComponentType

describe("Dashboard", () => {
  beforeEach(() => {
    mockUseAuth.mockClear()
  })

  it("displays welcome message with user's full name", () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: "test@example.com",
        full_name: "John Doe",
        is_active: true,
      },
    })

    renderWithProviders(<Dashboard />)

    expect(screen.getByText("Hi, John Doe 👋🏼")).toBeInTheDocument()
    expect(screen.getByText("Welcome back, nice to see you again!")).toBeInTheDocument()
  })

  it("displays welcome message with user's email when no full name", () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: "test@example.com",
        full_name: null,
        is_active: true,
      },
    })

    renderWithProviders(<Dashboard />)

    expect(screen.getByText("Hi, test@example.com 👋🏼")).toBeInTheDocument()
    expect(screen.getByText("Welcome back, nice to see you again!")).toBeInTheDocument()
  })

  it("handles case when user data is not available", () => {
    mockUseAuth.mockReturnValue({
      user: null,
    })

    renderWithProviders(<Dashboard />)

    expect(screen.getByText(/Hi,.*👋🏼/)).toBeInTheDocument()
    expect(screen.getByText("Welcome back, nice to see you again!")).toBeInTheDocument()
  })

  it("handles case when user has empty full name", () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: "test@example.com",
        full_name: "",
        is_active: true,
      },
    })

    renderWithProviders(<Dashboard />)

    expect(screen.getByText("Hi, test@example.com 👋🏼")).toBeInTheDocument()
  })
})