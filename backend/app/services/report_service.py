import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from typing import Dict, Any, List

from app.core.config import settings

BRAND_COLOR = colors.HexColor("#1e40af")
ACCENT_COLOR = colors.HexColor("#0891b2")
LIGHT_BLUE = colors.HexColor("#eff6ff")
TEXT_COLOR = colors.HexColor("#1e293b")
GRAY = colors.HexColor("#64748b")
MUTED_BG = colors.HexColor("#f8fafc")
BORDER_COLOR = colors.HexColor("#e2e8f0")


class ReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            name="TitleStyle",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=BRAND_COLOR,
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name="SubtitleStyle",
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            textColor=GRAY,
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name="SectionStyle",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=BRAND_COLOR,
            spaceAfter=6,
            spaceBefore=14
        ))
        self.styles.add(ParagraphStyle(
            name="BodyStyle",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=TEXT_COLOR
        ))
        self.styles.add(ParagraphStyle(
            name="PredictionStyle",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=ACCENT_COLOR,
            spaceBefore=4,
            spaceAfter=4
        ))
        self.styles.add(ParagraphStyle(
            name="DisclaimerStyle",
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=GRAY
        ))
        self.styles.add(ParagraphStyle(
            name="SmallStyle",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=TEXT_COLOR
        ))
        self.styles.add(ParagraphStyle(
            name="CalloutStyle",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=TEXT_COLOR,
            backColor=LIGHT_BLUE,
            borderColor=BORDER_COLOR,
            borderWidth=0.5,
            borderPadding=8,
            spaceBefore=4,
            spaceAfter=4,
        ))

    def _add_header(self, doc, filename, report_title="ECG Analysis Report"):
        story = []
        header_table = Table(
            [[Paragraph("CardioSense <font color='#0891b2'>AI</font>", self.styles["TitleStyle"])]],
            colWidths=[16 * cm]
        )
        header_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(f"<font color='#1e40af'><b>{report_title}</b></font>", self.styles["SubtitleStyle"]))
        story.append(Paragraph("Intelligent ECG Analysis. Clearer Cardiac Insights.", self.styles["SubtitleStyle"]))
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="100%", thickness=2, color=BRAND_COLOR))
        story.append(Spacer(1, 0.4 * cm))
        return story

    def _add_meta_table(self, story, analysis: Dict[str, Any]):
        analysis_type = analysis.get("analysis_type", "signal")
        meta_rows = [
            ["Report ID", f"#{analysis.get('id', 'N/A')}"],
            ["Date", analysis.get("created_at", datetime.now().isoformat())],
            ["File Name", analysis.get("file_name", "N/A")],
        ]
        if analysis_type == "image":
            meta_rows.append(["Analysis Type", "ECG Image Analysis"])
        else:
            meta_rows += [
                ["Sampling Rate", f"{analysis.get('sampling_rate', 'N/A')} Hz"],
                ["Leads", str(analysis.get("num_leads", "N/A"))],
                ["Duration", f"{analysis.get('duration', 'N/A'):.1f} s" if isinstance(analysis.get("duration"), (int, float)) else "N/A"],
            ]
        table = Table(meta_rows, colWidths=[4.5 * cm, 11.5 * cm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), BRAND_COLOR),
            ("TEXTCOLOR", (1, 0), (1, -1), TEXT_COLOR),
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5 * cm))

    def _add_predicted_ecg_pattern(self, story, analysis: Dict[str, Any]):
        story.append(Paragraph("A. Predicted ECG Pattern", self.styles["SectionStyle"]))
        primary_label = analysis.get("primary_label") or analysis.get("prediction") or "N/A"
        primary_conf = analysis.get("primary_confidence") or analysis.get("confidence") or 0
        dominant_group = analysis.get("dominant_group")
        story.append(Paragraph(f"{primary_label}", self.styles["PredictionStyle"]))
        sub_text = (
            f"Predicted subclass probability: <b>{primary_conf * 100:.1f}%</b>"
        )
        if dominant_group:
            sub_text += f"  |  Dominant ECG Group: <b>{dominant_group}</b>"
        story.append(Paragraph(sub_text, self.styles["BodyStyle"]))
        story.append(Spacer(1, 0.4 * cm))

    def _add_pattern_groups(self, story, analysis: Dict[str, Any]):
        group_probs = analysis.get("group_probabilities") or {}
        if not group_probs:
            return
        story.append(Paragraph("B. ECG Pattern Groups", self.styles["SectionStyle"]))
        rows = [["ECG Pattern Group", "Aggregated Probability", "Indicator"]]
        dominant = analysis.get("dominant_group")
        for group, prob in sorted(group_probs.items(), key=lambda x: x[1], reverse=True):
            indicator = "●" if group == dominant else "○"
            rows.append([group, f"{prob * 100:.1f}%", indicator])
        table = Table(rows, colWidths=[7 * cm, 6 * cm, 3 * cm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, MUTED_BG]),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5 * cm))

    def _add_subclass_probabilities(self, story, analysis: Dict[str, Any]):
        subclass_results = analysis.get("subclass_results")
        if not subclass_results:
            return
        story.append(Paragraph("C. ECG Subclass Probabilities", self.styles["SectionStyle"]))
        rows = [["Subclass", "Group", "Probability"]]
        for row in subclass_results:
            rows.append([
                row["human_readable_label"],
                row["group"],
                f"{row['probability'] * 100:.1f}%",
            ])
        table = Table(rows, colWidths=[7.5 * cm, 4.5 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, MUTED_BG]),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5 * cm))

    def _add_pattern_summary(self, story, analysis: Dict[str, Any]):
        summary = analysis.get("pattern_summary")
        if not summary:
            return
        story.append(Paragraph("D. ECG Pattern Summary", self.styles["SectionStyle"]))
        story.append(Paragraph(summary, self.styles["CalloutStyle"]))
        story.append(Spacer(1, 0.4 * cm))

    def _add_recommended_next_steps(self, story, analysis: Dict[str, Any]):
        next_steps = (
            analysis.get("recommended_next_steps")
            or analysis.get("next_steps")
            or []
        )
        if not next_steps:
            return
        story.append(Paragraph("E. Recommended Next Steps", self.styles["SectionStyle"]))
        for i, step in enumerate(next_steps, 1):
            story.append(Paragraph(f"<b>{i}.</b> {step}", self.styles["BodyStyle"]))
            story.append(Spacer(1, 0.1 * cm))
        story.append(Spacer(1, 0.3 * cm))

    def _add_gradcam_section(self, story, analysis: Dict[str, Any]):
        gradcam_path = analysis.get("gradcam_path")
        if not analysis.get("gradcam_available") or not gradcam_path or not os.path.exists(gradcam_path):
            return
        story.append(Paragraph("F. Grad-CAM Visualization", self.styles["SectionStyle"]))
        try:
            img = Image(str(os.path.abspath(gradcam_path)), width=12 * cm, height=8 * cm)
            story.append(img)
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph(
                "The heatmap highlights image regions the model found most influential "
                "for the prediction. Grad-CAM shows influential image regions only; it "
                "does not constitute a clinical finding.",
                self.styles["DisclaimerStyle"]
            ))
            story.append(Spacer(1, 0.4 * cm))
        except Exception:
            story.append(Paragraph("(Grad-CAM image could not be embedded.)", self.styles["BodyStyle"]))

    def _add_image_section(self, story, analysis: Dict[str, Any]):
        image_path = analysis.get("image_path")
        if not image_path or not os.path.exists(image_path):
            return
        story.append(Paragraph("Uploaded ECG Image", self.styles["SectionStyle"]))
        try:
            img = Image(str(os.path.abspath(image_path)), width=12 * cm, height=8 * cm)
            story.append(img)
            story.append(Spacer(1, 0.4 * cm))
        except Exception:
            story.append(Paragraph("(Image could not be embedded in the report.)", self.styles["BodyStyle"]))

    def _add_signal_section(self, story, analysis: Dict[str, Any]):
        story.append(Paragraph("Probability Distribution", self.styles["SectionStyle"]))
        probs = analysis.get("probabilities", {})
        if not probs:
            return
        rows = [["Class", "Probability", "Indicator"]]
        for cls, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
            indicator = "●" if prob >= 0.5 else "○"
            rows.append([cls, f"{prob * 100:.1f}%", indicator])
        table = Table(rows, colWidths=[6 * cm, 6 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, MUTED_BG]),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5 * cm))

    def _add_statistics_section(self, story, analysis: Dict[str, Any]):
        stats = analysis.get("ecg_statistics", {})
        overall = stats.get("overall", {})
        if overall:
            story.append(Paragraph("ECG Signal Statistics", self.styles["SectionStyle"]))
            stat_data = [
                ["Mean Amplitude", f"{overall.get('mean_amplitude', 'N/A'):.4f}" if isinstance(overall.get('mean_amplitude'), (int, float)) else "N/A"],
                ["Max Amplitude", f"{overall.get('max_amplitude', 'N/A'):.4f}" if isinstance(overall.get('max_amplitude'), (int, float)) else "N/A"],
                ["Signal Length", str(overall.get("signal_length", "N/A"))],
                ["Number of Leads", str(overall.get("num_leads", "N/A"))],
            ]
            table = Table(stat_data, colWidths=[6 * cm, 10 * cm])
            table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, MUTED_BG]),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.5 * cm))

    def _add_explainability_section(self, story, analysis: Dict[str, Any]):
        explainability = analysis.get("explainability")
        if explainability and "error" not in explainability:
            story.append(Paragraph("Explainability", self.styles["SectionStyle"]))
            lead_importance = explainability.get("lead_importance", {})
            if lead_importance:
                rows = [["Lead", "Importance"]]
                sorted_leads = sorted(lead_importance.items(), key=lambda x: x[1], reverse=True)
                for lead, imp in sorted_leads[:5]:
                    rows.append([lead, f"{imp * 100:.1f}%"])
                table = Table(rows, colWidths=[6 * cm, 6 * cm])
                table.setStyle(TableStyle([
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 0), (-1, 0), ACCENT_COLOR),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.2 * cm))
                story.append(Paragraph(
                    "Highlighted regions represent signal areas that contributed to the model prediction. They should not be interpreted as a clinical diagnosis.",
                    self.styles["DisclaimerStyle"]
                ))

    def _add_footer(self, story, analysis: Dict[str, Any]):
        story.append(Spacer(1, 0.5 * cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR))
        story.append(Spacer(1, 0.2 * cm))
        if analysis.get("analysis_type") == "image":
            story.append(Paragraph("G. Medical Disclaimer", self.styles["SectionStyle"]))
            disclaimer = analysis.get("medical_disclaimer") or (
                "ECG image analysis is generated by a deep learning model and should not "
                "be interpreted as a standalone medical diagnosis. CardioSense AI provides "
                "AI-generated ECG analysis for research and decision-support purposes. It "
                "is not a medical diagnosis and does not replace evaluation by a qualified "
                "healthcare professional."
            )
            story.append(Paragraph(disclaimer, self.styles["BodyStyle"]))
        else:
            disclaimer = (
                "CardioSense AI provides AI-generated ECG signal analysis for research and "
                "decision-support purposes. It is not a medical diagnosis and does not "
                "replace evaluation by a qualified healthcare professional."
            )
            story.append(Paragraph(disclaimer, self.styles["DisclaimerStyle"]))

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        reports_dir = Path(__file__).parent.parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)

        analysis_id = analysis.get("id", "unknown")
        analysis_type = analysis.get("analysis_type", "signal")
        suffix = "image" if analysis_type == "image" else "signal"
        file_path = reports_dir / f"cardiosense_{suffix}_report_{analysis_id}.pdf"

        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm
        )

        title = "ECG IMAGE ANALYSIS REPORT" if analysis_type == "image" else "ECG SIGNAL ANALYSIS REPORT"
        story = self._add_header(doc, analysis.get("file_name", ""), title)
        self._add_meta_table(story, analysis)

        if analysis_type == "image":
            self._add_image_section(story, analysis)
            self._add_predicted_ecg_pattern(story, analysis)
            self._add_pattern_groups(story, analysis)
            self._add_subclass_probabilities(story, analysis)
            self._add_pattern_summary(story, analysis)
            self._add_recommended_next_steps(story, analysis)
            self._add_gradcam_section(story, analysis)
        else:
            self._add_signal_section(story, analysis)
            self._add_statistics_section(story, analysis)
            self._add_explainability_section(story, analysis)

        self._add_footer(story, analysis)

        doc.build(story)
        return str(file_path)


report_service = ReportService()
