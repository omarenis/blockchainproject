// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.2 <0.9.0;

contract StorageJsonFile
{
    uint256 private numberPersons;

    struct JSonFileRef
    {
        string filename;
        string fileObject;
    }

    struct Person
    {
        string firstname;
        string lastname;
        string email;
        string password;
        address _address;
        uint256 numberFiles;
        mapping(uint256 => JSonFileRef) files;
    }

    struct PersonObject
    {
        string firstname;
        string lastname;
        string email;
        address _address;
        uint numberFiles;
        string password;
    }

    mapping(uint => Person) private persons;

    constructor() 
    {
        numberPersons = 0;
    }


    function getFilesOfPerson(uint personId) public view returns(JSonFileRef[] memory)
    {
        JSonFileRef[] memory jSonFileRefs = new JSonFileRef[](persons[personId].numberFiles);
        for(uint64 i = 0; i < persons[personId].numberFiles; i++)
        {
            jSonFileRefs[i] = persons[personId].files[i];
        }
        return jSonFileRefs;
    }


    function getPersons() public view returns(PersonObject[] memory)
    {
        PersonObject[] memory person_objects = new PersonObject[](numberPersons);
        for(uint64 i = 0; i < numberPersons; i++)
        {
            person_objects[i] = PersonObject(persons[i].firstname, persons[i].lastname, persons[i].email, persons[i]._address, persons[i].numberFiles, "");
        }
        return person_objects;
    }

    function addFile(uint personId, JSonFileRef memory jSonFileRef) public
    {
        persons[personId].files[persons[personId].numberFiles] = jSonFileRef;
        persons[personId].numberFiles ++;
    }

    function updateFile(uint personId, uint fileId, JSonFileRef memory jSonFileRef) public
    {
        persons[personId].files[fileId] = jSonFileRef;
    }

    function deleteFile(uint personId, uint fileId) public
    {
        delete persons[personId].files[fileId];
    }
    function updatePerson(uint personId, PersonObject memory person) public
    {
        persons[personId].firstname = person.firstname;
        persons[personId].lastname = person.lastname;
        persons[personId].email = person.email;
        persons[personId].password = person.password;
    }

    function deletePerson(uint personId, uint fileId) public
    {
        delete persons[personId].files[fileId];
    }
}
