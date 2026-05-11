import { useState, useRef, useEffect } from "react";
import { Search, ShoppingCart, Bell, ChevronDown, User, Settings, X, Menu } from "lucide-react";

const GRADIENT_MAP = {
  "gradient-1": "from-violet-400 to-indigo-600",
  "gradient-2": "from-rose-400 to-pink-600",
  "gradient-3": "from-amber-400 to-orange-500",
  "gradient-4": "from-emerald-400 to-teal-600",
  "gradient-5": "from-sky-400 to-blue-600",
  "gradient-6": "from-fuchsia-400 to-purple-600",
  "gradient-7": "from-lime-400 to-green-600",
  "gradient-8": "from-red-400 to-rose-600",
  "gradient-9": "from-cyan-400 to-sky-600",
  "gradient-10": "from-yellow-400 to-amber-600",
  "gradient-11": "from-slate-400 to-gray-700",
  "gradient-12": "from-indigo-400 to-violet-700",
};

const EMOJI_MAP = {
  "emoji-cat": "🐱", "emoji-fox": "🦊", "emoji-penguin": "🐧",
  "emoji-koala": "🐨", "emoji-bear": "🐻", "emoji-panda": "🐼",
  "emoji-frog": "🐸", "emoji-tiger": "🐯", "emoji-robot": "🤖",
  "emoji-alien": "👽", "emoji-ghost": "👻", "emoji-ninja": "🥷",
};

import Link from "next/link";
import { useRouter } from "next/router";
import { useCart } from "./CartContext";
import CartDrawer from "./CartDrawer";
import { getUsernameFromToken, getUserIdFromToken } from "../lib/api";

function AvatarBubble({ avatarId, initials, size = "w-7 h-7" }) {
  if (!avatarId) {
    return (
      <div className={`${size} rounded-full bg-gradient-to-br from-fog to-ink flex items-center justify-center`}>
        <span className="text-white text-[10px] font-bold leading-none">{initials}</span>
      </div>
    );
  }
  if (avatarId.startsWith("emoji-")) {
    return (
      <div className={`${size} rounded-full bg-ash flex items-center justify-center text-base leading-none`}>
        {EMOJI_MAP[avatarId]}
      </div>
    );
  }
  return (
    <div className={`${size} rounded-full bg-gradient-to-br ${GRADIENT_MAP[avatarId] ?? "from-fog to-ink"} flex items-center justify-center`}>
      <span className="text-white text-[10px] font-bold leading-none">{initials}</span>
    </div>
  );
}

export default function Topbar({ onSearch, onMenuToggle }) {
  const { count } = useCart();
  const [cartOpen, setCartOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [profileOpen, setProfileOpen] = useState(false);
  const [avatarId, setAvatarId] = useState(null);
  const [initials, setInitials] = useState("");
  const [showChatTooltip, setShowChatTooltip] = useState(false);
  const tooltipTimerRef = useRef(null);
  const profileRef = useRef(null);
  const router = useRouter();
  const showSearch = router.pathname === "/";

  // Load avatar + username initials from localStorage / JWT
  useEffect(() => {
    const load = () => setAvatarId(localStorage.getItem("user_avatar"));
    load();
    window.addEventListener("storage", load);
    const username = getUsernameFromToken();
    if (username) setInitials(username.slice(0, 2).toUpperCase());
    return () => window.removeEventListener("storage", load);
  }, []);

  // Show chat tooltip once per user after login
  useEffect(() => {
    const userId = getUserIdFromToken();
    if (!userId) return;
    const seenKey = `chat_tooltip_seen_${userId}`;
    if (!localStorage.getItem(seenKey)) {
      setShowChatTooltip(true);
      tooltipTimerRef.current = setTimeout(() => {
        setShowChatTooltip(false);
        localStorage.setItem(seenKey, "1");
      }, 7000);
    }
    return () => clearTimeout(tooltipTimerRef.current);
  }, []);

  const dismissChatTooltip = () => {
    clearTimeout(tooltipTimerRef.current);
    setShowChatTooltip(false);
    const userId = getUserIdFromToken();
    if (userId) localStorage.setItem(`chat_tooltip_seen_${userId}`, "1");
  };

  const handleSearch = (e) => {
    setQuery(e.target.value);
    onSearch?.(e.target.value);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <>
      <header className="fixed top-0 left-0 md:left-60 right-0 h-16 bg-white border-b border-mist flex items-center px-3 md:px-6 gap-4 z-20">
        {/* Hamburger — mobile only */}
        <button
          onClick={onMenuToggle}
          className="md:hidden w-9 h-9 flex items-center justify-center rounded-xl hover:bg-ash transition"
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>

        {/* Search — dashboard only */}
        {showSearch && (
          <div className="flex-1 relative max-w-2xl">
            <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-fog" />
            <input
              type="text"
              value={query}
              onChange={handleSearch}
              placeholder="Search products…"
              className="w-full pl-10 pr-4 py-2.5 bg-ash rounded-xl text-sm text-ink placeholder:text-fog
                focus:outline-none focus:ring-2 focus:ring-ink/10 transition"
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3 ml-auto">
          {/* Cart */}
          <button
            onClick={() => setCartOpen(true)}
            className="relative w-9 h-9 flex items-center justify-center rounded-xl hover:bg-ash transition"
          >
            <ShoppingCart size={18} />
            {count > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-pop text-ink text-[10px] font-bold
                rounded-full flex items-center justify-center leading-none">
                {count}
              </span>
            )}
          </button>

          {/* Notifications + chat tooltip */}
          <div className="relative">
            <button
              className="relative w-9 h-9 flex items-center justify-center rounded-xl hover:bg-ash transition"
              onClick={dismissChatTooltip}
            >
              <Bell size={18} />
              {showChatTooltip && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-pop rounded-full animate-ping" />
              )}
            </button>

            {showChatTooltip && (
              <div className="absolute top-full right-0 mt-2 z-50 animate-fade-in">
                {/* Arrow pointing up toward the bell */}
                <span className="absolute -top-2 right-3 w-0 h-0
                  border-l-[6px] border-l-transparent
                  border-r-[6px] border-r-transparent
                  border-b-[8px] border-b-ink" />
                <div className="bg-ink text-white text-xs rounded-2xl px-4 py-2.5 shadow-xl w-72 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold mb-0.5">Hey! Got questions?</p>
                    <p className="text-white/75">Ask me anything — orders, items, policies, or just chat!</p>
                  </div>
                  <button
                    onClick={dismissChatTooltip}
                    className="shrink-0 hover:opacity-70 transition"
                    aria-label="Dismiss"
                  >
                    <X size={13} />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Profile dropdown */}
          <div className="relative" ref={profileRef}>
            <button
              onClick={() => setProfileOpen((o) => !o)}
              className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-xl hover:bg-ash transition"
            >
              <AvatarBubble avatarId={avatarId} initials={initials} />
              <ChevronDown size={13} className={`text-fog transition-transform ${profileOpen ? "rotate-180" : ""}`} />
            </button>

            {profileOpen && (
              <div className="absolute right-0 top-full mt-2 w-44 bg-white border border-mist rounded-xl shadow-lg overflow-hidden z-50">
                <Link
                  href="/account"
                  onClick={() => setProfileOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 text-sm text-ink hover:bg-ash transition"
                >
                  <User size={15} className="text-fog" />
                  Account
                </Link>
                <Link
                  href="/settings"
                  onClick={() => setProfileOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 text-sm text-ink hover:bg-ash transition border-t border-mist"
                >
                  <Settings size={15} className="text-fog" />
                  Settings
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      <CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} />
    </>
  );
}
