"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "../store/auth.store";

export default function RegisterForm() {
  const router = useRouter();

  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    try {
      await register({
        full_name: fullName,
        email,
        password,
      });

      alert("Registration successful.");

      router.push("/login");
    } catch {
      alert("Registration failed.");
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-md space-y-4 rounded-lg border p-6"
    >
      <h1 className="text-3xl font-bold">
        Create Account
      </h1>

      <input
        className="w-full rounded border p-3"
        placeholder="Full Name"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
      />

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
        {isLoading ? "Creating..." : "Register"}
      </button>
    </form>
  );
}