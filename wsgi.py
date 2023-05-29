from flask_wtf.csrf import generate_csrf

from app import app
from controllers import login_controller, upload_file, verify_code_controller, WorkerCrud, \
    worker_create_form, file_view

app.add_url_rule('/', 'index', view_func=login_controller, methods=['GET'])
app.add_url_rule('/login', 'login', view_func=login_controller, methods=['GET', 'POST'])
app.add_url_rule('/verify_code', 'verify_code', view_func=verify_code_controller, methods=['GET', 'POST'])
app.add_url_rule('/upload', 'upload', view_func=upload_file, methods=['GET', 'POST'])
app.add_url_rule('/files', 'files', view_func=file_view, methods=['GET', 'POST'])
app.add_url_rule('/workers', view_func=WorkerCrud.as_view('workers'), methods=['GET', 'POST'])
app.add_url_rule('/add_worker', view_func=worker_create_form, methods=['GET'])
if __name__ == '__main__':
    app.run()
