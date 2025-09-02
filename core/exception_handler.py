from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response
    
    custom_response_data = {
        'errors': {
            'status_code': response.status_code,
        }
    }

    if isinstance(response.data, dict):
        custom_response_data['errors']['detail'] = response.data.get('detail', response.data)
        custom_response_data['errors']['code'] = response.data.get('code', 'invalid')
    else:
        custom_response_data['errors']['detail'] = response.data
        custom_response_data['errors']['code'] = 'validation_error'

    custom_response = Response(custom_response_data, status=response.status_code)

    return Response(custom_response_data, status=response.status_code)
