import React, { useState, useEffect } from "react";
import {
  Box,
  Text,
  useColorModeValue,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from "@chakra-ui/react";
import fs from "fs";

function ShowFiles() {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    fs.readdir(".", (err, files) => {
      if (err) {
        console.error(err);
        return;
      }
      setFiles(files);
    });
  }, []);

  const textColor = useColorModeValue("gray.800", "gray.100");

  return (
    <Box p={4} borderRadius="lg" backgroundColor="white" boxShadow="md">
      <Text fontSize="lg" fontWeight="bold" mb={4}>
        Files
      </Text>
      <Table variant="simple" color={textColor}>
        <Thead>
          <Tr>
            <Th>Name</Th>
          </Tr>
        </Thead>
        <Tbody>
          {files.map((file) => (
            <Tr key={file}>
              <Td>{file}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}

export default ShowFiles;
