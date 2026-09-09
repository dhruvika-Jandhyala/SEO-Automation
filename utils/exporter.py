import json
import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

class ReportExporter:
    """Generates PDF, Markdown, and JSON audit report documents."""

    def generate_json(self, data: Dict[str, Any]) -> str:
        """Returns pretty JSON string of full analysis report."""
        return json.dumps(data, indent=2, ensure_ascii=False)

    def generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generates executive Markdown audit report."""
        score_info = data.get("score", {})
        breakdown = score_info.get("breakdown", {})
        kw_info = data.get("target_keyword_analysis", {})
        issues_info = data.get("issues_and_recommendations", {})

        md = []
        md.append(f"# SEO Audit Report: {data.get('project_name', 'SEO Analysis')}\n")
        md.append(f"**Target Keyword**: `{kw_info.get('target_keyword', 'N/A')}`  ")
        md.append(f"**Overall SEO Score**: **{score_info.get('overall_score', 0)} / 100**  ")
        md.append(f"**Word Count**: {data.get('word_count', 0)} words  ")
        md.append(f"**Search Intent**: {kw_info.get('intent', 'Informational')}\n")

        md.append("## SEO Score Breakdown")
        md.append(f"- **Metadata Quality**: {breakdown.get('metadata_quality', 0)}/100")
        md.append(f"- **Keyword Optimization**: {breakdown.get('keyword_optimization', 0)}/100")
        md.append(f"- **Content Length**: {breakdown.get('content_length', 0)}/100")
        md.append(f"- **Heading Hierarchy**: {breakdown.get('heading_structure', 0)}/100")
        md.append(f"- **Readability**: {breakdown.get('readability', 0)}/100")
        md.append(f"- **Intent Alignment**: {breakdown.get('intent_alignment', 0)}/100\n")

        md.append("## Identified Issues")
        for issue in issues_info.get("issues", []):
            md.append(f"- **[{issue['severity'].upper()}]** ({issue['category']}): {issue['message']} *Solution*: {issue['solution']}")

        md.append("\n## Actionable Recommendations")
        for rec in issues_info.get("recommendations", []):
            md.append(f"1. {rec}")

        md.append("\n## Top Keywords & Density")
        for kw in data.get("top_keywords", [])[:10]:
            md.append(f"- **{kw['keyword']}**: Density: {kw['density_pct']}% | Intent: {kw['intent']}")

        return "\n".join(md)

    def generate_pdf(self, data: Dict[str, Any]) -> bytes:
        """Generates a professional PDF audit report using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=20, leading=24, textColor=colors.HexColor("#1e293b"))
        h2_style = ParagraphStyle("H2Style", parent=styles["Heading2"], fontSize=14, leading=18, textColor=colors.HexColor("#0f172a"), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#334155"))
        bold_body = ParagraphStyle("BoldBody", parent=body_style, fontName="Helvetica-Bold")

        story = []

        # Document Header
        story.append(Paragraph(f"SEO Audit Report: {data.get('project_name', 'Analysis')}", title_style))
        story.append(Spacer(1, 8))
        
        kw = data.get("target_keyword_analysis", {}).get("target_keyword", "N/A")
        score = data.get("score", {}).get("overall_score", 0)
        
        meta_table_data = [
            [Paragraph("Target Keyword:", bold_body), Paragraph(str(kw), body_style), Paragraph("Overall Score:", bold_body), Paragraph(f"<b>{score} / 100</b>", body_style)],
            [Paragraph("Word Count:", bold_body), Paragraph(str(data.get("word_count", 0)), body_style), Paragraph("Search Intent:", bold_body), Paragraph(str(data.get("target_keyword_analysis", {}).get("intent", "N/A")), body_style)]
        ]
        meta_table = Table(meta_table_data, colWidths=[110, 160, 110, 160])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 14))

        # Score Breakdown Table
        story.append(Paragraph("SEO Score Breakdown", h2_style))
        breakdown = data.get("score", {}).get("breakdown", {})
        score_rows = [
            [Paragraph("<b>Category</b>", bold_body), Paragraph("<b>Score (0-100)</b>", bold_body)],
            [Paragraph("Metadata Quality", body_style), Paragraph(str(breakdown.get("metadata_quality", 0)), body_style)],
            [Paragraph("Keyword Optimization", body_style), Paragraph(str(breakdown.get("keyword_optimization", 0)), body_style)],
            [Paragraph("Content Length", body_style), Paragraph(str(breakdown.get("content_length", 0)), body_style)],
            [Paragraph("Heading Hierarchy", body_style), Paragraph(str(breakdown.get("heading_structure", 0)), body_style)],
            [Paragraph("Readability Index", body_style), Paragraph(str(breakdown.get("readability", 0)), body_style)],
            [Paragraph("Search Intent Fit", body_style), Paragraph(str(breakdown.get("intent_alignment", 0)), body_style)],
        ]
        score_table = Table(score_rows, colWidths=[300, 240])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 14))

        # Actionable Recommendations
        story.append(Paragraph("Actionable Recommendations", h2_style))
        recs = data.get("issues_and_recommendations", {}).get("recommendations", [])
        if recs:
            for i, r in enumerate(recs, 1):
                story.append(Paragraph(f"<b>{i}.</b> {r}", body_style))
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph("No critical issues found! Content is well optimized.", body_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
