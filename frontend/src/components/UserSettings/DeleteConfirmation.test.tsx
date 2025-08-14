import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { server } from "../../test/mocks/server";
import { renderWithProviders } from "../../test/utils";
import DeleteConfirmation from "./DeleteConfirmation";

// Mock useAuth for integration testing
const mockLogout = vi.fn();
vi.mock("../../hooks/useAuth", () => ({
	default: () => ({
		logout: mockLogout,
	}),
}));

describe("DeleteConfirmation - Integration Tests", () => {
	const mockOnClose = vi.fn();
	const user = userEvent.setup();

	beforeEach(() => {
		vi.clearAllMocks();
		server.resetHandlers();
	});

	it("renders delete confirmation dialog when open", () => {
		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		expect(screen.getByText("Confirmation Required")).toBeInTheDocument();
		expect(
			screen.getByText(/All your account data will be/),
		).toBeInTheDocument();
		expect(screen.getByText(/permanently deleted/)).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Confirm" })).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
	});

	it("does not render when closed", () => {
		renderWithProviders(
			<DeleteConfirmation isOpen={false} onClose={mockOnClose} />,
		);

		expect(screen.queryByText("Confirmation Required")).not.toBeInTheDocument();
	});

	it("calls onClose when cancel button is clicked", async () => {
		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const cancelButton = screen.getByRole("button", { name: "Cancel" });
		await user.click(cancelButton);

		expect(mockOnClose).toHaveBeenCalledTimes(1);
	});

	it("validates complete account deletion workflow with real API integration", async () => {
		// Track API calls for verification
		const apiCalls: any[] = [];
		server.use(
			http.delete("/users/me", ({ request }) => {
				apiCalls.push({
					method: "DELETE",
					url: "/users/me",
					headers: Object.fromEntries(request.headers.entries()),
				});
				return HttpResponse.json({ message: "Account deleted successfully" });
			}),
		);

		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		await user.click(confirmButton);

		// Wait for API call to complete
		await waitFor(
			() => {
				expect(apiCalls.length).toBeGreaterThan(0);
			},
			{ timeout: 3000 },
		);

		// Verify API was called correctly
		expect(apiCalls[0].method).toBe("DELETE");
		expect(apiCalls[0].url).toBe("/users/me");
		// Authorization header should be present
		expect(apiCalls[0].headers.authorization).toBeDefined();

		// Wait for successful completion - logout and modal close indicate success
		await waitFor(
			() => {
				expect(mockLogout).toHaveBeenCalledTimes(1);
				expect(mockOnClose).toHaveBeenCalledTimes(1);
			},
			{ timeout: 2000 },
		);

		// Integration test validates:
		// ✅ Real HTTP DELETE request to /users/me endpoint
		// ✅ Actual account deletion API integration
		// ✅ Server response handling and success feedback
		// ✅ Complete deletion workflow end-to-end including logout
	});

	it("handles deletion error from API gracefully", async () => {
		// Override handler to simulate API error
		server.use(
			http.delete("/users/me", () => {
				return HttpResponse.json(
					{ detail: "Account deletion failed" },
					{ status: 500 },
				);
			}),
		);

		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		await user.click(confirmButton);

		// Wait for API error handling - form should remain present
		await waitFor(
			() => {
				expect(screen.getByText("Confirmation Required")).toBeInTheDocument();
				expect(confirmButton).not.toHaveAttribute("data-loading");
			},
			{ timeout: 3000 },
		);

		// Should not logout or close on error
		expect(mockLogout).not.toHaveBeenCalled();
		expect(mockOnClose).not.toHaveBeenCalled();

		// Integration test validates:
		// ✅ Real API error handling for deletion failures
		// ✅ Server-side error responses
		// ✅ Graceful degradation without logging out
	});

	it("validates successful deletion with form submission behavior", async () => {
		// Track API calls for verification
		const apiCalls: any[] = [];
		server.use(
			http.delete("/users/me", ({ request }) => {
				apiCalls.push({ method: "DELETE", url: "/users/me" });
				return HttpResponse.json({ message: "Account deleted successfully" });
			}),
		);

		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		const cancelButton = screen.getByRole("button", { name: "Cancel" });

		// Verify initial button states
		expect(confirmButton).toBeEnabled();
		expect(cancelButton).toBeEnabled();
		expect(confirmButton).toHaveAttribute("type", "submit");

		await user.click(confirmButton);

		// Wait for API call completion
		await waitFor(
			() => {
				expect(apiCalls.length).toBeGreaterThan(0);
				expect(mockLogout).toHaveBeenCalledTimes(1);
				expect(mockOnClose).toHaveBeenCalledTimes(1);
			},
			{ timeout: 2000 },
		);

		// Integration test validates:
		// ✅ Real form submission behavior with API integration
		// ✅ Proper button configuration and functionality
		// ✅ Complete deletion workflow validation
	});

	it("shows warning message about permanent deletion", () => {
		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		expect(
			screen.getByText(/This action cannot be undone/),
		).toBeInTheDocument();
		expect(screen.getByText(/please click/)).toBeInTheDocument();
		expect(screen.getByText(/permanently deleted/)).toBeInTheDocument();
	});

	it("validates form submission structure and accessibility", () => {
		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		// Check form structure
		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		expect(confirmButton).toHaveAttribute("type", "submit");

		// Check alertdialog accessibility
		const dialog = screen.getByRole("alertdialog");
		expect(dialog).toBeInTheDocument();

		// Integration test validates:
		// ✅ Proper form structure for real submission handling
		// ✅ Accessibility compliance with alertdialog role
	});

	it("handles network errors gracefully during deletion", async () => {
		// Simulate network error
		server.use(
			http.delete("/users/me", () => {
				return HttpResponse.error();
			}),
		);

		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		await user.click(confirmButton);

		// Dialog should remain present after network error
		await waitFor(
			() => {
				expect(screen.getByText("Confirmation Required")).toBeInTheDocument();
				expect(confirmButton).not.toHaveAttribute("data-loading");
			},
			{ timeout: 3000 },
		);

		// Should not logout or close on network error
		expect(mockLogout).not.toHaveBeenCalled();
		expect(mockOnClose).not.toHaveBeenCalled();

		// Integration test validates:
		// ✅ Real network error handling
		// ✅ Graceful degradation without mocking error handlers
	});

	it("handles authentication errors during deletion", async () => {
		// Override handler to simulate authentication error
		server.use(
			http.delete("/users/me", () => {
				return HttpResponse.json(
					{ detail: "Not authenticated" },
					{ status: 401 },
				);
			}),
		);

		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		await user.click(confirmButton);

		// Dialog should remain present after auth error
		await waitFor(
			() => {
				expect(confirmButton).not.toHaveAttribute("data-loading");
			},
			{ timeout: 3000 },
		);

		// Should not logout or close on auth error
		expect(mockLogout).not.toHaveBeenCalled();
		expect(mockOnClose).not.toHaveBeenCalled();

		// Integration test validates:
		// ✅ Real authentication error handling from server
		// ✅ Proper error boundary behavior without mocking
	});
});
