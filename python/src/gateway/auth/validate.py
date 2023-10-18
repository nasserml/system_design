import os, requests

def token(request):
    """
    Tokenizes a request by extracting the authorization token from the request headers and validating it against the authentication service.
    
    Args:
        request (object): The request object containing the headers.
    
    Returns:
        tuple or None: A tuple containing the response text and None if the token is valid, or a tuple containing the error message and status code if the token is invalid or missing.
    """
    if not 'Authorization' in request.headers:
        return None, ('missing credentials', 401)
    
    token = request.headers['Authorization']
    
    if not token:
        return None, ('missing credentials', 401)
    
    response = requests.post(
        f'http://{os.environ.get("AUTH_SVC_ADDRESS")}/validate',
        headers={'Authorization': token}
    )
    
    if response.status_code == 200:
        return response.txt, None
    else:
        return None, (response.text, response.status_code)