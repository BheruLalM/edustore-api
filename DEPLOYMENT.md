# Deployment Configuration Guide

To ensure **session persistence** and **stable authentication** on Render (or any production environment), you MUST configure the following Environment Variables.

## 🚨 Critical Variables (Required for Stability)

Failure to set these will result in users being logged out on every redeploy.

### 1. `SECRET_KEY`
**Purpose**: Used to sign JWTs (Access & Refresh Tokens).
**Requirement**: Must be a **static, long, random string**.
**Generation**: Run `openssl rand -hex 32` in your terminal.
**Value Example**: `a1b2c3d4e5f6...` (do not change this once set!)

### 2. `UPSTASH_REDIS_REST_URL` & `UPSTASH_REDIS_REST_TOKEN`
**Purpose**: Stores Refresh Tokens persistently.
**Requirement**: Must be a valid Upstash Redis instance (or compatible).
**Why**: If you rely on in-memory storage or a non-persistent Redis, all refresh tokens vanish on restart.

## 📝 Full Environment Checklist

| Variable | Value / Description | Critical? |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | ✅ |
| `SECRET_KEY` | `[Paste your static hex string]` | ✅ |
| `UPSTASH_REDIS_REST_URL` | `https://...upstash.io` | ✅ |
| `UPSTASH_REDIS_REST_TOKEN` | `Ad...=` | ✅ |
| `FRONTEND_URL` | `https://your-frontend.onrender.com` | ✅ |
| `DATABASE_URL` | `postgresql://...` | ✅ |

## How to Set on Render
1.  Go to your **Dashboard**.
2.  Select your **Backend Service**.
3.  Click **Environment**.
4.  Add the variables list above.
5.  **Redeploy** to apply changes.
