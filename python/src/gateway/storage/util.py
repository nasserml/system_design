import pika, json

def upload(f, fs, channel, access):
    """
    Uploads a file to a specified channel using the given file system and access credentials.
    
    Parameters:
        f (file): The file to be uploaded.
        fs (FileSystem): The file system to upload the file to.
        channel (Channel): The channel to publish the message to.
        access (dict): The access credentials for the user.

    Returns:
        tuple: A tuple containing the response message and status code.
            - response (str): The response message.
            - status_code (int): The HTTP status code.
    """
    try:
        fid = fs.put(f)
    except Exception as err:
        return 'internal server error', 500
    
    message = {
        'video_fid': str(fid),
        'mp3_fid':None,
        'username': access['ussername'],
    }
    
    try:
        channel.basic_publish(
            exchange = '',
            routing_key = 'video',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except:
        fs.delete(fid)
        return 'internal server error', 500