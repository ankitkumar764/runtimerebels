import React from "react";
import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import Sidebar from "./components/layout/Sidebar";
import Landing from "./pages/Landing";
import Upload from "./pages/Upload";
import Dashboard from "./pages/Dashboard";
import Approvals from "./pages/Approvals";
import Arena from "./pages/Arena";

function AppLayout() {
  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--bmw-canvas)" }}>
      <Navbar />
      <Sidebar />
      <main className="bmw-main-container">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Standalone Landing & Upload Flows */}
        <Route path="/" element={<Landing />} />
        <Route path="/upload" element={<Upload />} />
        
        {/* Core App dashboard, arena, approvals (with Navbar/Sidebar layout) */}
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/arena" element={<Arena />} />
          <Route path="/approvals" element={<Approvals />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
