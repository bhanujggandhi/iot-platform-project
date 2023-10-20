import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";

import { AuthProvider } from "./context/AuthProvider";
import { ChakraProvider } from "@chakra-ui/react";

// const theme = extendTheme({
//   colors: {
//     brand: {
//       50: "#f0e4ff",
//       100: "#cbb2ff",
//       200: "#a480ff",
//       300: "#7a4dff",
//       400: "#641bfe",
//       500: "#5a01e5",
//       600: "#5200b3",
//       700: "#430081",
//       800: "#2d004f",
//       900: "#14001f",
//     },
//   },
//   fonts: {
//     heading: `'Inter', sans-serif`,
//     body: `'Inter', sans-serif`,
//   },
// });

ReactDOM.createRoot(document.getElementById("root")).render(
  <ChakraProvider>
    <React.StrictMode>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/*" element={<App />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </React.StrictMode>
  </ChakraProvider>
);
