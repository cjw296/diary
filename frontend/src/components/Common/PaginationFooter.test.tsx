import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../../test/utils";
import { PaginationFooter } from "./PaginationFooter";

describe("PaginationFooter", () => {
	const mockOnChangePage = vi.fn();

	beforeEach(() => {
		mockOnChangePage.mockClear();
	});

	it("renders page information correctly", () => {
		renderWithProviders(
			<PaginationFooter
				page={5}
				hasNextPage={true}
				hasPreviousPage={true}
				onChangePage={mockOnChangePage}
			/>,
		);

		expect(screen.getByText("Page 5")).toBeInTheDocument();
		expect(screen.getByText("Previous")).toBeInTheDocument();
		expect(screen.getByText("Next")).toBeInTheDocument();
	});

	it("disables previous button when no previous page", () => {
		renderWithProviders(
			<PaginationFooter
				page={1}
				hasNextPage={true}
				hasPreviousPage={false}
				onChangePage={mockOnChangePage}
			/>,
		);

		const previousButton = screen.getByText("Previous");
		expect(previousButton).toBeDisabled();
	});

	it("disables next button when no next page", () => {
		renderWithProviders(
			<PaginationFooter
				page={10}
				hasNextPage={false}
				hasPreviousPage={true}
				onChangePage={mockOnChangePage}
			/>,
		);

		const nextButton = screen.getByText("Next");
		expect(nextButton).toBeDisabled();
	});

	it("calls onChangePage with previous page when previous button is clicked", async () => {
		const user = userEvent.setup();
		renderWithProviders(
			<PaginationFooter
				page={5}
				hasNextPage={true}
				hasPreviousPage={true}
				onChangePage={mockOnChangePage}
			/>,
		);

		const previousButton = screen.getByText("Previous");
		await user.click(previousButton);

		expect(mockOnChangePage).toHaveBeenCalledWith(4);
	});

	it("calls onChangePage with next page when next button is clicked", async () => {
		const user = userEvent.setup();
		renderWithProviders(
			<PaginationFooter
				page={3}
				hasNextPage={true}
				hasPreviousPage={true}
				onChangePage={mockOnChangePage}
			/>,
		);

		const nextButton = screen.getByText("Next");
		await user.click(nextButton);

		expect(mockOnChangePage).toHaveBeenCalledWith(4);
	});

	it("disables previous button when page is 1 even if hasPreviousPage is true", () => {
		renderWithProviders(
			<PaginationFooter
				page={1}
				hasNextPage={true}
				hasPreviousPage={true}
				onChangePage={mockOnChangePage}
			/>,
		);

		const previousButton = screen.getByText("Previous");
		expect(previousButton).toBeDisabled();
	});

	it("handles edge case when both buttons should be enabled", () => {
		renderWithProviders(
			<PaginationFooter
				page={2}
				hasNextPage={true}
				hasPreviousPage={true}
				onChangePage={mockOnChangePage}
			/>,
		);

		const previousButton = screen.getByText("Previous");
		const nextButton = screen.getByText("Next");

		expect(previousButton).not.toBeDisabled();
		expect(nextButton).not.toBeDisabled();
	});

	it("handles default props correctly", () => {
		renderWithProviders(
			<PaginationFooter page={1} onChangePage={mockOnChangePage} />,
		);

		const previousButton = screen.getByText("Previous");
		const nextButton = screen.getByText("Next");

		// When hasNextPage and hasPreviousPage are undefined, buttons should be disabled
		expect(previousButton).toBeDisabled();
		expect(nextButton).toBeDisabled();
	});
});
