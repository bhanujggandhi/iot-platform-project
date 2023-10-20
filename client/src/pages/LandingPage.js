import { Container, Heading } from "@chakra-ui/react";
import Sidebar from "../components/sidebar";
// import Navbar from "../components/NavBar";
import AboutUs from "../components/AboutUs";
import ContactUs from "../components/ContactUs";
import Footer from "../components/Footer";
import Hero from "../components/Hero";
import Nav from "../components/Nav";

import Testimonials from "../components/Testimonials";
import React, { useRef } from "react";
import { useDisclosure, Box } from "@chakra-ui/react";
import DrawerComponent from "../components/DrawerComponent";

export default function Dashboard() {
  return (
    <div>
      <div>
        <Nav />
        <Hero />
        <AboutUs />
        <Testimonials />
        <ContactUs />
        <Footer />
      </div>
    </div>
  );
}
