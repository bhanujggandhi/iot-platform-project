import React, { useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Spacer,
  Text,
  useColorModeValue,
  Link,
} from "@chakra-ui/react";

function WorkFlow() {
  const bgColor = useColorModeValue("gray.100", "gray.700");
  const [Type, setType] = useState("WorkFLow");
  const [isLoading, setIsLoading] = useState(false);
  const [deployedApp, setDeployedApp] = useState(null);
  const [file, setFile] = useState(null);
  const { userId, app_id } = useParams();
  const url = "https://google.com";
  const api = process.env.WORK_FLOW_URL;
  const handleUrlClick = () => {
    window.open(url, "_blank");
  };
  const handleDeployApp = async () => {
    setIsLoading(true);

    // Make a call to deploy the app with the specified information
    let response;
    if (Type === "node-red") {
      response = await axios.post(
        //   `/api/create/${userId}/${app_id}/${Type}/${file}`

        `/${api}/upload_file_nodered_flow`
      );
    } else {
      response = await axios.post(
        //   `/api/create/${userId}/${app_id}/${Type}/${file}`

        `/${api}/upload_file`
      );
    }

    // If the deployment was successful, update the state with the app information
    if (response.status === 200) {
      const data = await response.json();
      setDeployedApp(data);
    }

    setIsLoading(false);
  };

  return (
    <>
      <Box p={4} borderRadius="lg" backgroundColor={bgColor}>
        <Text fontSize="xl" fontWeight="bold" mb={4}>
          Deploy App
        </Text>

        <FormControl id="version" mb={4}>
          <FormLabel>WorkFlow</FormLabel>
          <Select value={Type} onChange={(e) => setType(e.target.value)}>
            <option value="WorkFLow">Customized workflow</option>
            <option value="node-red">Node-Red</option>
          </Select>
        </FormControl>

        <FormControl id="file" isRequired mb={4}>
          <FormLabel>workflow file</FormLabel>
          <Input type="file" onChange={(e) => setFile(e.target.files[0])} />
        </FormControl>

        <Button
          colorScheme="teal"
          onClick={handleDeployApp}
          isLoading={isLoading}
        >
          Deploy
        </Button>

        {deployedApp && (
          <Box mt={4}>
            <Text fontSize="md" fontWeight="bold">
              App Deployed!
            </Text>
            <Text>App Name: {deployedApp.appName}</Text>
            <Text>Language: {deployedApp.language}</Text>
            <Text>Version: {deployedApp.version}</Text>
          </Box>
        )}
      </Box>
      {Type == "node-red" && (
        <Box p={4} borderRadius="lg" backgroundColor="red" margin={5}>
          <Link onClick={handleUrlClick} cursor="pointer" fontSize="lg">
            {url}
          </Link>
        </Box>
      )}
    </>
  );
}

export default WorkFlow;
