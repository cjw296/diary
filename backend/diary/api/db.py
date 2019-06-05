from starlette.requests import Request


def db_session(request: Request):
    return request.state.db


def finish_session(session):
    session.rollback()
    session.close()
