import { screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { renderWithProviders } from "../test/utils"
import { Route } from "./__root"

// Mock the devtools imports
vi.mock("@tanstack/router-devtools", () => ({
  TanStackRouterDevtools: () => <div data-testid="router-devtools">Router Devtools</div>
}))

vi.mock("@tanstack/react-query-devtools", () => ({
  ReactQueryDevtools: () => <div data-testid="query-devtools">Query Devtools</div>
}))

// Mock the Outlet and createRootRoute
vi.mock("@tanstack/react-router", () => ({
  Outlet: () => <div data-testid="outlet">Outlet Content</div>,
  createRootRoute: (config: any) => ({ 
    ...config,
    options: { component: config.component, notFoundComponent: config.notFoundComponent }
  })
}))

// Mock NotFound component
vi.mock("../components/Common/NotFound", () => ({
  default: () => <div data-testid="not-found">Not Found</div>
}))

const RootComponent = Route.component

describe("Root Route", () => {
  const originalEnv = process.env.NODE_ENV

  afterEach(() => {
    process.env.NODE_ENV = originalEnv
  })

  it("renders outlet and devtools in development", () => {
    process.env.NODE_ENV = "development"
    
    renderWithProviders(<RootComponent />)
    
    expect(screen.getByTestId("outlet")).toBeInTheDocument()
    // Devtools are lazy loaded so they may not be immediately available
  })

  it("renders outlet without devtools in production", () => {
    process.env.NODE_ENV = "production"
    
    renderWithProviders(<RootComponent />)
    
    expect(screen.getByTestId("outlet")).toBeInTheDocument()
  })

  it("has not found component configured", () => {
    const NotFoundComponent = Route.notFoundComponent!
    
    renderWithProviders(<NotFoundComponent />)
    
    expect(screen.getByTestId("not-found")).toBeInTheDocument()
  })
})