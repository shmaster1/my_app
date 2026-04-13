import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { Heart } from "lucide-react";
import Layout from "../components/Layout";
import { api, getUserIdFromToken } from "../lib/api";

export default function Favorites() {
  const router = useRouter();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (!token) { router.push("/login"); return; }
    const userId = getUserIdFromToken();
    if (!userId) { router.push("/login"); return; }

    api.getFavorites(userId)
      .then(setFavorites)
      .catch(() => setFavorites([]))
      .finally(() => setLoading(false));
  }, []);

  const handleRemove = async (itemId) => {
    const userId = getUserIdFromToken();
    if (!userId) return;
    try {
      await api.removeFavorite(userId, itemId);
      setFavorites((prev) => prev.filter((f) => f.item_id !== itemId));
    } catch {
      // ignore
    }
  };

  return (
    <Layout>
      <div className="px-8 py-7">
        <h1 className="font-display text-4xl tracking-widest text-ink mb-6">FAVORITES</h1>

        {loading && (
          <p className="text-fog text-sm">Loading...</p>
        )}

        {!loading && favorites.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 text-fog">
            <Heart size={40} strokeWidth={1.2} className="mb-4" />
            <p className="text-sm">No favorites yet. Heart an item on the dashboard to save it here.</p>
          </div>
        )}

        {!loading && favorites.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {favorites.map((item) => (
              <div
                key={item.item_id}
                className="bg-white rounded-2xl overflow-hidden border border-mist/60
                  hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group"
              >
                <div className="relative aspect-square bg-ash overflow-hidden">
                  <img
                    src={item.image_url}
                    alt={item.item_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    onError={(e) => {
                      e.target.src = `https://via.placeholder.com/300x300/e8e6e1/0f0f0f?text=${encodeURIComponent(item.item_name)}`;
                    }}
                  />
                  <button
                    onClick={() => handleRemove(item.item_id)}
                    className="absolute top-2.5 right-2.5 w-7 h-7 rounded-full bg-white/80 backdrop-blur-sm
                      flex items-center justify-center opacity-0 group-hover:opacity-100 transition"
                    title="Remove from favorites"
                  >
                    <Heart size={13} fill="#d4a853" stroke="#d4a853" />
                  </button>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-sm text-ink leading-tight">{item.item_name}</h3>
                  <div className="flex items-center gap-1 mt-0.5">
                    <span className="text-sm font-semibold text-ink">${Number(item.price).toFixed(2)}</span>
                  </div>
                  <p className="text-xs text-fog mt-0.5">Stock: {item.stock_available}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
