import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { Package } from "lucide-react";
import Layout from "../components/Layout";
import { api, getUserIdFromToken } from "../lib/api";

const STATUS_STYLES = {
  TEMP:   "bg-amber-100 text-amber-700",
  CLOSED: "bg-green-100 text-green-700",
};

export default function Orders() {
  const router = useRouter();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (!token) { router.push("/login"); return; }
    const userId = getUserIdFromToken();
    if (!userId) { router.push("/login"); return; }

    api.getOrders(userId)
      .then((orders) => {
        // Flatten each order's items into individual rows
        const flat = orders.flatMap((order) =>
          (order.items ?? []).map((item) => ({
            item_name: item.item_name,
            price: Number(item.price),
            quantity: item.quantity,
            date: order.order_date,
            total: Number(item.price) * item.quantity,
            status: order.status,
          }))
        );
        setRows(flat);
      })
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <div className="px-4 md:px-8 py-5 md:py-7">
        <h1 className="font-display text-3xl md:text-4xl tracking-widest text-ink mb-6">ORDERS</h1>

        {loading && <p className="text-fog text-sm">Loading...</p>}

        {!loading && rows.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 text-fog">
            <Package size={40} strokeWidth={1.2} className="mb-4" />
            <p className="text-sm">No orders yet. Add items to your cart and checkout.</p>
          </div>
        )}

        {!loading && rows.length > 0 && (
          <>
            {/* Mobile card layout */}
            <div className="md:hidden space-y-3">
              {rows.map((row, idx) => (
                <div key={idx} className="bg-white border border-mist rounded-2xl px-4 py-4 space-y-2">
                  <div className="flex justify-between items-start gap-2">
                    <span className="font-semibold text-ink text-sm leading-tight">{row.item_name}</span>
                    <span className={`shrink-0 inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold
                      ${STATUS_STYLES[row.status] ?? "bg-mist text-fog"}`}>
                      {row.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 text-xs gap-y-1">
                    <span className="text-fog">Price</span>
                    <span className="text-fog">Qty</span>
                    <span className="text-fog">Total</span>
                    <span className="text-ink">${row.price.toFixed(2)}</span>
                    <span className="text-ink">{row.quantity}</span>
                    <span className="font-bold text-ink">${row.total.toFixed(2)}</span>
                  </div>
                  <p className="text-xs text-fog">
                    {new Date(row.date).toLocaleDateString("en-US", {
                      year: "numeric", month: "short", day: "numeric",
                    })}
                  </p>
                </div>
              ))}
              <div className="bg-ash border border-mist rounded-2xl px-4 py-3 flex justify-between items-center">
                <span className="text-xs font-semibold uppercase tracking-wider text-ink">Grand Total</span>
                <span className="font-bold text-ink">
                  ${rows.reduce((sum, row) => sum + row.total, 0).toFixed(2)}
                </span>
              </div>
            </div>

            {/* Desktop table layout */}
            <div className="hidden md:block rounded-2xl border border-mist overflow-hidden">
              {/* Header */}
              <div className="grid grid-cols-[2fr_100px_80px_140px_100px_100px] bg-ash
                px-5 py-3 text-[11px] font-semibold uppercase tracking-wider text-fog">
                <span>Item</span>
                <span>Price</span>
                <span>Qty</span>
                <span>Date</span>
                <span>Total</span>
                <span>Status</span>
              </div>

              {/* Rows */}
              {rows.map((row, idx) => (
                <div
                  key={idx}
                  className="grid grid-cols-[2fr_100px_80px_140px_100px_100px] items-center
                    px-5 py-4 border-t border-mist hover:bg-ash/40 transition text-sm"
                >
                  <span className="font-medium text-ink truncate pr-4">{row.item_name}</span>
                  <span className="text-fog">${row.price.toFixed(2)}</span>
                  <span className="text-ink">{row.quantity}</span>
                  <span className="text-fog">
                    {new Date(row.date).toLocaleDateString("en-US", {
                      year: "numeric", month: "short", day: "numeric",
                    })}
                  </span>
                  <span className="font-semibold text-ink">${row.total.toFixed(2)}</span>
                  <span>
                    <span className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold
                      ${STATUS_STYLES[row.status] ?? "bg-mist text-fog"}`}>
                      {row.status}
                    </span>
                  </span>
                </div>
              ))}

              {/* Grand Total */}
              <div className="grid grid-cols-[2fr_100px_80px_140px_100px_100px] items-center
                px-5 py-4 border-t-2 border-ink/20 bg-ash text-sm">
                <span className="font-semibold text-ink uppercase tracking-wider text-[11px]">Grand Total</span>
                <span />
                <span />
                <span />
                <span className="font-bold text-ink text-base">
                  ${rows.reduce((sum, row) => sum + row.total, 0).toFixed(2)}
                </span>
                <span />
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
