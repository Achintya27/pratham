from rest_framework.response import Response

def StandardResponse(status , data = None, message = None, error = None):
    res = {'status': status,
           'data': data,
           'message': message,
           'error': error}
    return Response(
        {k: v for k,v in res.items() if v}, status = status)