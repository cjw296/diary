import { screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import ActionsMenu from "./ActionsMenu"

// Mock the child components
vi.mock("../Admin/EditUser", () => ({
  default: ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => (
    <div data-testid="edit-user-modal">
      <div>Edit User Modal {isOpen ? "Open" : "Closed"}</div>
      <button onClick={onClose}>Close</button>
    </div>
  ),
}))

vi.mock("./DeleteAlert", () => ({
  default: ({ type, id, isOpen, onClose }: { type: string; id: number; isOpen: boolean; onClose: () => void }) => (
    <div data-testid="delete-alert-modal">
      <div>Delete {type} Modal {isOpen ? "Open" : "Closed"} (ID: {id})</div>
      <button onClick={onClose}>Close</button>
    </div>
  ),
}))

const mockUserValue = {
  id: 1,
  email: "user@example.com",
  is_superuser: false,
  full_name: "Test User",
}

const mockItemValue = {
  id: 2,
  title: "Test Item",
  description: "Test Description",
}

describe("ActionsMenu", () => {
  it("renders menu button and items", () => {
    renderWithProviders(<ActionsMenu type="User" value={mockUserValue} />)

    const menuButton = screen.getByRole("button", { expanded: false })
    expect(menuButton).toBeInTheDocument()
    expect(menuButton).not.toBeDisabled()
  })

  it("renders disabled menu button when disabled prop is true", () => {
    renderWithProviders(<ActionsMenu type="User" value={mockUserValue} disabled={true} />)

    const menuButton = screen.getByRole("button", { expanded: false })
    expect(menuButton).toBeDisabled()
  })

  it("opens edit modal when edit menu item is clicked", async () => {
    renderWithProviders(<ActionsMenu type="User" value={mockUserValue} />)

    const menuButton = screen.getByRole("button", { expanded: false })
    fireEvent.click(menuButton)

    // Wait for menu items to appear
    const editMenuItem = await screen.findByText("Edit User")
    expect(editMenuItem).toBeInTheDocument()

    fireEvent.click(editMenuItem)

    // Check that edit modal is opened
    expect(screen.getByText("Edit User Modal Open")).toBeInTheDocument()
  })

  it("opens delete modal when delete menu item is clicked", async () => {
    renderWithProviders(<ActionsMenu type="Item" value={mockItemValue} />)

    const menuButton = screen.getByRole("button", { expanded: false })
    fireEvent.click(menuButton)

    // Wait for menu items to appear
    const deleteMenuItem = await screen.findByText("Delete Item")
    expect(deleteMenuItem).toBeInTheDocument()

    fireEvent.click(deleteMenuItem)

    // Check that delete modal is opened
    expect(screen.getByText("Delete Item Modal Open (ID: 2)")).toBeInTheDocument()
  })

  it("displays menu items with correct type", async () => {
    renderWithProviders(<ActionsMenu type="Product" value={mockItemValue} />)

    const menuButton = screen.getByRole("button", { expanded: false })
    fireEvent.click(menuButton)

    expect(await screen.findByText("Edit Product")).toBeInTheDocument()
    expect(await screen.findByText("Delete Product")).toBeInTheDocument()
  })

  it("renders EditUser modal with correct props", () => {
    renderWithProviders(<ActionsMenu type="User" value={mockUserValue} />)

    // Modal should be closed initially
    expect(screen.getByText("Edit User Modal Closed")).toBeInTheDocument()
  })

  it("renders Delete modal with correct props", () => {
    renderWithProviders(<ActionsMenu type="User" value={mockUserValue} />)

    // Modal should be closed initially
    expect(screen.getByText("Delete User Modal Closed (ID: 1)")).toBeInTheDocument()
  })
})