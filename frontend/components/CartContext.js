import { createContext, useContext, useState, useEffect } from "react";
import { getUserIdFromToken } from "../lib/api";

const CartContext = createContext();

function getStorageKey() {
  if (typeof window === "undefined") return "cart_guest";
  const userId = getUserIdFromToken();
  return userId ? `cart_${userId}` : "cart_guest";
}

export function CartProvider({ children }) {
  const [cart, setCart] = useState(() => {
    if (typeof window === "undefined") return [];
    try {
      const saved = localStorage.getItem(getStorageKey());
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Persist cart to localStorage on every change
  useEffect(() => {
    if (typeof window === "undefined") return;
    localStorage.setItem(getStorageKey(), JSON.stringify(cart));
  }, [cart]);

  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.id === product.id);
      if (existing) return prev.map((i) => i.id === product.id ? { ...i, qty: i.qty + 1 } : i);
      return [...prev, { ...product, qty: 1 }];
    });
  };

  const removeFromCart = (id) => setCart((prev) => prev.filter((i) => i.id !== id));

  const clearCart = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(getStorageKey());
    }
    setCart([]);
  };

  const total = cart.reduce((sum, i) => sum + i.price * i.qty, 0);
  const count = cart.reduce((sum, i) => sum + i.qty, 0);

  return (
    <CartContext.Provider value={{ cart, addToCart, removeFromCart, clearCart, total, count }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
