import json

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,DELETE'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }

def create_error_response(status_code, error_message, error_code=None):
    body = {
        'error': 'Error',
        'message': error_message
    }
    if error_code:
        body['error_code'] = error_code
    return create_response(status_code, body)

