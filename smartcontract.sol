pragma solidity >=0.8.2 <0.9.0;

contract StorageJsonFile
{
    uint256 private numberPersons;
    uint256 private numberFiles;
    uint256 [] private personIds;
    mapping(uint256 => JSonFileRef) files;
    struct JSonFileRef
    {
        string filename;
        string fileObject;
    }

    struct Person
    {
        uint256 id;
        string firstname;
        string lastname;
        string email;
        string password;
        address _address;
        uint256 numberFiles;
        uint256[] fileIds;
    }

    mapping(uint => Person) private persons;


    struct PersonObject {
            uint256 id;
        string firstname;
        string lastname;
        string email;
        address _address;
        uint256 numberFiles;
    }
    constructor()
    {
        numberPersons = 0;
    }


    function createPerson(uint256 id, string memory firstname, string memory lastname, string memory email, string memory password, address _address) public
    {
        persons[id] = Person(id, firstname, lastname, email, password, _address, 0, new uint256[](0));
        numberPersons ++;
    }

    function getFilesOfPerson(uint personId) public view returns(JSonFileRef[] memory)
    {
        JSonFileRef[] memory jSonFileRefs = new JSonFileRef[](persons[personId].numberFiles);
        for(uint256 i=0; i < persons[personId].fileIds.length; i++)
        {
            jSonFileRefs[i] = files[persons[personId].fileIds[i]];
        }
        return jSonFileRefs;
    }


    function getPersons() public view returns(PersonObject[] memory)
    {
        PersonObject[] memory person_objects = new PersonObject[](numberPersons);
        for(uint64 i = 0; i < numberPersons; i++)
        {
            person_objects[i] = PersonObject(persons[personIds[i]].id, persons[personIds[i]].firstname, persons[personIds[i]].lastname, persons[personIds[i]].email, persons[personIds[i]]._address, persons[personIds[i]].numberFiles);
        }
        return person_objects;
    }

    function addFile(uint personId, JSonFileRef memory jSonFileRef) public
    {
        persons[personId].fileIds.push(numberFiles);
        files[numberFiles] = jSonFileRef;
        numberFiles ++;
    }

    function updateFile(uint fileId, JSonFileRef memory jSonFileRef) public
    {
        files[fileId] = jSonFileRef;
    }

    function deleteFile(uint fileId, uint256 personId) public
    {
        delete files[fileId];
        for(uint i = 0; i < persons[personId].fileIds.length; i++)
        {
            if(persons[personId].fileIds[i] == fileId)
            {
                persons[personId].fileIds[i]  = persons[personId].fileIds[persons[personId].numberFiles - 1];
                delete persons[personId].fileIds[persons[personId].numberFiles - 1];
                persons[personId].numberFiles --;
                return ;
            }
        }
    }

    function updatePerson(uint personId, string memory firstname, string memory lastname, string memory email, string memory password) public
    {
        persons[personId].firstname = firstname;
        persons[personId].lastname = lastname;
        persons[personId].email = email;
        persons[personId].password = password;
    }

    function deletePerson(uint personId) public
    {
        for(uint256 i = 0; i < persons[personId].fileIds.length; i++)
        {
            delete files[persons[personId].fileIds[i]];

        }
        delete persons[personId];
        for(uint256 i = 0; i < personIds.length; i++)
        {
            if(personIds[i] == personId)
            {
                personIds[i] = personIds[personIds.length - 1];
                personIds.pop();
                return ;
            }
        }
    }
}
