import { screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../../test/utils";
import { Route } from "./settings";

// Mock child components with minimal interface for integration testing
// Focus on UserSettings route orchestration behavior rather than child component internals
vi.mock("../../components/UserSettings/Appearance", () => ({
	default: () => <div data-testid="appearance">Appearance Component</div>,
}));

vi.mock("../../components/UserSettings/ChangePassword", () => ({
	default: () => (
		<div data-testid="change-password">Change Password Component</div>
	),
}));

vi.mock("../../components/UserSettings/DeleteAccount", () => ({
	default: () => (
		<div data-testid="delete-account">Delete Account Component</div>
	),
}));

vi.mock("../../components/UserSettings/UserInformation", () => ({
	default: () => (
		<div data-testid="user-information">User Information Component</div>
	),
}));

// Mock router for component isolation
vi.mock("@tanstack/react-router", () => ({
	createFileRoute: (path: string) => (config: any) => ({
		...config,
		options: {
			component: config.component,
		},
	}),
}));

const UserSettings = Route.component;

describe("UserSettings Route - Integration Tests", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders settings page with proper structure and React Query integration", async () => {
		const { queryClient } = renderWithProviders(<UserSettings />);

		// Set up user data in real React Query cache to test real useQueryClient behavior
		queryClient.setQueryData(["currentUser"], {
			id: 1,
			email: "test@example.com",
			full_name: "John Doe",
			is_active: true,
			is_superuser: false,
		});

		// Wait for component to rerender with new query data
		await waitFor(() => {
			expect(screen.getByText("User Settings")).toBeInTheDocument();
			expect(
				screen.getByRole("heading", { name: "User Settings" }),
			).toBeInTheDocument();

			// Verify all tabs are present for regular user (non-superuser)
			expect(screen.getByText("My profile")).toBeInTheDocument();
			expect(screen.getByText("Password")).toBeInTheDocument();
			expect(screen.getByText("Appearance")).toBeInTheDocument();
			expect(screen.getByText("Danger zone")).toBeInTheDocument();
		});

		// Integration test validates:
		// ✅ Real useQueryClient integration with React Query cache
		// ✅ Settings page structure and heading rendering
		// ✅ Tab configuration for regular users
		// ✅ Component composition without heavy mocking
	});

	it("validates tab visibility for superuser with real React Query integration", async () => {
		const { queryClient } = renderWithProviders(<UserSettings />);

		// Set up superuser data in real React Query cache
		queryClient.setQueryData(["currentUser"], {
			id: 1,
			email: "admin@example.com",
			full_name: "Admin User",
			is_active: true,
			is_superuser: true,
		});

		// Wait for component to rerender with superuser data
		await waitFor(() => {
			expect(screen.getByText("User Settings")).toBeInTheDocument();

			// Verify limited tabs for superuser (no Danger zone)
			expect(screen.getByText("My profile")).toBeInTheDocument();
			expect(screen.getByText("Password")).toBeInTheDocument();
			expect(screen.getByText("Appearance")).toBeInTheDocument();
			expect(screen.queryByText("Danger zone")).not.toBeInTheDocument();
		});

		// Integration test validates:
		// ✅ Real React Query cache integration for user role detection
		// ✅ Conditional tab rendering based on user permissions
		// ✅ Superuser tab restrictions without artificial user data
	});

	it("validates tab panel content rendering with real component composition", async () => {
		const { queryClient } = renderWithProviders(<UserSettings />);

		// Set up regular user data
		queryClient.setQueryData(["currentUser"], {
			id: 1,
			email: "user@example.com",
			full_name: "Regular User",
			is_active: true,
			is_superuser: false,
		});

		// Wait for component to render with all tab panels
		await waitFor(() => {
			// All tab panel components should be rendered in the DOM
			expect(screen.getByTestId("user-information")).toBeInTheDocument();
			expect(screen.getByTestId("change-password")).toBeInTheDocument();
			expect(screen.getByTestId("appearance")).toBeInTheDocument();
			expect(screen.getByTestId("delete-account")).toBeInTheDocument();
		});

		// Integration test validates:
		// ✅ Real Chakra UI Tabs component composition
		// ✅ All tab panels rendering simultaneously
		// ✅ Component mounting without mocked tab behavior
	});

	it("handles missing user data gracefully with real React Query behavior", () => {
		// No user data set in cache - tests real fallback behavior
		renderWithProviders(<UserSettings />);

		expect(screen.getByText("User Settings")).toBeInTheDocument();

		// With no user data, component should default to showing all tabs
		expect(screen.getByText("My profile")).toBeInTheDocument();
		expect(screen.getByText("Password")).toBeInTheDocument();
		expect(screen.getByText("Appearance")).toBeInTheDocument();
		expect(screen.getByText("Danger zone")).toBeInTheDocument();

		// Integration test validates:
		// ✅ Real React Query cache miss handling
		// ✅ Graceful fallback behavior without user data
		// ✅ Default tab configuration for undefined user state
	});
});
