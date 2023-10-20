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
  Text,
  useColorModeValue,
} from "@chakra-ui/react";

function DeployApp() {
  const bgColor = useColorModeValue("gray.100", "gray.700");
  const [version, setVersion] = useState("latest");
  const [isLoading, setIsLoading] = useState(false);
  const [deployedApp, setDeployedApp] = useState(null);
  const [file, setFile] = useState(null);
  const { userId, app_id } = useParams();
  const handleDeployApp = async () => {
    setIsLoading(true);

    // Make a call to deploy the app with the specified information

    const response = await axios.post(
      `/api/deploy/${userId}/${app_id}/${version}/${file}`
    );

    // If the deployment was successful, update the state with the app information
    if (response.status === 200) {
      const data = await response.json();
      setDeployedApp(data);
    }

    setIsLoading(false);
  };

  return (
    <Box p={4} borderRadius="lg" backgroundColor={bgColor}>
      <Text fontSize="xl" fontWeight="bold" mb={4}>
        Deploy App
      </Text>

      <FormControl id="version" mb={4}>
        <FormLabel>Version</FormLabel>
        <Select value={version} onChange={(e) => setVersion(e.target.value)}>
          <option value="latest">Latest</option>
          <option value="1.0">1.0</option>
          <option value="2.0">2.0</option>
          <option value="3.0">3.0</option>
        </Select>
      </FormControl>

      <FormControl id="file" isRequired mb={4}>
        <FormLabel>Zip File</FormLabel>
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
  );
}

export default DeployApp;
