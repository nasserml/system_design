import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
server.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
server.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
server.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
server.config['MYSQL_PORT'] = os.environ.get('MYSQL_PORT')


@server.route('/login', methods=['POST'])
def login():
	"""
	Handles the login request.

	Args:
	    None

	Returns:
	    str: The response message indicating the result of the login attempt.

	Raises:
	    None
	"""
	auth = request.authorization
	if not auth:
		return 'missing credentials', 401
	
	# chech db for username and password
	cur = mysql.connection.Cursor()
	res = cur.execute(
		'SELECT email, password FROM user WHERE email=%s', (auth.username,)
	)
	
	if res > 0:
		user_row = cur.fetchone()
		email = user_row[0]
		password = user_row[1]

		if auth.username != email or auth.password != password:
			return 'invalid credentials', 401
		else:
			return createJWT(auth.username, os.environ.get('JWT_SECRET'), True)
	else:
		return 'invalid credentials', 401

@server.route('/validate', methods=['POST'])
def validate():
	"""
	Validates the request by decoding the JWT token provided in the Authorization header.

	Parameters:
		None

	Returns:
		If the JWT token is missing, returns a tuple ('missing credentials', 401).
		If the JWT token is not authorized, returns a tuple ('not authorized', 403).
		If the JWT token is valid, returns a tuple (decoded, 200), where decoded is the decoded JWT token and 200 is the HTTP status code for success.
	"""
	encoded_jwt = request.headers['Authorization']
	if not encoded_jwt:
		return 'missing credentials', 401
	encoded_jwt = encoded_jwt.split(' ')[1]
 
	try:
		decoded = jwt.decode(
      				encoded_jwt, os.environ.get('JWT_SECRET'), algorithms=['HS256']
          )
	except:
		return 'not authorized', 403

	return decoded, 200


def createJWT(username, secret, authz):
	"""
	Creates a JSON Web Token (JWT) using the provided username, secret, and authorization.

	:param username: The username to include in the JWT.
	:type username: str
	:param secret: The secret key used to sign the JWT.
	:type secret: str
	:param authz: The authorization level for the JWT.
	:type authz: bool
	:return: The JWT as a string.
	:rtype: str
	"""
	return jwt.encode(
		{
			'username': username,
			'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
			'iat': datetime.datetime.utcnow(),
			'admin': authz,
		},
		secret,
		algorithm='HS256',
	)


if __name__ == '__main__':
	server.run(host='0.0.0.0', port=5000)
 