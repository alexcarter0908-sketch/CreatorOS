"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
  CreditCard,
  Coins,
  History,
  Loader2,
  ArrowUpRight,
  ArrowDownRight,
  Gift,
  RefreshCw,
  ShoppingCart,
} from "lucide-react";

import MainLayout from "@/components/layout/MainLayout";
import BrandWatermark from "@/components/common/BrandWatermark";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api/client";
import "@/styles/console-theme.css";

interface CreditPack {
  id: string;
  credits: number;
  price_usd: number;
}

interface Balance {
  credit_balance: number;
  free_quota_used_today: number;
}

interface Transaction {
  id: string;
  type: string;
  amount: number;
  balance_after: number;
  description: string | null;
  created_at: string;
}

function TransactionIcon({ type }: { type: string }) {
  if (type === "purchase") return <ArrowUpRight className="h-4 w-4 text-emerald-500" />;
  if (type === "consumption") return <ArrowDownRight className="h-4 w-4 text-destructive" />;
  if (type === "refund") return <RefreshCw className="h-4 w-4 text-blue-500" />;
  if (type === "bonus") return <Gift className="h-4 w-4 text-purple-500" />;
  return <Coins className="h-4 w-4 text-muted-foreground" />;
}

export default function BillingPage() {
  const [balance, setBalance] = useState<Balance | null>(null);
  const [packs, setPacks] = useState<CreditPack[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [checkoutLoadingId, setCheckoutLoadingId] = useState<string | null>(null);

  async function loadAll() {
    setIsLoading(true);
    try {
      const [balanceRes, packsRes, historyRes] = await Promise.all([
        apiClient.get<Balance>("/api/v1/billing/balance"),
        apiClient.get<CreditPack[]>("/api/v1/billing/packs"),
        apiClient.get<{ transactions: Transaction[] }>("/api/v1/billing/history"),
      ]);
      setBalance(balanceRes.data);
      setPacks(packsRes.data);
      setTransactions(historyRes.data.transactions);
    } catch {
      toast.error("Failed to load billing information.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleBuy(packId: string) {
    setCheckoutLoadingId(packId);
    try {
      const { data } = await apiClient.post<{ transaction_id: string; checkout_url: string | null }>(
        "/api/v1/billing/checkout",
        { pack_id: packId }
      );
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        toast.error("Checkout link not found. Please try again.");
      }
    } catch {
      toast.error("Failed to start checkout.");
    } finally {
      setCheckoutLoadingId(null);
    }
  }

  return (
    <MainLayout>
      <div className="console-theme relative isolate -m-8 min-h-[calc(100%+4rem)] overflow-hidden p-8">
        <BrandWatermark />
        <div className="relative z-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Billing</h1>
        <p className="mt-2 text-muted-foreground">Manage your credits and purchase history here.</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center rounded-2xl border border-border bg-card p-16">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <div className="space-y-8">
          {/* Balance card */}
          <div className="flex flex-col gap-6 rounded-2xl border border-border bg-card p-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
                <Coins className="h-7 w-7 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Current balance</p>
                <p className="text-3xl font-bold text-foreground">
                  {balance?.credit_balance ?? 0} <span className="text-base font-medium text-muted-foreground">credits</span>
                </p>
              </div>
            </div>
            <div className="rounded-xl border border-border bg-muted px-4 py-3 text-sm text-muted-foreground">
              Free quota used today: <span className="font-semibold text-foreground">{balance?.free_quota_used_today ?? 0}</span>
            </div>
          </div>

          {/* Credit packs */}
          <div>
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-foreground">
              <ShoppingCart className="h-5 w-5" />
              Credit Packs
            </h2>

            {packs.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-border bg-card p-10 text-center text-sm text-muted-foreground">
                No credit packs available right now.
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {packs.map((pack) => (
                  <div
                    key={pack.id}
                    className="flex flex-col justify-between rounded-2xl border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
                  >
                    <div>
                      <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10">
                        <CreditCard className="h-5 w-5 text-primary" />
                      </div>
                      <p className="text-2xl font-bold text-foreground">{pack.credits.toLocaleString()}</p>
                      <p className="text-sm text-muted-foreground">credits</p>
                    </div>

                    <div className="mt-6 flex items-center justify-between">
                      <span className="text-xl font-semibold text-foreground">${pack.price_usd.toFixed(2)}</span>
                      <Button
                        onClick={() => handleBuy(pack.id)}
                        disabled={checkoutLoadingId === pack.id}
                        size="sm"
                      >
                        {checkoutLoadingId === pack.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          "Buy"
                        )}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Transaction history */}
          <div>
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-foreground">
              <History className="h-5 w-5" />
              Transaction History
            </h2>

            {transactions.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-border bg-card p-10 text-center text-sm text-muted-foreground">
                No transactions yet.
              </div>
            ) : (
              <div className="overflow-hidden rounded-2xl border border-border bg-card">
                <div className="divide-y divide-border">
                  {transactions.map((txn) => (
                    <div key={txn.id} className="flex items-center justify-between gap-4 px-5 py-3.5">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-muted">
                          <TransactionIcon type={txn.type} />
                        </div>
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-foreground capitalize">{txn.type}</p>
                          <p className="truncate text-xs text-muted-foreground">
                            {txn.description || "-"}
                          </p>
                        </div>
                      </div>
                      <div className="shrink-0 text-right">
                        <p className={`text-sm font-semibold ${txn.amount >= 0 ? "text-emerald-500" : "text-destructive"}`}>
                          {txn.amount >= 0 ? "+" : ""}
                          {txn.amount}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(txn.created_at).toLocaleDateString([], { day: "2-digit", month: "short" })}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
        </div>
      </div>
    </MainLayout>
  );
}

