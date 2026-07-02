"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "../store/auth.store";

export default function LoginForm() {
  const router = useRouter();

  const login = useAuthStore((state) => state.login);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const isLoading = useAuthStore(
    (state) => state.isLoading
  );

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    try {
      await login({
        email,
        password,
      });

      router.push("/command-center");
    } catch {
      alert("Invalid email or password.");
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-md space-y-4 rounded-lg border p-6"
    >
      <h1 className="text-3xl font-bold">
        CreatorOS Login
      </h1>

      <input
        className="w-full rounded border p-3"
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        className="w-full rounded border p-3"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded bg-black p-3 text-white"
      >
        {isLoading ? "Signing in..." : "Login"}
      </button>
    </form>
  );
}