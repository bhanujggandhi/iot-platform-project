import React from "react";
import {
  Flex,
  Text,
  Icon,
  Link,
  Menu,
  MenuButton,
  MenuList,
} from "@chakra-ui/react";
import NavHoverBox from "./NavHoverBox";

export default function NavItem({
  icon,
  title,
  active,
  navSize,
  handleForm0Click,
  handleForm1Click,
  handleForm2Click,
  handleForm3Click,
}) {
  return (
    <Flex
      mt={30}
      flexDir="column"
      w="100%"
      alignItems={navSize == "small" ? "center" : "flex-start"}
    >
      <Menu placement="right">
        <Link
          backgroundColor={active && "#AEC8CA"}
          p={3}
          borderRadius={8}
          _hover={{ textDecor: "none", backgroundColor: "#AEC8CA" }}
          w={navSize == "large" && "100%"}
          onClick={() => {
            if (title === "Dashboard") {
              handleForm0Click();
            }
            if (title === "upload") {
              handleForm1Click();
            }
            if (title === "Analytics") {
              handleForm2Click();
            }

            if (title === "report") {
              handleForm3Click();
            }
          }}
        >
          <MenuButton w="100%">
            <Flex>
              <Icon
                as={icon}
                fontSize="xl"
                color={active ? "#82AAAD" : "gray.500"}
              />
              <Text ml={5} display={navSize == "small" ? "none" : "flex"}>
                {title}
              </Text>
            </Flex>
          </MenuButton>
        </Link>
        {/* <MenuList py={0} border="none" w={200} h={200} ml={5}> */}
        {/* <NavHoverBox title={title} icon={icon} description={description} /> */}
        {/* </MenuList> */}
      </Menu>
    </Flex>
  );
}
