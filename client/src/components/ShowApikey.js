import React, { useState } from "react";
import {
  Box,
  Text,
  useColorModeValue,
  Button,
  Input,
  InputGroup,
  InputRightElement,
  Flex,
  IconButton,
  useClipboard,
  Tooltip,
} from "@chakra-ui/react";
import { FiEye, FiEyeOff, FiCopy } from "react-icons/fi";

function AppKey({ appKey }) {
  const [showKey, setShowKey] = useState(false);
  const { onCopy, hasCopied } = useClipboard(appKey);

  const handleShowKey = () => {
    setShowKey(!showKey);
  };

  const bgColor = useColorModeValue("gray.320", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      backgroundColor={bgColor}
      boxShadow="2xl"
      p={6}
    >
      <Flex
        alignItems="center"
        justifyContent="space-between"
        width="50%"
        mb={4}
      >
        <Text fontSize="xl" fontWeight="bold">
          App Key
        </Text>
      </Flex>
      <InputGroup>
        <Input
          pr="4.5rem"
          type={showKey ? "text" : "password"}
          value={appKey}
          readOnly
        />
        <InputRightElement width="4.5rem">
          <Tooltip label={showKey ? "Hide Key" : "Show Key"}>
            <IconButton
              h="1.75rem"
              size="sm"
              onClick={handleShowKey}
              icon={showKey ? <FiEyeOff /> : <FiEye />}
            />
          </Tooltip>
          <Tooltip label={hasCopied ? "Copied!" : "Copy Key"}>
            <IconButton
              h="1.75rem"
              size="sm"
              onClick={onCopy}
              icon={<FiCopy />}
            />
          </Tooltip>
        </InputRightElement>
      </InputGroup>
    </Box>
  );
}

export default AppKey;
