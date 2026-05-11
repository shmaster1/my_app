import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { Check } from "lucide-react";
import Layout from "../components/Layout";
import { getUserIdFromToken, getUsernameFromToken } from "../lib/api";

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

function AvatarPreview({ selected, initials, size = "w-12 h-12" }) {
  if (!selected) {
    return (
      <div className={`${size} rounded-full bg-gradient-to-br from-fog to-ink flex items-center justify-center`}>
        <span className="text-white text-sm font-bold tracking-wide">{initials}</span>
      </div>
    );
  }
  if (selected.startsWith("emoji-")) {
    return (
      <div className={`${size} rounded-full bg-ash flex items-center justify-center text-3xl`}>
        {EMOJI_MAP[selected]}
      </div>
    );
  }
  return (
    <div className={`${size} rounded-full bg-gradient-to-br ${GRADIENT_MAP[selected] ?? "from-fog to-ink"} flex items-center justify-center`}>
      <span className="text-white text-sm font-bold tracking-wide drop-shadow">{initials}</span>
    </div>
  );
}

const AVATARS = [
  { id: "gradient-1", style: "from-violet-400 to-indigo-600" },
  { id: "gradient-2", style: "from-rose-400 to-pink-600" },
  { id: "gradient-3", style: "from-amber-400 to-orange-500" },
  { id: "gradient-4", style: "from-emerald-400 to-teal-600" },
  { id: "gradient-5", style: "from-sky-400 to-blue-600" },
  { id: "gradient-6", style: "from-fuchsia-400 to-purple-600" },
  { id: "gradient-7", style: "from-lime-400 to-green-600" },
  { id: "gradient-8", style: "from-red-400 to-rose-600" },
  { id: "gradient-9", style: "from-cyan-400 to-sky-600" },
  { id: "gradient-10", style: "from-yellow-400 to-amber-600" },
  { id: "gradient-11", style: "from-slate-400 to-gray-700" },
  { id: "gradient-12", style: "from-indigo-400 to-violet-700" },
];

const EMOJI_AVATARS = [
  { id: "emoji-cat", emoji: "🐱" },
  { id: "emoji-fox", emoji: "🦊" },
  { id: "emoji-penguin", emoji: "🐧" },
  { id: "emoji-koala", emoji: "🐨" },
  { id: "emoji-bear", emoji: "🐻" },
  { id: "emoji-panda", emoji: "🐼" },
  { id: "emoji-frog", emoji: "🐸" },
  { id: "emoji-tiger", emoji: "🐯" },
  { id: "emoji-robot", emoji: "🤖" },
  { id: "emoji-alien", emoji: "👽" },
  { id: "emoji-ghost", emoji: "👻" },
  { id: "emoji-ninja", emoji: "🥷" },
];

export default function Settings() {
  const router = useRouter();
  const [selected, setSelected] = useState(null);
  const [saved, setSaved] = useState(false);
  const [initials, setInitials] = useState("?");

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (!token) { router.push("/login"); return; }
    if (!getUserIdFromToken()) { router.push("/login"); return; }
    const stored = localStorage.getItem("user_avatar");
    if (stored) setSelected(stored);
    const username = getUsernameFromToken();
    if (username) setInitials(username.slice(0, 2).toUpperCase());
  }, []);

  const handleSelect = (id) => {
    setSelected(id);
    setSaved(false);
  };

  const handleSave = () => {
    if (selected) {
      localStorage.setItem("user_avatar", selected);
      window.dispatchEvent(new Event("storage"));
      setSaved(true);
      setTimeout(() => {
        const last = sessionStorage.getItem("last_main_page") || "/";
        router.push(last);
      }, 800);
    }
  };

  return (
    <Layout>
      <div className="px-4 md:px-8 py-5 md:py-7 max-w-2xl">
        <h1 className="font-display text-3xl md:text-4xl tracking-widest text-ink mb-8">SETTINGS</h1>

        {/* Avatar picker */}
        <div className="rounded-2xl border border-mist overflow-hidden">
          <div className="bg-ash px-5 py-3 text-[11px] font-semibold uppercase tracking-wider text-fog">
            Profile Avatar
          </div>
          <div className="px-5 py-6 space-y-6">

            {/* Live preview */}
            <div className="flex items-center gap-4">
              <AvatarPreview selected={selected} initials={initials} size="w-16 h-16 text-lg" />
              <div>
                <p className="text-sm font-semibold text-ink">{initials}</p>
                <p className="text-xs text-fog mt-0.5">
                  {selected ? "Looking good!" : "Select an avatar below"}
                </p>
              </div>
            </div>

            {/* Gradient avatars */}
            <div>
              <p className="text-xs font-semibold text-fog uppercase tracking-wider mb-3">Colors</p>
              <div className="grid grid-cols-6 gap-3">
                {AVATARS.map((av) => (
                  <button
                    key={av.id}
                    onClick={() => handleSelect(av.id)}
                    className="relative group flex items-center justify-center"
                  >
                    <div
                      className={`w-12 h-12 rounded-full bg-gradient-to-br ${av.style} ring-2 transition-all
                        flex items-center justify-center
                        ${selected === av.id
                          ? "ring-ink ring-offset-2"
                          : "ring-transparent group-hover:ring-fog group-hover:ring-offset-1"
                        }`}
                    >
                      <span className="text-white text-[11px] font-bold tracking-wide select-none drop-shadow">
                        {initials}
                      </span>
                    </div>
                    {selected === av.id && (
                      <div className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-ink rounded-full
                        flex items-center justify-center">
                        <Check size={9} className="text-white" strokeWidth={3} />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Emoji avatars */}
            <div>
              <p className="text-xs font-semibold text-fog uppercase tracking-wider mb-3">Characters</p>
              <div className="grid grid-cols-6 gap-3">
                {EMOJI_AVATARS.map((av) => (
                  <button
                    key={av.id}
                    onClick={() => handleSelect(av.id)}
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl
                      bg-ash ring-2 transition-all relative
                      ${selected === av.id
                        ? "ring-ink ring-offset-2"
                        : "ring-transparent hover:ring-fog hover:ring-offset-1"
                      }`}
                  >
                    {av.emoji}
                    {selected === av.id && (
                      <div className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-ink rounded-full
                        flex items-center justify-center">
                        <Check size={9} className="text-white" strokeWidth={3} />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

          </div>

          {/* Save bar */}
          <div className="border-t border-mist px-5 py-4 flex items-center justify-between bg-white">
            <p className="text-xs text-fog">
              {selected ? "Avatar selected — click Save to apply." : "Pick an avatar above."}
            </p>
            <button
              onClick={handleSave}
              disabled={!selected}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-ink text-white text-sm font-medium
                hover:bg-ink/80 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {saved ? <><Check size={14} /> Saved</> : "Save"}
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
