from models import Person, PersonModel, Contract, File, OperationModel, Operation
from app import db
from contract_interaction import W3, execute_set_function


class PersonRepository(object):
    coinbase = W3.eth.accounts[0]

    def __init__(self, contract):
        self.session = db.session
        self.contract = contract

    def list(self):
        results = self.session.execute(db.Select(PersonModel).filter_by(is_superuser=False)).all()
        persons = []
        for result in results:
            person_contact_data = self.contract.functions.getPersonById(int(result[0].get_id())).call()
            persons.append(Person(**{
                'firstname': person_contact_data[1],
                'lastname': person_contact_data[2],
                'email': person_contact_data[3],
                'telephone': person_contact_data[4],
                'location': person_contact_data[5],
                'image': person_contact_data[6],
                '_id': int(result[0].get_id())
            }))
        return persons

    def create(self, person_data: dict):
        person = PersonModel()
        person.is_superuser = False
        person.set_password(password=person_data.get('password'))
        self.session.add(person)
        self.session.commit()
        print(person.get_id())
        execute_set_function(self.contract.functions.createPerson, (
            int(person.get_id()), person_data.get('firstname'),
            person_data.get('lastname'),
            person_data.get('email'),
            person_data.get('telephone'),
            person_data.get('location'),
            person_data.get('image')
        ), address=Contract.coinbase)
        person_data['_id'] = int(person.get_id())
        return Person(**person_data)

    def get_person_by_id(self, _id: int):
        person_contact_data = self.contract.functions.getPersonById(_id).call()
        person_instance = db.session.execute(db.Select(PersonModel).filter_by(id=_id)).scalar_one()
        return Person(**{
            'firstname': person_contact_data[1],
            'lastname': person_contact_data[2],
            'email': person_contact_data[3],
            'telephone': person_contact_data[4],
            'location': person_contact_data[5],
            'image': person_contact_data[6],
            '_id': int(person_instance.get_id())
        })

    def update(self, data: dict, _id: int):
        result = self.session.execute(db.Select(PersonModel).filter_by(id=_id)).scalar_one_or_none()
        if result is None:
            raise ValueError('person not found with the current id')

        execute_set_function(self.contract.functions.updatePerson, (
            int(result.get_id()), data.get('firstname'), data.get('lastname'), data.get('telephone'),
            data.get('location'), data.get('image')), PersonRepository.coinbase)

    def delete(self, _id: int):
        result = self.session.execute(db.Select(PersonModel).filter_by(id=_id)).scalar_one_or_none()
        if result is None:
            raise ValueError('person not found')
        else:
            result.delete()
            self.session.commit()
            execute_set_function(self.contract.functions.deletePerson, (_id,), PersonRepository.coinbase)

    def update_password(self, person_id: int, password):
        person = self.session.execute(db.Select(PersonModel).filter_by(id=person_id)).first()[0]
        if person is None:
            raise ValueError(f'person not found with id {person_id}')
        person.set_password(password)
        db.session.commit()
        return person

    def delete(self, _id: int):

        person = self.session.execute(db.Select(PersonModel).filter_by(id=_id))[0]
        if person is None:
            raise ValueError('person not found with the specfic id')
        person.delete()
        execute_set_function(self.contract.functions.deletePerson, (_id,), self.coinbase)


class FileRepository(object):
    coinbase = W3.eth.accounts[0]

    def __init__(self, contract):
        self.session = db.session
        self.contract = contract

    def get_files(self):
        files = self.contract.functions.getFiles().call()
        if files:
            return [File(_id=i[0], filename=i[1], file_content=i[2]) for i in files]
        else:
            return []

    def create(self, file_data: dict):

        return execute_set_function(self.contract.functions.addFile, (
            file_data['filename'], file_data['file_content']
        ), address=self.coinbase)

    def get_file_by_id(self, _id: int):
        file_contract_data = self.contract.functions.getFileById(_id).call()
        return File(_id=file_contract_data[0], filename=file_contract_data[1], file_content=file_contract_data[2])

    def delete(self, _id: int):
        return execute_set_function(self.contract.functions.deleteFile, (_id,), self.coinbase)

    def update(self, _id: int, file_content: str):
        file_contract_data = self.contract.functions.getFileById(_id).call()
        file_contract_data[2] = file_content
        return execute_set_function(self.contract.functions.updateFile, (_id, file_contract_data), self.coinbase)


class OperationRepository(object):
    coinbase = W3.eth.accounts[0]

    def __init__(self, contract):
        self.session = db.session
        self.user_repository = PersonRepository(contract)
        self.contract = contract

    def create(self, operation_data):
        operation_instance = OperationModel()
        operation_instance.operation = operation_data['operation']
        operation_instance.filename = operation_data["filename"]
        operation_instance.created_at = operation_data['created_at']
        operation_instance.person_id = operation_data['person_id']
        operation_instance.transaction_hash = operation_data['transaction_hash']
        self.session.add(operation_instance)
        self.session.commit()

    def list(self):
        results = self.session.execute(db.Select(OperationModel)).all()
        operations = []
        for result in results:
            operation_instance = result[0]
            person = self.user_repository.get_person_by_id(operation_instance.person_id)
            operations.append(Operation(person=person, filename=operation_instance.filename,
                                        transaction_hash=operation_instance.transaction_hash,
                                        _id=operation_instance.id))
        return operations
