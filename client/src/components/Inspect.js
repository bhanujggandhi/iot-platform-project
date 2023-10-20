import React, { useState, useEffect } from "react";
import {
  Box,
  Text,
  useColorModeValue,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from "@chakra-ui/react";

function Inspect() {
  const bgColor = "teal";
  const [environment, setEnvironment] = useState({});
  const [port, setPort] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/api/inspect");
        const data = await response.json();
        setEnvironment(data.environment);
        setPort(data.port);
      } catch (error) {
        console.error(error);
      }
    };

    fetchData();
  }, []);

  return (
    <Box p={4} borderRadius="lg" backgroundColor={bgColor}>
      <Text fontSize="xl" fontWeight="bold" mb={4}>
        Inspect
      </Text>

      <Accordion defaultIndex={[0]} allowMultiple>
        <AccordionItem backgroundColor="white">
          <AccordionButton>
            <Box flex="1" textAlign="left">
              Environment
            </Box>
            <AccordionIcon />
          </AccordionButton>
          <AccordionPanel>
            <Box>
              <Text fontWeight="bold">NODE_ENV:</Text>{" "}
              {environment.NODE_ENV || "Not set"}
            </Box>
            <Box>
              <Text fontWeight="bold">REACT_APP_API_URL:</Text>{" "}
              {environment.REACT_APP_API_URL || "Not set"}
            </Box>
          </AccordionPanel>
        </AccordionItem>

        <AccordionItem backgroundColor="white">
          <AccordionButton>
            <Box flex="1" textAlign="left">
              Port
            </Box>
            <AccordionIcon />
          </AccordionButton>
          <AccordionPanel>
            <Box>
              <Text fontWeight="bold">PORT:</Text> {port || "Not set"}
            </Box>
          </AccordionPanel>
        </AccordionItem>
      </Accordion>
    </Box>
  );
}

export default Inspect;
