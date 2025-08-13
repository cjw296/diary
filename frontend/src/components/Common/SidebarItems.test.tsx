import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import SidebarItems from "./SidebarItems"

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

// Mock TanStack Router Link component
vi.mock("@tanstack/react-router", () => ({
  Link: ({ children, to, onClick, activeProps, ...props }: any) => (
    <a href={to} onClick={onClick} {...props}>
      {children}
    </a>
  ),
}))

// Mock Chakra UI color mode hook
vi.mock("@chakra-ui/react", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@chakra-ui/react")>()
  return {
    ...actual,
    useColorModeValue: (light: any, dark: any) => light,
  }
})

describe("SidebarItems", () => {
  const mockOnClose = vi.fn()

  beforeEach(() => {
    mockGetQueryData.mockClear()
    mockOnClose.mockClear()
  })

  it("renders default items for regular user", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<SidebarItems />)

    expect(screen.getByText("Dashboard")).toBeInTheDocument()
    expect(screen.getByText("User Settings")).toBeInTheDocument()
    expect(screen.queryByText("Admin")).not.toBeInTheDocument()
  })

  it("renders admin item for superuser", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "admin@example.com",
      is_superuser: true,
    })

    renderWithProviders(<SidebarItems />)

    expect(screen.getByText("Dashboard")).toBeInTheDocument()
    expect(screen.getByText("User Settings")).toBeInTheDocument()
    expect(screen.getByText("Admin")).toBeInTheDocument()
  })

  it("handles case when no user data is available", () => {
    mockGetQueryData.mockReturnValue(null)

    renderWithProviders(<SidebarItems />)

    expect(screen.getByText("Dashboard")).toBeInTheDocument()
    expect(screen.getByText("User Settings")).toBeInTheDocument()
    expect(screen.queryByText("Admin")).not.toBeInTheDocument()
  })

  it("calls onClose when item is clicked", async () => {
    const user = userEvent.setup()
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<SidebarItems onClose={mockOnClose} />)

    const dashboardLink = screen.getByText("Dashboard")
    await user.click(dashboardLink)

    expect(mockOnClose).toHaveBeenCalledOnce()
  })

  it("has correct links for each item", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "admin@example.com",
      is_superuser: true,
    })

    renderWithProviders(<SidebarItems />)

    const dashboardLink = screen.getByText("Dashboard").closest("a")
    const settingsLink = screen.getByText("User Settings").closest("a")
    const adminLink = screen.getByText("Admin").closest("a")

    expect(dashboardLink).toHaveAttribute("href", "/")
    expect(settingsLink).toHaveAttribute("href", "/settings")
    expect(adminLink).toHaveAttribute("href", "/admin")
  })

  it("renders icons for each item", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "admin@example.com", 
      is_superuser: true,
    })

    renderWithProviders(<SidebarItems />)

    // Check that SVG icons are rendered (they will be rendered as SVG elements)
    const links = screen.getAllByRole("link")
    expect(links).toHaveLength(3)
    
    // Each link should contain an SVG
    links.forEach(link => {
      expect(link.querySelector("svg")).toBeInTheDocument()
    })
  })
})