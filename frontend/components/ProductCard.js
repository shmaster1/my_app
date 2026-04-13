import { useState } from "react";
import { ShoppingCart, Heart, CheckCircle } from "lucide-react";
import { useCart } from "./CartContext";
import { api, getUserIdFromToken } from "../lib/api";

export default function ProductCard({ product, style }) {
  const { addToCart } = useCart();
  const [added, setAdded] = useState(false);
  const [liked, setLiked] = useState(false);

  const handleAdd = () => {
    addToCart(product);
    setAdded(true);
    setTimeout(() => setAdded(false), 1800);
  };

  const handleLike = async () => {
    const userId = getUserIdFromToken();
    if (!userId) return;
    try {
      if (liked) {
        await api.removeFavorite(userId, product.id);
      } else {
        await api.addFavorite(userId, product.id);
      }
      setLiked(!liked);
    } catch (e) {
      // silently ignore duplicate or not-found errors
    }
  };

  return (
    <div
      className="bg-white rounded-2xl overflow-hidden border border-mist/60
        hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group fade-up"
      style={style}
    >
      {/* Image */}
      <div className="relative aspect-square bg-ash overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => {
            e.target.src = `https://via.placeholder.com/300x300/e8e6e1/0f0f0f?text=${encodeURIComponent(product.name)}`;
          }}
        />
        {/* Stock badge */}
        {product.stock <= 2 && product.stock > 0 && (
          <span className="absolute top-2.5 left-2.5 bg-pop text-ink text-[10px] font-bold
            px-2 py-0.5 rounded-full uppercase tracking-wide">
            Low Stock
          </span>
        )}
        {product.stock === 0 && (
          <span className="absolute inset-0 bg-white/60 flex items-center justify-center
            text-ink font-display tracking-widest text-lg backdrop-blur-[2px]">
            SOLD OUT
          </span>
        )}

        {/* Wishlist */}
        <button
          onClick={handleLike}
          className="absolute top-2.5 right-2.5 w-7 h-7 rounded-full bg-white/80 backdrop-blur-sm
            flex items-center justify-center opacity-0 group-hover:opacity-100 transition"
        >
          <Heart size={13} fill={liked ? "#d4a853" : "none"} stroke={liked ? "#d4a853" : "#0f0f0f"} />
        </button>
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold text-sm text-ink leading-tight">{product.name}</h3>
        <div className="flex items-center gap-1 mt-0.5">
          <span className="text-sm font-semibold text-ink">${product.price.toFixed(2)}</span>
        </div>
        <p className="text-xs text-fog mt-0.5">Stock: {product.stock}</p>

        <div className="flex items-center gap-2 mt-3">
          <button
            onClick={handleAdd}
            disabled={product.stock === 0}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-semibold
              transition-all duration-200
              ${product.stock === 0
                ? "bg-mist text-fog cursor-not-allowed"
                : added
                  ? "bg-green-600 text-white scale-95"
                  : "bg-ink text-white hover:bg-accent active:scale-95"
              }`}
          >
            {added ? <CheckCircle size={12} /> : <ShoppingCart size={12} />}
            {added ? "Added!" : "Add to Cart"}
          </button>
        </div>
      </div>
    </div>
  );
}
