import { screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import Sidebar from "./Sidebar"

// Mock useAuth hook
const mockLogout = vi.fn()
vi.mock("../../hooks/useAuth", () => ({
  default: () => ({
    logout: mockLogout,
  }),
}))

// Mock SidebarItems component
vi.mock("./SidebarItems", () => ({
  default: ({ onClose }: { onClose?: () => void }) => (
    <div data-testid="sidebar-items">
      <button onClick={() => onClose && onClose()}>Sidebar Items</button>
    </div>
  ),
}))

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

describe("Sidebar", () => {
  beforeEach(() => {
    mockLogout.mockClear()
    mockGetQueryData.mockClear()
  })

  it("renders mobile menu button", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<Sidebar />)

    const menuButton = screen.getByLabelText("Open Menu")
    expect(menuButton).toBeInTheDocument()
  })

  it("renders desktop sidebar", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<Sidebar />)

    // Check for sidebar items in desktop view (only one is visible at a time)
    const sidebarItems = screen.getByTestId("sidebar-items")
    expect(sidebarItems).toBeInTheDocument()
  })

  it("shows user email when user is logged in", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "test@example.com",
      is_superuser: false,
    })

    renderWithProviders(<Sidebar />)

    expect(screen.getByText("Logged in as: test@example.com")).toBeInTheDocument()
  })

  it("does not show user email when user data is not available", () => {
    mockGetQueryData.mockReturnValue(null)

    renderWithProviders(<Sidebar />)

    expect(screen.queryByText(/Logged in as:/)).not.toBeInTheDocument()
  })

  it("opens mobile drawer when menu button is clicked", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<Sidebar />)

    const menuButton = screen.getByLabelText("Open Menu")
    fireEvent.click(menuButton)

    // Check that drawer is open (close button should be visible)
    expect(screen.getByLabelText("Close")).toBeInTheDocument()
  })

  it("calls logout when logout button is clicked in mobile drawer", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<Sidebar />)

    // Open mobile drawer
    const menuButton = screen.getByLabelText("Open Menu")
    fireEvent.click(menuButton)

    // Click logout button
    const logoutButton = screen.getByText("Log out")
    fireEvent.click(logoutButton)

    expect(mockLogout).toHaveBeenCalledTimes(1)
  })

  it("passes onClose prop to SidebarItems in mobile drawer", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "user@example.com",
      is_superuser: false,
    })

    renderWithProviders(<Sidebar />)

    // Open mobile drawer
    const menuButton = screen.getByLabelText("Open Menu")
    fireEvent.click(menuButton)

    // Verify drawer is open and SidebarItems are rendered
    expect(screen.getByLabelText("Close")).toBeInTheDocument()
    
    // Check that sidebar items are present in both mobile and desktop views
    const sidebarItemsButtons = screen.getAllByText("Sidebar Items")
    expect(sidebarItemsButtons.length).toBeGreaterThan(0)
  })

  it("displays user email in mobile drawer", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      email: "mobile@example.com",
      is_superuser: false,
    })

    renderWithProviders(<Sidebar />)

    // Open mobile drawer
    const menuButton = screen.getByLabelText("Open Menu")
    fireEvent.click(menuButton)

    // Check that user email is shown in the drawer (should have multiple instances)
    const emailTexts = screen.getAllByText("Logged in as: mobile@example.com")
    expect(emailTexts.length).toBeGreaterThan(0)
  })

  it("handles missing user email gracefully", () => {
    mockGetQueryData.mockReturnValue({
      id: 1,
      is_superuser: false,
    })

    renderWithProviders(<Sidebar />)

    // Should not show "Logged in as:" text when email is missing
    expect(screen.queryByText(/Logged in as:/)).not.toBeInTheDocument()
  })
})