import { useState } from "react";
import {
  Box,
  Image,
  Text,
  Button,
  IconButton,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  FormControl,
  FormLabel,
  Input,
  Stack,
  CheckboxGroup,
  Checkbox,
  useToast,
} from "@chakra-ui/react";
import { AddIcon } from "@chakra-ui/icons";
import axios from "axios";
import jwt_decode from "jwt-decode";
import AppForm from "./AppForm";

const Card = () => {
  const [data, setData] = useState(null);
  const [sensors, setSensors] = useState([]);
  const [services, setservices] = useState([]);
  const toast = useToast();

  const { isOpen, onOpen, onClose } = useDisclosure();
  const userid = localStorage.getItem("username");
  const [showAppForm, setShowAppForm] = useState(false);
  const handleAppFormClose = () => setShowAppForm(false);

  return (
    <>
      <Box maxW="sm" borderWidth="1px" borderRadius="lg" overflow="hidden">
        <Image src={data?.image} alt={data?.title} />
        <Box p="6">
          <Text fontWeight="bold" fontSize="2xl">
            Add New APP
          </Text>

          <IconButton
            aria-label="Add data"
            icon={<AddIcon />}
            onClick={() => setShowAppForm(true)}
            mt="4"
          />
        </Box>
      </Box>
      {showAppForm && <AppForm handleAppFormClose={handleAppFormClose} />}
    </>
  );
};

export default Card;
