import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../../test/utils";
import Appearance from "./Appearance";

// Mock useColorMode hook
const mockToggleColorMode = vi.fn();
vi.mock("@chakra-ui/react", async (importOriginal) => {
	const actual = await importOriginal<typeof import("@chakra-ui/react")>();
	return {
		...actual,
		useColorMode: () => ({
			colorMode: "light",
			toggleColorMode: mockToggleColorMode,
		}),
	};
});

describe("Appearance", () => {
	beforeEach(() => {
		mockToggleColorMode.mockClear();
	});

	it("renders appearance section with heading", () => {
		renderWithProviders(<Appearance />);

		expect(screen.getByText("Appearance")).toBeInTheDocument();
	});

	it("renders light and dark mode options", () => {
		renderWithProviders(<Appearance />);

		expect(screen.getByText("Light Mode")).toBeInTheDocument();
		expect(screen.getByText("Dark Mode")).toBeInTheDocument();
		expect(screen.getByText("Default")).toBeInTheDocument();
	});

	it("shows light mode as selected by default", () => {
		renderWithProviders(<Appearance />);

		const lightModeRadio = screen.getByRole("radio", { name: /light mode/i });
		const darkModeRadio = screen.getByRole("radio", { name: /dark mode/i });

		expect(lightModeRadio).toBeChecked();
		expect(darkModeRadio).not.toBeChecked();
	});

	it("calls toggleColorMode when radio selection changes", async () => {
		const user = userEvent.setup();
		renderWithProviders(<Appearance />);

		const darkModeRadio = screen.getByRole("radio", { name: /dark mode/i });
		await user.click(darkModeRadio);

		expect(mockToggleColorMode).toHaveBeenCalled();
	});

	it("shows default badge on light mode", () => {
		renderWithProviders(<Appearance />);

		const defaultBadge = screen.getByText("Default");
		expect(defaultBadge).toBeInTheDocument();
	});
});
