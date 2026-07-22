import { Icon } from "@iconify/react";
import { useEffect, useState } from "react";

function Navbar() {
  const [viewMode, setViewMode] = useState("light");

  useEffect(() => {
    if (viewMode === "dark") {
      document.querySelector("html")?.classList.add("dark");
    } else {
      document.querySelector("html")?.classList.remove("dark");
    }
  }, [viewMode]);

  const toggleViewMode = () => {
    setViewMode(viewMode === "light" ? "dark" : "light");
  };

  return (
    <>
      <div className="fixed top-0 left-0 right-0 h-14 p-2 pr-10 bg-card flex items-center justify-between">
        <div className="flex items-center justify-center gap-2 text-accent">
          <Icon icon="fa-solid:chart-line" className="h-7 w-7  rounded-sm" />
          <div className="font-bold text-2xl">BrandPulse</div>
        </div>

        <div className="flex items-center justify-center gap-3 text-white">
          <div className={viewMode=="light"?"p-1 text-accent hover:bg-accent hover:text-white rounded-sm transition-colors":"p-1 text-accent hover:bg-accent hover:text-white rounded-sm transition-colors"}>
            <Icon
              onClick={toggleViewMode}
              icon={viewMode === "light" ? "lucide:sun" : "lucide:moon"}
              className="w-6 h-6"
            />
          </div>

          <div className="">
            <button className="flex items-center justify-center hover:opacity-95 gap-2 bg-accent p-1 px-3 rounded-sm font-semibold transition-transform duration-150 active:scale-95">
                <Icon icon="fe:export" className="w-5 h-5"/>
                <div>Export Report</div>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default Navbar;
