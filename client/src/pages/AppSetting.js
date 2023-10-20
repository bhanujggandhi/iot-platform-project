import { useEffect, useState } from "react";

import axios from "axios";
import {
  Box,
  Heading,
  Text,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from "@chakra-ui/react";

import AppKey from "../components/ShowApikey";
import Nav from "../components/Nav";
import LogScreen from "../components/showAppLogs";
import Deploy from "../components/DeployApp";
import AppSensors from "../components/showAppSensors";
import AppStats from "../components/AppStat";
import WorkFlow from "../components/createWorkflow";
const AppPage = () => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const appKey = localStorage.getItem("apikey");
  // get api key from the database
  console.log(appKey);

  return (
    <Box>
      <Nav />
      <Tabs isFitted variant="enclosed" colorScheme="teal">
        <TabList backgroundColor="gray.100">
          <Tab>Api Key</Tab>
          <Tab>Logs</Tab>
          <Tab>Deploy</Tab>
          <Tab>Sensors</Tab>
          <Tab>Work Flow</Tab>
          <Tab>Stats</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <AppKey appKey={appKey} />
          </TabPanel>
          <TabPanel>
            <LogScreen />
          </TabPanel>

          <TabPanel>
            <Deploy />
          </TabPanel>
          <TabPanel>
            <AppSensors />
          </TabPanel>
          <TabPanel>
            <WorkFlow />
          </TabPanel>
          <TabPanel>
            <AppStats />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default AppPage;
