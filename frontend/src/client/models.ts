export type Body_login_access_token_login_access_token_post = {
	grant_type?: string | null;
	username: string;
	password: string;
	scope?: string;
	client_id?: string | null;
	client_secret?: string | null;
};

export type HTTPValidationError = {
	detail?: Array<ValidationError>;
};

export type Message = {
	message: string;
};

export type Token = {
	access_token: string;
	token_type?: string;
};

export type UpdatePassword = {
	current_password: string;
	new_password: string;
};

export type UserCreate = {
	email: string;
	is_active?: boolean;
	is_superuser?: boolean;
	full_name?: string | null;
	password: string;
};

export type UserPublic = {
	email: string;
	is_active?: boolean;
	is_superuser?: boolean;
	full_name?: string | null;
	id: string;
};

export type UserUpdate = {
	email?: string | null;
	is_active?: boolean;
	is_superuser?: boolean;
	full_name?: string | null;
	password?: string | null;
};

export type UserUpdateMe = {
	full_name?: string | null;
	email?: string | null;
};

export type UsersPublic = {
	data: Array<UserPublic>;
	count: number;
};

export type ValidationError = {
	loc: Array<string | number>;
	msg: string;
	type: string;
};
