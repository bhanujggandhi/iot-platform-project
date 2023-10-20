import { useState } from "react";
import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Checkbox,
  Stack,
  Button,
} from "@chakra-ui/react";
import AppKey from "./ShowApikey";

const EditableAppForm = ({ app }) => {
  return (
    <Box>
      <AppKey />
    </Box>
  );
};

export default EditableAppForm;
