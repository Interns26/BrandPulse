/* Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement. */

import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Sidebar from "../components/Sidebar";

function Layout() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      {/* Main Content Area with Sidebar */}
      <div className="flex flex-1 pt-14">
        <Sidebar />
        <main className="flex-1 flex flex-col">
          <Outlet />
        </main>
      </div>

      <Footer />
    </div>
  );
}

export default Layout;