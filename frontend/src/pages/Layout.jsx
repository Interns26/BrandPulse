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