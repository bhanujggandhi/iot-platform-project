import React, { useState, useEffect } from "react";
import {
  Flex,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useColorModeValue,
} from "@chakra-ui/react";
import axios from "axios";

function SensorDataPage({ userid }) {
  const [sensorData, setSensorData] = useState([]);

  useEffect(() => {
    // Fetch sensor data from the database
    async function fetchData() {
      try {
        const apiName = { api_name: "fetchsensors" };
        const response = await axios.post(
          "http://192.168.2.134:8000/",
          apiName,
          {
            headers: {
              "Content-Type": "application/json",
              accept: "application/json",
            },
          }
        );
        setSensorData(response.data.data);
        console.log(response.data);
      } catch (error) {
        console.error(error);
      }
    }
    fetchData();
  }, []);

  const tableBgColor = useColorModeValue("gray.100", "gray.700");
  const tableHeaderBgColor = useColorModeValue("gray.200", "gray.600");

  return (
    <Flex
      direction="column"
      align="top"
      justify="top"
      minH="100vh"
      bg={useColorModeValue("gray.50", "gray.900")}
    >
      <Heading as="h1" size="xl" mb="8">
        Sensor Data
      </Heading>
      <Table
        variant="simple"
        bg={tableBgColor}
        borderRadius="lg"
        boxShadow="md"
      >
        <Thead bg={tableHeaderBgColor}>
          <Tr>
            <Th>Sensor Description</Th>
            <Th>Sensor ID</Th>
            <Th>location</Th>
            <Th>Sensor Name</Th>
            <Th>Sensor Type</Th>
          </Tr>
        </Thead>
        <Tbody>
          {sensorData.map((data) => (
            <Tr key={data.sensorID}>
              <Td>{data.sensorDescription}</Td>
              <Td>{data.sensorID}</Td>
              <Td>{data.sensorLocation} </Td>
              <Td>{data.sensorName} </Td>
              <Td>{data.sensorType}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Flex>
  );
}

export default SensorDataPage;
