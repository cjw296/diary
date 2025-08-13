import { screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../../test/utils"
import { Route } from "./admin"

// Mock components
vi.mock("../../components/Admin/AddUser", () => ({
  default: () => <div data-testid="add-user-modal">Add User Modal</div>,
}))

vi.mock("../../components/Common/ActionsMenu", () => ({
  default: () => <div data-testid="actions-menu">Actions Menu</div>,
}))

vi.mock("../../components/Common/Navbar", () => ({
  default: ({ type }: { type: string }) => (
    <div data-testid="navbar">Navbar for {type}</div>
  ),
}))

vi.mock("../../components/Common/PaginationFooter.tsx", () => ({
  PaginationFooter: () => <div data-testid="pagination">Pagination</div>,
}))

// Mock router components
vi.mock("@tanstack/react-router", () => ({
  createFileRoute: (path: string) => (config: any) => ({
    ...config,
    options: { 
      component: config.component,
      validateSearch: config.validateSearch
    },
    useSearch: vi.fn().mockReturnValue({ page: 1 }),
    fullPath: path,
  }),
  useNavigate: vi.fn().mockReturnValue(vi.fn()),
}))

// Mock react-query
vi.mock("@tanstack/react-query", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@tanstack/react-query")>()
  return {
    ...actual,
    QueryClient: actual.QueryClient,
    useQuery: vi.fn().mockReturnValue({
      data: { data: [] },
      isPending: false,
      isPlaceholderData: false,
    }),
    useQueryClient: vi.fn().mockReturnValue({
      getQueryData: vi.fn().mockReturnValue({ id: 1, email: "admin@example.com", is_superuser: true }),
      prefetchQuery: vi.fn(),
    }),
  }
})

const Admin = Route.component

describe("Admin", () => {
  it("renders admin page with heading", () => {
    renderWithProviders(<Admin />)

    expect(screen.getByText("Users Management")).toBeInTheDocument()
    expect(screen.getByTestId("navbar")).toBeInTheDocument()
  })

  it("renders users table headers", () => {
    renderWithProviders(<Admin />)

    expect(screen.getByText("Full name")).toBeInTheDocument()
    expect(screen.getByText("Email")).toBeInTheDocument()
    expect(screen.getByText("Role")).toBeInTheDocument()
    expect(screen.getByText("Status")).toBeInTheDocument()
    expect(screen.getByText("Actions")).toBeInTheDocument()
  })

  it("renders table structure", () => {
    renderWithProviders(<Admin />)

    expect(screen.getByRole("table")).toBeInTheDocument()
    expect(screen.getByTestId("pagination")).toBeInTheDocument()
  })

  it("renders mocked components", () => {
    renderWithProviders(<Admin />)

    expect(screen.getByTestId("navbar")).toHaveTextContent("Navbar for User")
    expect(screen.getByTestId("pagination")).toBeInTheDocument()
  })

  it("has proper search validation schema", () => {
    expect(typeof Route.validateSearch).toBe("function")
  })
})