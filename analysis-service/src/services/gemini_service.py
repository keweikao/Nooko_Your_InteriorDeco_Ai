import os
import logging
import json
from typing import AsyncGenerator, Optional, Tuple, Dict, Any, List
from google import genai
from google.genai import types
import asyncio

from src.services.spec_tracking import SPEC_FIELDS, SpecTracker

logger = logging.getLogger(__name__)

class GeminiLLMService:
    """
    Real Gemini LLM service for interior design conversation.
    Handles role-based prompting to extract design specifications dynamically.
    Uses streaming for real-time responses and JSON mode for structured extraction.
    """

    def __init__(self):
        """Initialize Google Gen AI SDK with Vertex AI backend."""
        self.spec_tracker = SpecTracker()
        try:
            # Get project ID from environment
            project_id = os.getenv("PROJECT_ID", "nooko-yourinteriordeco-ai")
            location = os.getenv("VERTEX_LOCATION", "us-central1")

            # Initialize Google Gen AI client with Vertex AI
            self.client = genai.Client(
                vertexai=True,
                project=project_id,
                location=location
            )

            # Use gemini-2.0-flash-exp or gemini-1.5-flash
            self.model_name = "gemini-2.0-flash-exp"
            self.enabled = True
            logger.info(f"✓ Google Gen AI SDK initialized successfully with Vertex AI backend (project={project_id}, location={location}, model={self.model_name})")
        except Exception as e:
            self.enabled = False
            self.client = None
            self.model_name = None
            logger.error(f"✗ Failed to initialize Google Gen AI SDK: {e}")
            logger.warning("⚠ Using fallback responses")

    def _build_dynamic_system_prompt(self, extracted_specs: Dict[str, Any]) -> str:
        """
        Build a dynamic system prompt based on what specs we've already collected.
        Guides the conversation toward gathering missing information.
        """
        tracker_view = self.spec_tracker.evaluate(extracted_specs or {})
        collected = []
        for field in SPEC_FIELDS:
            entry = extracted_specs.get(field.field_id)
            value = entry.get("value") if isinstance(entry, dict) else entry
            if value:
                collected.append(f"✓ {field.label}：{value}")
        missing = [
            f"• {item['label']}（分類：{item['category']}）"
            for item in tracker_view["missing_fields"][:5]
        ]

        prompt = f"""你是 HouseIQ，一位資深的室內設計項目經理，擁有 15 年的業界經驗。

【已蒐集的信息】
{chr(10).join(collected) if collected else "還未開始蒐集"}

【你的思考點】
目前我需要引導用戶提供以下關鍵信息，但必須以自然、流暢的對話方式進行，避免直接提問或列出清單：
{chr(10).join(missing) if missing else "所有關鍵信息已蒐集完畢，現在可以提供總結或深入建議。"}

【你的職責】
1. **自然對話**：根據用戶回答進行自然的談話，不要列出清單。
2. **巧妙引導**：將上述「思考點」中的待蒐集信息巧妙地融入對話中，以間接、探索性的方式提問，讓用戶感覺像在聊天，而非被盤問。例如，如果缺少「預算」，可以問「您對這次裝修的投入有什麼初步想法嗎？」而不是「您的預算範圍是多少？」。
3. **專業建議**：根據已知信息給出初步建議，展現你的專業價值。
4. **確認理解**：在獲得關鍵信息後，以自然的語氣確認你的理解是否正確。
5. **優先用戶體驗**：始終以用戶的對話流為主導，不要打斷用戶的思路。

【對話風格】
- 親切專業，展現 15 年經驗。
- 避免過度銷售，真誠關注客戶需求。
- 根據客戶的回答自然流暢地提問。
- 使用客戶的詞彙和表達方式。
- 保持耐心和同理心。

【重要】
- **絕對不要**列出清單或檢查表給用戶。
- **絕對不要**生硬地逐個詢問缺失信息。
- 讓對話自然流暢，像真實的交流。
- 如果客戶表達清楚，就接受並繼續對話。
- 即使所有信息都已蒐集，也要繼續提供有價值的對話，例如提供更多建議、確認細節或詢問用戶是否有其他考量。"""

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
        fields_block = "\n".join([
            f'  "{field.field_id}": "填寫{field.label}，若未提及請輸出 null",'
            for field in SPEC_FIELDS
        ])

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
請以 JSON 格式提取以下欄位（若未提及請給 null）：
{{
{fields_block}
  "confidence_scores": {{
    "user_name": 0.8,
    "project_type": 0.9,
    "...": 0.0
  }}
}}

【重要】
- 只返回 JSON，不要有其他文字
- 信心分數表示該信息在對話中提及的清晰度
- 完全明確的信息：0.9-1.0
- 有點暗示但不完全明確：0.5-0.8
- 完全沒提及：null"""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=extraction_prompt,
                config=types.GenerateContentConfig(
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
            return self._mock_spec_extraction(message)

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
            text = self._mock_response(message)
            for char in text:
                yield (char, None)
                await asyncio.sleep(0)
            mock_specs = self._mock_spec_extraction(message)
            if mock_specs:
                yield ("", mock_specs)
            return

        try:
            # Build dynamic system prompt based on what we've extracted
            extracted_specs = context.get("extracted_specs", {})
            system_prompt = self._build_dynamic_system_prompt(extracted_specs)

            # Build message list with conversation history
            messages = [{"role": "user", "parts": [system_prompt]}]
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": "user" if msg.get("sender") == "user" else "model",
                    "parts": [msg.get("content", "")]
                })

            # Add current message
            messages.append({
                "role": "user",
                "parts": [message]
            })

            logger.info(f"Generating response for message: {message[:100]}...")

            # Build conversation content string
            conversation_text = system_prompt + "\n\n"
            for msg in conversation_history[-10:]:
                role = "User" if msg.get("sender") == "user" else "Assistant"
                conversation_text += f"{role}: {msg.get('content', '')}\n\n"
            conversation_text += f"User: {message}\n\nAssistant:"

            # Call Google Gen AI SDK with streaming
            response_stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=conversation_text
            )

            # Stream the response text
            full_response = ""
            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    for char in chunk.text:
                        full_response += char
                        yield (char, None)
                        await asyncio.sleep(0)  # Allow other tasks to run

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
            fallback_text = self._mock_response(message)
            for char in fallback_text:
                yield (char, None)
            mock_specs = self._mock_spec_extraction(message)
            if mock_specs:
                yield ("", mock_specs)

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
                "我是 HouseIQ，您的室內設計項目經理。請告訴我您的裝修需求。",
                None
            )

        try:
            extracted_specs = context.get("extracted_specs", {})
            system_prompt = self._build_dynamic_system_prompt(extracted_specs)

            # Build conversation content string
            conversation_text = system_prompt + "\n\n"
            for msg in conversation_history[-10:]:
                role = "User" if msg.get("sender") == "user" else "Assistant"
                conversation_text += f"{role}: {msg.get('content', '')}\n\n"
            conversation_text += f"User: {message}\n\nAssistant:"

            # Generate response with Google Gen AI SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=conversation_text,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                    top_p=0.9,
                    top_k=40
                )
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
        except Exception:
            mock_specs = self._mock_spec_extraction(message)
            text = self._mock_response(message)
            return (text, mock_specs)

    def _mock_response(self, message: str) -> str:
        return (
            "我是 HouseIQ。已收到您的最新說法，我會根據目前掌握的資訊整理建議。也歡迎補充更多細節，"
            "例如預算、風格或想優先改善的區域。"
        )

    def _mock_spec_extraction(self, message: str) -> Dict[str, Any]:
        """Basic keyword-based extraction when Gemini is unavailable."""
        specs: Dict[str, Any] = {}
        confidence: Dict[str, float] = {}

        lower_msg = message.lower()
        if any(word in message for word in ["全屋", "整體", "全室"]):
            specs["project_type"] = "全室裝修"
            confidence["project_type"] = 0.8
        if any(word in message for word in ["局部", "部分"]):
            specs["project_type"] = "局部裝修"
            confidence["project_type"] = 0.7

        for style in ["北歐", "現代", "無印", "工業", "美式"]:
            if style in message:
                specs["style_preference"] = f"{style}風"
                confidence["style_preference"] = 0.85
                break

        if "預算" in message or any(char.isdigit() for char in message):
            specs["budget_range"] = "待確認"
            confidence["budget_range"] = 0.6

        focus_keywords = []
        for area in ["廚房", "衛浴", "客廳", "臥室"]:
            if area in message:
                focus_keywords.append(area)
        if focus_keywords:
            specs["focus_areas"] = focus_keywords
            confidence["focus_areas"] = 0.7

        if not specs:
            return {}

        specs["confidence_scores"] = confidence
        return specs


# Singleton instance
gemini_service = GeminiLLMService()
