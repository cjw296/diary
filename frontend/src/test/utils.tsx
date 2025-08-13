import { ChakraProvider } from "@chakra-ui/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render } from "@testing-library/react"
import { ReactElement } from "react"
import theme from "../theme"

// Custom render function that includes providers
export function renderWithProviders(ui: ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    </ChakraProvider>
  )
}

export * from "@testing-library/react"