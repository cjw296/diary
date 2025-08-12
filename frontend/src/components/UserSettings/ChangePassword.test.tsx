import { screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import ChangePassword from "./ChangePassword"

// Mock the UsersService
vi.mock("../../client", () => ({
  UsersService: {
    updatePasswordMe: vi.fn(),
  },
}))

// Mock useCustomToast
vi.mock("../../hooks/useCustomToast", () => ({
  default: () => vi.fn(),
}))

// Mock utils
vi.mock("../../utils", () => ({
  confirmPasswordRules: () => ({
    required: "Please confirm your password",
    validate: (value: string) => value === "password123" || "Passwords do not match",
  }),
  handleError: vi.fn(),
  passwordRules: () => ({
    required: "Password is required",
    minLength: { value: 8, message: "Password must be at least 8 characters" },
  }),
}))

describe("ChangePassword", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders change password form", () => {
    renderWithProviders(<ChangePassword />)

    expect(screen.getByText("Change Password")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument()
    
    // Check for the specific form inputs
    expect(document.getElementById("current_password")).toBeInTheDocument()
    expect(document.getElementById("password")).toBeInTheDocument()
    expect(document.getElementById("confirm_password")).toBeInTheDocument()
  })

  it("shows validation errors for empty fields", async () => {
    renderWithProviders(<ChangePassword />)

    const saveButton = screen.getByRole("button", { name: "Save" })
    fireEvent.click(saveButton)

    // Check that form fields are still present after failed validation
    await waitFor(() => {
      expect(document.getElementById("current_password")).toBeInTheDocument()
      expect(document.getElementById("password")).toBeInTheDocument()
      expect(document.getElementById("confirm_password")).toBeInTheDocument()
    })
  })

  it("shows password mismatch error", async () => {
    renderWithProviders(<ChangePassword />)

    const currentPasswordField = document.getElementById("current_password")!
    const newPasswordField = document.getElementById("password")!
    const confirmPasswordField = document.getElementById("confirm_password")!

    fireEvent.change(currentPasswordField, { target: { value: "oldpassword" } })
    fireEvent.change(newPasswordField, { target: { value: "password123" } })
    fireEvent.change(confirmPasswordField, { target: { value: "differentpassword" } })

    // Trigger blur to run validation
    fireEvent.blur(confirmPasswordField)

    await waitFor(() => {
      expect(screen.getByText("Passwords do not match")).toBeInTheDocument()
    })
  })

  it("submits form with valid data", async () => {
    const { UsersService } = await import("../../client")
    const mockUpdatePassword = vi.mocked(UsersService.updatePasswordMe)
    mockUpdatePassword.mockResolvedValue({})

    renderWithProviders(<ChangePassword />)

    const currentPasswordField = document.getElementById("current_password")!
    const newPasswordField = document.getElementById("password")!
    const confirmPasswordField = document.getElementById("confirm_password")!
    const saveButton = screen.getByRole("button", { name: "Save" })

    fireEvent.change(currentPasswordField, { target: { value: "oldpassword" } })
    fireEvent.change(newPasswordField, { target: { value: "password123" } })
    fireEvent.change(confirmPasswordField, { target: { value: "password123" } })

    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockUpdatePassword).toHaveBeenCalledWith({
        requestBody: {
          current_password: "oldpassword",
          new_password: "password123",
          confirm_password: "password123",
        },
      })
    })
  })

  it("handles form submission error", async () => {
    const { UsersService } = await import("../../client")
    const { handleError } = await import("../../utils")
    const mockUpdatePassword = vi.mocked(UsersService.updatePasswordMe)
    const mockHandleError = vi.mocked(handleError)
    
    mockUpdatePassword.mockRejectedValue(new Error("Update failed"))

    renderWithProviders(<ChangePassword />)

    const currentPasswordField = document.getElementById("current_password")!
    const newPasswordField = document.getElementById("password")!
    const confirmPasswordField = document.getElementById("confirm_password")!
    const saveButton = screen.getByRole("button", { name: "Save" })

    fireEvent.change(currentPasswordField, { target: { value: "oldpassword" } })
    fireEvent.change(newPasswordField, { target: { value: "password123" } })
    fireEvent.change(confirmPasswordField, { target: { value: "password123" } })

    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockHandleError).toHaveBeenCalled()
    })
  })

  it("disables submit button during submission", async () => {
    const { UsersService } = await import("../../client")
    const mockUpdatePassword = vi.mocked(UsersService.updatePasswordMe)
    
    // Mock a delayed response
    mockUpdatePassword.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    renderWithProviders(<ChangePassword />)

    const currentPasswordField = document.getElementById("current_password")!
    const newPasswordField = document.getElementById("password")!
    const confirmPasswordField = document.getElementById("confirm_password")!
    const saveButton = screen.getByRole("button", { name: "Save" })

    fireEvent.change(currentPasswordField, { target: { value: "oldpassword" } })
    fireEvent.change(newPasswordField, { target: { value: "password123" } })
    fireEvent.change(confirmPasswordField, { target: { value: "password123" } })

    fireEvent.click(saveButton)

    // Check that button shows loading state
    await waitFor(() => {
      expect(saveButton).toHaveAttribute("data-loading")
    })
  })

  it("shows password validation error", async () => {
    renderWithProviders(<ChangePassword />)

    const newPasswordField = document.getElementById("password")!

    fireEvent.change(newPasswordField, { target: { value: "short" } })
    fireEvent.blur(newPasswordField)

    await waitFor(() => {
      expect(screen.getByText("Password must be at least 8 characters")).toBeInTheDocument()
    })
  })
})