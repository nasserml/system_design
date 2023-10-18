import os, requests

def login(request):
    """
    Logs in a user by sending a login request to the authentication service.

    Parameters:
        request (object): The HTTP request object.

    Returns:
        tuple: A tuple containing the login response and an error message, if any. The login response is a string containing the response text from the authentication service. The error message is a tuple containing the error message and the error code if the login request fails, or None if the request is successful.
    """
    auth = request.authorization
    if not auth:
        return None, ('missing credentials', 401)
    
    basicAuth = (auth.username, auth.password)
    
    response = requests.post(
        f'http://{os.environ.get("AUTH_SVC_ADDRESS")}/login',
        auth=basicAuth
    )
    
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)