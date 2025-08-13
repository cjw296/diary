import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import DeleteAccount from "./DeleteAccount"

// Mock the DeleteConfirmation component
vi.mock("./DeleteConfirmation", () => ({
  default: ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) =>
    isOpen ? <div data-testid="delete-confirmation-modal">Delete Confirmation Modal</div> : null,
}))

describe("DeleteAccount", () => {
  it("renders delete account section with heading and description", () => {
    renderWithProviders(<DeleteAccount />)

    expect(screen.getByText("Delete Account")).toBeInTheDocument()
    expect(
      screen.getByText(
        "Permanently delete your data and everything associated with your account."
      )
    ).toBeInTheDocument()
  })

  it("renders delete button", () => {
    renderWithProviders(<DeleteAccount />)

    const deleteButton = screen.getByText("Delete")
    expect(deleteButton).toBeInTheDocument()
  })

  it("opens confirmation modal when delete button is clicked", async () => {
    const user = userEvent.setup()
    renderWithProviders(<DeleteAccount />)

    const deleteButton = screen.getByText("Delete")
    await user.click(deleteButton)

    expect(screen.getByTestId("delete-confirmation-modal")).toBeInTheDocument()
  })

  it("modal is initially closed", () => {
    renderWithProviders(<DeleteAccount />)

    expect(screen.queryByTestId("delete-confirmation-modal")).not.toBeInTheDocument()
  })
})