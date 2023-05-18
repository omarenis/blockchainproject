pragma solidity >=0.8.2 <0.9.0;

contract StorageJsonFile
{
    uint256[] private fileIds;
    uint256 private numberPersons;
    uint256 private numberFiles;
    uint256 [] private personIds;
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
        address _address;
    }

    mapping(uint => Person) private persons;
    mapping(uint256 => JSonFileRef) private files;
    constructor()
    {
        numberPersons = 0;
        numberFiles = 0;
    }



    function addFile(JSonFileRef memory jSonFileRef) public
    {
        files[numberFiles] = jSonFileRef;
        fileIds.push(numberFiles);
        numberFiles ++;
    }

    function updateFile(uint fileId, JSonFileRef memory jSonFileRef) public
    {
        files[fileId] = jSonFileRef;
    }

    function deleteFile(uint fileId) public
    {
        delete files[fileId];
        numberFiles --;
        for(uint i=0; i<numberFiles; i++)
        {
            if(fileIds[i] == fileId)
            {
                fileIds[i] = fileIds[numberFiles - 1];
                fileIds.pop();
                return;
            }
        }
    }

    function getFiles()  public view returns(JSonFileRef[] memory){
        JSonFileRef[] memory fileObjects = new JSonFileRef[](numberFiles);
        for(uint i=0; i< numberFiles; i++)
        {
            fileObjects[i] = files[fileIds[i]];
        }
        return fileObjects;
    }


    function createPerson(uint256 id, string memory firstname, string memory lastname, string memory email, address _address) public
    {
        persons[id] = Person(id, firstname, lastname, email, _address);
        personIds.push(id);
        numberPersons ++;
    }

    function getPersons() public view returns(Person[] memory)
    {
        Person[] memory person_objects = new Person[](numberPersons);
        for(uint64 i = 0; i < numberPersons; i++)
        {
            person_objects[i] = persons[personIds[i]];
        }
        return person_objects;
    }

    function updatePerson(uint256 personId, string memory firstname, string memory lastname, string memory email) public
    {
        persons[personId].firstname = firstname;
        persons[personId].lastname = lastname;
        persons[personId].email = email;
    }

    function deletePerson(uint personId) public
    {
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

    function getPersonByEmail(string memory email) public view returns(Person memory)  {
        for(uint i=0; i < personIds.length; i++)
        {
            if(keccak256(bytes(email)) == keccak256(bytes(persons[personIds[i]].email)))
            {
                return persons[personIds[i]];
            }
        }
        revert('Not found');
    }
}
