import type { CancelablePromise } from "./core/CancelablePromise";
import { OpenAPI } from "./core/OpenAPI";
import { request as __request } from "./core/request";

import type {
	Body_login_access_token_login_access_token_post,
	Token,
	UserPublic,
	Message,
	UpdatePassword,
	UserCreate,
	UsersPublic,
	UserUpdate,
	UserUpdateMe,
} from "./models";

export type LoginData = {
	LoginAccessTokenLoginAccessTokenPost: {
		formData: Body_login_access_token_login_access_token_post;
	};
};

export type UsersData = {
	ReadUsersUsersGet: {
		limit?: number;
		skip?: number;
	};
	CreateUserUsersPost: {
		requestBody: UserCreate;
	};
	UpdateUserMeUsersMePatch: {
		requestBody: UserUpdateMe;
	};
	UpdatePasswordMeUsersMePasswordPatch: {
		requestBody: UpdatePassword;
	};
	ReadUserByIdUsersUserIdGet: {
		userId: string;
	};
	UpdateUserUsersUserIdPatch: {
		requestBody: UserUpdate;
		userId: string;
	};
	DeleteUserUsersUserIdDelete: {
		userId: string;
	};
};

export class LoginService {
	/**
	 * Login Access Token
	 * OAuth2 compatible token login, get an access token for future requests
	 * @returns Token Successful Response
	 * @throws ApiError
	 */
	public static loginAccessTokenLoginAccessTokenPost(
		data: LoginData["LoginAccessTokenLoginAccessTokenPost"],
	): CancelablePromise<Token> {
		const { formData } = data;
		return __request(OpenAPI, {
			method: "POST",
			url: "/login/access-token",
			formData: formData,
			mediaType: "application/x-www-form-urlencoded",
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Test Token
	 * Test access token
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static testTokenLoginTestTokenPost(): CancelablePromise<UserPublic> {
		return __request(OpenAPI, {
			method: "POST",
			url: "/login/test-token",
		});
	}
}

export class UsersService {
	/**
	 * Read Users
	 * Retrieve users.
	 * @returns UsersPublic Successful Response
	 * @throws ApiError
	 */
	public static readUsersUsersGet(
		data: UsersData["ReadUsersUsersGet"] = {},
	): CancelablePromise<UsersPublic> {
		const { skip = 0, limit = 100 } = data;
		return __request(OpenAPI, {
			method: "GET",
			url: "/users/",
			query: {
				skip,
				limit,
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Create User
	 * Create new user.
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static createUserUsersPost(
		data: UsersData["CreateUserUsersPost"],
	): CancelablePromise<UserPublic> {
		const { requestBody } = data;
		return __request(OpenAPI, {
			method: "POST",
			url: "/users/",
			body: requestBody,
			mediaType: "application/json",
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Read User Me
	 * Get current user.
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static readUserMeUsersMeGet(): CancelablePromise<UserPublic> {
		return __request(OpenAPI, {
			method: "GET",
			url: "/users/me",
		});
	}

	/**
	 * Delete User Me
	 * Delete own user.
	 * @returns Message Successful Response
	 * @throws ApiError
	 */
	public static deleteUserMeUsersMeDelete(): CancelablePromise<Message> {
		return __request(OpenAPI, {
			method: "DELETE",
			url: "/users/me",
		});
	}

	/**
	 * Update User Me
	 * Update own user.
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static updateUserMeUsersMePatch(
		data: UsersData["UpdateUserMeUsersMePatch"],
	): CancelablePromise<UserPublic> {
		const { requestBody } = data;
		return __request(OpenAPI, {
			method: "PATCH",
			url: "/users/me",
			body: requestBody,
			mediaType: "application/json",
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Update Password Me
	 * Update own password.
	 * @returns Message Successful Response
	 * @throws ApiError
	 */
	public static updatePasswordMeUsersMePasswordPatch(
		data: UsersData["UpdatePasswordMeUsersMePasswordPatch"],
	): CancelablePromise<Message> {
		const { requestBody } = data;
		return __request(OpenAPI, {
			method: "PATCH",
			url: "/users/me/password",
			body: requestBody,
			mediaType: "application/json",
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Read User By Id
	 * Get a specific user by id.
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static readUserByIdUsersUserIdGet(
		data: UsersData["ReadUserByIdUsersUserIdGet"],
	): CancelablePromise<UserPublic> {
		const { userId } = data;
		return __request(OpenAPI, {
			method: "GET",
			url: "/users/{user_id}",
			path: {
				user_id: userId,
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Update User
	 * Update a user.
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static updateUserUsersUserIdPatch(
		data: UsersData["UpdateUserUsersUserIdPatch"],
	): CancelablePromise<UserPublic> {
		const { userId, requestBody } = data;
		return __request(OpenAPI, {
			method: "PATCH",
			url: "/users/{user_id}",
			path: {
				user_id: userId,
			},
			body: requestBody,
			mediaType: "application/json",
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Delete User
	 * Delete a user.
	 * @returns Message Successful Response
	 * @throws ApiError
	 */
	public static deleteUserUsersUserIdDelete(
		data: UsersData["DeleteUserUsersUserIdDelete"],
	): CancelablePromise<Message> {
		const { userId } = data;
		return __request(OpenAPI, {
			method: "DELETE",
			url: "/users/{user_id}",
			path: {
				user_id: userId,
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}
}
