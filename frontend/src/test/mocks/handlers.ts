import { http, HttpResponse } from "msw";

// In-memory data stores for testing
let currentUser = {
	id: 1,
	email: "test@example.com",
	full_name: "John Doe",
	is_active: true,
	is_superuser: false,
};

// In-memory users database for admin operations
let usersDb = [
	{
		id: 1,
		email: "test@example.com",
		full_name: "John Doe",
		is_active: true,
		is_superuser: false,
	},
	{
		id: 2,
		email: "admin@example.com",
		full_name: "Admin User",
		is_active: true,
		is_superuser: true,
	},
	{
		id: 3,
		email: "user2@example.com",
		full_name: "Jane Smith",
		is_active: false,
		is_superuser: false,
	},
];

// Track next user ID
let nextUserId = 4;

export const handlers = [
	// Authentication endpoints
	http.post("/login/access-token", async ({ request }) => {
		const formData = await request.formData();
		const username = formData.get("username");
		const password = formData.get("password");

		// Simulate authentication logic
		if (username === "test@example.com" && password === "testpassword") {
			return HttpResponse.json({
				access_token: "mock-token",
				token_type: "bearer",
			});
		}

		return HttpResponse.json(
			{ detail: "Incorrect email or password" },
			{ status: 400 },
		);
	}),

	http.get("/users/me", ({ request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		return HttpResponse.json(currentUser);
	}),

	http.patch("/users/me", async ({ request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		try {
			const body = (await request.json()) as Partial<typeof currentUser>;

			// Validate email format
			if (body.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email)) {
				return HttpResponse.json(
					{ detail: "Invalid email format" },
					{ status: 422 },
				);
			}

			// Simulate email already exists error
			if (body.email === "existing@example.com") {
				return HttpResponse.json(
					{ detail: "Email already exists" },
					{ status: 409 },
				);
			}

			// Update user data
			currentUser = { ...currentUser, ...body };

			return HttpResponse.json(currentUser);
		} catch (error) {
			return HttpResponse.json({ detail: "Invalid JSON" }, { status: 400 });
		}
	}),

	// Users management endpoints
	http.get("/users/", ({ request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		const url = new URL(request.url);
		const skip = Number.parseInt(url.searchParams.get("skip") || "0");
		const limit = Number.parseInt(url.searchParams.get("limit") || "20");

		// Simulate pagination
		const paginatedUsers = usersDb.slice(skip, skip + limit);

		return HttpResponse.json({
			data: paginatedUsers,
			count: usersDb.length,
		});
	}),

	http.post("/users/", async ({ request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		try {
			const body = await request.json();

			// Validate required fields
			if (!body.email || !body.password) {
				return HttpResponse.json(
					{ detail: "Email and password are required" },
					{ status: 422 },
				);
			}

			// Check if email already exists
			if (usersDb.some((user) => user.email === body.email)) {
				return HttpResponse.json(
					{ detail: "Email already registered" },
					{ status: 409 },
				);
			}

			// Validate email format
			if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email)) {
				return HttpResponse.json(
					{ detail: "Invalid email format" },
					{ status: 422 },
				);
			}

			// Create new user
			const newUser = {
				id: nextUserId++,
				email: body.email,
				full_name: body.full_name || "",
				is_active: body.is_active ?? true,
				is_superuser: body.is_superuser ?? false,
			};

			// Add to users database
			usersDb.push(newUser);

			return HttpResponse.json(newUser, { status: 201 });
		} catch (error) {
			return HttpResponse.json({ detail: "Invalid JSON" }, { status: 400 });
		}
	}),

	// Individual user management endpoints
	http.get("/users/:userId", ({ params, request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		const userId = Number.parseInt(params.userId as string);
		const user = usersDb.find((u) => u.id === userId);

		if (!user) {
			return HttpResponse.json({ detail: "User not found" }, { status: 404 });
		}

		return HttpResponse.json(user);
	}),

	http.patch("/users/:userId", async ({ params, request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		const userId = Number.parseInt(params.userId as string);
		const userIndex = usersDb.findIndex((u) => u.id === userId);

		if (userIndex === -1) {
			return HttpResponse.json({ detail: "User not found" }, { status: 404 });
		}

		try {
			const body = await request.json();

			// Validate email if provided
			if (body.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email)) {
				return HttpResponse.json(
					{ detail: "Invalid email format" },
					{ status: 422 },
				);
			}

			// Check email uniqueness if changing email
			if (body.email && body.email !== usersDb[userIndex].email) {
				if (usersDb.some((user) => user.email === body.email)) {
					return HttpResponse.json(
						{ detail: "Email already registered" },
						{ status: 409 },
					);
				}
			}

			// Update user
			usersDb[userIndex] = { ...usersDb[userIndex], ...body };

			return HttpResponse.json(usersDb[userIndex]);
		} catch (error) {
			return HttpResponse.json({ detail: "Invalid JSON" }, { status: 400 });
		}
	}),

	http.delete("/users/:userId", ({ params, request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		const userId = Number.parseInt(params.userId as string);
		const userIndex = usersDb.findIndex((u) => u.id === userId);

		if (userIndex === -1) {
			return HttpResponse.json({ detail: "User not found" }, { status: 404 });
		}

		// Remove user from database
		usersDb.splice(userIndex, 1);

		return HttpResponse.json({ message: "User deleted successfully" });
	}),

	// Password change endpoint
	http.patch("/users/me/password", async ({ request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		try {
			const body = await request.json();

			if (!body.current_password || !body.new_password) {
				return HttpResponse.json(
					{ detail: "Current password and new password are required" },
					{ status: 422 },
				);
			}

			// Simulate password validation - in real app this would verify current password
			if (body.current_password !== "currentpassword") {
				return HttpResponse.json(
					{ detail: "Current password is incorrect" },
					{ status: 400 },
				);
			}

			// Validate new password strength
			if (body.new_password.length < 8) {
				return HttpResponse.json(
					{ detail: "New password must be at least 8 characters" },
					{ status: 422 },
				);
			}

			return HttpResponse.json({ message: "Password updated successfully" });
		} catch (error) {
			return HttpResponse.json({ detail: "Invalid JSON" }, { status: 400 });
		}
	}),

	// Account deletion endpoint
	http.delete("/users/me", ({ request }) => {
		const authHeader = request.headers.get("authorization");

		if (!authHeader || !authHeader.startsWith("Bearer ")) {
			return HttpResponse.json(
				{ detail: "Not authenticated" },
				{ status: 401 },
			);
		}

		return HttpResponse.json({ message: "Account deleted successfully" });
	}),

	// Default fallback for unmatched API routes
	http.get("/api/*", () => {
		return HttpResponse.json({ message: "Mock response" });
	}),
];

// Helper functions for tests
export const resetUserData = () => {
	currentUser = {
		id: 1,
		email: "test@example.com",
		full_name: "John Doe",
		is_active: true,
		is_superuser: false,
	};

	// Reset users database to initial state
	usersDb = [
		{
			id: 1,
			email: "test@example.com",
			full_name: "John Doe",
			is_active: true,
			is_superuser: false,
		},
		{
			id: 2,
			email: "admin@example.com",
			full_name: "Admin User",
			is_active: true,
			is_superuser: true,
		},
		{
			id: 3,
			email: "user2@example.com",
			full_name: "Jane Smith",
			is_active: false,
			is_superuser: false,
		},
	];

	nextUserId = 4;
};

// Helper to get current users database (for testing purposes)
export const getUsersDb = () => [...usersDb];

// Helper to set current user (for testing different user states)
export const setCurrentUser = (user: Partial<typeof currentUser>) => {
	currentUser = { ...currentUser, ...user };
};
