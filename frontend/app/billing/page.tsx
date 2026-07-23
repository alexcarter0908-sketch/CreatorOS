"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
  AlertTriangle,
  Sparkles,
} from "lucide-react";

import MainLayout from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api/client";

interface CreditPack {
  id: string;
  credits: number;
  price_usd: number;
  popular: boolean;
}

interface Balance {
  credit_balance: number;
  free_quota_used_today: number;
  low_balance: boolean;
}

interface Transaction {
  id: string;
  type: string;
  amount: number;
  balance_after: number;
  description: string | null;
  created_at: string;
}

const HISTORY_PAGE_SIZE = 20;
// Payment providers process webhooks async, so the balance doesn't
// update the instant the user is redirected back - poll briefly
// instead of just showing a stale number.
const PAYMENT_POLL_ATTEMPTS = 8;
const PAYMENT_POLL_INTERVAL_MS = 2500;

function TransactionIcon({ type }: { type: string }) {
  if (type === "purchase") return <ArrowUpRight className="h-4 w-4 text-emerald-500" />;
  if (type === "consumption") return <ArrowDownRight className="h-4 w-4 text-destructive" />;
  if (type === "refund") return <RefreshCw className="h-4 w-4 text-blue-500" />;
  if (type === "bonus") return <Gift className="h-4 w-4 text-purple-500" />;
  return <Coins className="h-4 w-4 text-muted-foreground" />;
}

function BillingPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [balance, setBalance] = useState<Balance | null>(null);
  const [packs, setPacks] = useState<CreditPack[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [checkoutLoadingId, setCheckoutLoadingId] = useState<string | null>(null);
  const [isAwaitingPayment, setIsAwaitingPayment] = useState(false);
  const [historyOffset, setHistoryOffset] = useState(0);
  const [hasMoreHistory, setHasMoreHistory] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  const balanceRef = useRef<number | null>(null);

  async function fetchBalance(): Promise<Balance> {
    const { data } = await apiClient.get<Balance>("/api/v1/billing/balance");
    return data;
  }

  async function fetchHistory(offset: number): Promise<Transaction[]> {
    const { data } = await apiClient.get<{ transactions: Transaction[] }>(
      "/api/v1/billing/history",
      { params: { limit: HISTORY_PAGE_SIZE, offset } }
    );
    return data.transactions;
  }

  async function loadAll() {
    setIsLoading(true);
    try {
      const [balanceData, packsRes, historyData] = await Promise.all([
        fetchBalance(),
        apiClient.get<CreditPack[]>("/api/v1/billing/packs"),
        fetchHistory(0),
      ]);
      setBalance(balanceData);
      balanceRef.current = balanceData.credit_balance;
      setPacks(packsRes.data);
      setTransactions(historyData);
      setHistoryOffset(historyData.length);
      setHasMoreHistory(historyData.length === HISTORY_PAGE_SIZE);
    } catch {
      toast.error("Failed to load billing information.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadMoreHistory() {
    setIsLoadingMore(true);
    try {
      const more = await fetchHistory(historyOffset);
      setTransactions((prev) => [...prev, ...more]);
      setHistoryOffset((prev) => prev + more.length);
      setHasMoreHistory(more.length === HISTORY_PAGE_SIZE);
    } catch {
      toast.error("Failed to load more transactions.");
    } finally {
      setIsLoadingMore(false);
    }
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handle returning from Paddle's hosted checkout. Paddle's webhook
  // (which actually credits the account) arrives asynchronously, so
  // instead of trusting the redirect alone, poll briefly for the
  // balance to actually change before declaring success.
  useEffect(() => {
    const checkoutStatus = searchParams.get("checkout");
    if (!checkoutStatus) return;

    if (checkoutStatus === "cancelled") {
      toast.info("Checkout cancelled - no charge was made.");
      router.replace("/billing");
      return;
    }

    if (checkoutStatus === "success") {
      setIsAwaitingPayment(true);
      const startingBalance = balanceRef.current ?? 0;
      let attempts = 0;

      const poll = setInterval(async () => {
        attempts += 1;
        try {
          const fresh = await fetchBalance();
          if (fresh.credit_balance !== startingBalance) {
            setBalance(fresh);
            balanceRef.current = fresh.credit_balance;
            const historyData = await fetchHistory(0);
            setTransactions(historyData);
            setHistoryOffset(historyData.length);
            setHasMoreHistory(historyData.length === HISTORY_PAGE_SIZE);
            setIsAwaitingPayment(false);
            toast.success("Payment received - credits added!");
            clearInterval(poll);
            router.replace("/billing");
            return;
          }
        } catch {
          // keep trying silently - a single failed poll isn't fatal
        }

        if (attempts >= PAYMENT_POLL_ATTEMPTS) {
          setIsAwaitingPayment(false);
          toast.message("Payment is still processing - refresh in a moment if your balance hasn't updated.");
          clearInterval(poll);
          router.replace("/billing");
        }
      }, PAYMENT_POLL_INTERVAL_MS);

      return () => clearInterval(poll);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

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
          {isAwaitingPayment && (
            <div className="flex items-center gap-3 rounded-2xl border border-primary/30 bg-primary/5 px-5 py-3.5 text-sm text-foreground">
              <Loader2 className="h-4 w-4 shrink-0 animate-spin text-primary" />
              Payment received - waiting for your credits to be added. This usually takes a few seconds.
            </div>
          )}

          {!isAwaitingPayment && balance?.low_balance && (
            <div className="flex items-center gap-3 rounded-2xl border border-amber-500/30 bg-amber-500/10 px-5 py-3.5 text-sm text-foreground">
              <AlertTriangle className="h-4 w-4 shrink-0 text-amber-500" />
              You&apos;re running low on credits. Top up below to keep generating without interruption.
            </div>
          )}

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
                {packs.map((pack) => {
                  const perCredit = pack.price_usd / pack.credits;
                  return (
                    <div
                      key={pack.id}
                      className={`relative flex flex-col justify-between rounded-2xl border bg-card p-6 shadow-sm transition-shadow hover:shadow-md ${
                        pack.popular ? "border-primary/50 ring-1 ring-primary/20" : "border-border"
                      }`}
                    >
                      {pack.popular && (
                        <span className="absolute -top-3 left-6 flex items-center gap-1 rounded-full bg-primary px-3 py-1 text-[11px] font-semibold text-primary-foreground">
                          <Sparkles className="h-3 w-3" />
                          Most popular
                        </span>
                      )}

                      <div>
                        <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10">
                          <CreditCard className="h-5 w-5 text-primary" />
                        </div>
                        <p className="text-2xl font-bold text-foreground">{pack.credits.toLocaleString()}</p>
                        <p className="text-sm text-muted-foreground">credits</p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          ${perCredit.toFixed(4)} / credit
                        </p>
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
                  );
                })}
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

                {hasMoreHistory && (
                  <div className="flex justify-center border-t border-border p-3">
                    <Button variant="ghost" size="sm" onClick={loadMoreHistory} disabled={isLoadingMore}>
                      {isLoadingMore ? <Loader2 className="h-4 w-4 animate-spin" /> : "Load more"}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </MainLayout>
  );
}

export default function BillingPage() {
  return (
    <Suspense fallback={null}>
      <BillingPageContent />
    </Suspense>
  );
}