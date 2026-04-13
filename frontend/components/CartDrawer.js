import { useState } from "react";
import { X, Trash2, CheckCircle, AlertCircle } from "lucide-react";
import { useCart } from "./CartContext";
import { api } from "../lib/api";

export default function CartDrawer({ open, onClose }) {
  const { cart, removeFromCart, clearCart, total } = useCart();
  const [address, setAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [orderTotal, setOrderTotal] = useState(null);

  const handleCheckout = async () => {
    if (!address.trim()) { setError("Please enter a shipping address."); return; }
    setLoading(true);
    setError(null);
    try {
      for (const item of cart) {
        await api.addItemToOrder(item.id, item.qty, address.trim());
      }
      const order = await api.purchaseOrder();
      clearCart();
      setAddress("");
      setOrderTotal(order?.total_price ?? null);
      setSuccess(true);
      setTimeout(() => { setSuccess(false); setOrderTotal(null); onClose(); }, 3000);
    } catch (e) {
      setError("Checkout failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-ink/20 z-40 backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      <div className={`fixed top-0 right-0 h-screen w-80 bg-white z-50 flex flex-col
        shadow-2xl transition-transform duration-300 ${open ? "translate-x-0" : "translate-x-full"}`}>

        <div className="flex items-center justify-between px-6 py-5 border-b border-mist">
          <h2 className="font-display text-2xl tracking-widest">CART</h2>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-ash">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {cart.length === 0 ? (
            <div className="text-center text-fog text-sm mt-16">Your cart is empty</div>
          ) : cart.map((item) => (
            <div key={item.id} className="flex items-center gap-3 p-3 bg-ash rounded-xl">
              <img src={item.image} alt={item.name}
                className="w-14 h-14 object-cover rounded-lg bg-mist" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{item.name}</p>
                <p className="text-xs text-fog">${item.price} × {item.qty}</p>
              </div>
              <button onClick={() => removeFromCart(item.id)}
                className="text-fog hover:text-ink transition">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>

        {success && (
          <div className="px-6 py-5 border-t border-mist">
            <div className="w-full flex flex-col items-center justify-center gap-1 bg-green-600 text-white
              py-4 rounded-xl font-medium text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle size={15} /> Order placed successfully!
              </div>
              {orderTotal != null && (
                <span className="text-green-100 text-xs font-normal">
                  Total: ${Number(orderTotal).toFixed(2)}
                </span>
              )}
            </div>
          </div>
        )}

        {!success && cart.length > 0 && (
          <div className="px-6 py-5 border-t border-mist space-y-3">
            <div className="flex justify-between text-sm font-medium">
              <span>Total</span>
              <span>${total.toFixed(2)}</span>
            </div>

            <input
              type="text"
              placeholder="Shipping address"
              value={address}
              onChange={(e) => { setAddress(e.target.value); setError(null); }}
              className="w-full border border-mist rounded-xl px-3 py-2.5 text-sm
                focus:outline-none focus:border-ink placeholder:text-fog"
            />

            {error && (
              <div className="flex items-center gap-2 text-red-500 text-xs">
                <AlertCircle size={13} /> {error}
              </div>
            )}

            <button
              onClick={handleCheckout}
              disabled={loading}
              className="w-full bg-ink text-white py-3.5 rounded-xl font-medium text-sm
                hover:bg-accent transition disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? "Placing order…" : "Checkout"}
            </button>
          </div>
        )}
      </div>
    </>
  );
}
