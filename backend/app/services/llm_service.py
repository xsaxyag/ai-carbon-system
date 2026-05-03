"""
AI碳枢算 - LLM服务层
支持OpenAI兼容API（DeepSeek、通义千问、文心一言、本地Ollama等）
"""
import json
from typing import Optional, List, Dict
from openai import OpenAI
from app import config

# 系统提示词 - 碳中和AI顾问
SYSTEM_PROMPT = """你是「AI碳枢算」系统的智能顾问，专精于企业碳排放管理、碳中和战略规划。

## 你的能力
1. **碳排放咨询**：解答碳排放核算、碳交易、碳足迹、碳标签等问题
2. **政策解读**：解读中国碳达峰碳中和相关政策法规（GB/T 32150、温室气体核算指南等）
3. **减排建议**：基于企业实际数据提供定制化减排方案
4. **合规指导**：帮助中小企业了解碳排放报告和核查要求
5. **行业对标**：分析不同行业的碳排放水平和最佳实践

## 回答规范
- 务实具体，给出可执行的方案而非空泛建议
- 数据引用需注明来源（如GB/T 32150、IPCC指南等）
- 对中小企业场景给出成本效益分析
- 如果用户提供了碳数据，结合数据给出针对性分析
"""

# OCR智能提取提示词
OCR_EXTRACT_PROMPT = """你是一个专业的碳数据文档智能提取助手。用户会提供OCR识别的原始文本（来自发票、电费单、燃气费单、采购单等能源相关票据）。

请从文本中提取与碳排放核算相关的关键信息，以JSON格式返回。

## 提取字段说明
- doc_type: 文档类型（invoice增值税发票/utility_bill水电燃气费/purchase_order采购单/transport_receipt运输单/other其他）
- amount: 金额（元，数值类型）
- date: 日期（YYYY-MM-DD格式）
- seller: 销售方/供应方名称
- buyer: 购买方名称
- item_name: 商品/服务名称（如天然气、电力、汽油等）
- quantity: 数量（数值类型）
- unit: 单位（如kWh、m3、L、kg、t）
- unit_price: 单价
- tax_rate: 税率（如0.13表示13%）
- carbon_related: 是否与碳排放直接相关（true/false）
- suggested_scope: 建议碳排放范围（scope1/scope2/scope3/null）
- suggested_source: 建议排放源（natural_gas/coal/electricity/gasoline/diesel/renewable/null）
- confidence: 提取置信度（0-1）
- notes: 备注（如有特殊发现）

## 规则
1. 如果某些字段无法从文本中提取，填null
2. 仅返回JSON，不要其他文字
3. 根据商品名称智能判断碳排放范围和排放源
4. 燃气/汽油/柴油 → scope1，电力 → scope2，供应链采购 → scope3
"""


class LLMService:
    """LLM服务（单例模式）"""

    _instance = None
    _client = None
    _available = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self):
        if self._client is None:
            self._init_client()
        return self._client

    def _init_client(self):
        """初始化OpenAI兼容客户端"""
        try:
            self._client = OpenAI(
                api_key=config.LLM_API_KEY,
                base_url=config.LLM_BASE_URL,
                timeout=30.0
            )
            self._available = True
        except Exception as e:
            self._available = False
            self._error = str(e)

    @property
    def available(self) -> bool:
        if self._available is None:
            try:
                self._init_client()
            except Exception:
                self._available = False
        return self._available

    def chat(
        self,
        messages: List[Dict],
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        发送对话请求

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            str: 模型回复文本
        """
        if not self.available:
            raise RuntimeError(f"LLM服务不可用: {getattr(self, '_error', '未配置API Key')}")

        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=full_messages,
            temperature=temperature or config.LLM_TEMPERATURE,
            max_tokens=max_tokens or config.LLM_MAX_TOKENS
        )

        return response.choices[0].message.content

    def extract_ocr_data(self, ocr_text: str) -> Dict:
        """
        从OCR文本中智能提取碳相关数据

        Args:
            ocr_text: OCR识别的原始文本

        Returns:
            dict: 结构化提取结果
        """
        if not self.available:
            return self._mock_extract(ocr_text)

        try:
            response = self.chat(
                messages=[{"role": "user", "content": f"请从以下OCR文本中提取碳数据相关信息：\n\n{ocr_text}"}],
                temperature=0.1,  # 低温度保证结构化输出稳定
                max_tokens=1024
            )

            # 解析JSON响应
            text = response.strip()
            # 处理可能被```json包裹的情况
            if text.startswith("```"):
                lines = text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                text = "\n".join(lines)

            result = json.loads(text)
            result["ai_extracted"] = True
            return result

        except json.JSONDecodeError:
            return {
                "doc_type": "unknown",
                "carbon_related": False,
                "confidence": 0.0,
                "notes": "AI提取结果解析失败，请手动填写",
                "ai_extracted": True
            }
        except Exception as e:
            return self._mock_extract(ocr_text)

    def analyze_company_emission(self, company_data: dict, emission_records: list) -> str:
        """
        分析企业碳排放数据，给出定制化建议

        Args:
            company_data: 企业信息
            emission_records: 碳排放记录列表

        Returns:
            str: 分析报告
        """
        if not self.available:
            return self._mock_analysis(company_data, emission_records)

        # 构造数据分析prompt
        data_summary = json.dumps({
            "company": company_data,
            "records": emission_records[-20:]  # 最近20条记录
        }, ensure_ascii=False, indent=2)

        prompt = f"""请基于以下企业的碳排放数据，给出一份简明的分析报告和减排建议：

{data_summary}

要求：
1. 概括企业当前碳排放状况（1-2句话）
2. 指出主要排放源和排放范围分布
3. 给出3条具体可执行的减排建议（需考虑成本效益）
4. 评估企业碳中和进展水平
5. 建议下一步行动优先级"""

        return self.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=config.LLM_MAX_TOKENS
        )

    def _mock_extract(self, ocr_text: str) -> Dict:
        """模拟OCR数据提取（LLM不可用时）"""
        import re

        # 简单正则提取作为降级方案
        amount = None
        amount_match = re.search(r'([\d,]+\.?\d*)\s*元', ocr_text)
        if amount_match:
            amount = float(amount_match.group(1).replace(',', ''))

        date_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', ocr_text)
        date = None
        if date_match:
            date = date_match.group(1).replace('年', '-').replace('月', '-').replace('日', '')

        # 简单关键词判断碳排放相关
        keywords_scope1 = ['天然气', '燃气', '汽油', '柴油', '煤炭', '煤']
        keywords_scope2 = ['电力', '电费', '用电', '度']
        keywords_scope3 = ['采购', '供应链', '运输', '物流']

        suggested_scope = None
        suggested_source = None

        for kw in keywords_scope1:
            if kw in ocr_text:
                suggested_scope = "scope1"
                if '天然气' in kw or '燃气' in kw:
                    suggested_source = "natural_gas"
                elif '汽油' in kw:
                    suggested_source = "gasoline"
                elif '柴油' in kw:
                    suggested_source = "diesel"
                else:
                    suggested_source = "coal"
                break

        if not suggested_scope:
            for kw in keywords_scope2:
                if kw in ocr_text:
                    suggested_scope = "scope2"
                    suggested_source = "electricity"
                    break

        if not suggested_scope:
            for kw in keywords_scope3:
                if kw in ocr_text:
                    suggested_scope = "scope3"
                    break

        return {
            "doc_type": "unknown",
            "amount": amount,
            "date": date,
            "carbon_related": suggested_scope is not None,
            "suggested_scope": suggested_scope,
            "suggested_source": suggested_source,
            "confidence": 0.5 if suggested_scope else 0.2,
            "notes": "规则引擎提取（LLM未配置）" if not self.available else "AI提取失败，降级为规则提取",
            "ai_extracted": False
        }

    def _mock_analysis(self, company_data: dict, emission_records: list) -> str:
        """模拟企业排放分析"""
        if not emission_records:
            return "当前暂无碳排放数据，建议先录入企业的能源消耗数据后再进行分析。"

        total = sum(r.get("co2_emission", 0) for r in emission_records)
        sources = {}
        for r in emission_records:
            s = r.get("emission_source", "unknown")
            sources[s] = sources.get(s, 0) + r.get("co2_emission", 0)

        top_source = max(sources.items(), key=lambda x: x[1]) if sources else ("unknown", 0)

        return f"""## 碳排放分析报告（基础版）

**企业**: {company_data.get('name', '未知')}
**行业**: {company_data.get('industry', '未知')}
**记录数**: {len(emission_records)}

### 碳排放概况
- 总排放量: {total:.2f} kgCO2
- 主要排放源: {top_source[0]} ({top_source[1]:.2f} kgCO2, 占{top_source[1]/total*100:.1f}%)
- 排放源分布: {', '.join(f'{k}={v:.1f}' for k,v in sources.items())}

### 减排建议
1. 针对主要排放源"{top_source[0]}"制定专项节能方案
2. 考虑购买绿色电力证书或安装分布式光伏
3. 建立碳排放台账制度，按月监测排放趋势

> 💡 提示: 配置AI大模型后可获得更精准的定制化分析建议"""

    def get_status(self) -> Dict:
        """获取LLM服务状态"""
        return {
            "available": self.available,
            "model": config.LLM_MODEL if self.available else None,
            "base_url": config.LLM_BASE_URL if self.available else None,
            "api_key_configured": config.LLM_API_KEY != "sk-xxx",
            "error": getattr(self, '_error', None) if not self.available else None
        }


# 全局实例
llm_service = LLMService()
