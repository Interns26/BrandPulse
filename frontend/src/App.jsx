import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./pages/Layout";
import Dashboard from "./pages/Dashboard";
import CompetitiveIntel from "./pages/CompetitiveIntel";
import RawDataPipeline from "./pages/RawDataPipeline";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="competitive-intel" element={<CompetitiveIntel />} />
          <Route path="raw-data-pipeline" element={<RawDataPipeline />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;