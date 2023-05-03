from  app import  app
from controllers import login_controller, signup_controller, upload_file

app.add_url_rule('/', 'index', view_func=login_controller, methods=['GET'])
app.add_url_rule('/login', 'login', view_func=login_controller, methods=['GET', 'POST'])
app.add_url_rule('/signup', 'signup', view_func=signup_controller, methods=['GET', 'POST'])
app.add_url_rule('/upload', 'upload', view_func=upload_file, methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run()
