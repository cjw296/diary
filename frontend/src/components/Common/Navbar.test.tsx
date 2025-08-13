import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import Navbar from "./Navbar"

// Mock modal component
const MockAddModal = vi.fn(({ isOpen, onClose }) => (
  isOpen ? <div data-testid="mock-modal">Mock Modal</div> : null
))

describe("Navbar", () => {
  it("renders add button with correct type", () => {
    renderWithProviders(<Navbar type="User" addModalAs={MockAddModal} />)
    
    expect(screen.getByText("Add User")).toBeInTheDocument()
  })

  it("opens modal when add button is clicked", async () => {
    const user = userEvent.setup()
    renderWithProviders(<Navbar type="Item" addModalAs={MockAddModal} />)
    
    const addButton = screen.getByText("Add Item")
    await user.click(addButton)

    expect(screen.getByTestId("mock-modal")).toBeInTheDocument()
  })

  it("passes isOpen and onClose props to modal component", async () => {
    const user = userEvent.setup()
    renderWithProviders(<Navbar type="Test" addModalAs={MockAddModal} />)
    
    // Initially closed
    expect(MockAddModal).toHaveBeenCalledWith(
      expect.objectContaining({
        isOpen: false,
        onClose: expect.any(Function)
      }),
      expect.anything()
    )

    // Open modal
    const addButton = screen.getByText("Add Test")
    await user.click(addButton)

    // Should be open
    expect(MockAddModal).toHaveBeenCalledWith(
      expect.objectContaining({
        isOpen: true,
        onClose: expect.any(Function)
      }),
      expect.anything()
    )
  })
})