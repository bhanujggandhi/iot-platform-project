// App.js

import React, { useState } from "react";
import {
  ChakraProvider,
  Box,
  Flex,
  Spacer,
  Button,
  Text,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Heading,
} from "@chakra-ui/react";
import UserForm from "../components/UserForm";
import LogsScreen from "../components/showLogs";
import Inspect from "../components/Inspect";
import ShowFiles from "../components/files";
import SystemStats from "../components/stat";

function App() {
  const [showUserForm, setShowUserForm] = useState(false);
  const [showSensorForm, setShowSensorForm] = useState(false);

  const handleUserFormClose = () => setShowUserForm(false);
  const textColor = useColorModeValue("gray.800", "gray.100");
  const bgColor = useColorModeValue("gray.100", "gray.700");
  const handleLogout = () => {
    // Handle logout functionality here
    // For example, you could redirect the user to the login page
    localStorage.removeItem("token");
    localStorage.setItem("username", "");
    localStorage.setItem("isLoggedIn", false);
    window.location.href = "/devLogin";
  };
  return (
    <ChakraProvider>
      <>
        <Flex direction="column" h="100vh">
          <Box p="4" backgroundColor="gray.100">
            <Flex alignItems="center">
              <Box p="2">
                <Heading size="xl">🫦Admin Dashboard</Heading>
              </Box>
              <Spacer />
              <Button
                colorScheme="teal"
                mr="4"
                onClick={() => setShowUserForm(true)}
              >
                Add User
              </Button>
              <Button colorScheme="teal" onClick={handleLogout}>
                logout
              </Button>
            </Flex>
          </Box>
          <Tabs isFitted variant="enclosed" colorScheme="green">
            <TabList backgroundColor="gray.100">
              <Tab>Logs</Tab>
              <Tab>Inspect</Tab>
              <Tab>Stats</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <LogsScreen />
              </TabPanel>
              <TabPanel>
                <Inspect />
              </TabPanel>

              <TabPanel>
                <SystemStats />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Flex>
        {showUserForm && <UserForm onClose={handleUserFormClose} />}
      </>
    </ChakraProvider>
  );
}

export default App;
