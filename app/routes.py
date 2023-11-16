from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Shaza'}
    return '''
<html>
    <head>
        <title>Home Page - Microblog</title>
    </head>
    <body>
<h1>Hello, ''' + user.get('username') + '''!</h1>
</body>
</html>'''