import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";


function Layout(){
    return (
        <>

        <div className="flex flex-col  min-h-screen">
            <Navbar/>

            <main className="flex-1 flex flex-col p-11 pt-20">
                <Outlet />
            </main>

            <Footer/>
        </div>
        </>
    );
}

export default Layout;