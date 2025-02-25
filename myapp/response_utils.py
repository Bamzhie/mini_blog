def success_response(data, message="success"):
    """
    Utility function to create a success response.
    """
    return {
        "status": "01",
        "message": message,
        "data": data,
    }


def error_response(errors, message="failure"):
    """
    Utility function to create an error response.
    """
    return {
        "status": "02",
        "message": message,
        "data": errors,
    }


def unauthorized_response(message="Unauthorized access"):
    """
    Utility function to create an unauthorized access response.
    """
    return {
        "status": "03",
        "message": message,
        "data": None,
    }


def not_found_response(message="Not found"):
    """
    Utility function to create a not found response.
    """
    return {
        "status": "04",
        "message": message,
        "data": None,
    }


def forbidden_response(message="Forbidden"):
    """
    Utility function to create a forbidden response.
    """
    return {
        "status": "05",
        "message": message,
        "data": None,
    }


def internal_server_error_response(message="Internal Server Error"):
    """
    Utility function to create an internal server error response.
    """
    return {
        "status": "06",
        "message": message,
        "data": None,
    }


def bad_request_response(errors, message="Bad Request"):
    """
    Utility function to create a bad request response.
    """
    return {
        "status": "07",
        "message": message,
        "data": errors,
    }
