import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import ChatWidget from "./ChatWidget";

const MAIN_PAGES = ["/", "/orders", "/favorites"];

export default function Layout({ children, onSearch }) {
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    setSidebarOpen(false);
  }, [router.pathname]);

  useEffect(() => {
    if (MAIN_PAGES.includes(router.pathname)) {
      sessionStorage.setItem("last_main_page", router.pathname);
    }
  }, [router.pathname]);

  return (
    <div className="min-h-screen bg-ash">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <Topbar onSearch={onSearch} onMenuToggle={() => setSidebarOpen((o) => !o)} />
      <main className="md:ml-60 pt-16 min-h-screen">
        {children}
      </main>
      <ChatWidget />
    </div>
  );
}
