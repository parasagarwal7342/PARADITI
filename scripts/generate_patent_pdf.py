from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Patent Application Draft', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

pdf = PDF()
pdf.add_page()

# Title Page
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 20, 'NON-PROVISIONAL PATENT APPLICATION', 0, 1, 'C')
pdf.ln(20)

pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, 'TITLE OF THE INVENTION:', 0, 1)
pdf.set_font('Arial', '', 12)
pdf.multi_cell(0, 8, 'SYSTEM AND METHOD FOR AI-DRIVEN AUTOMATED DISCOVERY, PERSONALIZATION, AND RECOMMENDATION OF GOVERNMENT WELFARE SCHEMES')
pdf.ln(10)

pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, 'INVENTORS:', 0, 1)
pdf.set_font('Arial', '', 12)
pdf.cell(0, 8, '[Insert Full Name(s) of Inventors]', 0, 1)
pdf.cell(0, 8, '[Insert City, State, Country]', 0, 1)
pdf.ln(10)

pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, 'APPLICANT:', 0, 1)
pdf.set_font('Arial', '', 12)
pdf.cell(0, 8, '[Insert Company/University/Individual Name]', 0, 1)
pdf.add_page()

# Sections
sections = [
    ("CROSS-REFERENCE TO RELATED APPLICATIONS", "[If applicable, insert: This application claims priority to Provisional Application No. ______ filed on ______.]"),
    ("FIELD OF THE INVENTION", "The present invention relates generally to the field of Artificial Intelligence, Information Retrieval, and E-Governance. More specifically, it relates to a system and method for aggregating fragmented government welfare scheme data, creating semantic user profiles, and generating personalized recommendations using a hybrid machine learning engine."),
    ("BACKGROUND OF THE INVENTION", """Governments worldwide launch numerous welfare schemes to assist citizens based on demographics, socio-economic status, and specific needs. However, a significant gap exists between the availability of these schemes and their utilization by intended beneficiaries.

1. Fragmentation of Information: Scheme details are often scattered across multiple disparate government portals (central, state, departmental), making manual search inefficient.
2. Complex Eligibility Criteria: Schemes often have intricate eligibility rules involving age, income, caste/category, occupation, and geography, which are difficult for average citizens to interpret.
3. Lack of Awareness: Studies indicate that a vast majority (up to 95%) of eligible beneficiaries are unaware of schemes they qualify for.
4. Technical Barriers: Existing portals often rely on rigid keyword matching that fails to understand the "intent" or "context" of a user's situation (e.g., a query for "farming help" might not match a scheme titled "PM-KISAN" if the description lacks the exact keyword).

Therefore, there is a need for an intelligent, unified platform that can semantically understand user profiles and automatically match them against a real-time aggregated database of government schemes."""),
    ("OBJECTS OF THE INVENTION", """The primary object of the present invention is to provide a system that aggregates government schemes from multiple sources (including API Setu) into a unified database.

Another object is to provide a Hybrid Machine Learning Engine that utilizes both Semantic Embeddings (e.g., Sentence Transformers) and Statistical matching (e.g., TF-IDF) to ensure high-accuracy recommendations even in resource-constrained environments.

A further object is to provide an automated "One-Click Apply" mechanism that validates user documents via OCR (Optical Character Recognition) and simulates application submission."""),
    ("SUMMARY OF THE INVENTION", """The present invention discloses a system and method for automated welfare scheme recommendation, currently embodied as a prototype under development. The system comprises:
1. A Data Aggregation Module (partially implemented) that synchronizes scheme data from external government APIs (e.g., API Setu) and local databases.
2. A User Profiling Module that captures demographic data (age, income, location, occupation) and converts it into a "Profile Vector."
3. A Hybrid AI Recommendation Engine configured to:
    * Generate semantic embeddings for both user profiles and scheme descriptions using a Transformer-based model (e.g., all-MiniLM-L6-v2).
    * Compute cosine similarity between the Profile Vector and Scheme Vectors.
    * Automatically fall back to a TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer if the transformer model is unavailable or computationally expensive.
4. A Document Verification Module utilizing OCR to extract and validate identity data (e.g., Aadhaar, PAN) from uploaded documents against the user profile."""),
    ("BRIEF DESCRIPTION OF THE DRAWINGS", """FIG. 1 illustrates the high-level system architecture of the SAHAJ platform.
FIG. 2 is a flowchart demonstrating the Hybrid AI Recommendation logic.
FIG. 3 illustrates the user profile vectorization and scheme matching process.
FIG. 4 shows the document upload and OCR verification workflow."""),
    ("DETAILED DESCRIPTION OF THE INVENTION", """The system is implemented as a web-based platform comprising a Frontend (Client Device) and a Backend Server.

1. Data Aggregation & Management
The system maintains a dynamic database of schemes. A specialized service (api_setu.py) communicates with external Government Open Data Platforms (e.g., API Setu). It fetches scheme metadata (Title, Description, Eligibility Rules) and normalizes it into a standardized schema stored in a relational database (e.g., SQLite/PostgreSQL).

2. User Profiling & Vectorization
When a user registers, the system collects structured data: Age, Gender, State, Income, Category (Caste), and Occupation.
The ML Engine (ml_engine.py) synthesizes this structured data into a natural language string.
* Example: "Age: 45 years. State: Maharashtra. Income: Rs. 5000 per month. Occupation: Farmer."
This string is passed to the embedding model to create a high-dimensional User Profile Vector.

3. Hybrid Recommendation Engine
The core invention lies in the dual-mode recommendation logic:
* Primary Mode (Semantic): Uses a pre-trained Sentence Transformer model. It encodes the User Profile Vector and all Scheme Description Vectors into a shared vector space. It calculates the Cosine Similarity score. This allows the system to match "farming help" with "PM-KISAN" even without direct keyword overlap.
* Fallback Mode (Statistical): If the deep learning model fails to load (e.g., server constraints), the system automatically initializes a TfidfVectorizer. It computes similarity based on n-gram overlaps. This ensures system robustness and uptime.

4. Automated Application & OCR
The system includes a withdraw_application and submit_application module. When a user uploads a document (PDF/Image), the OCR Service (ocr_service.py):
1. Extracts raw text using Tesseract or PDF parsing.
2. Uses Regex patterns to identify unique identifiers (e.g., \d{4}\s\d{4}\s\d{4} for Aadhaar).
3. Verifies that the document belongs to the logged-in user before allowing the application to proceed.

5. Prototype Implementation and Development Status
The system disclosed herein is currently implemented as a working prototype and is in an active stage of development.
* Current Status: The core Hybrid Recommendation Engine, User Profiling Module, and basic Data Aggregation logic have been built and validated. The system successfully demonstrates the novel use of semantic embeddings to match users with schemes.
* Ongoing Work: Active development is focused on:
    * Enhancing the OCR Service to support a wider variety of regional document formats.
    * Scaling the API Setu integration to move from simulated/seed data to real-time, large-scale data synchronization.
    * Refining the "One-Click Apply" workflow to handle complex, multi-stage government form submissions.

The present invention therefore encompasses both the currently realized prototype features and the fully integrated architecture described herein."""),
    ("CLAIMS", """We Claim:

1. A system for automated discovery and recommendation of government welfare schemes, comprising:
    (a) a database storing a plurality of welfare schemes, each associated with eligibility criteria and a descriptive text;
    (b) a user interface configured to receive demographic and socio-economic data from a user;
    (c) a processor configured to execute a Hybrid Machine Learning Engine, wherein said engine is programmed to:
        (i) synthesize said user data into a natural language profile string;
        (ii) generate a numerical vector representation of said profile string using a Transformer-based Deep Learning model;
        (iii) calculate a similarity score between said profile vector and pre-computed vectors of said welfare schemes; and
        (iv) rank and display schemes exceeding a predefined similarity threshold.

2. The system of Claim 1, wherein said Hybrid Machine Learning Engine further comprises a Fallback Mechanism configured to automatically switch from said Transformer-based model to a Statistical Model (TF-IDF) upon detection of resource constraints or model initialization failure.

3. The system of Claim 1, further comprising a Data Synchronization Module configured to interface with external Government Open Data APIs (e.g., API Setu) to fetch, update, and normalize scheme data in real-time.

4. A method for verifying eligibility for welfare schemes, comprising the steps of:
    (a) receiving an uploaded document image or PDF from a user;
    (b) performing Optical Character Recognition (OCR) on said document to extract textual content;
    (c) parsing said textual content using Regular Expressions to identify specific government identifiers (e.g., Aadhaar number, PAN number); and
    (d) comparing said extracted identifiers against the user's registered profile data to validate authenticity prior to application submission.

5. The system of Claim 1, wherein the user interface further comprises a "One-Click Apply" feature that simulates the submission of an application by validating said user profile against scheme-specific constraints and updating a persistent application state in the database.

6. A non-transitory computer-readable medium storing instructions which, when executed by a processor, cause a computer to perform the method of:
    (a) generating a semantic embedding for a user based on diverse attributes including age, income, location, and occupation;
    (b) retrieving a set of candidate schemes based on semantic similarity; and
    (c) filtering said candidate schemes by applying hard constraints (e.g., strict age limits or gender exclusivity) to ensure 100% eligibility accuracy."""),
    ("ABSTRACT OF THE DISCLOSURE", """A system and method for AI-driven discovery and recommendation of government welfare schemes is disclosed. The system addresses the problem of information fragmentation by aggregating scheme data from disparate sources into a unified repository. The invention is currently realized as a functional prototype utilizing a Hybrid Machine Learning Engine (Sentence Transformers with TF-IDF fallback) to semantically match user profiles to schemes. While the core recommendation and profiling modules are implemented, the system is under active development to expand the automated "One-Click Apply" capabilities and document verification features. The disclosed architecture serves as a blueprint for bridging the gap between government benefits and citizens through scalable AI intervention.""")
]

for title, body in sections:
    pdf.chapter_title(title)
    pdf.chapter_body(body)

output_path = "Paraditi_Patent_Application_Draft.pdf"
pdf.output(output_path)
print(f"PDF generated successfully: {output_path}")