import "@testing-library/jest-dom";
import { afterAll, afterEach, beforeAll, beforeEach } from "vitest";
import { OpenAPI } from "../client";
import { resetUserData } from "./mocks/handlers";
import { server } from "./mocks/server";

// Establish API mocking before all tests
beforeAll(() => {
	server.listen({ onUnhandledRequest: "error" });
	// Set up a mock auth token for tests
	localStorage.setItem("access_token", "mock-token");

	// Configure OpenAPI client for tests
	OpenAPI.BASE = ""; // Use empty base for MSW to intercept requests
	OpenAPI.TOKEN = async () => {
		return localStorage.getItem("access_token") || "";
	};
});

// Reset state between tests
beforeEach(() => {
	resetUserData();
});

// Clean up after each test case
afterEach(() => {
	server.resetHandlers();
	localStorage.clear();
	// Re-set the auth token for next test
	localStorage.setItem("access_token", "mock-token");
});

// Clean up after all tests are done
afterAll(() => server.close());
