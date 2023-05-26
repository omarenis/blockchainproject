from models import Person, PersonModel, Contract
from app import db
from contract_interaction import W3, execute_set_function


class PersonRepository(object):
    def __init__(self, contract):
        self.session = db.session
        self.contract = contract

    def create(self, person_data: dict):
        person = PersonModel()
        person.set_password(password=person_data.get('password'))
        self.session.add(person)
        self.session.commit()

        execute_set_function(self.contract.contract_object.contract.functions.createPerson, (
            person.get_id(), person_data.get('firstname'),
            person_data.get('lastname'),
            person_data.get('email'),
            person_data.get('telephone'),
            person_data.get('location'),
            person_data.get('image')
        ), address=Contract.coinbase)
        return Person(**person_data)

    def get_person_by_id(self, _id: int):
        person_contact_data = self.contract.contract_object.functions.getPersonById(_id).call()
        
    def update_password(self, person_id: int, password):
        person = self.session.execute(db.Select(PersonModel).filter_by(id=person_id)).first()[0]
        if person is None:
            raise ValueError(f'person not found with id {person_id}')
        person.set_password(password)
        db.session.commit()
        return person

    def delete(self, _id: int):

        person = self.session.execute(db.Select(PersonModel).filter_by(id=_id))[0]
        if person

