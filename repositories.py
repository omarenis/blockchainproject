from models import Person, PersonModel
from app import db
from contract_interaction import W3


class PersonRepository(object):
    def __init__(self):
        self.session = db.session

    def create(self, person_data: dict):
        person = PersonModel(address=person_data.get('address'), private_key=person_data.get('private_key'),
                             is_superuser=False)
        person.set_password(password=person_data.get('password'))
        self.session.add(person)
        self.session.commit()
        return Person(**person_data)

    def update_password(self, person_id: int, password):
        person = self.session.execute(db.Select(PersonModel))
