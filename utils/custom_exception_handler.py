from rest_framework.views import exception_handler
from django.http import JsonResponse


def get_response(message="", result={}, errors=None, success=False, status=200):
    return {
        "success": success,
        "message": message,
        "data": result,
        "errors": errors,
        "status_code": status,
    }


def get_error_message(error_dict):
    response = error_dict[next(iter(error_dict))]
    if isinstance(response, dict):
        response = get_error_message(response)
    elif isinstance(response, list):
        response_message = response[0]
        if isinstance(response_message, dict):
            response = get_error_message(response_message)
        else:
            response = response[0]
    return response


def handle_exception(exc, context):
    error_response = exception_handler(exc, context)
    if error_response is not None:
        error = error_response.data
        print(error_response)
        if isinstance(error, list) and error:
            if isinstance(error[0], dict):
                error_response.data = get_response(
                    message=error_response.data["detail"],
                    errors=error,
                    status=error_response.status_code,
                )

            elif isinstance(error[0], str):
                error_response.data = get_response(
                    message=error[0],
                    status=error_response.status_code
                )

        if isinstance(error, dict):
            error_response.data = get_response(
                message=error_response.data["detail"],
                errors=error,
                status=error_response.status_code
            )
    return error_response


class ExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        if response.status_code == 500:
            response = get_response(
                message="Internal server error, please try again later",
                status=response.status_code
            )
            return JsonResponse(response, status=response['status_code'])

        if response.status_code == 404 and "Page not found" in str(response.content):
            response = get_response(
                message="Page not found, invalid url",
                status=response.status_code
            )
            return JsonResponse(response, status=response['status_code'])

        return response
