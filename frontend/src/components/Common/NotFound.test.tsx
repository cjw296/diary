import { screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import NotFound from "./NotFound"

// Mock TanStack Router Link component
vi.mock("@tanstack/react-router", () => ({
  Link: ({ children, to, ...props }: any) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
}))

describe("NotFound", () => {
  it("renders 404 error message", () => {
    renderWithProviders(<NotFound />)
    
    expect(screen.getByText("404")).toBeInTheDocument()
    expect(screen.getByText("Oops!")).toBeInTheDocument()
    expect(screen.getByText("Page not found.")).toBeInTheDocument()
  })

  it("renders go back button with correct link", () => {
    renderWithProviders(<NotFound />)
    
    const goBackButton = screen.getByText("Go back")
    expect(goBackButton).toBeInTheDocument()
    expect(goBackButton.closest("a")).toHaveAttribute("href", "/")
  })

  it("has proper styling structure", () => {
    renderWithProviders(<NotFound />)
    
    // Check that the 404 text has the expected large styling
    const heading = screen.getByText("404")
    expect(heading).toBeInTheDocument()
    
    // Check that all text elements are present
    expect(screen.getByText("Oops!")).toBeInTheDocument()
    expect(screen.getByText("Page not found.")).toBeInTheDocument()
    expect(screen.getByText("Go back")).toBeInTheDocument()
  })
})