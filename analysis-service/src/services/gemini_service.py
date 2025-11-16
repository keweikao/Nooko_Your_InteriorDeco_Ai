import os
import logging
import json
from typing import AsyncGenerator, Optional, Tuple, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiLLMService:
    """
    Real Gemini LLM service for interior design conversation.
    Handles role-based prompting to extract design specifications dynamically.
    Uses streaming for real-time responses and JSON mode for structured extraction.
    """

    def __init__(self):
        """Initialize Gemini API with credentials."""
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel("gemini-2.0-flash")
            self.enabled = True
            logger.info("✓ Gemini API initialized successfully")
        else:
            self.enabled = False
            logger.warning("⚠ GEMINI_API_KEY not set - using fallback responses")

    def _build_dynamic_system_prompt(self, extracted_specs: Dict[str, Any]) -> str:
        """
        Build a dynamic system prompt based on what specs we've already collected.
        Guides the conversation toward gathering missing information.
        """
        collected = []
        missing = []

        # Check what we've collected
        if extracted_specs.get("project_type"):
            collected.append(f"✓ 項目類型：{extracted_specs['project_type']}")
        else:
            missing.append("• 項目類型（全屋翻新或局部改造）")

        if extracted_specs.get("budget_range"):
            collected.append(f"✓ 預算：{extracted_specs['budget_range']}")
        else:
            missing.append("• 預算範圍")

        if extracted_specs.get("style_preference"):
            collected.append(f"✓ 風格：{extracted_specs['style_preference']}")
        else:
            missing.append("• 風格偏好（現代、北歐、日式、古典等）")

        if extracted_specs.get("focus_areas"):
            collected.append(f"✓ 重點區域：{', '.join(extracted_specs['focus_areas'])}")
        else:
            missing.append("• 重點改造區域（廚房、浴室、臥室等）")

        if extracted_specs.get("total_area"):
            collected.append(f"✓ 面積：{extracted_specs['total_area']} 平方米")
        else:
            missing.append("• 空間面積與配置")

        if extracted_specs.get("timeline"):
            collected.append(f"✓ 時程：{extracted_specs['timeline']}")
        else:
            missing.append("• 施工時間限制")

        prompt = f"""你是 Stephen，一位資深的室內設計項目經理，擁有 15 年的業界經驗。

【已蒐集的信息】
{chr(10).join(collected) if collected else "還未開始蒐集"}

【待蒐集的信息】
{chr(10).join(missing)}

【你的職責】
1. **自然對話**：根據用戶回答進行自然的談話，不要列出清單
2. **有針對性提問**：優先追問上述待蒐集的信息
3. **專業建議**：根據已知信息給出初步建議
4. **確認理解**：在獲得關鍵信息後確認你的理解是否正確

【對話風格】
- 親切專業，展現 15 年經驗
- 避免過度銷售，真誠關注客戶需求
- 根據客戶的回答自然流暢地提問
- 使用客戶的詞彙和表達方式

【語言】繁體中文（台灣）

【重要】
- 不要列出清單或檢查表
- 不要生硬地逐個詢問缺失信息
- 讓對話自然流暢，像真實的交流
- 如果客戶表達清楚，就接受並繼續對話"""

        return prompt

    async def _extract_specifications(
        self,
        message: str,
        conversation_history: list
    ) -> Dict[str, Any]:
        """
        Use Gemini to extract structured specifications from the conversation.
        Returns a dictionary with extracted fields and confidence scores.
        """
        try:
            # Build conversation context for extraction
            history_text = "\n".join([
                f"{msg.get('sender', '').upper()}: {msg.get('content', '')}"
                for msg in conversation_history[-10:]
            ])

            extraction_prompt = f"""分析以下對話，提取結構化的室內設計規格信息。

【對話歷史】
{history_text}

【最新消息】
用戶: {message}

【任務】
請以 JSON 格式提取以下信息（如果未提及則為 null）：
{{
  "project_type": "全屋翻新 或 局部改造 (如果提及)",
  "style_preference": "風格偏好（如現代、北歐、日式、古典等）",
  "budget_range": "預算範圍（如 500,000-1,000,000）",
  "timeline": "施工時間（如 3 個月）",
  "total_area": "房間面積（數字，單位平方米）",
  "focus_areas": ["廚房", "浴室", "臥室" 等],
  "material_preference": "材料偏好（如木質、石材、瓷磚等）",
  "quality_level": "品質等級（經濟、標準、高端）",
  "special_requirements": ["特殊需求列表"],
  "confidence_scores": {{
    "project_type": 0.9,
    "style_preference": 0.8,
    ...其他字段的信心分數 (0-1)
  }}
}}

【重要】
- 只返回 JSON，不要有其他文字
- 信心分數表示該信息在對話中提及的清晰度
- 完全明確的信息：0.9-1.0
- 有點暗示但不完全明確：0.5-0.8
- 完全沒提及：null"""

            response = self.client.generate_content(
                extraction_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent extraction
                    max_output_tokens=1024
                )
            )

            # Parse the JSON response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            extracted = json.loads(response_text)
            logger.debug(f"Extracted specifications: {extracted}")
            return extracted

        except Exception as e:
            logger.error(f"Error extracting specifications: {e}")
            return {}

    async def generate_response_stream(
        self,
        message: str,
        conversation_history: list,
        context: dict
    ) -> AsyncGenerator[Tuple[str, Optional[Dict[str, Any]]], None]:
        """
        Generate streaming response using Gemini API and extract specs.
        Yields tuples of (text_chunk, spec_updates).

        Args:
            message: User's current message
            conversation_history: Previous messages in conversation
            context: Additional context (project_id, role, extracted_specs, etc)

        Yields:
            Tuple of (text_chunk, spec_updates) or just (text_chunk, None)
        """

        if not self.enabled:
            # Fallback to mock response
            yield ("我是 Stephen，您的室內設計項目經理。\n\n", None)
            yield ("請告訴我，您主要想要裝修哪些區域呢？廚房、浴室、臥室，還是整個空間？", None)
            return

        try:
            # Build dynamic system prompt based on what we've extracted
            extracted_specs = context.get("extracted_specs", {})
            system_prompt = self._build_dynamic_system_prompt(extracted_specs)

            # Build message list with conversation history
            messages = []
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": "user" if msg.get("sender") == "user" else "assistant",
                    "parts": [msg.get("content", "")]
                })

            # Add current message
            messages.append({
                "role": "user",
                "parts": [message]
            })

            logger.info(f"Generating response for message: {message[:100]}...")

            # Call Gemini API with streaming
            response = self.client.generate_content(
                messages,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                    top_p=0.9,
                    top_k=40
                ),
                system_instruction=system_prompt
            )

            # Stream the response text
            full_response = ""
            for chunk in response:
                if chunk.text:
                    for char in chunk.text:
                        full_response += char
                        yield (char, None)

            # After streaming completes, extract specifications
            logger.info("Response complete, extracting specifications...")
            extracted = await self._extract_specifications(
                message,
                conversation_history + [{"sender": "agent", "content": full_response}]
            )

            if extracted:
                yield ("", extracted)  # Yield specs without text

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            # Fallback response
            error_msg = "抱歉，暫時無法連接到 AI 服務。請稍後再試。"
            for char in error_msg:
                yield (char, None)

    async def generate_response(
        self,
        message: str,
        conversation_history: list,
        context: dict
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Non-streaming version: generate complete response at once.
        Returns (response_text, extracted_specs).
        """
        if not self.enabled:
            return (
                "我是 Stephen，您的室內設計項目經理。請告訴我您的裝修需求。",
                None
            )

        try:
            extracted_specs = context.get("extracted_specs", {})
            system_prompt = self._build_dynamic_system_prompt(extracted_specs)

            messages = []
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": "user" if msg.get("sender") == "user" else "assistant",
                    "parts": [msg.get("content", "")]
                })

            messages.append({
                "role": "user",
                "parts": [message]
            })

            # Generate response
            response = self.client.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                    top_p=0.9,
                    top_k=40
                ),
                system_instruction=system_prompt
            )

            response_text = response.text

            # Extract specifications
            extracted = await self._extract_specifications(
                message,
                conversation_history + [{"sender": "agent", "content": response_text}]
            )

            return (response_text, extracted)

        except Exception as e:
            logger.error(f"Error in non-streaming response: {e}")
            return ("抱歉，無法連接到 AI 服務。請稍後再試。", None)


# Singleton instance
gemini_service = GeminiLLMService()
