from flask_wtf.csrf import generate_csrf
from app import app, db
from controllers import login_controller, verify_code_controller, get_workers, \
    worker_create_form, file_view, logout, get_operations
from models import PersonModel, ContractModel, Contract

app.add_url_rule('/', 'index', view_func=login_controller, methods=['GET'])
app.add_url_rule('/login', 'login', view_func=login_controller, methods=['GET', 'POST'])
app.add_url_rule('/verify_code', 'verify_code', view_func=verify_code_controller, methods=['GET', 'POST'])
app.add_url_rule('/files', 'files', view_func=file_view, methods=['GET', 'POST'])
app.add_url_rule('/workers', 'workers', view_func=get_workers, methods=['GET'])
app.add_url_rule('/worker', 'worker', view_func=worker_create_form, methods=['GET'])
app.add_url_rule('/operations', 'operations', view_func=get_operations, methods=['GET'])
app.add_url_rule('/logout', 'logout', view_func=logout)
if __name__ == '__main__':
    with app.app_context():
        result = db.session.execute(db.Select(PersonModel).filter_by(username='admin')).scalar_one_or_none()
        if result is None:
            PersonModel.create_admin_account()
    app.run()
