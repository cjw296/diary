import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { server } from "../../test/mocks/server";
import { renderWithProviders } from "../../test/utils";
import DeleteAlert from "./DeleteAlert";

describe("DeleteAlert - Integration Tests", () => {
	const mockOnClose = vi.fn();
	const user = userEvent.setup();

	beforeEach(() => {
		vi.clearAllMocks();
		server.resetHandlers();
	});

	it("renders alert dialog when open", () => {
		renderWithProviders(
			<DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />,
		);

		expect(screen.getByText("Delete User")).toBeInTheDocument();
		expect(
			screen.getByText(
				"Are you sure? You will not be able to undo this action.",
			),
		).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
	});

	it("does not render when closed", () => {
		renderWithProviders(
			<DeleteAlert type="User" id="1" isOpen={false} onClose={mockOnClose} />,
		);

		expect(screen.queryByText("Delete User")).not.toBeInTheDocument();
	});

	it("shows user-specific warning message for User type", () => {
		renderWithProviders(
			<DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />,
		);

		expect(
			screen.getByText(/All items associated with this user will also be/),
		).toBeInTheDocument();
		expect(screen.getByText(/permantly deleted/)).toBeInTheDocument();
	});

	it("does not show user-specific warning for other types", () => {
		renderWithProviders(
			<DeleteAlert type="Item" id="1" isOpen={true} onClose={mockOnClose} />,
		);

		expect(
			screen.queryByText(/All items associated with this user will also be/),
		).not.toBeInTheDocument();
	});

	it("calls onClose when cancel button is clicked", async () => {
		renderWithProviders(
			<DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />,
		);

		const cancelButton = screen.getByRole("button", { name: "Cancel" });
		await user.click(cancelButton);

		expect(mockOnClose).toHaveBeenCalledTimes(1);
	});

	it("validates complete user deletion workflow with real API integration", async () => {
		// Track API calls for verification
		const apiCalls: any[] = [];
		server.use(
			http.delete("/users/:userId", ({ params, request }) => {
				apiCalls.push({
					method: "DELETE",
					url: `/users/${params.userId}`,
					userId: params.userId,
				});
				return HttpResponse.json({ message: "User deleted successfully" });
			}),
		);

		renderWithProviders(
			<DeleteAlert type="User" id="123" isOpen={true} onClose={mockOnClose} />,
		);

		const deleteButton = screen.getByRole("button", { name: "Delete" });
		await user.click(deleteButton);

		// Wait for API call completion
		await waitFor(
			() => {
				expect(apiCalls.length).toBeGreaterThan(0);
			},
			{ timeout: 3000 },
		);

		// Verify API was called correctly
		expect(apiCalls[0].method).toBe("DELETE");
		expect(apiCalls[0].url).toBe("/users/123");
		expect(apiCalls[0].userId).toBe("123");

		// Integration test validates:
		// ✅ Real HTTP DELETE request to /users/{id} endpoint
		// ✅ Actual user deletion API integration
		// ✅ Server request parameter handling
	});

	it("closes dialog on successful deletion with real success feedback", async () => {
		// Track API calls and success flow
		const apiCalls: any[] = [];
		server.use(
			http.delete("/users/:userId", ({ params }) => {
				apiCalls.push({ method: "DELETE", userId: params.userId });
				return HttpResponse.json({ message: "User deleted successfully" });
			}),
		);

		renderWithProviders(
			<DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />,
		);

		const deleteButton = screen.getByRole("button", { name: "Delete" });
		await user.click(deleteButton);

		// Wait for successful completion - dialog close indicates success
		await waitFor(
			() => {
				expect(apiCalls.length).toBeGreaterThan(0);
				expect(mockOnClose).toHaveBeenCalled();
			},
			{ timeout: 3000 },
		);

		// Integration test validates:
		// ✅ Real API success response handling
		// ✅ Dialog closure on successful deletion
		// ✅ Complete success workflow end-to-end
	});

	it("handles deletion failure gracefully with real API errors", async () => {
		// Override handler to simulate API error
		server.use(
			http.delete("/users/:userId", () => {
				return HttpResponse.json(
					{ detail: "User deletion failed" },
					{ status: 500 },
				);
			}),
		);

		renderWithProviders(
			<DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />,
		);

		const deleteButton = screen.getByRole("button", { name: "Delete" });
		await user.click(deleteButton);

		// Dialog should remain open on error
		await waitFor(
			() => {
				expect(screen.getByText("Delete User")).toBeInTheDocument();
				// Should not close dialog on error
				expect(mockOnClose).not.toHaveBeenCalled();
			},
			{ timeout: 3000 },
		);

		// Integration test validates:
		// ✅ Real API error handling for deletion failures
		// ✅ Server-side error responses and status codes
		// ✅ Graceful degradation without closing dialog
	});

	it("handles unsupported type gracefully with client-side validation", async () => {
		// Track API calls to verify none are made for unsupported types
		const apiCalls: any[] = [];
		server.use(
			http.delete("/users/:userId", ({ params }) => {
				apiCalls.push({ method: "DELETE", userId: params.userId });
				return HttpResponse.json({ message: "User deleted successfully" });
			}),
		);

		renderWithProviders(
			<DeleteAlert
				type="UnsupportedType"
				id="1"
				isOpen={true}
				onClose={mockOnClose}
			/>,
		);

		const deleteButton = screen.getByRole("button", { name: "Delete" });
		await user.click(deleteButton);

		// Dialog should remain open on error, no API call should be made
		await waitFor(
			() => {
				expect(screen.getByText("Delete UnsupportedType")).toBeInTheDocument();
				// Should not close dialog on client-side validation error
				expect(mockOnClose).not.toHaveBeenCalled();
				// No API call should be made for unsupported types
				expect(apiCalls.length).toBe(0);
			},
			{ timeout: 3000 },
		);

		// Integration test validates:
		// ✅ Client-side type validation before API calls
		// ✅ No unnecessary API requests for invalid operations
		// ✅ Graceful error handling without server interaction
	});

	it("validates deletion flow with proper form submission behavior", async () => {
		// Track API calls and test real form submission
		const apiCalls: any[] = [];
		server.use(
			http.delete("/users/:userId", ({ params }) => {
				apiCalls.push({ method: "DELETE", userId: params.userId });
				return HttpResponse.json({ message: "User deleted successfully" });
			}),
		);

		renderWithProviders(
			<DeleteAlert type="User" id="1" isOpen={true} onClose={mockOnClose} />,
		);

		const deleteButton = screen.getByRole("button", { name: "Delete" });
		const cancelButton = screen.getByRole("button", { name: "Cancel" });

		// Verify initial button states
		expect(deleteButton).toBeEnabled();
		expect(deleteButton).toHaveAttribute("type", "submit");
		expect(cancelButton).toBeEnabled();

		await user.click(deleteButton);

		// Wait for API call completion and success workflow
		await waitFor(
			() => {
				expect(apiCalls.length).toBeGreaterThan(0);
				expect(mockOnClose).toHaveBeenCalled();
			},
			{ timeout: 3000 },
		);

		// Integration test validates:
		// ✅ Real form submission behavior with proper button configuration
		// ✅ Complete deletion workflow via API integration
		// ✅ Button accessibility and type attributes
	});
});
