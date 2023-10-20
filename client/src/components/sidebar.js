import React, { useState } from "react";
import {
  Flex,
  Text,
  IconButton,
  Divider,
  Avatar,
  Heading,
} from "@chakra-ui/react";
import {
  FiMenu,
  FiHome,
  FiCalendar,
  FiUser,
  FiDollarSign,
  FiActivity,
  FiBriefcase,
  FiSettings,
  FiUploadCloud,
} from "react-icons/fi";
import { IoPawOutline } from "react-icons/io5";
import NavItem from "./NavItem";

import SensorDataPage from "./showSensor";
import UploadJsonFile from "./uploadWorkFlow";

export default function Sidebar({
  handleForm0Click,
  handleForm1Click,
  handleForm2Click,
  handleForm3Click,
}) {
  const [navSize, changeNavSize] = useState("large");
  return (
    <Flex
      pos="sticky"
      left="5"
      h="95vh"
      marginTop="2.5vh"
      boxShadow="0 4px 12px 0 rgba(0, 0, 0, 0.05)"
      borderRadius={navSize === "small" ? "15px" : "30px"}
      w={navSize === "small" ? "75px" : "200px"}
      flexDir="column"
      justifyContent="space-between"
    >
      <Flex
        p="5%"
        flexDir="column"
        w="100%"
        alignItems={navSize === "small" ? "center" : "flex-start"}
        as="nav"
      >
        <IconButton
          background="none"
          mt={5}
          _hover={{ background: "none" }}
          icon={<FiMenu />}
          onClick={() => {
            if (navSize === "small") changeNavSize("large");
            else changeNavSize("small");
          }}
        />
        <NavItem
          navSize={navSize}
          icon={FiHome}
          title="Dashboard"
          description="This is the description for the dashboard."
          handleForm0Click={handleForm0Click}
          handleForm1Click={handleForm1Click}
          handleForm2Click={handleForm2Click}
          handleForm3Click={handleForm3Click}
        />
        <NavItem
          navSize={navSize}
          icon={FiUploadCloud}
          title="upload"
          handleForm0Click={handleForm0Click}
          handleForm1Click={handleForm1Click}
          handleForm2Click={handleForm2Click}
          handleForm3Click={handleForm3Click}
        />

        <NavItem
          navSize={navSize}
          icon={FiActivity}
          title="Analytics"
          handleForm0Click={handleForm0Click}
          handleForm1Click={handleForm1Click}
          handleForm2Click={handleForm2Click}
          handleForm3Click={handleForm3Click}
        />

        <NavItem
          navSize={navSize}
          icon={FiBriefcase}
          title="Reports"
          handleForm0Click={handleForm0Click}
          handleForm1Click={handleForm1Click}
          handleForm2Click={handleForm2Click}
          handleForm3Click={handleForm3Click}
        />
        {/* <NavItem
          navSize={navSize}
          icon={FiSettings}
          title="Settings"
          handleAnalyticsClick={handleAnalyticsClick}
          handleshowUpload={handleshowUpload}
        /> */}
      </Flex>

      <Flex
        p="5%"
        flexDir="column"
        w="100%"
        alignItems={navSize === "small" ? "center" : "flex-start"}
        mb={4}
      >
        <Divider display={navSize === "small" ? "none" : "flex"} />
        <Flex mt={4} align="center">
          <Avatar size="sm" src="avatar-1.jpg" />
          <Flex
            flexDir="column"
            ml={4}
            display={navSize === "small" ? "none" : "flex"}
          >
            <Heading as="h3" size="sm">
              Avishek
            </Heading>
            <Text color="gray">Admin</Text>
          </Flex>
        </Flex>
      </Flex>
    </Flex>
  );
}
