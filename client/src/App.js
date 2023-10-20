import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
  Routes,
} from "react-router-dom";

// layouts and pages
import RootLayout from "./layouts/RootLayout";
import AdminDashboard from "./pages/adminDashboard";
import DevDashboard from "./pages/DevDashboard";

import AdminLogin from "./pages/AdminLogin";
import DevLogin from "./pages/DevLogin";
import DevRegisteration from "./pages/DevRegisteration";
import LandingPage from "./pages/LandingPage";

import Appsettings from "./pages/AppSetting";
import RequireAuth from "./components/RequireAuth";

const ROLES = {
  User: 2001,
  Editor: 1984,
  Admin: 5150,
};
// // router and routes
// const router = createBrowserRouter(
//   createRoutesFromElements(
//     <Route path="/" element={<RootLayout />}>
//       <Route index element={<LandingPage />} />
//       <Route path="create" element={<Create />} />
//       <Route path="profile" element={<Profile />} />
//       <Route path="adminLogin" element={<AdminLogin />} />
//       <Route path="devLogin" element={<DevLogin />} />
//       <Route path="devRegisteration" element={<DevRegisteration />} />
//       <Route path="adminDashboard" element={<AdminDashboard />} />
//       <Route path="devDashboard" element={<DevDashboard />} />
//       <Route path="register" element={<Register />} />
//       <Route path="login" element={<Login />} />
//       <Route path="/appsetting/:user_id/:app_id" Component={Appsettings} />
//     </Route>
//   )
// );

function App() {
  return (
    <Routes>
      <Route path="/" element={<RootLayout />}>
        <Route index element={<LandingPage />} />
        {/* <Route path="create" element={<Create />} />
        <Route path="profile" element={<Profile />} /> */}
        <Route path="adminLogin" element={<AdminLogin />} />
        <Route path="devLogin" element={<DevLogin />} />
        <Route path="devRegisteration" element={<DevRegisteration />} />
        <Route element={<RequireAuth allowedRoles={[ROLES.Admin]} />}>
          <Route path="adminDashboard" element={<AdminDashboard />} />
        </Route>
        <Route element={<RequireAuth allowedRoles={[ROLES.User]} />}>
          <Route path="devDashboard" element={<DevDashboard />} />
          <Route path="/appsetting/:user_id/:app_id" Component={Appsettings} />
        </Route>

        <Route path="*" element={<LandingPage />} />
      </Route>
    </Routes>
  );
}

export default App;
