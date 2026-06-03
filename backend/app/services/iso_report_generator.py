# -*- coding: utf-8 -*-
"""
AI Carbon Hub - ISO Standard Report Generator
Supports ISO 14064-1 (Organization Carbon) and ISO 14067 (Product Carbon Footprint)
"""
import io
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register Chinese fonts
def _register_fonts():
    font_paths = [
        ('SimHei', [r'C:\Windows\Fonts\simhei.ttf', r'C:\Windows\Fonts\msyh.ttc']),
        ('SimSun', [r'C:\Windows\Fonts\simsun.ttc', r'C:\Windows\Fonts\msyh.ttc']),
    ]
    registered = {}
    for name, paths in font_paths:
        for p in paths:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(name, p))
                    registered[name] = True
                    break
                except Exception:
                    pass
    return registered

FONT_MAP = _register_fonts()
CN_FONT = 'SimHei' if 'SimHei' in FONT_MAP else 'Helvetica'
CN_FONT_BODY = 'SimSun' if 'SimSun' in FONT_MAP else 'Helvetica'

# Colors
PRIMARY = HexColor('#1a73e8')
GRAY = HexColor('#5f6368')
LIGHT_GRAY = HexColor('#e8eaed')
BG_BLUE = HexColor('#e8f0fe')


class ISOReportGenerator:
    """ISO Standard Carbon Report Generator"""
    
    def __init__(self):
        self.styles = self._create_styles()
    
    def _create_styles(self):
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            'CoverTitle', fontName=CN_FONT, fontSize=28, leading=36,
            alignment=TA_CENTER, textColor=PRIMARY, spaceAfter=20
        ))
        
        styles.add(ParagraphStyle(
            'ChapterTitle', fontName=CN_FONT, fontSize=18, leading=26,
            textColor=PRIMARY, spaceBefore=20, spaceAfter=12
        ))
        
        styles.add(ParagraphStyle(
            'SectionTitle', fontName=CN_FONT, fontSize=14, leading=20,
            textColor=PRIMARY, spaceBefore=12, spaceAfter=8
        ))
        
        styles.add(ParagraphStyle(
            'CNBodyText', fontName=CN_FONT_BODY, fontSize=10, leading=16,
            textColor=HexColor('#333333'), alignment=TA_JUSTIFY
        ))
        
        styles.add(ParagraphStyle(
            'TableCaption', fontName=CN_FONT_BODY, fontSize=9, leading=14,
            textColor=GRAY, alignment=TA_CENTER, spaceBefore=6, spaceAfter=6
        ))
        
        return styles
    
    def generate_iso14064_report(
        self,
        company_data: Dict[str, Any],
        emission_data: Dict[str, Any],
        report_period: str = "2025 Annual",
        report_date: str = None
    ) -> bytes:
        """
        Generate ISO 14064-1 Organization Carbon Report
        """
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=2.5*cm, rightMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm
        )
        
        elements = []
        report_date = report_date or datetime.now().strftime("%Y-%m-%d")
        
        # Cover Page
        elements.append(Spacer(1, 80))
        elements.append(Paragraph("Enterprise Carbon Emission Report", self.styles['CoverTitle']))
        elements.append(Paragraph("(ISO 14064-1 Organization Carbon Inventory)", self.styles['SectionTitle']))
        elements.append(Spacer(1, 40))
        
        cover_info = [
            ["Organization Name", company_data.get("name", "N/A")],
            ["Report Period", report_period],
            ["Issue Date", report_date],
        ]
        
        t = Table(cover_info, colWidths=[150, 250])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), CN_FONT_BODY),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TEXTCOLOR', (0, 0), (0, -1), GRAY),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(t)
        elements.append(PageBreak())
        
        # Chapter 1: Organization Overview
        elements.append(Paragraph("Chapter 1: Organization Overview", self.styles['ChapterTitle']))
        
        info_data = [
            ["Organization Name", company_data.get("name", "N/A")],
            ["Industry", company_data.get("industry", "N/A")],
            ["Address", company_data.get("address", "N/A")],
            ["Employee Count", str(company_data.get("employee_count", "N/A"))],
        ]
        
        t = Table(info_data, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), CN_FONT_BODY),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (0, -1), BG_BLUE),
            ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        elements.append(PageBreak())
        
        # Chapter 2: Emission Results
        elements.append(Paragraph("Chapter 2: Emission Results", self.styles['ChapterTitle']))
        
        total = emission_data.get("total_emission", 0)
        scope1 = emission_data.get("scope1", 0)
        scope2 = emission_data.get("scope2", 0)
        scope3 = emission_data.get("scope3", 0)
        
        summary_data = [
            ["Emission Scope", "Emission (tCO2e)", "Percentage"],
            ["Scope 1 (Direct)", f"{scope1:.2f}", f"{scope1/max(total,1)*100:.1f}%"],
            ["Scope 2 (Indirect)", f"{scope2:.2f}", f"{scope2/max(total,1)*100:.1f}%"],
            ["Scope 3 (Other)", f"{scope3:.2f}", f"{scope3/max(total,1)*100:.1f}%"],
            ["Total", f"{total:.2f}", "100%"],
        ]
        
        t = Table(summary_data, colWidths=[200, 120, 100])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), CN_FONT_BODY),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, -1), (-1, -1), BG_BLUE),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        elements.append(Paragraph("Table 2-1: GHG Emission Summary", self.styles['TableCaption']))
        elements.append(PageBreak())
        
        # Chapter 3: Methodology
        elements.append(Paragraph("Chapter 3: Methodology", self.styles['ChapterTitle']))
        elements.append(Paragraph(
            "This report follows ISO 14064-1:2018 standard for GHG quantification and reporting. "
            "Emission factors are sourced from IPCC 2006 Guidelines and China Regional Grid Emission Factors.",
            self.styles['CNBodyText']
        ))
        elements.append(Spacer(1, 12))
        
        factor_data = [
            ["Emission Source", "Emission Factor", "Data Source"],
            ["Natural Gas", "2.1620 kgCO2/m3", "IPCC 2006"],
            ["Electricity (East China)", "0.7921 kgCO2/kWh", "2024 China Grid Factor"],
            ["Gasoline", "2.1625 kgCO2/L", "IPCC 2006"],
        ]
        
        t = Table(factor_data, colWidths=[150, 120, 180])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), CN_FONT_BODY),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ]))
        elements.append(t)
        elements.append(Paragraph("Table 3-1: Main Emission Factors", self.styles['TableCaption']))
        
        # Build PDF
        doc.build(elements)
        return buf.getvalue()
    
    def generate_iso14067_report(
        self,
        product_data: Dict[str, Any],
        lca_data: Dict[str, Any],
        report_date: str = None
    ) -> bytes:
        """
        Generate ISO 14067 Product Carbon Footprint Report
        """
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=2.5*cm, rightMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm
        )
        
        elements = []
        report_date = report_date or datetime.now().strftime("%Y-%m-%d")
        
        # Cover Page
        elements.append(Spacer(1, 80))
        elements.append(Paragraph("Product Carbon Footprint Report", self.styles['CoverTitle']))
        elements.append(Paragraph("(ISO 14067:2018)", self.styles['SectionTitle']))
        elements.append(Spacer(1, 40))
        
        cover_info = [
            ["Product Name", product_data.get("name", "N/A")],
            ["Functional Unit", product_data.get("functional_unit", "N/A")],
            ["System Boundary", product_data.get("system_boundary", "Cradle-to-Gate")],
            ["Issue Date", report_date],
        ]
        
        t = Table(cover_info, colWidths=[150, 250])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), CN_FONT_BODY),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TEXTCOLOR', (0, 0), (0, -1), GRAY),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(t)
        elements.append(PageBreak())
        
        # Chapter 1: Goal and Scope
        elements.append(Paragraph("Chapter 1: Goal and Scope", self.styles['ChapterTitle']))
        elements.append(Paragraph(
            f"This report aims to quantify the carbon footprint of {product_data.get('name', 'the product')} "
            f"following ISO 14067:2018 standard.",
            self.styles['CNBodyText']
        ))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            f"Functional Unit: {product_data.get('functional_unit', '1 unit')}",
            self.styles['CNBodyText']
        ))
        elements.append(Paragraph(
            f"System Boundary: {product_data.get('system_boundary', 'Cradle-to-Gate')}",
            self.styles['CNBodyText']
        ))
        elements.append(PageBreak())
        
        # Chapter 2: LCA Results
        elements.append(Paragraph("Chapter 2: Life Cycle Assessment Results", self.styles['ChapterTitle']))
        
        total_footprint = lca_data.get("total_footprint", 0)
        elements.append(Paragraph(
            f"Total Carbon Footprint: {total_footprint:.2f} kgCO2e/{lca_data.get('functional_unit', 'unit')}",
            self.styles['CNBodyText']
        ))
        elements.append(Spacer(1, 12))
        
        # Stage distribution
        stages = lca_data.get("stages", [])
        stage_names = {
            "raw_material": "Raw Material",
            "production": "Production",
            "transport": "Transport",
            "use": "Use Phase",
            "disposal": "End of Life"
        }
        
        stage_data = [["Stage", "Emission (kgCO2e)", "Percentage"]]
        for stage in stages:
            emission = stage.get("emission", 0)
            ratio = emission / max(total_footprint, 1) * 100
            stage_data.append([
                stage_names.get(stage.get("id", ""), stage.get("id", "")),
                f"{emission:.2f}",
                f"{ratio:.1f}%"
            ])
        
        t = Table(stage_data, colWidths=[150, 120, 100])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), CN_FONT_BODY),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ]))
        elements.append(t)
        elements.append(Paragraph("Table 2-1: Emission Distribution by Stage", self.styles['TableCaption']))
        
        # Build PDF
        doc.build(elements)
        return buf.getvalue()


# Global instance
iso_report_generator = ISOReportGenerator()
