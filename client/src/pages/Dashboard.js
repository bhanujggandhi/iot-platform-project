import { useState, useEffect } from "react";
import {
  Box,
  Image,
  Text,
  Link,
  Button,
  Stack,
  Flex,
  Spacer,
} from "@chakra-ui/react";
import axios from "axios";
import { Routes, Route, useNavigate } from "react-router-dom";
import jwt_decode from "jwt-decode";
const Cards = () => {
  const [apps, setApps] = useState([]);
  const [u_id, setUid] = useState("");
  const [numCards, setNumCards] = useState(3); // state variable to keep track of number of cards to display
  const userId = localStorage.getItem("username");
  const fetchApps = async () => {
    const response = await axios.get(
      `http://127.0.0.1:5000/fetchapps?user_id=${userId}`
    );
    setApps(response.data);
  };

  useEffect(() => {
    fetchApps();
    setUid(userId);
  }, [userId]);

  const navigate = useNavigate();
  const [runningAppId, setRunningAppId] = useState(null);

  const handleStart = (appId) => {
    setRunningAppId(appId);
    // Add code to start the app
  };

  const handleStop = (appId) => {
    setRunningAppId(null);
    // Add code to stop the app
  };

  const toggleNumCards = () => {
    // Increase or decrease the number of displayed cards based on the current state
    setNumCards(numCards === 3 ? apps.length : 3);
  };

  return (
    <>
      <Box display="flex" flexWrap="wrap" justifyContent="space-between">
        {apps.slice(0, numCards).map((app) => (
          <Box
            key={app.app_id}
            m="5"
            borderWidth="1px"
            borderRadius="lg"
            width="30%"
            height="300px"
            margin="10px"
          >
            <Box p="6" height="100%">
              <Text fontWeight="bold" fontSize="2xl">
                {app.app_name}
              </Text>
              <Text mt="2">{app.modules}</Text>
              <Stack>
                <Button
                  onClick={() => {
                    if (runningAppId === app.app_id) {
                      handleStop(app.app_id);
                    } else {
                      handleStart(app.app_id);
                    }
                  }}
                  mt={4}
                  colorScheme={runningAppId === app.app_id ? "red" : "green"}
                >
                  {runningAppId === app.app_id ? "Stop" : "Start"}
                </Button>
                <Button
                  onClick={() => {
                    navigate(`/appsetting/${u_id}/${app.app_id}`);
                  }}
                >
                  Setting
                </Button>
              </Stack>
            </Box>
            <Spacer />
          </Box>
        ))}
      </Box>
      {numCards < apps.length && (
        <Button mt="4" onClick={toggleNumCards}>
          {numCards === 3 ? "Show more" : "Show less"}
        </Button>
      )}
    </>
  );
};

export default Cards;
