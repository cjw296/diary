import { screen, fireEvent, waitFor, act } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import UserInformation from "./UserInformation"

// Mock the UsersService
vi.mock("../../client", () => ({
  UsersService: {
    updateUserMe: vi.fn(),
  },
}))

// Mock useCustomToast
vi.mock("../../hooks/useCustomToast", () => ({
  default: () => vi.fn(),
}))

// Mock useAuth
const mockUseAuth = vi.fn()
vi.mock("../../hooks/useAuth", () => ({
  default: () => mockUseAuth(),
}))

// Mock utils
vi.mock("../../utils", () => ({
  emailPattern: {
    value: /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/,
    message: "Please enter a valid email",
  },
  handleError: vi.fn(),
}))

describe("UserInformation", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: "user@example.com",
        full_name: "John Doe",
        is_superuser: false,
      },
    })
  })

  it("renders user information in view mode", () => {
    renderWithProviders(<UserInformation />)

    expect(screen.getByText("User Information")).toBeInTheDocument()
    expect(screen.getByText("John Doe")).toBeInTheDocument()
    expect(screen.getByText("user@example.com")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Edit" })).toBeInTheDocument()
  })

  it("handles user with no full name", () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: "user@example.com",
        full_name: null,
        is_superuser: false,
      },
    })

    renderWithProviders(<UserInformation />)

    expect(screen.getByText("N/A")).toBeInTheDocument()
    expect(screen.getByText("user@example.com")).toBeInTheDocument()
  })

  it("enters edit mode when edit button is clicked", async () => {
    renderWithProviders(<UserInformation />)

    const editButton = screen.getByRole("button", { name: "Edit" })
    fireEvent.click(editButton)

    // Should show form inputs
    await waitFor(() => {
      expect(screen.getByDisplayValue("John Doe")).toBeInTheDocument()
      expect(screen.getByDisplayValue("user@example.com")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /Save/ })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument()
    })
  })

  it("cancels edit mode when cancel button is clicked", async () => {
    renderWithProviders(<UserInformation />)

    // Enter edit mode
    const editButton = screen.getByRole("button", { name: "Edit" })
    fireEvent.click(editButton)

    // Wait for edit mode
    await waitFor(() => {
      expect(screen.getByDisplayValue("John Doe")).toBeInTheDocument()
    })

    // Modify a field
    const nameInput = screen.getByDisplayValue("John Doe")
    fireEvent.change(nameInput, { target: { value: "Jane Doe" } })

    // Cancel editing
    const cancelButton = screen.getByRole("button", { name: "Cancel" })
    fireEvent.click(cancelButton)

    // Should be back in view mode with original values
    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Edit" })).toBeInTheDocument()
      expect(screen.queryByRole("button", { name: "Cancel" })).not.toBeInTheDocument()
    })
  })

  it("submits form with valid data", async () => {
    const { UsersService } = await import("../../client")
    const mockUpdateUser = vi.mocked(UsersService.updateUserMe)
    mockUpdateUser.mockResolvedValue({})

    renderWithProviders(<UserInformation />)

    // Enter edit mode
    const editButton = screen.getByRole("button", { name: "Edit" })
    await act(async () => {
      fireEvent.click(editButton)
    })

    // Wait for edit mode and modify the name
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Save/ })).toBeInTheDocument()
    })
    
    const nameInput = screen.getByDisplayValue("John Doe")
    await act(async () => {
      fireEvent.change(nameInput, { target: { value: "Jane Smith" } })
    })

    // Submit the form
    const saveButton = screen.getByRole("button", { name: /Save/ })
    await act(async () => {
      fireEvent.click(saveButton)
    })

    await waitFor(() => {
      expect(mockUpdateUser).toHaveBeenCalledWith({
        requestBody: expect.objectContaining({
          email: "user@example.com",
        }),
      })
    })
  })

  it("shows email validation error", async () => {
    renderWithProviders(<UserInformation />)

    // Enter edit mode
    const editButton = screen.getByRole("button", { name: "Edit" })
    fireEvent.click(editButton)

    // Enter invalid email
    const emailInput = screen.getByDisplayValue("user@example.com")
    fireEvent.change(emailInput, { target: { value: "invalid-email" } })
    fireEvent.blur(emailInput)

    await waitFor(() => {
      expect(screen.getByText("Please enter a valid email")).toBeInTheDocument()
    })
  })

  it("shows required email error when email is empty", async () => {
    renderWithProviders(<UserInformation />)

    // Enter edit mode
    const editButton = screen.getByRole("button", { name: "Edit" })
    fireEvent.click(editButton)

    // Clear email
    const emailInput = screen.getByDisplayValue("user@example.com")
    fireEvent.change(emailInput, { target: { value: "" } })
    fireEvent.blur(emailInput)

    await waitFor(() => {
      expect(screen.getByText("Email is required")).toBeInTheDocument()
    })
  })

  it("disables save button when form is not dirty", async () => {
    renderWithProviders(<UserInformation />)

    // Enter edit mode
    const editButton = screen.getByRole("button", { name: "Edit" })
    fireEvent.click(editButton)

    // Save button should be disabled when no changes are made
    await waitFor(() => {
      const saveButton = screen.getByRole("button", { name: /Save/ })
      expect(saveButton).toBeDisabled()
    })
  })

  it("enables save button when form is dirty and email is valid", async () => {
    renderWithProviders(<UserInformation />)

    // Enter edit mode
    const editButton = screen.getByRole("button", { name: "Edit" })
    fireEvent.click(editButton)

    // Wait for edit mode to activate
    await waitFor(() => {
      expect(screen.getByDisplayValue("John Doe")).toBeInTheDocument()
    })

    // Make a change
    const nameInput = screen.getByDisplayValue("John Doe")
    fireEvent.change(nameInput, { target: { value: "Jane Doe" } })

    // Save button should be enabled
    await waitFor(() => {
      const saveButton = screen.getByRole("button", { name: /Save/ })
      expect(saveButton).not.toBeDisabled()
    })
  })

  it("handles form submission error", async () => {
    const { UsersService } = await import("../../client")
    const { handleError } = await import("../../utils")
    const mockUpdateUser = vi.mocked(UsersService.updateUserMe)
    const mockHandleError = vi.mocked(handleError)
    
    mockUpdateUser.mockRejectedValue(new Error("Update failed"))

    renderWithProviders(<UserInformation />)

    // Enter edit mode and make changes
    const editButton = screen.getByRole("button", { name: "Edit" })
    await act(async () => {
      fireEvent.click(editButton)
    })

    const nameInput = screen.getByDisplayValue("John Doe")
    await act(async () => {
      fireEvent.change(nameInput, { target: { value: "Jane Smith" } })
    })

    // Submit the form
    const saveButton = screen.getByRole("button", { name: /Save/ })
    await act(async () => {
      fireEvent.click(saveButton)
    })

    await waitFor(() => {
      expect(mockHandleError).toHaveBeenCalled()
    })
  })

})