"""
payment-mcp — MCP Server for Payment Processing (Midtrans)
Tools:
  - create_payment_transaction: Create a Midtrans Snap payment transaction
  - verify_payment_status: Check payment status by order_id
  - process_webhook: Process Midtrans payment notification webhook
"""
import os
import json
import base64
import hashlib
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="payment-mcp",
    instructions="MCP server untuk payment processing via Midtrans Snap API (sandbox & production).",
)

MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY", "")
MIDTRANS_CLIENT_KEY = os.getenv("MIDTRANS_CLIENT_KEY", "")
IS_PRODUCTION = os.getenv("MIDTRANS_IS_PRODUCTION", "false").lower() == "true"
UNLOCK_PRICE_IDR = int(os.getenv("UNLOCK_PRICE_IDR", "25000"))

MIDTRANS_SNAP_BASE = "https://app.midtrans.com" if IS_PRODUCTION else "https://app.sandbox.midtrans.com"
MIDTRANS_API_BASE = "https://api.midtrans.com" if IS_PRODUCTION else "https://api.sandbox.midtrans.com"


def get_auth_header() -> str:
    return "Basic " + base64.b64encode(f"{MIDTRANS_SERVER_KEY}:".encode()).decode()


@mcp.tool()
async def create_payment_transaction(
    order_id: str,
    session_id: str,
    amount: int = UNLOCK_PRICE_IDR,
    customer_name: str = "Pengguna Ergon",
    customer_email: str = "",
    item_name: str = "Ergon — Buka Semua Saran + CV Revisi",
) -> dict:
    """
    Buat transaksi pembayaran Midtrans Snap untuk unlock analisis.

    Args:
        order_id: ID unik transaksi (format: ERGON-{session}-{random})
        session_id: Session ID analisis yang akan di-unlock
        amount: Nominal pembayaran dalam IDR (default dari config)
        customer_name: Nama pelanggan
        customer_email: Email pelanggan (optional)
        item_name: Nama item yang dijual

    Returns:
        Dict dengan snap_token, redirect_url, client_key, dan order_id
    """
    payload = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": amount,
        },
        "credit_card": {"secure": True},
        "item_details": [{
            "id": "ergon-unlock",
            "price": amount,
            "quantity": 1,
            "name": item_name,
        }],
        "customer_details": {
            "first_name": customer_name,
            "email": customer_email or "customer@ergon.app",
        },
        "callbacks": {
            "finish": f"http://localhost:3000/unlock/confirm?order_id={order_id}&session={session_id}",
        },
        "custom_field1": session_id,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(
                f"{MIDTRANS_SNAP_BASE}/snap/v1/transactions",
                headers={
                    "Authorization": get_auth_header(),
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "success": True,
                "order_id": order_id,
                "session_id": session_id,
                "snap_token": data.get("token"),
                "redirect_url": data.get("redirect_url"),
                "client_key": MIDTRANS_CLIENT_KEY,
                "amount": amount,
                "is_production": IS_PRODUCTION,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id,
            }


@mcp.tool()
async def verify_payment_status(order_id: str) -> dict:
    """
    Cek status pembayaran dari Midtrans API.

    Args:
        order_id: ID transaksi yang ingin dicek

    Returns:
        Dict dengan payment status: pending/settlement/capture/cancel/expire/deny
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                f"{MIDTRANS_API_BASE}/v2/{order_id}/status",
                headers={"Authorization": get_auth_header()},
            )
            resp.raise_for_status()
            data = resp.json()
            status = data.get("transaction_status", "unknown")
            fraud = data.get("fraud_status", "")
            is_paid = status in ("settlement", "capture") and fraud in ("accept", "")
            return {
                "order_id": order_id,
                "transaction_status": status,
                "fraud_status": fraud,
                "is_paid": is_paid,
                "payment_type": data.get("payment_type", ""),
                "gross_amount": data.get("gross_amount", ""),
                "session_id": data.get("custom_field1", ""),
            }
        except Exception as e:
            return {
                "order_id": order_id,
                "transaction_status": "error",
                "is_paid": False,
                "error": str(e),
            }


@mcp.tool()
async def process_webhook(
    notification_payload: dict,
) -> dict:
    """
    Proses notifikasi webhook dari Midtrans dan kembalikan status unlock.

    Args:
        notification_payload: Raw payload dari Midtrans webhook notification

    Returns:
        Dict dengan should_unlock (bool), session_id, dan order_id
    """
    order_id = notification_payload.get("order_id", "")
    transaction_status = notification_payload.get("transaction_status", "")
    fraud_status = notification_payload.get("fraud_status", "")
    signature_key = notification_payload.get("signature_key", "")
    status_code = notification_payload.get("status_code", "")
    gross_amount = notification_payload.get("gross_amount", "")

    # Verify signature
    signature_input = f"{order_id}{status_code}{gross_amount}{MIDTRANS_SERVER_KEY}"
    expected_sig = hashlib.sha512(signature_input.encode()).hexdigest()

    if signature_key and signature_key != expected_sig:
        return {
            "valid": False,
            "should_unlock": False,
            "error": "Signature verification failed",
            "order_id": order_id,
        }

    should_unlock = (
        transaction_status in ("settlement", "capture") and
        fraud_status in ("accept", "")
    )

    session_id = notification_payload.get("custom_field1", "")

    return {
        "valid": True,
        "should_unlock": should_unlock,
        "order_id": order_id,
        "session_id": session_id,
        "transaction_status": transaction_status,
        "fraud_status": fraud_status,
    }


if __name__ == "__main__":
    port = int(os.getenv("PAYMENT_MCP_PORT", "8007"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
