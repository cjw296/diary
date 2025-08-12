import "@testing-library/jest-dom"
import { beforeAll, afterEach, afterAll } from "vitest"
import { server } from "./mocks/server"

// Establish API mocking before all tests
beforeAll(() => server.listen())

// Clean up after each test case
afterEach(() => server.resetHandlers())

// Clean up after all tests are done
afterAll(() => server.close())