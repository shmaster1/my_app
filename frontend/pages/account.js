import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { User, Trash2 } from "lucide-react";
import Layout from "../components/Layout";
import { api, getUserIdFromToken } from "../lib/api";

export default function Account() {
  const router = useRouter();
  const [confirm, setConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (!token) { router.push("/login"); return; }
    if (!getUserIdFromToken()) { router.push("/login"); }
  }, []);

  const handleDelete = async () => {
    setDeleting(true);
    setError("");
    try {
      await api.deleteUser();
      api.logout();
      router.push("/login");
    } catch {
      setError("Failed to delete account. Please try again.");
      setDeleting(false);
    }
  };

  return (
    <Layout>
      <div className="px-4 md:px-8 py-5 md:py-7 max-w-lg">
        <h1 className="font-display text-3xl md:text-4xl tracking-widest text-ink mb-8">ACCOUNT</h1>

        {/* Danger Zone */}
        <div className="rounded-2xl border border-red-200 overflow-hidden">
          <div className="bg-red-50 px-5 py-3 text-[11px] font-semibold uppercase tracking-wider text-red-400">
            Danger Zone
          </div>
          <div className="px-5 py-5 flex items-start justify-between gap-6">
            <div>
              <p className="text-sm font-semibold text-ink">Delete Account</p>
              <p className="text-xs text-fog mt-1">
                Permanently remove your account and all associated data. This action cannot be undone.
              </p>
              {error && <p className="text-xs text-red-500 mt-2">{error}</p>}
            </div>

            {!confirm ? (
              <button
                onClick={() => setConfirm(true)}
                className="shrink-0 flex items-center gap-2 px-4 py-2 rounded-xl border border-red-300
                  text-red-500 text-sm font-medium hover:bg-red-50 transition"
              >
                <Trash2 size={14} />
                Delete
              </button>
            ) : (
              <div className="shrink-0 flex flex-col items-end gap-2">
                <p className="text-xs text-fog text-right">Are you sure?</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setConfirm(false)}
                    disabled={deleting}
                    className="px-3 py-1.5 rounded-lg border border-mist text-sm text-fog hover:bg-ash transition"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={deleting}
                    className="px-3 py-1.5 rounded-lg bg-red-500 text-white text-sm font-medium
                      hover:bg-red-600 transition disabled:opacity-60"
                  >
                    {deleting ? "Deleting…" : "Confirm"}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
