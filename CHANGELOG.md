# Changelog

## [5.4.0] - 2026-02-09
### Security Enforcement & Resilience (Claim V)
- **Hybrid State Security Mesh (HSSM)**: Implemented "Fail-Safe" in-memory rate limiting that activates instantly when Redis is unavailable, ensuring 100% uptime for brute-force protection.
- **Bleach Sanitization**: Integrated industry-standard `bleach` library for robust XSS protection, stripping all malicious HTML tags from user inputs.
- **Production Guardrails**: Added critical startup checks that prevent the application from launching in production with default secret keys.
- **Strict Rate Limiting**: Enforced granular limits (5-10 req/min) on sensitive Auth endpoints to mitigate automated attacks.

## [5.3.0] - 2026-02-06
### Advanced AI & IP Expansion
- **Patent Claim Expansion**: Successfully implemented and documented the full **A-U Patent Claim Range**, including Future Horizon Labs (Claims S-T-U).
- **Backend Global Synchronization**: Fully synchronized all proprietary headers, database names (`paraditi.db`), and firewall rebranding across the entire project structure.
- **Intelligent Document Logic**: Enhanced the Smart Document Hub to dynamically list specific missing Tier-1 documents required for eligibility.
- **Aditi AI v5.2**: Finalized the backend transition from legacy "Asha" to the state-of-the-art **Aditi AI** intent engine.

## [5.2.0] - 2026-02-06
### Stability & Branding
- **Global Rebranding Harmonization**: Unified all Copyright headers to **2026 P Λ R Λ D I T I**.
- **IP Consolidation**: Finalized 18 Patent Claims (A-R) across all documentation.
- **Frontend Refinement**: Enhanced Glassmorphism consistency in Auth pages.

## [5.1.0] - 2026-02-06
### Added
- **P Λ R Λ D I T I Rebranding**: Complete visual and linguistic transformation from SAHAJ to P Λ R Λ D I T I (परादिति).
- **Founder Identification**: Officially integrated **PARAS AGRAWAL** as the project Founder across all footers, legal docs, and metadata.
- **Cyber-Dark Aesthetic**: Implemented a high-contrast theme across all frontend pages and navigation bars.
- **Aditi AI v5.0**: Renamed the AI assistant from Asha to Aditi with updated conversational logic and branding.

## [5.0.0] - 2026-02-05
### Added
- **Intelligent Document Orchestrator (IDO)**: New backend service (`backend/services/document_processor.py`) that automatically compresses and resizes documents to meet government portal requirements (Claim G).
- **Smart Document Hub**: A new dashboard widget for managing identity documents with status indicators for Verification and Expiry.
- **One-Click Automated Filing**: `ApplicationService` now combines user profile data with OCR-extracted document data to auto-fill scheme applications (Claim H).
- **OCR Integration**: Tesseract-based text extraction from uploaded images to auto-populate profile fields.
- **Direct SQLite Migration**: Added `scripts/migrate_sqlite_direct.py` for seamless database schema upgrades.
- **Personalized Recommendations Badge**: UI indicator showing which profile attributes triggered a specific scheme recommendation.
- **Life Journey Timeline**: Dynamic roadmap visualization in the dashboard.

### Changed
- **Dashboard Metrics**: "Schemes Viewed" now dynamically reflects the count of currently eligible/recommended schemes (fixing the 21 vs 41 mismatch).
- **API Response**: `/api/schemes/recommended` now returns `limit=50` by default to ensure maximum coverage.
- **Database Model**: `Document` model updated to include `file_size`, `original_size`, `category`, and `is_verified` fields.
- **Frontend State Management**: Improved synchronization between recommendation fetching and user stats (UBS/Viewed Count).

### Fixed
- **API 500 Error**: Resolved timezone mismatch crash in `/api/documents` endpoint by implementing robust naive/aware datetime checks.
- **Frontend Loading**: Fixed race condition where user stats loaded before recommendations were fully processed.
