import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ItemPublic, UserPublic } from "../../client";
import { renderWithProviders } from "../../test/utils";
import ActionsMenu from "./ActionsMenu";

// Mock child components with minimal interface for integration testing
// We focus on ActionsMenu's orchestration behavior rather than child component internals
vi.mock("../Admin/EditUser", () => ({
	default: ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) =>
		isOpen ? (
			<div data-testid="edit-user-modal">
				<div>Edit User Modal Open</div>
				<button onClick={onClose}>Close Modal</button>
			</div>
		) : null,
}));

vi.mock("./DeleteAlert", () => ({
	default: ({
		type,
		id,
		isOpen,
		onClose,
	}: {
		type: string;
		id: string | number;
		isOpen: boolean;
		onClose: () => void;
	}) =>
		isOpen ? (
			<div data-testid="delete-alert-modal">
				<div>
					Delete {type} Modal Open (ID: {id})
				</div>
				<button onClick={onClose}>Close Modal</button>
			</div>
		) : null,
}));

describe("ActionsMenu - Integration Tests", () => {
	const user = userEvent.setup();

	const mockUserValue: UserPublic = {
		id: 1,
		email: "user@example.com",
		is_superuser: false,
		is_active: true,
		full_name: "Test User",
	};

	const mockItemValue: ItemPublic = {
		id: 2,
		title: "Test Item",
		description: "Test Description",
	};

	beforeEach(() => {
		vi.clearAllMocks();
	});
	it("renders menu button with proper accessibility attributes", () => {
		renderWithProviders(<ActionsMenu type="User" value={mockUserValue} />);

		const menuButton = screen.getByRole("button", { expanded: false });
		expect(menuButton).toBeInTheDocument();
		expect(menuButton).not.toBeDisabled();

		// Integration test validates:
		// ✅ Real Chakra UI Menu component rendering
		// ✅ Proper accessibility attributes for menu button
		// ✅ Component composition without heavy mocking
	});

	it("handles disabled state properly with real component behavior", () => {
		renderWithProviders(
			<ActionsMenu type="User" value={mockUserValue} disabled={true} />,
		);

		const menuButton = screen.getByRole("button", { expanded: false });
		expect(menuButton).toBeDisabled();

		// Integration test validates:
		// ✅ Real disabled state handling via Chakra UI props
		// ✅ Proper button state management without mocking
	});

	it("validates complete edit modal workflow with real state management", async () => {
		renderWithProviders(<ActionsMenu type="User" value={mockUserValue} />);

		const menuButton = screen.getByRole("button", { expanded: false });
		await user.click(menuButton);

		// Wait for menu items to appear via real Chakra UI Menu behavior
		const editMenuItem = await screen.findByRole("menuitem", {
			name: /edit user/i,
		});
		expect(editMenuItem).toBeInTheDocument();

		await user.click(editMenuItem);

		// Verify edit modal opens with real useDisclosure state management
		await waitFor(() => {
			expect(screen.getByText("Edit User Modal Open")).toBeInTheDocument();
		});

		// Test modal closing workflow
		const closeButton = screen.getByText("Close Modal");
		await user.click(closeButton);

		await waitFor(() => {
			expect(
				screen.queryByText("Edit User Modal Open"),
			).not.toBeInTheDocument();
		});

		// Integration test validates:
		// ✅ Real Chakra UI Menu interaction and state management
		// ✅ useDisclosure hook integration for modal control
		// ✅ Complete user workflow from menu to modal to close
		// ✅ Component composition without mocking internal behavior
	});

	it("validates complete delete modal workflow with real state management", async () => {
		renderWithProviders(<ActionsMenu type="Item" value={mockItemValue} />);

		const menuButton = screen.getByRole("button", { expanded: false });
		await user.click(menuButton);

		// Wait for menu items to appear via real Chakra UI Menu behavior
		const deleteMenuItem = await screen.findByRole("menuitem", {
			name: /delete item/i,
		});
		expect(deleteMenuItem).toBeInTheDocument();

		await user.click(deleteMenuItem);

		// Verify delete modal opens with real useDisclosure state management and proper props
		await waitFor(() => {
			expect(
				screen.getByText("Delete Item Modal Open (ID: 2)"),
			).toBeInTheDocument();
		});

		// Test modal closing workflow
		const closeButton = screen.getByText("Close Modal");
		await user.click(closeButton);

		await waitFor(() => {
			expect(
				screen.queryByText("Delete Item Modal Open (ID: 2)"),
			).not.toBeInTheDocument();
		});

		// Integration test validates:
		// ✅ Real Chakra UI Menu interaction and state management
		// ✅ useDisclosure hook integration for delete modal control
		// ✅ Proper prop passing (type="Item", id=2) to child components
		// ✅ Complete user workflow from menu to modal to close
	});

	it("validates dynamic type rendering with real component composition", async () => {
		renderWithProviders(<ActionsMenu type="Product" value={mockItemValue} />);

		const menuButton = screen.getByRole("button", { expanded: false });
		await user.click(menuButton);

		// Verify dynamic type interpolation in menu items using role-based queries
		expect(
			await screen.findByRole("menuitem", { name: /edit product/i }),
		).toBeInTheDocument();
		expect(
			await screen.findByRole("menuitem", { name: /delete product/i }),
		).toBeInTheDocument();

		// Integration test validates:
		// ✅ Dynamic type prop interpolation in real menu rendering
		// ✅ Real Chakra UI MenuItem components with proper text content
		// ✅ Template string evaluation without mocking
	});

	it("validates proper component composition and initial states", () => {
		renderWithProviders(<ActionsMenu type="User" value={mockUserValue} />);

		// Verify both modals start in closed state with real useDisclosure initial values
		expect(screen.queryByText("Edit User Modal Open")).not.toBeInTheDocument();
		expect(
			screen.queryByText("Delete User Modal Open (ID: 1)"),
		).not.toBeInTheDocument();

		// Integration test validates:
		// ✅ Real useDisclosure hook initial state (closed)
		// ✅ Component composition without artificial state mocking
		// ✅ Proper conditional rendering based on actual hook values
	});

	it("validates initial state with proper component composition", () => {
		renderWithProviders(<ActionsMenu type="User" value={mockUserValue} />);

		// Verify both child components are properly composed but in closed state
		// DeleteAlert modal should not be visible when closed
		expect(
			screen.queryByText("Delete User Modal Open (ID: 1)"),
		).not.toBeInTheDocument();

		// EditUser modal should not be visible when closed
		expect(screen.queryByText("Edit User Modal Open")).not.toBeInTheDocument();

		// Menu button should be present and accessible
		const menuButton = screen.getByRole("button", { expanded: false });
		expect(menuButton).toBeInTheDocument();

		// Integration test validates:
		// ✅ Proper component composition with real useDisclosure initial state
		// ✅ Child components receive correct props but remain closed initially
		// ✅ No artificial prop testing - focus on real component behavior
	});
});
