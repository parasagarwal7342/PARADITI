# Google Cloud Run - Manual Deployment Guide (Hackathon Submission)

Follow these steps to get your **P Λ R Λ D I T I** Live URL for the Hack2Skill submission form.

---

### 1. Access Google Cloud Console
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Select or create a new Project (e.g., `paraditi-hackathon`).

### 2. Create Cloud Run Service
1.  In the search bar, type **"Cloud Run"** and select it.
2.  Click **CREATE SERVICE**.
3.  Choose **"Continuously deploy new revisions from a source repository"**.
4.  Click **SET UP WITH CLOUD BUILD**.
    - **Repository Provider**: GitHub.
    - **Repository**: Select `parasagarwal7342/PARADITI`.
    - **Build Type**: Select **Docker**.
    - **Source**: `/Dockerfile` (Leave at default).
    - Click **SAVE**.

### 3. Service Configuration (CRITICAL SETTINGS)
- **Service Name**: `paraditi-platform`
- **Region**: `us-central1` (or your preferred region)
- **Authentication**: Select **"Allow unauthenticated invocations"** (This makes it public for judges).

### 4. Container Settings (Port & Capacity)
Click on **"Container, Networking, Security"** to expand the section:

- **Container Port**: `5000`
- **Memory**: `2 GiB` (Required for AI/ML workloads like sentence-transformers).
- **CPU**: `1` (or higher if needed).

### 5. Environment Variables
Add these under the **"Variables & Secrets"** tab:
- `FLASK_ENV`: `production`
- `DATABASE_URL`: `sqlite:///instance/sahaj.db`
- `SECRET_KEY`: `hack2skill-paraditi-v5-secret`
- `JWT_SECRET_KEY`: `hack2skill-paraditi-v5-jwt-secret`

### 6. Deploy
1.  Click **CREATE**.
2.  Wait 2-3 minutes for the build and deployment to finish.
3.  Once finished, the **URL** will appear at the top of the page.

---

👉 **COPY THIS URL** and paste it into the **"Deployed Link - (Cloud run URL)"** field in your Hack2Skill submission form!
