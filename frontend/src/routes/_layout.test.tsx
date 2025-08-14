import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../test/utils";
import { Route } from "./_layout";

// Mock useAuth hook
const mockUseAuth = vi.fn();
vi.mock("../hooks/useAuth", () => ({
	default: () => mockUseAuth(),
	isLoggedIn: vi.fn().mockReturnValue(true),
}));

// Mock components
vi.mock("../components/Common/Sidebar", () => ({
	default: () => <div data-testid="sidebar">Sidebar</div>,
}));

vi.mock("../components/Common/UserMenu", () => ({
	default: () => <div data-testid="user-menu">User Menu</div>,
}));

// Mock router components
vi.mock("@tanstack/react-router", () => ({
	Outlet: () => <div data-testid="outlet">Layout Outlet</div>,
	createFileRoute: (path: string) => (config: any) => ({
		...config,
		options: {
			component: config.component,
			beforeLoad: config.beforeLoad,
		},
	}),
	redirect: vi.fn(),
}));

const Layout = Route.component;

describe("Layout", () => {
	beforeEach(() => {
		mockUseAuth.mockClear();
	});

	it("renders layout components when not loading", () => {
		mockUseAuth.mockReturnValue({
			isLoading: false,
		});

		renderWithProviders(<Layout />);

		expect(screen.getByTestId("sidebar")).toBeInTheDocument();
		expect(screen.getByTestId("user-menu")).toBeInTheDocument();
		expect(screen.getByTestId("outlet")).toBeInTheDocument();
		expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
	});

	it("renders spinner when loading", () => {
		mockUseAuth.mockReturnValue({
			isLoading: true,
		});

		renderWithProviders(<Layout />);

		expect(screen.getByTestId("sidebar")).toBeInTheDocument();
		expect(screen.getByTestId("user-menu")).toBeInTheDocument();
		expect(screen.queryByTestId("outlet")).not.toBeInTheDocument();

		// Check for spinner by class or text
		expect(screen.getByText("Loading...")).toBeInTheDocument();
	});

	it("has beforeLoad guard configured", () => {
		expect(typeof Route.beforeLoad).toBe("function");
	});
});
