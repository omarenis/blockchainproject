from app import app, db, client
from controllers import login_controller, verify_code_controller, workers, \
    worker_form, files_view, logout, get_operations, file_view, send_code_view
from models import PersonModel

app.add_url_rule('/', 'index', view_func=login_controller, methods=['GET'])
app.add_url_rule('/login', 'login', view_func=login_controller, methods=['GET', 'POST'])
app.add_url_rule('/verify_code', 'verify_code', view_func=verify_code_controller, methods=['GET', 'POST'])
app.add_url_rule('/files', 'files', view_func=files_view, methods=['GET', 'POST'])
app.add_url_rule('/files/<int:pk>', view_func=file_view, methods=['PUT'])
app.add_url_rule('/workers', 'workers', view_func=workers, methods=['GET', 'POST'])
app.add_url_rule('/workers/<int:pk>', 'worker', view_func=worker_form, methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/operations', 'operations', view_func=get_operations, methods=['GET'])
app.add_url_rule('/logout', 'logout', view_func=logout)
app.add_url_rule('/send_code', view_func=send_code_view, methods=['POST'])


if __name__ == '__main__':
    with app.app_context():
        result = db.session.execute(db.Select(PersonModel).filter_by(username='admin')).scalar_one_or_none()
        if result is None:
            PersonModel.create_admin_account()
    app.run()
