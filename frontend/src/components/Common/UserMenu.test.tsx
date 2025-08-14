import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { forwardRef } from "react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../../test/utils";
import UserMenu from "./UserMenu";

// Mock the useAuth hook
const mockLogout = vi.fn();
vi.mock("../../hooks/useAuth", () => ({
	default: () => ({
		logout: mockLogout,
	}),
}));

// Mock TanStack Router Link component with proper ref forwarding
vi.mock("@tanstack/react-router", () => ({
	Link: forwardRef<HTMLAnchorElement, any>(
		({ children, to, ...props }, ref) => (
			<a href={to} ref={ref} {...props}>
				{children}
			</a>
		),
	),
}));

describe("UserMenu", () => {
	it("renders user menu button", () => {
		renderWithProviders(<UserMenu />);

		const menuButton = screen.getByTestId("user-menu");
		expect(menuButton).toBeInTheDocument();
	});

	it("opens menu and shows menu items when clicked", async () => {
		const user = userEvent.setup();
		renderWithProviders(<UserMenu />);

		const menuButton = screen.getByTestId("user-menu");
		await user.click(menuButton);

		expect(screen.getByText("My profile")).toBeInTheDocument();
		expect(screen.getByText("Log out")).toBeInTheDocument();
	});

	it("calls logout when logout menu item is clicked", async () => {
		const user = userEvent.setup();
		renderWithProviders(<UserMenu />);

		const menuButton = screen.getByTestId("user-menu");
		await user.click(menuButton);

		const logoutItem = screen.getByText("Log out").closest("button");
		if (logoutItem) {
			await user.click(logoutItem);
		}

		expect(mockLogout).toHaveBeenCalledOnce();
	});

	it("has correct link for profile", async () => {
		const user = userEvent.setup();
		renderWithProviders(<UserMenu />);

		const menuButton = screen.getByTestId("user-menu");
		await user.click(menuButton);

		const profileLink = screen.getByText("My profile").closest("a");
		expect(profileLink).toHaveAttribute("href", "settings");
	});
});
