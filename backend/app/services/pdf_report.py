"""
AI碳枢算 - PDF报告生成服务
使用reportlab生成专业碳排报告（纯Python，无系统依赖）
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 注册中文字体
def _register_fonts():
    """尝试注册Windows中文字体"""
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

# 颜色常量
BLUE = HexColor('#2c3e50')
LIGHT_BLUE = HexColor('#3498db')
RED = HexColor('#e74c3c')
ORANGE = HexColor('#f39c12')
GREEN = HexColor('#27ae60')
GRAY = HexColor('#7f8c8d')
LIGHT_GRAY = HexColor('#ecf0f1')
BG_BLUE = HexColor('#eaf2f8')
BG_RED = HexColor('#fdedec')
BG_ORANGE = HexColor('#fef9e7')
BG_GREEN = HexColor('#eafaf1')


def _make_styles():
    """创建段落样式"""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'CNTitle', fontName=CN_FONT, fontSize=20, leading=28,
        alignment=TA_CENTER, textColor=BLUE, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'CNSubtitle', fontName=CN_FONT_BODY, fontSize=10, leading=14,
        alignment=TA_CENTER, textColor=GRAY, spaceAfter=16
    ))
    styles.add(ParagraphStyle(
        'CNH2', fontName=CN_FONT, fontSize=14, leading=20,
        textColor=BLUE, spaceBefore=20, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        'CNBody', fontName=CN_FONT_BODY, fontSize=10, leading=16,
        textColor=HexColor('#333333')
    ))
    styles.add(ParagraphStyle(
        'CNSmall', fontName=CN_FONT_BODY, fontSize=8, leading=12,
        textColor=GRAY, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'CNSuggestion', fontName=CN_FONT_BODY, fontSize=9, leading=14,
        textColor=HexColor('#606266'), leftIndent=12
    ))
    return styles


def _build_summary_table(summary: dict, styles):
    """构建排放汇总表"""
    data = [
        [Paragraph('<b>指标</b>', styles['CNBody']),
         Paragraph('<b>排放量(kgCO2)</b>', styles['CNBody']),
         Paragraph('<b>占比</b>', styles['CNBody'])],
        [Paragraph('范围1 直接排放', styles['CNBody']),
         Paragraph(f'{summary.get("scope1", 0):.2f}', styles['CNBody']),
         Paragraph(f'{summary.get("scope1", 0)/max(summary.get("total_emission",1),1)*100:.1f}%', styles['CNBody'])],
        [Paragraph('范围2 间接排放', styles['CNBody']),
         Paragraph(f'{summary.get("scope2", 0):.2f}', styles['CNBody']),
         Paragraph(f'{summary.get("scope2", 0)/max(summary.get("total_emission",1),1)*100:.1f}%', styles['CNBody'])],
        [Paragraph('范围3 其他间接', styles['CNBody']),
         Paragraph(f'{summary.get("scope3", 0):.2f}', styles['CNBody']),
         Paragraph(f'{summary.get("scope3", 0)/max(summary.get("total_emission",1),1)*100:.1f}%', styles['CNBody'])],
        [Paragraph('<b>总计</b>', styles['CNBody']),
         Paragraph(f'<b>{summary.get("total_emission", 0):.2f}</b>', styles['CNBody']),
         Paragraph('<b>100%</b>', styles['CNBody'])],
    ]
    t = Table(data, colWidths=[180, 140, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, 1), BG_RED),
        ('BACKGROUND', (0, 2), (-1, 2), BG_ORANGE),
        ('BACKGROUND', (0, 3), (-1, 3), BG_GREEN),
        ('BACKGROUND', (0, 4), (-1, 4), BG_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
    ]))
    return t


def _build_monthly_chart(monthly_data: dict):
    """构建月度排放柱状图"""
    if not monthly_data:
        return Paragraph('暂无月度数据', _make_styles()['CNBody'])

    months = sorted(monthly_data.keys())
    values = [monthly_data[m] for m in months]
    max_val = max(values) if values else 1

    d = Drawing(460, 180)
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 30
    bc.height = 120
    bc.width = 380
    bc.data = [values]
    bc.categoryAxis.categoryNames = [m[-5:] for m in months]
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max_val * 1.15
    bc.valueAxis.valueStep = max_val / 5 if max_val > 0 else 1
    bc.bars[0].fillColor = LIGHT_BLUE
    bc.bars[0].strokeColor = None
    bc.categoryAxis.labels.fontName = CN_FONT_BODY
    bc.categoryAxis.labels.fontSize = 8
    bc.valueAxis.labels.fontName = 'Helvetica'
    bc.valueAxis.labels.fontSize = 8
    d.add(bc)

    # 标题
    d.add(String(230, 165, '月度排放趋势', fontName=CN_FONT, fontSize=10, textAnchor='middle', fillColor=BLUE))
    return d


def _build_source_table(source_data: dict, styles):
    """构建排放源分布表"""
    source_label_map = {
        "natural_gas": "天然气", "coal": "煤炭", "electricity": "外购电力",
        "gasoline": "汽油", "diesel": "柴油", "renewable": "可再生能源",
        "business_flight_short": "短途航班", "business_flight_medium": "中途航班",
        "business_flight_long": "长途航班", "business_train": "火车", "business_car": "公务汽车",
        "waste_landfill": "填埋", "waste_incineration": "焚烧", "waste_composting": "堆肥",
        "purchased_office": "办公用品", "purchased_equipment": "设备采购"
    }
    total = sum(source_data.values()) or 1
    sorted_sources = sorted(source_data.items(), key=lambda x: -x[1])

    data = [[Paragraph('<b>排放源</b>', styles['CNBody']),
             Paragraph('<b>排放量(kgCO2)</b>', styles['CNBody']),
             Paragraph('<b>占比</b>', styles['CNBody'])]]
    for src, val in sorted_sources:
        label = source_label_map.get(src, src)
        pct = val / total * 100
        data.append([
            Paragraph(label, styles['CNBody']),
            Paragraph(f'{val:.4f}', styles['CNBody']),
            Paragraph(f'{pct:.1f}%', styles['CNBody']),
        ])

    t = Table(data, colWidths=[180, 140, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    return t


def _build_suggestion_section(suggestions: list, styles):
    """构建减排建议"""
    elements = []
    if not suggestions:
        elements.append(Paragraph('暂无减排建议', styles['CNBody']))
        return elements
    for sug in suggestions:
        title = sug.get('title', '')
        desc = sug.get('description', '')
        potential = sug.get('potential', 0)
        elements.append(Paragraph(
            f'<b>{title}</b>  — 预计减排 <font color="#27ae60"><b>{potential} kgCO2</b></font>',
            styles['CNBody']
        ))
        elements.append(Paragraph(f'　{desc}', styles['CNSuggestion']))
        elements.append(Spacer(1, 4))
    return elements


def generate_pdf_report(report_data: dict) -> bytes:
    """生成PDF报告，返回字节流"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )

    styles = _make_styles()
    elements = []

    company = report_data.get("company", {})
    summary = report_data.get("summary", {})
    monthly_data = report_data.get("monthly_data", {})
    source_data = report_data.get("source_data", {})
    suggestions = report_data.get("suggestions", [])
    generated_at = report_data.get("generated_at", datetime.now().isoformat())
    report_type = report_data.get("report_type", "monthly")

    type_names = {"monthly": "月度", "quarterly": "季度", "annual": "年度"}
    type_name = type_names.get(report_type, "月度")
    gen_time = generated_at[:19].replace("T", " ") if generated_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # === 标题 ===
    elements.append(Paragraph('企业碳排放报告', styles['CNTitle']))
    elements.append(Paragraph(
        f'{company.get("name", "企业")} · {type_name}报告 · {gen_time}',
        styles['CNSubtitle']
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=LIGHT_BLUE, spaceAfter=12))

    # === 一、企业信息 ===
    elements.append(Paragraph('一、企业信息', styles['CNH2']))
    info_data = [
        [Paragraph('<b>企业名称</b>', styles['CNBody']), Paragraph(str(company.get('name', '-')), styles['CNBody']),
         Paragraph('<b>所属行业</b>', styles['CNBody']), Paragraph(str(company.get('industry', '-')), styles['CNBody'])],
        [Paragraph('<b>信用代码</b>', styles['CNBody']), Paragraph(str(company.get('registration_no', '-')), styles['CNBody']),
         Paragraph('<b>企业地址</b>', styles['CNBody']), Paragraph(str(company.get('address', '-')), styles['CNBody'])],
    ]
    info_table = Table(info_data, colWidths=[80, 150, 80, 150])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f5f7fa')),
        ('BACKGROUND', (2, 0), (2, -1), HexColor('#f5f7fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8))

    # === 二、排放汇总 ===
    elements.append(Paragraph('二、排放汇总', styles['CNH2']))
    elements.append(_build_summary_table(summary, styles))

    # === 三、月度趋势 ===
    elements.append(Paragraph('三、月度排放趋势', styles['CNH2']))
    elements.append(_build_monthly_chart(monthly_data))

    # === 四、排放源分布 ===
    elements.append(Paragraph('四、排放源分布', styles['CNH2']))
    elements.append(_build_source_table(source_data, styles))

    # === 五、减排建议 ===
    elements.append(Paragraph('五、减排建议', styles['CNH2']))
    elements.extend(_build_suggestion_section(suggestions, styles))

    # === 页脚 ===
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY))
    elements.append(Paragraph(
        f'本报告由 AI碳枢算·中小微企业碳中和智能管理系统 自动生成  |  生成时间：{gen_time}  |  数据标准：GB/T 32150-2015',
        styles['CNSmall']
    ))

    doc.build(elements)
    return buf.getvalue()
