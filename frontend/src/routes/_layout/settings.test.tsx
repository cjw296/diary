import { screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import { Route } from "./settings"

// Mock useQueryClient
const mockGetQueryData = vi.fn()
vi.mock("@tanstack/react-query", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@tanstack/react-query")>()
  return {
    ...actual,
    useQueryClient: () => ({
      getQueryData: mockGetQueryData,
    }),
  }
})

// Mock the component imports
vi.mock("../../components/UserSettings/Appearance", () => ({
  default: () => <div data-testid="appearance">Appearance Component</div>,
}))

vi.mock("../../components/UserSettings/ChangePassword", () => ({
  default: () => <div data-testid="change-password">Change Password Component</div>,
}))

vi.mock("../../components/UserSettings/DeleteAccount", () => ({
  default: () => <div data-testid="delete-account">Delete Account Component</div>,
}))

vi.mock("../../components/UserSettings/UserInformation", () => ({
  default: () => <div data-testid="user-information">User Information Component</div>,
}))

// Mock router
vi.mock("@tanstack/react-router", () => ({
  createFileRoute: (path: string) => (config: any) => ({
    ...config,
    options: { component: config.component }
  }),
}))

const UserSettings = Route.component

describe("UserSettings", () => {
  beforeEach(() => {
    mockGetQueryData.mockClear()
  })

  it("renders all tabs for regular user", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<UserSettings />)

    expect(screen.getByText("User Settings")).toBeInTheDocument()
    expect(screen.getByText("My profile")).toBeInTheDocument()
    expect(screen.getByText("Password")).toBeInTheDocument()
    expect(screen.getByText("Appearance")).toBeInTheDocument()
    expect(screen.getByText("Danger zone")).toBeInTheDocument()
  })

  it("renders limited tabs for superuser", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "admin@example.com",
      is_superuser: true,
    })

    renderWithProviders(<UserSettings />)

    expect(screen.getByText("User Settings")).toBeInTheDocument()
    expect(screen.getByText("My profile")).toBeInTheDocument()
    expect(screen.getByText("Password")).toBeInTheDocument()
    expect(screen.getByText("Appearance")).toBeInTheDocument()
    expect(screen.queryByText("Danger zone")).not.toBeInTheDocument()
  })

  it("handles case when no user data is available", () => {
    mockGetQueryData.mockReturnValue(null)

    renderWithProviders(<UserSettings />)

    expect(screen.getByText("User Settings")).toBeInTheDocument()
    // Should default to showing all tabs when user data is not available
    expect(screen.getByText("My profile")).toBeInTheDocument()
    expect(screen.getByText("Password")).toBeInTheDocument()
    expect(screen.getByText("Appearance")).toBeInTheDocument()
    expect(screen.getByText("Danger zone")).toBeInTheDocument()
  })

  it("renders tab panels with correct components", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<UserSettings />)

    // Tab panels should be present (though not necessarily visible without clicking)
    // The components should be rendered in the DOM
    expect(screen.getByTestId("user-information")).toBeInTheDocument()
    expect(screen.getByTestId("change-password")).toBeInTheDocument()
    expect(screen.getByTestId("appearance")).toBeInTheDocument()
    expect(screen.getByTestId("delete-account")).toBeInTheDocument()
  })
})