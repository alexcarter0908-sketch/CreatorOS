"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { toast } from "sonner";
import {
  User,
  ShieldCheck,
  Palette,
  Youtube,
  Coins,
  Bell,
  AlertTriangle,
  Eye,
  EyeOff,
  Loader2,
  BadgeCheck,
  LogOut,
  ExternalLink,
  Sun,
  Moon,
  Monitor,
  CheckCheck,
  Sparkles,
} from "lucide-react";

import MainLayout from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { apiClient } from "@/lib/api/client";
import { useAuthStore } from "@/features/auth/store/auth.store";
import { updateProfile, changePassword, deleteAccount } from "@/features/auth/services/auth.service";
import {
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from "@/features/notifications/services/notifications.service";
import type { AppNotification } from "@/features/notifications/types/notification.types";

/* ---------- shared bits ---------- */

const LOW_CREDIT_THRESHOLD = 10;

type TabId = "profile" | "security" | "appearance" | "connections" | "credits" | "notifications" | "danger";

const TABS: { id: TabId; label: string; icon: typeof User }[] = [
  { id: "profile", label: "Profile", icon: User },
  { id: "security", label: "Security", icon: ShieldCheck },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "connections", label: "Connected Accounts", icon: Youtube },
  { id: "credits", label: "Credits & Usage", icon: Coins },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "danger", label: "Danger Zone", icon: AlertTriangle },
];

function SectionCard({
  icon: Icon,
  title,
  description,
  children,
  tone = "default",
  headerAction,
}: {
  icon: typeof User;
  title: string;
  description?: string;
  children: React.ReactNode;
  tone?: "default" | "danger";
  headerAction?: React.ReactNode;
}) {
  return (
    <div
      className={`rounded-2xl border p-6 ${
        tone === "danger" ? "border-destructive/30 bg-card" : "border-border bg-card"
      }`}
    >
      <div className="mb-5 flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
              tone === "danger" ? "bg-destructive/10" : "bg-primary/10"
            }`}
          >
            <Icon className={`h-5 w-5 ${tone === "danger" ? "text-destructive" : "text-primary"}`} />
          </div>
          <div>
            <h2 className={`text-lg font-semibold ${tone === "danger" ? "text-destructive" : "text-foreground"}`}>
              {title}
            </h2>
            {description && <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>}
          </div>
        </div>
        {headerAction}
      </div>
      {children}
    </div>
  );
}

function LiveBadge() {
  return (
    <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Live
    </span>
  );
}

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  const [saving, setSaving] = useState(false);

  async function handleClick() {
    setSaving(true);
    try {
      await onChange(!checked);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex items-center justify-between rounded-xl border border-border px-4 py-3">
      <div className="pr-4">
        <p className="text-sm font-medium text-foreground">{label}</p>
        {description && <p className="text-xs text-muted-foreground">{description}</p>}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={saving}
        onClick={handleClick}
        className={`relative h-5 w-9 shrink-0 rounded-full transition-colors disabled:opacity-60 ${
          checked ? "bg-primary" : "bg-muted"
        }`}
      >
        <span
          className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${
            checked ? "translate-x-4" : "translate-x-0.5"
          }`}
        />
      </button>
    </div>
  );
}

function PasswordInput({
  id,
  value,
  onChange,
  autoComplete,
}: {
  id: string;
  value: string;
  onChange: (v: string) => void;
  autoComplete: string;
}) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="relative">
      <Input
        id={id}
        type={visible ? "text" : "password"}
        minLength={8}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete={autoComplete}
        required
        className="pr-10"
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
        tabIndex={-1}
        aria-label={visible ? "Hide password" : "Show password"}
      >
        {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
      </button>
    </div>
  );
}

function passwordStrength(pw: string) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return Math.min(score, 4);
}

const STRENGTH_LABEL = ["Very weak", "Weak", "Fair", "Good", "Strong"];
const STRENGTH_COLOR = ["bg-red-500", "bg-orange-500", "bg-yellow-500", "bg-lime-500", "bg-green-500"];

function timeAgo(iso: string) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

/* ---------- types for data fetched on this page ---------- */

interface ConnectedAccount {
  id: string;
  platform: string;
  account_label: string | null;
  external_account_id: string | null;
}

interface Balance {
  credit_balance: number;
  free_quota_used_today: number;
}

/* ---------- page ---------- */

export default function SettingsPage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const logout = useAuthStore((s) => s.logout);
  const { theme, setTheme } = useTheme();
  const [mountedTheme, setMountedTheme] = useState(false);

  const [activeTab, setActiveTab] = useState<TabId>("profile");

  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url ?? "");
  const [savingProfile, setSavingProfile] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);

  const [balance, setBalance] = useState<Balance | null>(null);
  const [youtubeAccounts, setYoutubeAccounts] = useState<ConnectedAccount[]>([]);
  const [loadingExtras, setLoadingExtras] = useState(true);

  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loadingNotifications, setLoadingNotifications] = useState(true);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    setMountedTheme(true);
  }, []);

  useEffect(() => {
    if (user?.full_name) setFullName(user.full_name);
    if (user?.avatar_url) setAvatarUrl(user.avatar_url);
  }, [user?.full_name, user?.avatar_url]);

  useEffect(() => {
    Promise.all([
      apiClient.get<Balance>("/api/v1/billing/balance").catch(() => null),
      apiClient
        .get<{ accounts: ConnectedAccount[] }>("/api/v1/publish/accounts")
        .catch(() => null),
    ]).then(([balanceRes, accountsRes]) => {
      if (balanceRes) setBalance(balanceRes.data);
      if (accountsRes) {
        setYoutubeAccounts((accountsRes.data.accounts || []).filter((a) => a.platform === "youtube"));
      }
      setLoadingExtras(false);
    });
  }, []);

  async function refreshNotifications() {
    try {
      const data = await listNotifications();
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch {
      // non-critical
    } finally {
      setLoadingNotifications(false);
    }
  }

  useEffect(() => {
    refreshNotifications();
  }, []);

  async function handleOpenNotification(n: AppNotification) {
    if (n.is_read) return;
    setNotifications((prev) => prev.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)));
    setUnreadCount((c) => Math.max(0, c - 1));
    try {
      await markNotificationRead(n.id);
    } catch {
      // ignore
    }
  }

  async function handleMarkAllRead() {
    setNotifications((prev) => prev.map((x) => ({ ...x, is_read: true })));
    setUnreadCount(0);
    try {
      await markAllNotificationsRead();
    } catch {
      // ignore
    }
  }

  async function handleToggleDigest(value: boolean) {
    try {
      const updated = await updateProfile({ notify_email_digest: value });
      setUser(updated);
      toast.success(value ? "Daily digest enabled." : "Daily digest disabled.");
    } catch {
      toast.error("Could not update preference.");
    }
  }

  async function handleToggleLowCredit(value: boolean) {
    try {
      const updated = await updateProfile({ notify_low_credit_email: value });
      setUser(updated);
      toast.success(value ? "Low credit alerts enabled." : "Low credit alerts disabled.");
    } catch {
      toast.error("Could not update preference.");
    }
  }

  async function handleDeleteAccount() {
    setDeleting(true);
    try {
      await deleteAccount({ password: deletePassword || undefined });
      logout();
      router.push("/login");
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Could not delete account.");
    } finally {
      setDeleting(false);
    }
  }

  if (!user) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="h-24 animate-pulse rounded-2xl bg-muted" />
          <div className="h-64 animate-pulse rounded-2xl bg-muted" />
        </div>
      </MainLayout>
    );
  }

  const profileDirty =
    fullName.trim() !== (user.full_name ?? "").trim() || avatarUrl.trim() !== (user.avatar_url ?? "").trim();
  const strength = passwordStrength(newPassword);
  const passwordsMismatch = confirmPassword.length > 0 && newPassword !== confirmPassword;
  const initial = (user.full_name || user.email || "?").charAt(0).toUpperCase();

  async function handleProfileSave(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!profileDirty) return;
    setSavingProfile(true);
    try {
      const updated = await updateProfile({
        full_name: fullName.trim(),
        avatar_url: avatarUrl.trim() || undefined,
      });
      setUser(updated);
      toast.success("Profile updated.");
    } catch {
      toast.error("Could not update profile.");
    } finally {
      setSavingProfile(false);
    }
  }

  async function handlePasswordSave(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error("New passwords don't match.");
      return;
    }
    if (strength < 2) {
      toast.error("Choose a stronger password.");
      return;
    }
    setSavingPassword(true);
    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      toast.success("Password changed.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Could not change password.");
    } finally {
      setSavingPassword(false);
    }
  }

  return (
    <MainLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Manage your CreatorOS account, security, and workspace preferences.
        </p>
      </div>

      {/* Overview hero */}
      <div className="mb-8 flex flex-col gap-6 rounded-2xl border border-border bg-card p-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={user.full_name}
              className="h-16 w-16 rounded-2xl object-cover"
            />
          ) : (
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-xl font-semibold text-primary">
              {initial}
            </div>
          )}
          <div>
            <div className="flex items-center gap-2">
              <p className="text-lg font-semibold text-foreground">{user.full_name || "Unnamed"}</p>
              {user.is_email_verified && (
                <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                  <BadgeCheck className="h-3.5 w-3.5" /> Verified
                </span>
              )}
            </div>
            <p className="text-sm text-muted-foreground">{user.email}</p>
            {user.created_at && (
              <p className="mt-1 text-xs text-muted-foreground">
                Member since {new Date(user.created_at).toLocaleDateString(undefined, { month: "long", year: "numeric" })}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 rounded-xl border border-border bg-muted px-4 py-3">
          <Coins className="h-5 w-5 text-primary" />
          <div>
            <p className="text-xs text-muted-foreground">Credit balance</p>
            <p className="text-lg font-bold text-foreground">
              {loadingExtras ? "..." : balance?.credit_balance ?? 0}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs + content */}
      <div className="flex flex-col gap-6 lg:flex-row">
        <nav className="flex shrink-0 gap-1 overflow-x-auto lg:sticky lg:top-6 lg:h-fit lg:w-56 lg:flex-col lg:overflow-visible">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex shrink-0 items-center gap-2.5 whitespace-nowrap rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  active
                    ? "bg-primary/10 text-primary"
                    : tab.id === "danger"
                    ? "text-destructive/80 hover:bg-destructive/10 hover:text-destructive"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {tab.label}
                {tab.id === "notifications" && unreadCount > 0 && (
                  <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-semibold text-primary-foreground">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="min-w-0 flex-1 space-y-6">
          {activeTab === "profile" && (
            <form onSubmit={handleProfileSave}>
              <SectionCard icon={User} title="Profile" description="This is how you appear across CreatorOS.">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      autoComplete="name"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="avatarUrl">Avatar URL</Label>
                    <Input
                      id="avatarUrl"
                      placeholder="https://..."
                      value={avatarUrl}
                      onChange={(e) => setAvatarUrl(e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground">Paste a link to an image to use as your avatar.</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" value={user.email ?? ""} disabled />
                    <p className="text-xs text-muted-foreground">Email can&apos;t be changed here.</p>
                  </div>

                  <Button type="submit" disabled={savingProfile || !profileDirty}>
                    {savingProfile ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    {savingProfile ? "Saving..." : "Save Profile"}
                  </Button>
                </div>
              </SectionCard>
            </form>
          )}

          {activeTab === "security" && (
            <div className="space-y-6">
              <form onSubmit={handlePasswordSave}>
                <SectionCard icon={ShieldCheck} title="Change Password" description="Use a strong, unique password.">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="currentPassword">Current Password</Label>
                      <PasswordInput
                        id="currentPassword"
                        value={currentPassword}
                        onChange={setCurrentPassword}
                        autoComplete="current-password"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="newPassword">New Password</Label>
                      <PasswordInput
                        id="newPassword"
                        value={newPassword}
                        onChange={setNewPassword}
                        autoComplete="new-password"
                      />
                      {newPassword.length > 0 && (
                        <div className="space-y-1">
                          <div className="flex h-1.5 gap-1">
                            {[0, 1, 2, 3].map((i) => (
                              <div
                                key={i}
                                className={`flex-1 rounded-full ${i < strength ? STRENGTH_COLOR[strength] : "bg-muted"}`}
                              />
                            ))}
                          </div>
                          <p className="text-xs text-muted-foreground">{STRENGTH_LABEL[strength]}</p>
                        </div>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">Confirm New Password</Label>
                      <PasswordInput
                        id="confirmPassword"
                        value={confirmPassword}
                        onChange={setConfirmPassword}
                        autoComplete="new-password"
                      />
                      {passwordsMismatch && <p className="text-xs text-destructive">Passwords don&apos;t match.</p>}
                    </div>

                    <Button type="submit" disabled={savingPassword}>
                      {savingPassword ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                      {savingPassword ? "Updating..." : "Change Password"}
                    </Button>
                  </div>
                </SectionCard>
              </form>

              <SectionCard icon={LogOut} title="Session" description="Currently signed in on this device.">
                <Button variant="outline" type="button" onClick={logout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign out
                </Button>
              </SectionCard>
            </div>
          )}

          {activeTab === "appearance" && (
            <SectionCard icon={Palette} title="Appearance" description="Choose how CreatorOS looks on this device.">
              {mountedTheme && (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                  {[
                    { value: "light", label: "Light", icon: Sun },
                    { value: "dark", label: "Dark", icon: Moon },
                    { value: "system", label: "System", icon: Monitor },
                  ].map((opt) => {
                    const Icon = opt.icon;
                    const active = theme === opt.value;
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => setTheme(opt.value)}
                        className={`flex flex-col items-center gap-2 rounded-xl border p-4 text-sm font-medium transition-colors ${
                          active
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                        }`}
                      >
                        <Icon className="h-5 w-5" />
                        {opt.label}
                      </button>
                    );
                  })}
                </div>
              )}
            </SectionCard>
          )}

          {activeTab === "connections" && (
            <SectionCard
              icon={Youtube}
              title="Connected Accounts"
              description="Publish generated videos directly from CreatorOS."
            >
              {loadingExtras ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : youtubeAccounts.length === 0 ? (
                <div className="rounded-xl border border-dashed border-border p-6 text-center">
                  <p className="text-sm text-muted-foreground">No YouTube account connected yet.</p>
                  <Button asChild variant="outline" className="mt-4">
                    <a href="/connections">
                      Connect YouTube
                      <ExternalLink className="ml-2 h-3.5 w-3.5" />
                    </a>
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {youtubeAccounts.map((acc) => (
                    <div
                      key={acc.id}
                      className="flex items-center justify-between rounded-xl border border-border px-4 py-3"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-500/10">
                          <Youtube className="h-4 w-4 text-red-500" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-foreground">{acc.account_label || "YouTube"}</p>
                          <p className="text-xs text-muted-foreground">Connected</p>
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button asChild variant="outline" size="sm">
                    <a href="/connections">
                      Manage connections
                      <ExternalLink className="ml-2 h-3.5 w-3.5" />
                    </a>
                  </Button>
                </div>
              )}
            </SectionCard>
          )}

          {activeTab === "credits" && (
            <SectionCard icon={Coins} title="Credits & Usage" description="Your current balance and daily free quota.">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="rounded-xl border border-border bg-muted p-4">
                  <p className="text-xs text-muted-foreground">Credit balance</p>
                  <p className="mt-1 text-2xl font-bold text-foreground">
                    {loadingExtras ? "..." : balance?.credit_balance ?? 0}
                  </p>
                </div>
                <div className="rounded-xl border border-border bg-muted p-4">
                  <p className="text-xs text-muted-foreground">Free quota used today</p>
                  <p className="mt-1 text-2xl font-bold text-foreground">
                    {loadingExtras ? "..." : balance?.free_quota_used_today ?? 0}
                  </p>
                </div>
              </div>
              <Button asChild className="mt-4" variant="outline" size="sm">
                <a href="/billing">
                  Go to Billing
                  <ExternalLink className="ml-2 h-3.5 w-3.5" />
                </a>
              </Button>
            </SectionCard>
          )}

          {activeTab === "notifications" && (
            <SectionCard
              icon={Bell}
              title="Notifications"
              description="Fires automatically based on your account activity."
              headerAction={
                unreadCount > 0 ? (
                  <button
                    type="button"
                    onClick={handleMarkAllRead}
                    className="flex shrink-0 items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                  >
                    <CheckCheck className="h-3.5 w-3.5" />
                    Mark all read
                  </button>
                ) : undefined
              }
            >
              <div className="mb-4 flex items-center justify-between rounded-xl border border-border px-4 py-3">
                <div>
                  <p className="text-sm font-medium text-foreground">Project completed</p>
                  <p className="text-xs text-muted-foreground">
                    Success, partial errors, or failure — you get an in-app notification either way.
                  </p>
                </div>
                <LiveBadge />
              </div>

              {loadingNotifications ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : notifications.length === 0 ? (
                <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-border py-10 text-center">
                  <Sparkles className="h-5 w-5 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Nothing yet — run a project and check back here.</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {notifications.map((n) => (
                    <button
                      key={n.id}
                      type="button"
                      onClick={() => handleOpenNotification(n)}
                      className={`flex w-full flex-col gap-0.5 rounded-xl border border-border px-4 py-3 text-left transition-colors hover:bg-accent ${
                        n.is_read ? "" : "bg-primary/5"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {!n.is_read && <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />}
                        <p className="text-sm font-medium text-foreground">{n.title}</p>
                      </div>
                      {n.message && <p className="text-xs text-muted-foreground">{n.message}</p>}
                      <p className="text-[11px] text-muted-foreground">{timeAgo(n.created_at)}</p>
                    </button>
                  ))}
                </div>
              )}

              <div className="mt-5 space-y-3 border-t border-border pt-5">
                <ToggleRow
                  label="Daily activity digest"
                  description="One email each morning summarizing yesterday's generations, failures, and credits spent — only sent on days you had activity."
                  checked={user.notify_email_digest}
                  onChange={handleToggleDigest}
                />
                <ToggleRow
                  label="Low credit balance email"
                  description={`Sent once when your balance drops under ${LOW_CREDIT_THRESHOLD} credits.`}
                  checked={user.notify_low_credit_email}
                  onChange={handleToggleLowCredit}
                />
              </div>
            </SectionCard>
          )}

          {activeTab === "danger" && (
            <SectionCard
              icon={AlertTriangle}
              title="Danger Zone"
              description="Irreversible actions for your account."
              tone="danger"
            >
              <div className="flex items-center justify-between rounded-xl border border-destructive/30 px-4 py-3">
                <div>
                  <p className="text-sm font-medium text-foreground">Delete account</p>
                  <p className="text-xs text-muted-foreground">
                    Permanently deletes your account, projects, assets, and billing history. This cannot be undone.
                  </p>
                </div>
                <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
                  <DialogTrigger asChild>
                    <Button variant="destructive" type="button">
                      Delete
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Delete your account?</DialogTitle>
                      <DialogDescription>
                        This permanently deletes your account and everything in it. This cannot be undone.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-2">
                      <Label htmlFor="deletePassword">Confirm your password</Label>
                      <Input
                        id="deletePassword"
                        type="password"
                        placeholder="Leave blank if you sign in with Google"
                        value={deletePassword}
                        onChange={(e) => setDeletePassword(e.target.value)}
                      />
                    </div>
                    <DialogFooter>
                      <Button variant="outline" type="button" onClick={() => setDeleteOpen(false)}>
                        Cancel
                      </Button>
                      <Button variant="destructive" type="button" disabled={deleting} onClick={handleDeleteAccount}>
                        {deleting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                        {deleting ? "Deleting..." : "Permanently delete"}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </SectionCard>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
