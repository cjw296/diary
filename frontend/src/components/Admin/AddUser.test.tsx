import { screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import AddUser from "./AddUser"

// Mock the UsersService
vi.mock("../../client", () => ({
  UsersService: {
    createUser: vi.fn(),
  },
}))

// Mock useCustomToast
const mockShowToast = vi.fn()
vi.mock("../../hooks/useCustomToast", () => ({
  default: () => mockShowToast,
}))

// Mock utils
vi.mock("../../utils", () => ({
  emailPattern: {
    value: /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/,
    message: "Please enter a valid email",
  },
  handleError: vi.fn(),
}))

// Mock react-query
const mockMutate = vi.fn()
const mockQueryInvalidate = vi.fn()

vi.mock("@tanstack/react-query", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@tanstack/react-query")>()
  return {
    ...actual,
    useMutation: vi.fn(() => ({
      mutate: mockMutate,
    })),
    useQueryClient: vi.fn(() => ({
      invalidateQueries: mockQueryInvalidate,
    })),
  }
})

describe("AddUser", () => {
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders add user modal when open", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    expect(screen.getByText("Add User")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("Full name")).toBeInTheDocument()
    expect(screen.getAllByPlaceholderText("Password")).toHaveLength(2)
    expect(screen.getByText("Is superuser?")).toBeInTheDocument()
    expect(screen.getByText("Is active?")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument()
  })

  it("does not render when closed", () => {
    renderWithProviders(<AddUser isOpen={false} onClose={mockOnClose} />)

    expect(screen.queryByText("Add User")).not.toBeInTheDocument()
  })

  it("calls onClose when cancel button is clicked", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const cancelButton = screen.getByRole("button", { name: "Cancel" })
    fireEvent.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it("calls onClose when modal close button is clicked", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const closeButton = screen.getByLabelText("Close")
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it("has email field with required attribute", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const emailField = screen.getByPlaceholderText("Email")
    expect(emailField).toHaveAttribute("required")
    expect(emailField).toHaveAttribute("type", "email")
  })

  it("allows user input in email field", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const emailField = screen.getByPlaceholderText("Email")
    
    fireEvent.change(emailField, { target: { value: "test@example.com" } })
    expect(emailField).toHaveValue("test@example.com")
  })

  it("has password fields with required attributes", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const passwordFields = screen.getAllByPlaceholderText("Password")
    expect(passwordFields).toHaveLength(2)
    expect(passwordFields[0]).toHaveAttribute("required")
    expect(passwordFields[0]).toHaveAttribute("type", "password")
    expect(passwordFields[1]).toHaveAttribute("required") 
    expect(passwordFields[1]).toHaveAttribute("type", "password")
  })

  it("allows user input in password fields", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const passwordFields = screen.getAllByPlaceholderText("Password")
    
    fireEvent.change(passwordFields[0], { target: { value: "password123" } })
    fireEvent.change(passwordFields[1], { target: { value: "password123" } })
    
    expect(passwordFields[0]).toHaveValue("password123")
    expect(passwordFields[1]).toHaveValue("password123")
  })

  it("renders checkbox controls properly", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const superuserCheckbox = screen.getByLabelText("Is superuser?")
    const activeCheckbox = screen.getByLabelText("Is active?")
    
    expect(superuserCheckbox).toHaveAttribute("type", "checkbox")
    expect(activeCheckbox).toHaveAttribute("type", "checkbox")
    expect(superuserCheckbox).not.toBeChecked()
    expect(activeCheckbox).not.toBeChecked()
  })

  it("has form structure with proper elements", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    // Check that all form elements exist
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("Full name")).toBeInTheDocument()
    expect(screen.getAllByPlaceholderText("Password")).toHaveLength(2)
    expect(screen.getByLabelText("Is superuser?")).toBeInTheDocument()
    expect(screen.getByLabelText("Is active?")).toBeInTheDocument()
  })

  it("submits form with valid data", async () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const emailField = screen.getByPlaceholderText("Email")
    const fullNameField = screen.getByPlaceholderText("Full name")
    const passwordFields = screen.getAllByPlaceholderText("Password")
    const passwordField = passwordFields[0]
    const confirmPasswordField = passwordFields[1]
    const superuserCheckbox = screen.getByLabelText("Is superuser?")
    const activeCheckbox = screen.getByLabelText("Is active?")
    const submitButton = screen.getByRole("button", { name: "Save" })

    fireEvent.change(emailField, { target: { value: "user@example.com" } })
    fireEvent.change(fullNameField, { target: { value: "Test User" } })
    fireEvent.change(passwordField, { target: { value: "password123" } })
    fireEvent.change(confirmPasswordField, { target: { value: "password123" } })
    fireEvent.click(superuserCheckbox)
    fireEvent.click(activeCheckbox)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith({
        email: "user@example.com",
        full_name: "Test User",
        password: "password123",
        confirm_password: "password123",
        is_superuser: true,
        is_active: true,
      })
    })
  })

  it("handles checkbox states correctly", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const superuserCheckbox = screen.getByLabelText("Is superuser?")
    const activeCheckbox = screen.getByLabelText("Is active?")

    // Initially unchecked
    expect(superuserCheckbox).not.toBeChecked()
    expect(activeCheckbox).not.toBeChecked()

    // Check superuser
    fireEvent.click(superuserCheckbox)
    expect(superuserCheckbox).toBeChecked()

    // Check active
    fireEvent.click(activeCheckbox)
    expect(activeCheckbox).toBeChecked()

    // Uncheck superuser
    fireEvent.click(superuserCheckbox)
    expect(superuserCheckbox).not.toBeChecked()
  })

  it("has submit button with correct type", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const submitButton = screen.getByRole("button", { name: "Save" })
    expect(submitButton).toHaveAttribute("type", "submit")
  })

  it("renders form with proper accessibility", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    // Check that form fields have proper labels and placeholders
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("Full name")).toBeInTheDocument()
    expect(screen.getAllByPlaceholderText("Password")).toHaveLength(2)

    // Check that the modal has proper role
    expect(screen.getByRole("dialog")).toBeInTheDocument()
  })

  it("handles form submission as form element", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    const submitButton = screen.getByRole("button", { name: "Save" })
    expect(submitButton).toHaveAttribute("type", "submit")
  })

  it("displays all form sections", () => {
    renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />)

    // Check modal sections
    expect(screen.getByText("Add User")).toBeInTheDocument() // Header
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument() // Body with form
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument() // Footer

    // Check all form controls
    expect(screen.getByText("Is superuser?")).toBeInTheDocument()
    expect(screen.getByText("Is active?")).toBeInTheDocument()
  })
})