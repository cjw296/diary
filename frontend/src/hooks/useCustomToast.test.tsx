import { renderHook } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import useCustomToast from "./useCustomToast"

// Mock the useToast hook from Chakra UI
const mockToast = vi.fn()
vi.mock("@chakra-ui/react", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@chakra-ui/react")>()
  return {
    ...actual,
    useToast: () => mockToast,
  }
})

describe("useCustomToast", () => {
  beforeEach(() => {
    mockToast.mockClear()
  })

  it("returns a function", () => {
    const { result } = renderHook(() => useCustomToast())

    expect(typeof result.current).toBe("function")
  })

  it("calls toast with correct parameters for success", () => {
    const { result } = renderHook(() => useCustomToast())

    result.current("Success Title", "Success Description", "success")

    expect(mockToast).toHaveBeenCalledWith({
      title: "Success Title",
      description: "Success Description",
      status: "success",
      isClosable: true,
      position: "bottom-right",
    })
  })

  it("calls toast with correct parameters for error", () => {
    const { result } = renderHook(() => useCustomToast())

    result.current("Error Title", "Error Description", "error")

    expect(mockToast).toHaveBeenCalledWith({
      title: "Error Title",
      description: "Error Description",  
      status: "error",
      isClosable: true,
      position: "bottom-right",
    })
  })

  it("maintains referential equality across renders", () => {
    const { result, rerender } = renderHook(() => useCustomToast())

    const firstRender = result.current
    rerender()
    const secondRender = result.current

    expect(firstRender).toBe(secondRender)
  })
})