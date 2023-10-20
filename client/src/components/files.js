import React, { useState, useEffect } from "react";
import { Box, Text, Button } from "@chakra-ui/react";

function ShowFiles() {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    async function fetchFiles() {
      try {
        const response = await fetch("/api/files");
        const data = await response.json();
        setFiles(data.files);
      } catch (error) {
        console.error(error);
      }
    }
    fetchFiles();
  }, []);

  return (
    <Box>
      <Text fontSize="lg" fontWeight="bold" mb={4}>
        Files and Directories
      </Text>
      {files.map((file) => (
        <Box
          key={file.name}
          border="1px solid"
          borderColor="gray.300"
          borderRadius="md"
          p={2}
          mb={2}
        >
          <Text fontSize="md" fontWeight="bold">
            {file.name}
          </Text>
          <Text fontSize="sm" color="gray.500">
            {file.type}
          </Text>
          <Button
            as="a"
            href={`/api/files/${file.name}`}
            download={file.name}
            mt={2}
          >
            Download
          </Button>
        </Box>
      ))}
    </Box>
  );
}

export default ShowFiles;
