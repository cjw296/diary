import { screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { renderWithProviders } from "../../test/utils"
import DeleteAlert from "./DeleteAlert"
import { UsersService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

// Mock the UsersService
vi.mock("../../client", () => ({
  UsersService: {
    deleteUser: vi.fn(),
  },
}))

// Mock useCustomToast
vi.mock("../../hooks/useCustomToast", () => ({
  default: () => vi.fn(),
}))

describe("DeleteAlert", () => {
  const mockOnClose = vi.fn()
  
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders alert dialog when open", () => {
    renderWithProviders(
      <DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />
    )

    expect(screen.getByText("Delete User")).toBeInTheDocument()
    expect(screen.getByText("Are you sure? You will not be able to undo this action.")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument()
  })

  it("does not render when closed", () => {
    renderWithProviders(
      <DeleteAlert type="User" id="1" isOpen={false} onClose={mockOnClose} />
    )

    expect(screen.queryByText("Delete User")).not.toBeInTheDocument()
  })

  it("shows user-specific warning message for User type", () => {
    renderWithProviders(
      <DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />
    )

    expect(screen.getByText(/All items associated with this user will also be/)).toBeInTheDocument()
    expect(screen.getByText(/permantly deleted/)).toBeInTheDocument()
  })

  it("does not show user-specific warning for other types", () => {
    renderWithProviders(
      <DeleteAlert type="Item" id="1" isOpen={true} onClose={mockOnClose} />
    )

    expect(screen.queryByText(/All items associated with this user will also be/)).not.toBeInTheDocument()
  })

  it("calls onClose when cancel button is clicked", () => {
    renderWithProviders(
      <DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />
    )

    const cancelButton = screen.getByRole("button", { name: "Cancel" })
    fireEvent.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it("calls UsersService.deleteUser when delete is submitted for User type", async () => {
    const mockDeleteUser = vi.mocked(UsersService.deleteUser)
    mockDeleteUser.mockResolvedValue({})

    renderWithProviders(
      <DeleteAlert type="User" id="123" isOpen={true} onClose={mockOnClose} />
    )

    const deleteButton = screen.getByRole("button", { name: "Delete" })
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(mockDeleteUser).toHaveBeenCalledWith({ userId: "123" })
    })
  })

  it("closes dialog on successful deletion", async () => {
    const mockDeleteUser = vi.mocked(UsersService.deleteUser)
    mockDeleteUser.mockResolvedValue({})

    renderWithProviders(
      <DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />
    )

    const deleteButton = screen.getByRole("button", { name: "Delete" })
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  it("handles deletion failure gracefully", async () => {
    const mockDeleteUser = vi.mocked(UsersService.deleteUser)
    mockDeleteUser.mockRejectedValue(new Error("Delete failed"))

    renderWithProviders(
      <DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />
    )

    const deleteButton = screen.getByRole("button", { name: "Delete" })
    fireEvent.click(deleteButton)

    // Dialog should remain open on error
    await waitFor(() => {
      expect(screen.getByText("Delete User")).toBeInTheDocument()
    })
  })

  it("handles unsupported type gracefully", async () => {    
    renderWithProviders(
      <DeleteAlert type="UnsupportedType" id="1" isOpen={true} onClose={mockOnClose} />
    )

    const deleteButton = screen.getByRole("button", { name: "Delete" })
    fireEvent.click(deleteButton)

    // Dialog should remain open on error
    await waitFor(() => {
      expect(screen.getByText("Delete UnsupportedType")).toBeInTheDocument()
    })
  })

  it("disables buttons when submitting", async () => {
    const mockDeleteUser = vi.mocked(UsersService.deleteUser)
    // Mock a delayed response to test loading state
    mockDeleteUser.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    renderWithProviders(
      <DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />
    )

    const deleteButton = screen.getByRole("button", { name: "Delete" })
    const cancelButton = screen.getByRole("button", { name: "Cancel" })

    fireEvent.click(deleteButton)

    // Check that buttons are disabled during submission
    await waitFor(() => {
      expect(cancelButton).toBeDisabled()
      expect(deleteButton).toHaveAttribute("data-loading")
    })
  })
})