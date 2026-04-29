import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/router";
import Layout from "../components/Layout";
import ProductCard from "../components/ProductCard";
import { api, getUserIdFromToken } from "../lib/api";

export default function Dashboard() {
  const router = useRouter();
  const [products, setProducts] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState(new Set());
  const allProductsRef = useRef([]);

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (!token) { router.push("/login"); return; }
    api.getProducts().then((p) => {
      allProductsRef.current = p;
      setProducts(p);
    }).catch(() => {});

    const userId = getUserIdFromToken();
    if (userId) {
      api.getFavorites(userId).then((favs) => {
        setFavoriteIds(new Set(favs.map((f) => f.item_id ?? f.id)));
      }).catch(() => {});
    }
  }, []);

  const searchSeqRef = useRef(0);

  const handleSearch = useCallback(async (query) => {
    if (!query.trim()) {
      setProducts(allProductsRef.current);
      return;
    }
    const seq = ++searchSeqRef.current;
    try {
      const results = await api.searchProducts(query);
      if (seq === searchSeqRef.current) setProducts(results);
    } catch {
      if (seq === searchSeqRef.current) setProducts([]);
    }
  }, []);

  return (
    <Layout onSearch={handleSearch}>
      <div className="px-8 py-7">
        <h1 className="font-display text-4xl tracking-widest text-ink mb-6">DASHBOARD</h1>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} isFavorited={favoriteIds.has(product.id)} />
          ))}
        </div>
      </div>
    </Layout>
  );
}