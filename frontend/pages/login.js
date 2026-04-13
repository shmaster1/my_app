import { useState } from "react";
import { useRouter } from "next/router";
import { api } from "../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState("login");

  // Login state
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [loginError, setLoginError] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);

  // Register state
  const [registerForm, setRegisterForm] = useState({
    username: "", first_name: "", last_name: "",
    email: "", phone: "", country: "", city: "",
    password: "", confirm_password: "",
  });
  const [registerError, setRegisterError] = useState("");
  const [registerLoading, setRegisterLoading] = useState(false);

  // ── Login ──────────────────────────────────────────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError("");
    setLoginLoading(true);
    try {
      await api.login(loginForm.username, loginForm.password);
      router.push("/");
    } catch {
      setLoginError("Invalid username or password.");
    } finally {
      setLoginLoading(false);
    }
  };

  // ── Register ───────────────────────────────────────────────────────────
  const handleRegister = async (e) => {
    e.preventDefault();
    setRegisterError("");

    // All fields required
    const fields = Object.values(registerForm);
    if (fields.some((f) => !f)) {
      setRegisterError("All fields marked with * are mandatory.");
      return;
    }

    // Password match
    if (registerForm.password !== registerForm.confirm_password) {
      setRegisterError("Passwords do not match.");
      return;
    }

    setRegisterLoading(true);
    try {
      // 1. Check username availability
      const { is_taken } = await api.checkUsername(registerForm.username);
      if (is_taken) {
        setRegisterError("Username taken, please try again ❌");
        setRegisterLoading(false);
        return;
      }

      // 2. Register
      const user = await api.register({
        username: registerForm.username,
        first_name: registerForm.first_name,
        last_name: registerForm.last_name,
        email: registerForm.email,
        phone: registerForm.phone,
        country: registerForm.country,
        city: registerForm.city,
        password: registerForm.password,
      });

      if (!user?.id) {
        setRegisterError("Registration failed: user ID missing from backend.");
        setRegisterLoading(false);
        return;
      }

      // 3. Auto-login after registration
      await api.login(registerForm.username, registerForm.password);
      router.push("/");
    } catch (err) {
      setRegisterError(err.message || "Connection error.");
    } finally {
      setRegisterLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-ash flex items-center justify-center px-4">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 bg-ink rounded-xl flex items-center justify-center mb-3">
            <span className="text-white font-display text-3xl leading-none">S</span>
          </div>
          <h1 className="font-display text-4xl tracking-widest text-ink">shlomi-store</h1>
        </div>

        <div className="bg-white rounded-2xl border border-mist p-8 shadow-sm">

          {/* Mode toggle */}
          <div className="flex rounded-xl bg-ash p-1 mb-7">
            <button
              onClick={() => { setMode("login"); setLoginError(""); }}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all
                ${mode === "login" ? "bg-white shadow-sm text-ink" : "text-fog hover:text-ink"}`}
            >
              Log In
            </button>
            <button
              onClick={() => { setMode("register"); setRegisterError(""); }}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all
                ${mode === "register" ? "bg-white shadow-sm text-ink" : "text-fog hover:text-ink"}`}
            >
              Sign Up
            </button>
          </div>

          {/* ── LOGIN FORM ── */}
          {mode === "login" && (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="text-xs text-fog font-medium uppercase tracking-wide">Username *</label>
                <input
                  type="text"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                  className="mt-1 w-full px-4 py-3 bg-ash rounded-xl text-sm text-ink
                    focus:outline-none focus:ring-2 focus:ring-ink/10 transition"
                  placeholder="your username"
                  required
                />
              </div>
              <div>
                <label className="text-xs text-fog font-medium uppercase tracking-wide">Password *</label>
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  className="mt-1 w-full px-4 py-3 bg-ash rounded-xl text-sm text-ink
                    focus:outline-none focus:ring-2 focus:ring-ink/10 transition"
                  placeholder="••••••••"
                  required
                />
              </div>

              {loginError && (
                <p className="text-red-500 text-xs">{loginError}</p>
              )}

              <button
                type="submit"
                disabled={loginLoading}
                className="w-full bg-ink text-white py-3.5 rounded-xl font-medium text-sm
                  hover:bg-accent transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loginLoading ? "Logging in…" : "Log In"}
              </button>
            </form>
          )}

          {/* ── REGISTER FORM ── */}
          {mode === "register" && (
            <form onSubmit={handleRegister} className="space-y-4">
              {[
                { key: "username",    label: "Username",         type: "text" },
                { key: "first_name",  label: "First Name",       type: "text" },
                { key: "last_name",   label: "Last Name",        type: "text" },
                { key: "email",       label: "Email",            type: "email" },
                { key: "phone",       label: "Phone",            type: "tel" },
                { key: "country",     label: "Country",          type: "text" },
                { key: "city",        label: "City",             type: "text" },
                { key: "password",         label: "Password",         type: "password" },
                { key: "confirm_password", label: "Confirm Password", type: "password" },
              ].map(({ key, label, type }) => (
                <div key={key}>
                  <label className="text-xs text-fog font-medium uppercase tracking-wide">{label} *</label>
                  <input
                    type={type}
                    value={registerForm[key]}
                    onChange={(e) => setRegisterForm({ ...registerForm, [key]: e.target.value })}
                    className="mt-1 w-full px-4 py-3 bg-ash rounded-xl text-sm text-ink
                      focus:outline-none focus:ring-2 focus:ring-ink/10 transition"
                    placeholder={label.toLowerCase()}
                    required
                  />
                </div>
              ))}

              {registerError && (
                <p className="text-red-500 text-xs">{registerError}</p>
              )}

              <button
                type="submit"
                disabled={registerLoading}
                className="w-full bg-ink text-white py-3.5 rounded-xl font-medium text-sm
                  hover:bg-accent transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {registerLoading ? "Registering…" : "Register"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}