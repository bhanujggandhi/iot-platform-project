import { useState } from "react";
import { Box, Button, FormControl, FormLabel, Input } from "@chakra-ui/react";

const FileUploadForm = () => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = () => {
    setIsUploading(true);
    // Perform file upload logic here using the "file" state
    // Once upload is complete, set isUploading to false
  };

  const handleStopUpload = () => {
    // Cancel file upload logic here
    setIsUploading(false);
  };

  return (
    <Box maxW="md" borderWidth="1px" borderRadius="lg" overflow="hidden" p="4">
      <FormControl>
        <FormLabel>Upload File</FormLabel>
        <Input type="file" onChange={handleFileChange} />
      </FormControl>
      <Box mt="4">
        {isUploading ? (
          <Button onClick={handleStopUpload}>Stop Upload</Button>
        ) : (
          <Button onClick={handleUpload} disabled={!file}>
            Start Upload
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default FileUploadForm;
