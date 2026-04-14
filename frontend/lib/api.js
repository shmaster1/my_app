// Utility for connecting to your Python backend
// Set NEXT_PUBLIC_API_URL in your .env.local or Vercel environment variables

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function apiFetch(path, options = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("jwt_token") : null;
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });
  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("jwt_token");
      window.location.href = "/login";
    }
    throw new Error("Session expired. Please log in again.");
  }
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  // Products
  getProducts: async () => {
    const items = await apiFetch("/item/");
    return items.map((p) => ({
      id: p.id,
      name: p.item_name,
      price: p.price,
      stock: p.stock_available,
      image: p.image_url,
    }));
  },

  searchProducts: async (name) => {
    const items = await apiFetch(`/item/search?name=${name}`);
    return items.map((p) => ({
      id: p.id,
      name: p.item_name,
      price: p.price,
      stock: p.stock_available,
      image: p.image_url,
    }));
  },

  getProduct: async (id) => {
    const p = await apiFetch(`/item/${id}`);
    return {
      id: p.id,
      name: p.item_name,
      price: p.price,
      stock: p.stock_available,
      image: p.image_url,
    };
  },

  // Auth
  login: async (username, password) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  const res = await fetch(`${API_BASE}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const text = await res.text();
  console.log("login raw response:", text);
  const data = JSON.parse(text);
  console.log("login parsed data:", data);
  localStorage.setItem("jwt_token", data.jwt_token);
  return data;
},
  logout: () => {
    localStorage.removeItem("jwt_token");
  },

  // User
  register: (data) => apiFetch("/user/", {
    method: "POST",
    body: JSON.stringify({
      username: data.username,
      first_name: data.first_name,
      last_name: data.last_name,
      email: data.email,
      phone: data.phone,
      country: data.country,
      city: data.city,
      password: data.password,
    }),
  }),
  getUsers: () => apiFetch("/user/"),
  deleteUser: () => apiFetch("/user/", { method: "DELETE" }),
  checkUsername: (username) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("jwt_token") : null;
  return fetch(`${API_BASE}/user/check-username/${username}`, {
    method: "GET",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  }).then((res) => res.json());
},

  // Orders
  getOrders: (userId) => apiFetch(`/order/user_id/${userId}`),
  addItemToOrder: (itemId, quantity, shippingAddress) => apiFetch("/order/item", {
    method: "POST",
    body: JSON.stringify({ item_id: itemId, quantity, shipping_address: shippingAddress }),
  }),
  purchaseOrder: () => apiFetch("/order/purchase_order", { method: "POST" }),

  // Chat with RAG
  sendChat: (userId, userText) => apiFetch("/ragchat/", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, user_text: userText }),
  }),

  // Favorites
  getFavorites: (userId) => apiFetch(`/favorites/user_id/${userId}`),
  addFavorite: (userId, itemId) => apiFetch(`/favorites/user_id/${userId}?item_id=${itemId}`, { method: "POST" }),
  removeFavorite: (userId, itemId) => apiFetch(`/favorites/user_id/${userId}?item_id=${itemId}`, { method: "DELETE" }),
};

export function getUserIdFromToken() {
  const token = typeof window !== "undefined" ? localStorage.getItem("jwt_token") : null;
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.id ?? null;
  } catch {
    return null;
  }
}

export function getUsernameFromToken() {
  const token = typeof window !== "undefined" ? localStorage.getItem("jwt_token") : null;
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.subject ?? payload.sub ?? payload.username ?? null;
  } catch {
    return null;
  }
}