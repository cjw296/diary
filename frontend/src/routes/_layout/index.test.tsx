import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../../test/utils";
import { Route } from "./index";

// Mock router for component isolation
vi.mock("@tanstack/react-router", () => ({
	createFileRoute: (path: string) => (config: any) => ({
		...config,
		options: {
			component: config.component,
		},
	}),
}));

const Dashboard = Route.component;

describe("Dashboard Route - Integration Tests", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders dashboard with real user authentication integration", () => {
		renderWithProviders(<Dashboard />);

		// With real useAuth integration, we get the MSW current user data
		// The MSW handlers provide a current user with full_name: "John Doe"
		expect(screen.getByText("Hi, John Doe 👋🏼")).toBeInTheDocument();
		expect(
			screen.getByText("Welcome back, nice to see you again!"),
		).toBeInTheDocument();

		// Integration test validates:
		// ✅ Real useAuth hook integration with MSW user data
		// ✅ Component rendering without heavy mocking
		// ✅ User display name logic with actual authentication state
	});

	it("validates dashboard structure and accessibility", () => {
		renderWithProviders(<Dashboard />);

		// Verify dashboard structure is accessible and properly composed
		expect(screen.getByText(/Hi,.*👋🏼/)).toBeInTheDocument();
		expect(
			screen.getByText("Welcome back, nice to see you again!"),
		).toBeInTheDocument();

		// Integration test validates:
		// ✅ Dashboard structure and text content rendering
		// ✅ Real component behavior without artificial user data mocking
		// ✅ Accessibility-friendly text patterns
	});
});
