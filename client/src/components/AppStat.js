import React, { useState, useEffect } from "react";
import {
  Box,
  Heading,
  Stat,
  StatLabel,
  StatNumber,
  useColorModeValue,
} from "@chakra-ui/react";
import { useParams } from "react-router-dom";

function SystemStats() {
  const [cpuUsage, setCpuUsage] = useState(0);
  const [apiHitCount, setApiHitCount] = useState(0);
  const api = process.env.MAIN_SERVER_URL;
  const { userid, appid } = useParams();
  useEffect(() => {
    // Fetch CPU usage and API hit count from the server
    const fetchStats = async () => {
      try {
        const response = await fetch(`/${api}/stats/${userid}/${appid}`);
        const { cpuUsage, apiHitCount } = await response.json();
        setCpuUsage(cpuUsage);
        setApiHitCount(apiHitCount);
      } catch (error) {
        console.error(error);
      }
    };

    // Fetch stats every 5 seconds
    const intervalId = setInterval(fetchStats, 5000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const bgColor = "teal";

  return (
    <Box p={4} borderRadius="lg" backgroundColor={bgColor}>
      <Heading as="h2" size="md" mb={4}>
        System Stats
      </Heading>

      <Stat>
        <StatLabel>CPU Usage</StatLabel>
        <StatNumber>{cpuUsage.toFixed(2)}%</StatNumber>
      </Stat>

      <Stat mt={4}>
        <StatLabel>API Hit Count</StatLabel>
        <StatNumber>{apiHitCount}</StatNumber>
      </Stat>
    </Box>
  );
}

export default SystemStats;
