// UserForm.js

import React, { useState } from "react";
import axios from "axios";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  DrawerHeader,
  DrawerCloseButton,
  DrawerBody,
  DrawerFooter,
  FormControl,
  FormLabel,
  Input,
  Button,
  useToast,
  useDisclosure,
  Drawer,
  DrawerOverlay,
  DrawerContent,
} from "@chakra-ui/react";

function UserForm({ handleAppFormClose }) {
  const [AppName, setAppName] = useState("");
  const [Organisation, setOrganisation] = useState("");
  const [ProjectName, setProjectName] = useState("");
  const [userPassword, setuserPassword] = useState("");
  const toast = useToast();
  const userid = localStorage.getItem("username");

  const { isOpen, onOpen, onClose } = useDisclosure();
  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = {
      user_id: userid,
      app_name: AppName,
    };

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/addapp",
        payload
      );
      // const tokenResponse = await axios.get(
      //   `http://127.0.0.1:5000/appKey/${AppName}`
      // );

      localStorage.setItem("apikey", response.data.token);
      //   console.log(response.data.message);
      toast({
        title: "Registration successful!",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: "Registration failed!",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      //   setError(error.response.data.message);
    }
    {
      handleAppFormClose();
    }
  };
  return (
    <Drawer isOpen={true} onClose={handleAppFormClose}>
      <DrawerOverlay />
      <DrawerContent>
        <DrawerHeader>Add User</DrawerHeader>
        <DrawerCloseButton />
        <form onSubmit={handleSubmit}>
          <DrawerBody>
            <FormControl mt="4">
              <FormLabel>AppName</FormLabel>
              <Input
                isRequired
                type="text"
                value={AppName}
                onChange={(e) => setAppName(e.target.value)}
              />
            </FormControl>
            <FormControl mt="4">
              <FormLabel>Organisation</FormLabel>
              <Input
                isRequired
                type="text"
                value={Organisation}
                onChange={(e) => setOrganisation(e.target.value)}
              />
            </FormControl>
            <FormControl mt="4">
              <FormLabel>Project Name</FormLabel>
              <Input
                isRequired
                type="text"
                value={ProjectName}
                onChange={(e) => setProjectName(e.target.value)}
              />
            </FormControl>
          </DrawerBody>

          <DrawerFooter>
            <Button variant="ghost" mr="3" onClick={handleAppFormClose}>
              Cancel
            </Button>
            <Button colorScheme="teal" type="submit">
              Save
            </Button>
          </DrawerFooter>
        </form>
      </DrawerContent>
    </Drawer>
  );
}

export default UserForm;
