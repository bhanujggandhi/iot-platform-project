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

function UserForm(props) {
  const [uid, setUid] = useState("");
  const [cn, setCn] = useState("");
  const [sn, setSn] = useState("");
  const [userPassword, setuserPassword] = useState("");
  const toast = useToast();

  const { isOpen, onOpen, onClose } = useDisclosure();
  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await axios.post(
        `http://127.0.0.1:8001/auth/adduser/${uid}/${cn}/${sn}/${userPassword}`,

        { headers: { "Content-Type": "application/json" } }
      );
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
    props.onClose();
  };
  return (
    <Drawer isOpen={true} onClose={props.onClose}>
      <DrawerOverlay />
      <DrawerContent>
        <DrawerHeader>Add User</DrawerHeader>
        <DrawerCloseButton />
        <form onSubmit={handleSubmit}>
          <DrawerBody>
            <FormControl mt="4">
              <FormLabel>Uid</FormLabel>
              <Input
                isRequired
                type="text"
                value={uid}
                onChange={(e) => setUid(e.target.value)}
              />
            </FormControl>
            <FormControl mt="4">
              <FormLabel>cn</FormLabel>
              <Input
                isRequired
                type="text"
                value={cn}
                onChange={(e) => setCn(e.target.value)}
              />
            </FormControl>
            <FormControl mt="4">
              <FormLabel>sn</FormLabel>
              <Input
                isRequired
                type="text"
                value={sn}
                onChange={(e) => setSn(e.target.value)}
              />
            </FormControl>
            <FormControl mt="4">
              <FormLabel>userPassword</FormLabel>
              <Input
                isRequired
                type="password"
                value={userPassword}
                onChange={(e) => setuserPassword(e.target.value)}
              />
            </FormControl>
          </DrawerBody>

          <DrawerFooter>
            <Button variant="ghost" mr="3" onClick={props.onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue" type="submit">
              Save
            </Button>
          </DrawerFooter>
        </form>
      </DrawerContent>
    </Drawer>
  );
}

export default UserForm;
