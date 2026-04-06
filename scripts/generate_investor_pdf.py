import os
from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.cell(0, 10, 'P Λ R Λ D I T I - Investor Brief', 0, 1, 'C')
        # Line break
        self.ln(5)
        # Draw a line
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')
        self.cell(0, 10, f'Generated: {datetime.date.today()}', 0, 0, 'R')

    def chapter_title(self, label):
        # Arial 12
        self.set_font('Arial', 'B', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, label, 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, body):
        # Read text file
        self.set_font('Arial', '', 11)
        # Output justified text
        self.multi_cell(0, 5, body)
        # Line break
        self.ln()

    def bullet_point(self, text):
        self.set_font('Arial', '', 11)
        self.cell(5) # Indent
        self.cell(5, 5, chr(149), 0, 0) # Bullet
        self.multi_cell(0, 5, text)
        self.ln(2)

def generate_pdf():
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # 1. Executive Summary
    pdf.chapter_title('1. Executive Summary')
    pdf.chapter_body(
        "SAHAJ is a digital platform designed to bridge the critical gap between Indian citizens "
        "and government welfare schemes. By leveraging AI and simplified workflows, SAHAJ ensures "
        "that the 'last-mile' delivery of benefits reaches the intended beneficiaries efficiently."
    )

    # 2. The Problem
    pdf.chapter_title('2. The Problem')
    pdf.chapter_body(
        "Despite thousands of government schemes, awareness and accessibility remain major hurdles:"
    )
    pdf.bullet_point("95% of rural citizens are unaware of schemes they are eligible for.")
    pdf.bullet_point("66% of beneficiaries cannot recall the names of schemes they applied to.")
    pdf.bullet_point("Manual application processes are complex, paper-heavy, and error-prone.")

    # 3. The SAHAJ Solution
    pdf.chapter_title('3. The Solution')
    pdf.chapter_body(
        "SAHAJ provides a unified interface for scheme discovery, application, and tracking."
    )
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, "Key Features:", 0, 1)
    
    pdf.bullet_point("AI-Powered Recommendations: A hybrid ML engine (Transformer models + TF-IDF) analyzes user profiles to suggest the most relevant schemes.")
    pdf.bullet_point("One-Click Apply: Streamlined application process with document previews and auto-filling.")
    pdf.bullet_point("Government Integration: Direct integration with API Setu for real-time scheme data and updates.")
    pdf.bullet_point("Withdrawal & Management: Users have full control to track and withdraw applications if needed.")

    # 4. Technical Architecture
    pdf.chapter_title('4. Technical Architecture')
    pdf.chapter_body(
        "Built for scale and security, SAHAJ utilizes a modern tech stack:"
    )
    pdf.bullet_point("Backend: Python Flask with SQLAlchemy ORM for robust data management.")
    pdf.bullet_point("Security: JWT (JSON Web Tokens) for secure, stateless authentication.")
    pdf.bullet_point("Data Science: Integrated NLP pipeline using Sentence Transformers for semantic matching.")
    pdf.bullet_point("OCR Capabilities: Optical Character Recognition to digitize physical documents.")

    # 5. Market Impact
    pdf.chapter_title('5. Market Impact')
    pdf.chapter_body(
        "SAHAJ empowers citizens by removing information asymmetry. For the government, it means "
        "higher success rates for welfare programs and reduced administrative overhead. "
        "We are targeting the 800M+ rural population who stand to benefit most from digital inclusion."
    )

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'SAHAJ_Investor_Brief.pdf')
    pdf.output(output_path, 'F')
    print(f"PDF generated successfully at: {output_path}")

if __name__ == '__main__':
    generate_pdf()