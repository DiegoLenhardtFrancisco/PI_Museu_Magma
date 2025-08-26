from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response
    
    custom_response_data = {
        'errors': {
            'status_code': response.status_code,
            'datail': None,
            'code': response.data.get('code', None),
        }
    }

    if isinstance(response.data, dict):
        detail = response.data.get('detail', response.data)
    else:
        detail = response.data

    custom_response_data['errors']['detail'] = detail

    return Response(custom_response_data, status=response.status_code)
