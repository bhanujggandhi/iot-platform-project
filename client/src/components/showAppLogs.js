import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Box,
  Flex,
  Text,
  useColorModeValue,
  VStack,
  HStack,
} from "@chakra-ui/react";

const LogScreen = () => {
  const [logs, setLogs] = useState([]);
  const api = process.env.MAIN_SERVER_URL;
  useEffect(() => {
    // Fetch logs from the server and update the state
    fetchLogs();
  }, []);

  const { userId, app_id } = useParams();
  console.log(app_id);
  const fetchLogs = async () => {
    try {
      const response = await fetch(`/${api}/logs/${userId}/${app_id}`);
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error(error);
    }
  };

  const textColor = "gray.100";
  const bgColor = "teal";

  return (
    <Box p={4} borderRadius="lg" backgroundColor={bgColor}>
      <Text fontSize="lg" fontWeight="bold" mb={4}>
        Logs
      </Text>
      {logs.length > 0 ? (
        <Box p={4} borderRadius="lg" backgroundColor="gray.800" boxShadow="md">
          {logs.map((log, index) => (
            <Flex key={index} alignItems="center">
              <Box as="span" color={getColor(log.level)} mr={2}>
                {log.level.toUpperCase()}
              </Box>
              <Box as="span" color={textColor} flex="1" mr={2}>
                {log.msg}
              </Box>
              <Box as="span" color={textColor} fontSize="sm" flex="0" mr={2}>
                {new Date(log.timestamp).toLocaleString()}
              </Box>
            </Flex>
          ))}
        </Box>
      ) : (
        <Box p={4} borderRadius="lg" backgroundColor="gray.800" boxShadow="md">
          <Text color={textColor}>No logs to show.</Text>
        </Box>
      )}
    </Box>
  );
};

const getColor = (level) => {
  switch (level) {
    case "info":
      return "green.500";
    case "warning":
      return "yellow.500";
    case "error":
      return "red.500";
    default:
      return "gray.500";
  }
};

export default LogScreen;
