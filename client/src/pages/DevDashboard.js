import {
  Container,
  Heading,
  Stack,
  VStack,
  StackDivider,
  Text,
  Flex,
  Spacer,
  IconButton,
  useColorMode,
  useColorModeValue,
  ButtonGroup,
  Button,
  useMediaQuery,
  AspectRatio,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
} from "@chakra-ui/react";

import React, { useRef } from "react";
import { useState } from "react";
import { useLocation } from "react-router-dom";

import { useDisclosure, Box } from "@chakra-ui/react";
import DrawerComponent from "../components/DrawerComponent";

import Sidebar from "../components/sidebar";
import Nav from "../components/Nav";
import AddApp from "../components/AddApplication";
import Dash from "./Dashboard";
import SensorDataPage from "../components/showSensor";
import UploadJsonFile from "../components/uploadWorkFlow";

export default function Dashboard() {
  const navBg = useColorModeValue("white", "blackAlpha.200");
  const [showAnalytic, setShowAnalytics] = useState(false);

  const [showDash0, setShowForm0] = useState(true);
  const [showDash1, setShowForm1] = useState(false);
  const [showDash2, setShowForm2] = useState(false);
  const [showDash3, setShowForm3] = useState(false);

  const handleForm0Click = () => {
    setShowForm0(true);
    if (!showDash0) {
      setShowForm1(false);
      setShowForm2(false);
      setShowForm3(false);
    }
  };
  const handleForm1Click = () => {
    setShowForm1(!showDash1);
    if (showDash1) {
      setShowForm0(true);
      setShowForm2(false);
      setShowForm3(false);
    } else {
      setShowForm0(false);
      setShowForm2(false);
      setShowForm3(false);
    }
  };
  const handleForm2Click = () => {
    setShowForm2(!showDash2);
    if (showDash2) {
      setShowForm0(true);
      setShowForm1(false);
      setShowForm3(false);
    } else {
      setShowForm0(false);
      setShowForm1(false);
      setShowForm3(false);
    }
  };
  const handleForm3Click = () => {
    setShowForm3(!showDash3);
    if (showDash3) {
      setShowForm0(true);
      setShowForm1(false);
      setShowForm2(false);
    } else {
      setShowForm0(false);
      setShowForm2(false);
      setShowForm1(false);
    }
  };

  return (
    <div>
      <Flex alignItems="top" p="6" top="0" zIndex="sticky" w="full" bg={navBg}>
        <Sidebar
          handleForm0Click={handleForm0Click}
          handleForm1Click={handleForm1Click}
          handleForm2Click={handleForm2Click}
          handleForm3Click={handleForm3Click}
        />
        <Stack spacing={4} align="stretch" direction="Column" w="100%">
          <Nav />
          <Stack m="4" w="100%" align="stretch">
            {showDash0 && (
              <>
                <Dash />
                <AddApp />
              </>
            )}
            {showDash2 && <SensorDataPage />}
            {showDash1 && <UploadJsonFile />}
            {showDash3 && <UploadJsonFile />}
          </Stack>
        </Stack>
      </Flex>
    </div>
  );
}
