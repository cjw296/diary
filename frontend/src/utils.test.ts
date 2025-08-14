import { describe, expect, it, vi } from "vitest";
import {
	confirmPasswordRules,
	emailPattern,
	handleError,
	namePattern,
	passwordRules,
} from "./utils";

describe("utils", () => {
	describe("emailPattern", () => {
		it("has correct regex pattern and message", () => {
			expect(emailPattern.value).toEqual(
				/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
			);
			expect(emailPattern.message).toBe("Invalid email address");
		});

		it("validates correct email addresses", () => {
			const validEmails = [
				"test@example.com",
				"user.name@domain.co.uk",
				"TEST@EXAMPLE.COM",
			];

			validEmails.forEach((email) => {
				expect(emailPattern.value.test(email)).toBe(true);
			});
		});

		it("rejects invalid email addresses", () => {
			const invalidEmails = [
				"invalid-email",
				"@example.com",
				"test@",
				"test.example.com",
			];

			invalidEmails.forEach((email) => {
				expect(emailPattern.value.test(email)).toBe(false);
			});
		});
	});

	describe("namePattern", () => {
		it("has correct regex pattern and message", () => {
			expect(namePattern.value).toEqual(/^[A-Za-z\s\u00C0-\u017F]{1,30}$/);
			expect(namePattern.message).toBe("Invalid name");
		});

		it("validates correct names", () => {
			const validNames = ["John Doe", "José María", "Anne", "Connor"];

			validNames.forEach((name) => {
				expect(namePattern.value.test(name)).toBe(true);
			});
		});

		it("rejects invalid names", () => {
			const invalidNames = ["John123", "user@domain", "a".repeat(31)];

			invalidNames.forEach((name) => {
				expect(namePattern.value.test(name)).toBe(false);
			});
		});
	});

	describe("passwordRules", () => {
		it("returns rules with required field when isRequired is true", () => {
			const rules = passwordRules(true);

			expect(rules.required).toBe("Password is required");
			expect(rules.minLength.value).toBe(8);
			expect(rules.minLength.message).toBe(
				"Password must be at least 8 characters",
			);
		});

		it("returns rules without required field when isRequired is false", () => {
			const rules = passwordRules(false);

			expect(rules.required).toBeUndefined();
			expect(rules.minLength.value).toBe(8);
			expect(rules.minLength.message).toBe(
				"Password must be at least 8 characters",
			);
		});

		it("defaults to required when no parameter provided", () => {
			const rules = passwordRules();

			expect(rules.required).toBe("Password is required");
		});
	});

	describe("confirmPasswordRules", () => {
		it("returns rules with required field when isRequired is true", () => {
			const mockGetValues = vi.fn().mockReturnValue({ password: "test123" });
			const rules = confirmPasswordRules(mockGetValues, true);

			expect(rules.required).toBe("Password confirmation is required");
			expect(typeof rules.validate).toBe("function");
		});

		it("returns rules without required field when isRequired is false", () => {
			const mockGetValues = vi.fn().mockReturnValue({ password: "test123" });
			const rules = confirmPasswordRules(mockGetValues, false);

			expect(rules.required).toBeUndefined();
			expect(typeof rules.validate).toBe("function");
		});

		it("validates matching passwords", () => {
			const mockGetValues = vi.fn().mockReturnValue({ password: "test123" });
			const rules = confirmPasswordRules(mockGetValues, true);

			expect(rules.validate("test123")).toBe(true);
		});

		it("validates matching new_password", () => {
			const mockGetValues = vi
				.fn()
				.mockReturnValue({ new_password: "test123" });
			const rules = confirmPasswordRules(mockGetValues, true);

			expect(rules.validate("test123")).toBe(true);
		});

		it("rejects non-matching passwords", () => {
			const mockGetValues = vi.fn().mockReturnValue({ password: "test123" });
			const rules = confirmPasswordRules(mockGetValues, true);

			expect(rules.validate("different")).toBe("The passwords do not match");
		});

		it("defaults to required when no parameter provided", () => {
			const mockGetValues = vi.fn().mockReturnValue({ password: "test123" });
			const rules = confirmPasswordRules(mockGetValues);

			expect(rules.required).toBe("Password confirmation is required");
		});
	});

	describe("handleError", () => {
		it("handles simple error detail", () => {
			const mockShowToast = vi.fn();
			const error = {
				body: { detail: "Custom error message" },
			} as any;

			handleError(error, mockShowToast);

			expect(mockShowToast).toHaveBeenCalledWith(
				"Error",
				"Custom error message",
				"error",
			);
		});

		it("handles array error detail", () => {
			const mockShowToast = vi.fn();
			const error = {
				body: {
					detail: [
						{ msg: "First validation error" },
						{ msg: "Second validation error" },
					],
				},
			} as any;

			handleError(error, mockShowToast);

			expect(mockShowToast).toHaveBeenCalledWith(
				"Error",
				"First validation error",
				"error",
			);
		});

		it("handles error without detail", () => {
			const mockShowToast = vi.fn();
			const error = {
				body: {},
			} as any;

			handleError(error, mockShowToast);

			expect(mockShowToast).toHaveBeenCalledWith(
				"Error",
				"Something went wrong.",
				"error",
			);
		});

		it("handles empty array detail", () => {
			const mockShowToast = vi.fn();
			const error = {
				body: { detail: [] },
			} as any;

			handleError(error, mockShowToast);

			expect(mockShowToast).toHaveBeenCalledWith("Error", [], "error");
		});
	});
});
