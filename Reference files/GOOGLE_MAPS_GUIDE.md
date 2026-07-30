# WariMitra Maps Setup & Free API Key Guide

## 1. Do You Need an API Key?

> [!NOTE]
> **NO, YOU DO NOT NEED AN API KEY!**
> 
> WariMitra includes a built-in, **100% FREE Wari GIS Vector Map Engine**. It works out of the box with zero setup, zero credit card requirements, and zero costs. It displays the entire Pandharpur Wari Palkhi Route (*Alandi → Pune → Dive Ghat → Saswad → Jejuri → Lonand → Pandharpur*), live moving responder markers, zoom controls, and entity detail modals!

---

## 2. If You Want Real Google Maps (100% Free Usage Tiers)

If you explicitly want Google Maps satellite/street view tiles, Google Maps Platform offers **generous free monthly usage tiers** (e.g. up to 10,000 map loads every month for free).

### Step-by-Step Guide to Get Your Free Google Maps API Key:

#### Step 1: Open Google Cloud Console
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Log in with your standard Google / Gmail account.

#### Step 2: Create a New Project
1. Click the Project dropdown at the top navigation bar.
2. Click **"New Project"**.
3. Name your project **`WariMitra-GIS`** and click **Create**.

#### Step 3: Enable Google Maps APIs
1. Go to **APIs & Services > Library** from the left menu.
2. Search for **"Maps JavaScript API"** and click **Enable**.
3. Search for **"Places API"** and click **Enable**.
4. Search for **"Directions API"** and click **Enable**.

#### Step 4: Create & Copy Your API Key
1. Go to **APIs & Services > Credentials**.
2. Click **"+ Create Credentials"** → select **API Key**.
3. Copy the generated API Key (it looks like `AIzaSy...`).

#### Step 5: Add Key to WariMitra
1. In your `frontend` directory, create a file named `.env.local` (or copy `.env.local.example`).
2. Add your key:
   ```env
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=AIzaSyYourGeneratedKeyHere
   ```
3. Restart your dev server (`npm run dev`).

---

## 3. Best 100% Free Alternatives (No Credit Card Required)

If you don't want to enter a credit card on Google Cloud, here are the best 100% free options:

| Option | Cost | Billing Required? | Monthly Free Tier |
| :--- | :--- | :--- | :--- |
| **Built-in Wari GIS Engine** *(Default)* | **100% Free** | **NO** | **Unlimited** |
| **OpenStreetMap / Leaflet** | **100% Free** | **NO** | **Unlimited** |
| **Mapbox GL** | **Free** | No card for basic tier | 100,000 map loads / month |
| **Google Maps Platform** | **Free Tier** | Card required for signup | ~10,000 loads / month free |

---

## Summary Recommendation

- **For local dev, demo, and production without paying anything**: Keep using WariMitra's built-in **Wari GIS Vector Engine**.
- **For real Google Maps**: Follow the 5 steps above to generate your free API key and add it to `frontend/.env.local`.
