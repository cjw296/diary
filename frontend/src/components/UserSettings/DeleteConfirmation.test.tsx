import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../../test/utils";
import DeleteConfirmation from "./DeleteConfirmation";

// Mock the UsersService
vi.mock("../../client", () => ({
	UsersService: {
		deleteUserMe: vi.fn(),
	},
}));

// Mock useCustomToast
vi.mock("../../hooks/useCustomToast", () => ({
	default: () => vi.fn(),
}));

// Mock useAuth
const mockLogout = vi.fn();
vi.mock("../../hooks/useAuth", () => ({
	default: () => ({
		logout: mockLogout,
	}),
}));

// Mock utils
vi.mock("../../utils", () => ({
	handleError: vi.fn(),
}));

describe("DeleteConfirmation", () => {
	const mockOnClose = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
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

	it("calls onClose when cancel button is clicked", () => {
		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const cancelButton = screen.getByRole("button", { name: "Cancel" });
		fireEvent.click(cancelButton);

		expect(mockOnClose).toHaveBeenCalledTimes(1);
	});

	it("submits deletion and handles success", async () => {
		const { UsersService } = await import("../../client");
		const mockDeleteUser = vi.mocked(UsersService.deleteUserMe);
		mockDeleteUser.mockResolvedValue({});

		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		fireEvent.click(confirmButton);

		await waitFor(() => {
			expect(mockDeleteUser).toHaveBeenCalledTimes(1);
		});

		await waitFor(() => {
			expect(mockLogout).toHaveBeenCalledTimes(1);
			expect(mockOnClose).toHaveBeenCalledTimes(1);
		});
	});

	it("handles deletion error", async () => {
		const { UsersService } = await import("../../client");
		const { handleError } = await import("../../utils");
		const mockDeleteUser = vi.mocked(UsersService.deleteUserMe);
		const mockHandleError = vi.mocked(handleError);

		mockDeleteUser.mockRejectedValue(new Error("Deletion failed"));

		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		fireEvent.click(confirmButton);

		await waitFor(() => {
			expect(mockHandleError).toHaveBeenCalled();
		});

		// Should not logout or close on error
		expect(mockLogout).not.toHaveBeenCalled();
		expect(mockOnClose).not.toHaveBeenCalled();
	});

	it("disables buttons during submission", async () => {
		const { UsersService } = await import("../../client");
		const mockDeleteUser = vi.mocked(UsersService.deleteUserMe);

		// Mock a delayed response
		mockDeleteUser.mockImplementation(
			() => new Promise((resolve) => setTimeout(resolve, 100)),
		);

		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		const cancelButton = screen.getByRole("button", { name: "Cancel" });

		fireEvent.click(confirmButton);

		// Check that buttons are disabled during submission
		await waitFor(() => {
			expect(confirmButton).toHaveAttribute("data-loading");
			expect(cancelButton).toBeDisabled();
		});
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

	it("uses form submission for confirm action", () => {
		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		const confirmButton = screen.getByRole("button", { name: "Confirm" });
		expect(confirmButton).toHaveAttribute("type", "submit");
	});

	it("sets up proper dialog accessibility", () => {
		renderWithProviders(
			<DeleteConfirmation isOpen={true} onClose={mockOnClose} />,
		);

		// Check for alertdialog role
		const dialog = screen.getByRole("alertdialog");
		expect(dialog).toBeInTheDocument();

		// Check for proper header and body
		expect(screen.getByText("Confirmation Required")).toBeInTheDocument();
		expect(
			screen.getByText(/All your account data will be/),
		).toBeInTheDocument();
	});
});
