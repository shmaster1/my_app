import Link from "next/link";
import { useRouter } from "next/router";
import {
  LayoutDashboard, Heart, Package, LogOut,
} from "lucide-react";
import { api } from "../lib/api";

const navItems = [
  { label: "Storefront", items: [
    { href: "/", icon: LayoutDashboard, label: "Dashboard" },
    { href: "/favorites", icon: Heart, label: "Favorites" },
    { href: "/orders", icon: Package, label: "Orders" },
  ]},
];

export default function Sidebar() {
  const router = useRouter();

  const handleLogout = () => {
    api.logout();
    router.push("/login");
  };

  return (
    <aside className="fixed top-0 left-0 h-screen w-60 bg-white border-r border-mist flex flex-col z-30">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3 px-6 py-5 border-b border-mist hover:bg-ash transition">
        <div className="w-8 h-8 bg-ink rounded flex items-center justify-center">
          <span className="text-white font-display text-lg leading-none">S</span>
        </div>
        <div>
          <div className="font-display text-xl tracking-widest leading-none text-ink">SHAPP</div>
          <div className="text-[10px] tracking-[0.2em] text-fog font-medium uppercase">Dashboard</div>
        </div>
      </Link>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {navItems.map((section) => (
          <div key={section.label}>
            <p className="text-[10px] tracking-[0.2em] uppercase text-fog font-semibold px-2 mb-2">
              {section.label}
            </p>
            <ul className="space-y-0.5">
              {section.items.map(({ href, icon: Icon, label }) => {
                const active = router.pathname === href;
                return (
                  <li key={href}>
                    <Link href={href}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
                        ${active
                          ? "bg-ink text-white"
                          : "text-accent hover:bg-ash"
                        }`}
                    >
                      <Icon size={16} strokeWidth={active ? 2.5 : 1.8} />
                      {label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Logout */}
      <div className="px-4 pb-6">
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 bg-accent text-white rounded-xl py-3 text-sm font-medium
            hover:bg-ink transition-colors"
        >
          <LogOut size={15} />
          Logout
        </button>
      </div>
    </aside>
  );
}
