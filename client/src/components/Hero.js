import {
  Box,
  Button,
  Flex,
  Img,
  Spacer,
  Text,
  useMediaQuery,
  Stack,
} from "@chakra-ui/react";
import React from "react";
import { Routes, Route, useNavigate } from "react-router-dom";

import chakraHero from "../assets/chakraHero.jpg";
import Sidebar from "./sidebar";

const Hero = () => {
  const navigate = useNavigate();

  const navigateToLogin = () => {
    // 👇️ navigate to /contacts
    navigate("/devLogin");
  };

  const navigateToRegister = () => {
    // 👇️ navigate to /devRegisteration
    navigate("/devRegisteration");
  };
  const [isLargerThanLG] = useMediaQuery("(min-width: 62em)");
  return (
    <Flex
      alignItems="center"
      w="full"
      px={isLargerThanLG ? "16" : "6"}
      py="16"
      minHeight="90vh"
      justifyContent="space-between"
      flexDirection={isLargerThanLG ? "row" : "column"}
    >
      <Box mr={isLargerThanLG ? "6" : "0"} w={isLargerThanLG ? "60%" : "full"}>
        <Text
          fontSize={isLargerThanLG ? "5xl" : "4xl"}
          fontWeight="bold"
          mb="4"
        >
          {" "}
          Team 1 platform
        </Text>

        <Text mb="6" fontSize={isLargerThanLG ? "lg" : "base"} opacity={0.7}>
          Sample Code for the blog article React MUI Components - Learn by
          Coding. The article explains how to code from scratch all components:
          navBar, hero section, app features, contact, and footer.
        </Text>

        <Stack direction="row" spacing={4} align="center">
          <Button colorScheme="teal" variant="solid" onClick={navigateToLogin}>
            LOGIN
          </Button>
          <Button
            colorScheme="teal"
            variant="outline"
            onClick={navigateToRegister}
          >
            Register
          </Button>
        </Stack>
      </Box>
      <Spacer />
      <Flex
        w={isLargerThanLG ? "40%" : "full"}
        alignItems="center"
        justifyContent="center"
      >
        <Img src={chakraHero} alt="Chakra UI" />
      </Flex>
    </Flex>
  );
};

export default Hero;
