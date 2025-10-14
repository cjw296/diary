import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../../test/utils";
import AddUser from "./AddUser";

describe("AddUser", () => {
	const mockOnClose = vi.fn();
	let user: ReturnType<typeof userEvent.setup>;

	beforeEach(() => {
		vi.clearAllMocks();
		user = userEvent.setup();
	});

	it("does not render when closed", () => {
		renderWithProviders(<AddUser isOpen={false} onClose={mockOnClose} />);

		expect(screen.queryByText("Add User")).not.toBeInTheDocument();
	});

	it("validates complete user creation workflow with real API integration", async () => {
		renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />);

		const emailField = screen.getByLabelText(/email/i);
		const fullNameField = screen.getByLabelText(/full name/i);
		const passwordField = screen.getByLabelText(/set password/i);
		const confirmPasswordField = screen.getByLabelText(/confirm password/i);
		const submitButton = screen.getByRole("button", { name: "Save" });

		await user.type(emailField, "newuser@example.com");
		await user.type(fullNameField, "New Test User");
		await user.type(passwordField, "password123");
		await user.type(confirmPasswordField, "password123");
		await user.click(submitButton);

		// Wait for success toast to appear
		await waitFor(
			() => {
				expect(
					screen.getByText("User created successfully."),
				).toBeInTheDocument();
			},
			{ timeout: 3000 },
		);

		// Verify modal is closed after successful creation
		expect(mockOnClose).toHaveBeenCalledTimes(1);
	});

	it("validates email format and shows error for invalid email", async () => {
		renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />);

		const emailField = screen.getByLabelText(/email/i);
		const submitButton = screen.getByRole("button", { name: "Save" });

		await user.type(emailField, "invalid-email");
		await user.click(submitButton);

		await waitFor(() => {
			expect(
				screen.getByText("Please enter a valid email"),
			).toBeInTheDocument();
		});
	});

	it("validates password requirements and shows error for short password", async () => {
		renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />);

		const passwordField = screen.getByLabelText(/set password/i);
		const submitButton = screen.getByRole("button", { name: "Save" });

		await user.type(passwordField, "short");
		await user.click(submitButton);

		await waitFor(() => {
			expect(
				screen.getByText("Password must be at least 8 characters"),
			).toBeInTheDocument();
		});
	});

	it("validates password confirmation and shows error for mismatched passwords", async () => {
		renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />);

		const passwordField = screen.getByLabelText(/set password/i);
		const confirmPasswordField = screen.getByLabelText(/confirm password/i);
		const submitButton = screen.getByRole("button", { name: "Save" });

		await user.type(passwordField, "password123");
		await user.type(confirmPasswordField, "differentpassword");
		await user.click(submitButton);

		await waitFor(() => {
			expect(
				screen.getByText("The passwords do not match"),
			).toBeInTheDocument();
		});
	});

	it("handles duplicate email error from API", async () => {
		renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />);

		const emailField = screen.getByLabelText(/email/i);
		const fullNameField = screen.getByLabelText(/full name/i);
		const passwordField = screen.getByLabelText(/set password/i);
		const confirmPasswordField = screen.getByLabelText(/confirm password/i);
		const submitButton = screen.getByRole("button", { name: "Save" });

		// Use existing email from MSW handlers
		await user.type(emailField, "test@example.com");
		await user.type(fullNameField, "Test User");
		await user.type(passwordField, "password123");
		await user.type(confirmPasswordField, "password123");
		await user.click(submitButton);

		// Wait for error toast to appear
		await waitFor(
			() => {
				expect(
					screen.getByText("Email already registered"),
				).toBeInTheDocument();
			},
			{ timeout: 3000 },
		);
	});

	it("creates user with minimal data (only required fields)", async () => {
		renderWithProviders(<AddUser isOpen={true} onClose={mockOnClose} />);

		const emailField = screen.getByLabelText(/email/i);
		const passwordField = screen.getByLabelText(/set password/i);
		const confirmPasswordField = screen.getByLabelText(/confirm password/i);
		const submitButton = screen.getByRole("button", { name: "Save" });

		await user.type(emailField, "minimal@example.com");
		await user.type(passwordField, "password123");
		await user.type(confirmPasswordField, "password123");
		await user.click(submitButton);

		// Wait for success toast to appear
		await waitFor(
			() => {
				expect(
					screen.getByText("User created successfully."),
				).toBeInTheDocument();
			},
			{ timeout: 3000 },
		);

		// Verify modal is closed after successful creation
		expect(mockOnClose).toHaveBeenCalledTimes(1);
	});
});
