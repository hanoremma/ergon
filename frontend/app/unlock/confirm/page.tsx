"use client";
import { Suspense, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";

function ConfirmInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const orderId = searchParams.get("order_id");
  const sessionId = searchParams.get("session");

  useEffect(() => {
    if (sessionId && orderId) {
      router.replace(`/unlock/${sessionId}?order_id=${orderId}`);
    } else {
      router.replace("/");
    }
  }, [sessionId, orderId, router]);

  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "center",
      minHeight: "100vh", background: "var(--bg-page)",
    }}>
      <div style={{
        width: 40, height: 40, borderRadius: "50%",
        border: "3px solid var(--accent-soft)",
        borderTop: "3px solid var(--accent)",
        animation: "spin 1s linear infinite",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export default function UnlockConfirmPage() {
  return (
    <Suspense fallback={
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        minHeight: "100vh", background: "var(--bg-page)",
      }}>
        <div style={{
          width: 40, height: 40, borderRadius: "50%",
          border: "3px solid var(--accent-soft)",
          borderTop: "3px solid var(--accent)",
          animation: "spin 1s linear infinite",
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    }>
      <ConfirmInner />
    </Suspense>
  );
}
