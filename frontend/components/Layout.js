import { useEffect } from "react";
import { useRouter } from "next/router";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

const MAIN_PAGES = ["/", "/orders", "/favorites"];

export default function Layout({ children, onSearch }) {
  const router = useRouter();

  useEffect(() => {
    if (MAIN_PAGES.includes(router.pathname)) {
      sessionStorage.setItem("last_main_page", router.pathname);
    }
  }, [router.pathname]);

  return (
    <div className="min-h-screen bg-ash">
      <Sidebar />
      <Topbar onSearch={onSearch} />
      <main className="ml-60 pt-16 min-h-screen">
        {children}
      </main>
    </div>
  );
}
