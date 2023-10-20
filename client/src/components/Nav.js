import React, { useState } from "react";
import {
  Text,
  Flex,
  Spacer,
  IconButton,
  useColorMode,
  useColorModeValue,
  Box,
  Heading,
  ButtonGroup,
  Button,
  useMediaQuery,
} from "@chakra-ui/react";
import { MoonIcon, SunIcon } from "@chakra-ui/icons";
import { FaAlignJustify } from "react-icons/fa";
import { Icon } from "@chakra-ui/react";

const Nav = ({ onOpen, ref }) => {
  const [scroll, setScroll] = useState(false);
  const { colorMode, toggleColorMode } = useColorMode();
  const navBg = useColorModeValue("white", "blackAlpha.200");
  const [isLargerThanMD] = useMediaQuery("(min-width: 48em)");

  const changeScroll = () =>
    document.body.scrollTop > 80 || document.documentElement.scrollTop > 80
      ? setScroll(true)
      : setScroll(false);

  window.addEventListener("scroll", changeScroll);

  const token = localStorage.getItem("token");

  const handleLogout = () => {
    // Handle logout functionality here
    // For example, you could redirect the user to the login page
    localStorage.removeItem("token");
    localStorage.setItem("username", "");
    localStorage.setItem("isLoggedIn", false);
    window.location.href = "/devLogin";
  };
  return (
    <Flex
      h="10vh"
      alignItems="center"
      p="6"
      boxShadow={scroll ? "base" : "none"}
      top="0"
      zIndex="sticky"
      w="full"
      bg={navBg}
    >
      <Box p="2">
        <Heading size="md">🫦IASBrew</Heading>
      </Box>
      <Spacer />
      {token && (
        <Button colorScheme="teal" onClick={handleLogout}>
          logout
        </Button>
      )}
    </Flex>
  );
};

export default Nav;
