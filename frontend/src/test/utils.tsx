import { ChakraProvider } from "@chakra-ui/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import theme from "../theme";

// For testing components that use router hooks, we need to provide mocks
const MockRouter = ({ children }: { children: ReactElement }) => {
	return <div>{children}</div>;
};

// Custom render function that includes providers but not router
export function renderWithProviders(ui: ReactElement) {
	const queryClient = new QueryClient({
		defaultOptions: {
			queries: {
				retry: false,
				staleTime: 0,
			},
		},
	});

	const renderResult = render(
		<ChakraProvider theme={theme}>
			<QueryClientProvider client={queryClient}>
				<MockRouter>{ui}</MockRouter>
			</QueryClientProvider>
		</ChakraProvider>,
	);
	
	// Return both render result and queryClient for integration testing
	return {
		...renderResult,
		queryClient,
	};
}

export * from "@testing-library/react";
