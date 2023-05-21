from crypt import methods

from app import app, db
from models import Person
from controllers import login_controller, signup_controller, upload_file, verify_code_controller, WorkerCrud

app.add_url_rule('/', 'index', view_func=login_controller, methods=['GET'])
app.add_url_rule('/login', 'login', view_func=login_controller, methods=['GET', 'POST'])
app.add_url_rule('/signup', 'signup', view_func=signup_controller, methods=['GET', 'POST'])
app.add_url_rule('/verify_code', 'verify_code', view_func=verify_code_controller, methods=['GET', 'POST'])
app.add_url_rule('/upload', 'upload', view_func=upload_file, methods=['GET', 'POST'])
app.add_url_rule('/workers', view_func=WorkerCrud.as_view('workers'), methods=['GET', 'POST'])
if __name__ == '__main__':
    with app.app_context():

        admin = db.session.execute(db.select(Person).filter_by())

    app.run()
