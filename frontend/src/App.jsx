/* Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement. */

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