import { screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import EditUser from "./EditUser"
import type { UserPublic } from "../../client"

// Mock the UsersService
vi.mock("../../client", () => ({
  UsersService: {
    updateUser: vi.fn(),
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

describe("EditUser", () => {
  const mockOnClose = vi.fn()
  const mockUser: UserPublic = {
    id: 1,
    email: "test@example.com",
    full_name: "Test User",
    is_superuser: false,
    is_active: true,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders edit user modal when open", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    expect(screen.getByText("Edit User")).toBeInTheDocument()
    expect(screen.getByDisplayValue("test@example.com")).toBeInTheDocument()
    expect(screen.getByDisplayValue("Test User")).toBeInTheDocument()
    expect(screen.getAllByPlaceholderText("Password")).toHaveLength(2)
    expect(screen.getByText("Is superuser?")).toBeInTheDocument()
    expect(screen.getByText("Is active?")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument()
  })

  it("does not render when closed", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={false} onClose={mockOnClose} />)

    expect(screen.queryByText("Edit User")).not.toBeInTheDocument()
  })

  it("calls onClose when cancel button is clicked", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const cancelButton = screen.getByRole("button", { name: "Cancel" })
    fireEvent.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it("calls onClose when modal close button is clicked", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const closeButton = screen.getByLabelText("Close")
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it("pre-populates form with user data", () => {
    const superUser: UserPublic = {
      id: 2,
      email: "admin@example.com",
      full_name: "Admin User",
      is_superuser: true,
      is_active: true,
    }

    renderWithProviders(<EditUser user={superUser} isOpen={true} onClose={mockOnClose} />)

    expect(screen.getByDisplayValue("admin@example.com")).toBeInTheDocument()
    expect(screen.getByDisplayValue("Admin User")).toBeInTheDocument()
    expect(screen.getByLabelText("Is superuser?")).toBeChecked()
    expect(screen.getByLabelText("Is active?")).toBeChecked()
  })

  it("shows inactive user checkbox state", () => {
    const inactiveUser: UserPublic = {
      id: 3,
      email: "inactive@example.com",
      full_name: "Inactive User",
      is_superuser: false,
      is_active: false,
    }

    renderWithProviders(<EditUser user={inactiveUser} isOpen={true} onClose={mockOnClose} />)

    expect(screen.getByLabelText("Is superuser?")).not.toBeChecked()
    expect(screen.getByLabelText("Is active?")).not.toBeChecked()
  })

  it("allows editing email field", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const emailField = screen.getByDisplayValue("test@example.com")
    fireEvent.change(emailField, { target: { value: "newemail@example.com" } })

    expect(emailField).toHaveValue("newemail@example.com")
  })

  it("allows editing full name field", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const nameField = screen.getByDisplayValue("Test User")
    fireEvent.change(nameField, { target: { value: "New Name" } })

    expect(nameField).toHaveValue("New Name")
  })

  it("allows toggling checkboxes", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const superuserCheckbox = screen.getByLabelText("Is superuser?")
    const activeCheckbox = screen.getByLabelText("Is active?")

    // Initial state: not superuser, is active
    expect(superuserCheckbox).not.toBeChecked()
    expect(activeCheckbox).toBeChecked()

    // Toggle superuser
    fireEvent.click(superuserCheckbox)
    expect(superuserCheckbox).toBeChecked()

    // Toggle active
    fireEvent.click(activeCheckbox)
    expect(activeCheckbox).not.toBeChecked()
  })

  it("allows password input", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const passwordFields = screen.getAllByPlaceholderText("Password")
    
    fireEvent.change(passwordFields[0], { target: { value: "newpassword123" } })
    fireEvent.change(passwordFields[1], { target: { value: "newpassword123" } })

    expect(passwordFields[0]).toHaveValue("newpassword123")
    expect(passwordFields[1]).toHaveValue("newpassword123")
  })

  it("submits form with updated data", async () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const emailField = screen.getByDisplayValue("test@example.com")
    const nameField = screen.getByDisplayValue("Test User")
    const superuserCheckbox = screen.getByLabelText("Is superuser?")
    const submitButton = screen.getByRole("button", { name: "Save" })

    fireEvent.change(emailField, { target: { value: "updated@example.com" } })
    fireEvent.change(nameField, { target: { value: "Updated User" } })
    fireEvent.click(superuserCheckbox)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        expect.objectContaining({
          email: "updated@example.com",
          full_name: "Updated User",
          password: undefined,
          is_superuser: true,
          is_active: true,
        })
      )
    })
  })

  it("allows clearing password fields", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const passwordFields = screen.getAllByPlaceholderText("Password")

    // Set and then clear password
    fireEvent.change(passwordFields[0], { target: { value: "newpassword" } })
    fireEvent.change(passwordFields[0], { target: { value: "" } })

    expect(passwordFields[0]).toHaveValue("")
  })

  it("has form structure with proper elements", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    expect(screen.getByDisplayValue("test@example.com")).toBeInTheDocument()
    expect(screen.getByDisplayValue("Test User")).toBeInTheDocument()
    expect(screen.getAllByPlaceholderText("Password")).toHaveLength(2)
    expect(screen.getByLabelText("Is superuser?")).toBeInTheDocument()
    expect(screen.getByLabelText("Is active?")).toBeInTheDocument()
  })

  it("has email field with correct type", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const emailField = screen.getByDisplayValue("test@example.com")
    expect(emailField).toHaveAttribute("type", "email")
    expect(emailField).toHaveAttribute("name", "email")
  })

  it("has password fields with correct attributes", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const passwordFields = screen.getAllByPlaceholderText("Password")
    expect(passwordFields).toHaveLength(2)
    passwordFields.forEach(field => {
      expect(field).toHaveAttribute("type", "password")
    })
  })

  it("renders form with proper accessibility", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    // Check that the modal has proper role
    expect(screen.getByRole("dialog")).toBeInTheDocument()
    
    // Check form controls
    expect(screen.getByLabelText("Is superuser?")).toBeInTheDocument()
    expect(screen.getByLabelText("Is active?")).toBeInTheDocument()
  })

  it("has submit button with correct type", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    const submitButton = screen.getByRole("button", { name: "Save" })
    expect(submitButton).toHaveAttribute("type", "submit")
  })

  it("displays proper form sections", () => {
    renderWithProviders(<EditUser user={mockUser} isOpen={true} onClose={mockOnClose} />)

    // Check modal sections
    expect(screen.getByText("Edit User")).toBeInTheDocument() // Header
    expect(screen.getByDisplayValue("test@example.com")).toBeInTheDocument() // Body with form
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument() // Footer

    // Check close button
    expect(screen.getByLabelText("Close")).toBeInTheDocument()
  })

  it("handles user with no full name", () => {
    const userWithoutName: UserPublic = {
      id: 4,
      email: "noname@example.com",
      full_name: "",
      is_superuser: false,
      is_active: true,
    }

    renderWithProviders(<EditUser user={userWithoutName} isOpen={true} onClose={mockOnClose} />)

    // Check that the email is displayed correctly
    expect(screen.getByDisplayValue("noname@example.com")).toBeInTheDocument()
    
    // Check that the form has a full name field (it will be empty but present)
    const fullNameInput = screen.getByRole("textbox", { name: /full name/i })
    expect(fullNameInput).toHaveAttribute("type", "text")
  })
})