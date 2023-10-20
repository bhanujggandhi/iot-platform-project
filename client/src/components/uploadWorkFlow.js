import React, { useState } from "react";
import axios from "axios";
import { Button } from "@chakra-ui/react";

function UploadJsonFile() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");

  const handleFileInput = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleFileSubmit = () => {
    const formData = new FormData();
    formData.append("file", selectedFile);

    axios
      .post("http://192.168.137.27:8001/upload_file", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        if (response.data.success === 1) {
          setSuccessMessage("File uploaded successfully");
        }
      })
      .catch((error) => console.error(error));
  };

  return (
    <>
      <input type="file" name="file" onChange={handleFileInput} />

      <Button onClick={handleFileSubmit}>Upload</Button>

      {successMessage && <p>{successMessage}</p>}
    </>
  );
}

export default UploadJsonFile;
