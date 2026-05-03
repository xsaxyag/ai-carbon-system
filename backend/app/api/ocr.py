"""
AI碳枢算 - OCR识别API
优先使用RapidOCR（轻量、速度快），备选EasyOCR

安装方式:
1. pip install rapidocr_onnxruntime (推荐, 轻量快速)
2. pip install easyocr (完整, 占用大)
"""
import base64
import re
import os
import random
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

router = APIRouter()

# OCR状态
_ocr_engine = None
_ocr_type = None
_init_error = None

def get_ocr_engine():
    """获取可用的OCR引擎（RapidOCR优先）"""
    global _ocr_engine, _ocr_type, _init_error

    if _init_error is not None:
        return None, None, _init_error

    if _ocr_engine is not None:
        return _ocr_engine, _ocr_type, None

    # 优先尝试RapidOCR
    try:
        from rapidocr_onnxruntime import RapidOCR
        _ocr_engine = RapidOCR()
        _ocr_type = "rapidocr"
        return _ocr_engine, _ocr_type, None
    except Exception as e:
        _init_error = f"RapidOCR初始化失败: {str(e)}"

    # 备选EasyOCR
    try:
        import easyocr
        _ocr_engine = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        _ocr_type = "easyocr"
        _init_error = None
        return _ocr_engine, _ocr_type, None
    except Exception as e:
        _init_error = f"EasyOCR也不可用: {str(e)}"

    return None, None, _init_error


def parse_invoice_text(texts: List[str]) -> Dict:
    """从OCR文本中解析发票信息"""
    full_text = "\n".join(texts)

    result = {
        "invoice_code": None,
        "invoice_no": None,
        "date": None,
        "seller": None,
        "buyer": None,
        "amount": None,
        "tax": None,
        "total": None
    }

    # 发票代码 (各种格式)
    patterns_code = [
        r'发票代码\s*[：:]\s*(\d{10,12})',
        r'发票代码\s*(\d{10,12})',
        r'Code\s*[：:]\s*(\d{10,12})',
    ]
    for p in patterns_code:
        m = re.search(p, full_text)
        if m:
            result["invoice_code"] = m.group(1)
            break

    # 发票号码
    patterns_no = [
        r'发票号码\s*[：:]\s*(\d{8})',
        r'发票号码\s*(\d{8})',
        r'No\s*[.:]\s*(\d{8})',
    ]
    for p in patterns_no:
        m = re.search(p, full_text)
        if m:
            result["invoice_no"] = m.group(1)
            break

    # 日期
    dates = re.findall(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', full_text)
    if dates:
        d = dates[0].replace('年', '-').replace('月', '-').replace('/', '-').replace('日', '')
        result["date"] = d

    # 金额相关 - 多种格式匹配
    # 价税合计
    patterns_total = [
        r'[价税合][计总计]\s*[：:￥¥]*\s*([\d,]+\.?\d*)',
        r'合计\s*[金额]*\s*[：:￥¥]*\s*([\d,]+\.?\d*)',
        r'Total\s*[：:￥¥]*\s*([\d,]+\.?\d*)',
    ]
    for p in patterns_total:
        m = re.search(p, full_text)
        if m:
            try:
                result["total"] = float(m.group(1).replace(',', ''))
            except:
                pass
            break

    # 税额
    patterns_tax = [
        r'税\s*额\s*[：:￥¥]*\s*([\d,]+\.?\d*)',
        r'Tax\s*[：:￥¥]*\s*([\d,]+\.?\d*)',
    ]
    for p in patterns_tax:
        m = re.search(p, full_text)
        if m:
            try:
                result["tax"] = float(m.group(1).replace(',', ''))
            except:
                pass
            break

    # 金额
    patterns_amount = [
        r'[不含税]*[金金额]\s*[：:￥¥]*\s*([\d,]+\.?\d*)',
        r'Amount\s*[：:￥¥]*\s*([\d,]+\.?\d*)',
    ]
    for p in patterns_amount:
        m = re.search(p, full_text)
        if m:
            try:
                result["amount"] = float(m.group(1).replace(',', ''))
            except:
                pass
            break

    # 如果有total没有amount，反推
    if result.get("total") and not result.get("amount") and result.get("tax"):
        result["amount"] = round(result["total"] - result["tax"], 2)

    # 销售方
    seller_match = re.search(r'销[售卖]方[名称]*\s*[：:]\s*(.+)', full_text)
    if seller_match:
        result["seller"] = seller_match.group(1).strip()

    # 购买方
    buyer_match = re.search(r'购[买买]方[名称]*\s*[：:]\s*(.+)', full_text)
    if buyer_match:
        result["buyer"] = buyer_match.group(1).strip()

    return result


def do_ocr(image_path: str) -> Dict:
    """执行OCR识别"""
    engine, ocr_type, err = get_ocr_engine()

    if engine is None:
        return {
            "success": False,
            "message": f"OCR不可用: {err}",
            "extracted_data": None,
            "confidence": 0.0,
            "raw_texts": []
        }

    try:
        if ocr_type == "rapidocr":
            result, _ = engine(image_path)
            raw_texts = []
            texts = []
            if result:
                for item in result:
                    bbox, text, confidence = item
                    texts.append(text)
                    raw_texts.append({
                        "text": text,
                        "confidence": float(confidence)
                    })
            confidence = sum(t["confidence"] for t in raw_texts) / len(raw_texts) if raw_texts else 0
            fields = parse_invoice_text(texts)
        elif ocr_type == "easyocr":
            result = engine.readtext(image_path)
            raw_texts = []
            texts = []
            for box, text, conf in result:
                texts.append(text)
                raw_texts.append({"text": text, "confidence": float(conf)})
            confidence = sum(t["confidence"] for t in raw_texts) / len(raw_texts) if raw_texts else 0
            fields = parse_invoice_text(texts)
        else:
            return {"success": False, "message": "未知OCR引擎", "extracted_data": None, "confidence": 0, "raw_texts": []}

        return {
            "success": True,
            "message": f"{ocr_type}识别成功，共识别{len(texts)}行文本",
            "extracted_data": {
                "type": "invoice",
                "fields": fields
            },
            "confidence": round(confidence, 4),
            "raw_texts": raw_texts
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"OCR识别异常: {str(e)}",
            "extracted_data": None,
            "confidence": 0.0,
            "raw_texts": []
        }


def mock_ocr() -> Dict:
    """模拟OCR识别结果（用于演示和测试）"""
    amount = round(random.uniform(100, 5000), 2)
    tax = round(amount * 0.13, 2)
    total = round(amount + tax, 2)
    return {
        "success": True,
        "message": "模拟识别模式（演示用）",
        "extracted_data": {
            "type": "invoice",
            "fields": {
                "invoice_code": "044031900110",
                "invoice_no": f"{random.randint(10000000, 99999999)}",
                "amount": amount,
                "tax": tax,
                "total": total,
                "date": "2026-04-26",
                "seller": "北京智联新能源科技有限公司",
                "buyer": "测试企业"
            }
        },
        "confidence": 0.85,
        "raw_texts": [
            {"text": "增值税专用发票", "confidence": 0.99},
            {"text": "发票代码: 044031900110", "confidence": 0.95},
            {"text": f"价税合计: ¥{total}", "confidence": 0.92},
            {"text": "销售方: 北京智联新能源科技有限公司", "confidence": 0.88}
        ]
    }


@router.post("/recognize")
async def recognize_invoice(
    file: UploadFile = File(...),
    use_mock: bool = False
):
    """
    识别发票图片

    - file: 图片文件 (支持jpg/png/bmp/webp)
    - use_mock: True使用模拟识别, False使用真实OCR
    """
    image_data = await file.read()

    if len(image_data) < 100:
        raise HTTPException(status_code=400, detail="图片数据无效")

    if use_mock:
        return mock_ocr()

    # 写入临时文件
    suffix = os.path.splitext(file.filename)[1] or '.jpg'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(image_data)
        tmp_path = tmp.name

    try:
        result = do_ocr(tmp_path)
        if not result["success"]:
            # OCR失败时返回模拟数据，并标注
            fallback = mock_ocr()
            fallback["message"] = f"{result['message']}，已切换为模拟模式"
            fallback["is_mock"] = True
            return fallback
        result["is_mock"] = False
        return result
    except Exception as e:
        fallback = mock_ocr()
        fallback["message"] = f"识别异常: {str(e)}，已切换为模拟模式"
        fallback["is_mock"] = True
        return fallback
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/recognize/base64")
async def recognize_base64(image_data: str):
    """识别base64编码的图片"""
    try:
        img_bytes = base64.b64decode(image_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name

        result = do_ocr(tmp_path)
        os.unlink(tmp_path)

        if not result["success"]:
            fallback = mock_ocr()
            fallback["message"] = f"{result['message']}，已切换为模拟模式"
            fallback["is_mock"] = True
            return fallback
        result["is_mock"] = False
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
async def ocr_status():
    """检查OCR引擎状态"""
    engine, ocr_type, err = get_ocr_engine()
    return {
        "available": engine is not None,
        "engine": ocr_type,
        "message": "就绪" if ocr_type else (err or "未安装OCR库")
    }
