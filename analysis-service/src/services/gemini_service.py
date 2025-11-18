import os
import logging
import json
import re
from typing import AsyncGenerator, Optional, Tuple, Dict, Any, List
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions
import asyncio

from src.services.spec_tracking import SpecTracker
# from src.services.image_service import image_service

logger = logging.getLogger(__name__)

MAX_HISTORY_TOKENS = 8000

class GeminiLLMService:
    def __init__(self):
        """
        Initialize the Gemini LLM service exclusively with the Vertex AI backend.
        """
        self.spec_tracker = SpecTracker()
        self.enabled = False
        self.model = None
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-001")
        project_id = os.getenv("PROJECT_ID")
        location = os.getenv("VERTEX_LOCATION", "asia-east1")

        if not project_id:
            logger.error("✗ PROJECT_ID environment variable is not set.")
            return

        try:
            genai.configure(project=project_id, location=location)
            self.model = genai.GenerativeModel(self.model_name)
            self.enabled = True
            logger.info(
                f"✓ Gemini client configured with Vertex AI backend (project={project_id}, location={location}, model={self.model_name})."
            )
        except Exception as e:
            logger.error(f"✗ Failed to initialize Google Gen AI SDK with Vertex AI: {e}")

    def _count_tokens(self, text: str) -> int:
        # A simple approximation
        return len(text) // 4

    async def _get_summarized_history(self, conversation_history: List[Dict[str, Any]], max_tokens: int) -> List[Dict[str, Any]]:
        # This is a placeholder. A real implementation would summarize older messages.
        return conversation_history

    def _build_gemini_contents(
        self,
        system_prompt: str,
        history: List[Dict[str, Any]],
        latest_user_message: str
    ) -> List[types.Content]:
        # Vertex AI SDK works best with alternating user/model roles.
        # We'll prepend the system prompt to the first user message.
        contents: List[types.Content] = []
        is_first_user_message = True

        for msg in history:
            text = msg.get("content", "")
            if not text:
                continue
            role = "user" if msg.get("sender") == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))
            if role == "user":
                is_first_user_message = False

        user_message = latest_user_message
        if is_first_user_message:
            user_message = f"{system_prompt}\n\n---\n\nUSER_MESSAGE:\n{latest_user_message}"

        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
        return contents

    def _build_dynamic_system_prompt(self, extracted_specs: Dict[str, Any]) -> str:
        """
        Builds the entire, state-aware system prompt based on the user's detailed instructions.
        """
        tracker_view = self.spec_tracker.evaluate(extracted_specs or {})
        missing_fields = tracker_view.get("missing_fields", [])
        
        # --- BASE PROMPT (Persona, Guidelines, Rules) ---
        base_prompt = """
你是一位「住宅室內裝修顧問＋報價風險審核專家」，服務對象是一般屋主（消費者）。
你的任務是：讀取使用者提供的報價單與補充資訊，透過對話一步一步釐清工程內容，最後產出一份結構完整、風險透明、方便比價的「新報價草稿」。

-------------------------
一、語言與互動風格
-------------------------
1. 全程使用「台灣繁體中文」，用清楚但不過度專業的說法，必要時再解釋專有名詞。
2. 每一輪對話，一次提出 1 個關鍵問題，讓使用者好回覆，不要一次丟一大堆。
3. 你要像現場丈量的設計師／統包主管一樣，邏輯清楚、誠實說明風險，不推銷特定產品。
4. 若資訊不足，不要硬估價，要明確說「需要先確認 XXX 才能給估算」，並用問題引導。

-------------------------
二、你內建的裝修 Guideline
-------------------------
【1. 施工順序視角】
你看工程時，腦中要有這個順序，檢查每一步有沒有在報價中被照顧到：
1. 拆除與保護工程
2. 水電與機電工程（電源、照明、插座、可能的排水）
3. 泥作／修補工程（防水、批土、找平）
4. 木作工程（隔間、天花、櫃體、床架等）
5. 油漆工程（底漆、面漆、特殊塗料）
6. 地坪工程（找平、防潮層、木地板／磁磚等）
7. 玻璃與門窗工程（如有）
8. 收尾與清潔（踢腳板、收邊、五金調整、清潔）
9. 工程管理與保固

【2. 法律／規範視角（僅用來提醒，不做法律解釋）】
根據《建築物室內裝修管理辦法》，以下四種行為在多數情況下需要申請室內裝修審查：
1. 固著於建築物構造體之天花板裝修
2. 固著於構造體之內部牆面裝修
3. 高度超過地板面 1.2 公尺之「固定隔屏」或兼作櫥櫃之隔屏裝修
4. 分間牆之變更
你的工作是標示「疑似涉及室內裝修審查」的地方，並提醒使用者：「這部分建議與設計師或合格技師確認是否需報審」。

-------------------------
三、錯誤避免與限制
-------------------------
1. 你不能假裝自己是有執照的建築師、技師或法律專業，只能做「風險提醒與溝通建議」。
2. 當使用者直接問「這樣報價算不算貴」，你可以用「市場大致區間」與「影響單價的因素」來回應，但要提醒他實價仍需以現場條件為準。
3. 任何估價數字都要清楚標註「為估算區間，非實際報價」。
"""

        # --- DYNAMIC TASK INSTRUCTION ---
        task_instruction = ""
        if not missing_fields:
            # All stages are complete, generate the final output
            task_instruction = """
-------------------------
四、當前任務：產出最終報告
-------------------------
所有資訊已收集完畢。請根據對話歷史，執行以下兩項任務：

任務一：產出「標準化的報價草稿」
嚴格遵循以下格式要求，以 Markdown 表格方式呈現。
- 報價項目要依「施工順序」排序。
- 將「原報價有寫」與「你建議補上的工項」都放進表格，並在「風險提示」欄標示來源（例如：「原報價已含」或「建議補列，避免日後追加」）。
- 欄位：工項編號, 分類, 子項目, 單位, 數量, 單價, 小計, 材料品牌／等級, 工法說明, 是否疑似需送審, 風險提示

任務二：產出「建議對設計師／統包發問」的問題清單
- 根據對話內容，生成一份條列式、好複製貼上的問題清單。
- 至少涵蓋：舊漆處理、壁癌處理、地板找平、清潔收尾、保固與追加方式。

完成以上兩項任務後，在訊息的最後，加上以下這句 CTA：
「如果你希望進一步確認現場狀況，我們可以根據這份報價內容，提供一次免費到府說明與丈量服務。需要我幫你預約嗎？」
"""
        else:
            next_stage = missing_fields[0] # Get the next stage to work on
            stage_id = next_stage['id']
            
            stage_prompts = {
                "stage_1_situation_purpose": """
-------------------------
四、當前任務：【階段 1：釐清屋況與目的】
-------------------------
你的目標是釐清是新成屋、舊屋翻修、還是局部修繕，以及是自住／出租。
請根據對話歷史，向使用者提出下一個最關鍵的問題來收集資訊。一次只問一題。
範例問題：
- 「這份報價是針對整個房子，還是某幾個空間？」
- 「這個空間是自住、出租，還是其他用途？」
- 「你這次主要是想解決什麼問題？（例如：牆面舊、壁癌、想換地板…）」
""",
                "stage_2_scope_condition": """
-------------------------
四、當前任務：【階段 2：釐清施工範圍與現況】
-------------------------
你的目標是知道哪些空間會施工、牆面狀況、地板狀況、櫃體保留與否。
請根據對話歷史，向使用者提出下一個最關鍵的問題來收集資訊。一次只問一題。
範例問題：
- 「這次施工會包含哪些空間？（例如：主臥、書房、小孩房…）」
- 「牆面目前狀況大概是：完整舊漆？裂縫？壁癌？有貼壁紙？」
- 「地板會保留還是拆掉重做？櫃體會保留嗎？需不要做保護？」
""",
                "stage_3_material_style": """
-------------------------
四、當前任務：【階段 3：釐清材質與風格】
-------------------------
你的目標是瞭解油漆／地板／燈具的方向，用來推薦工項與風險。
請用消費者的角度提問，避免客戶不清楚。一次只問一題。
範例問題：
- 「牆面你比較在意的是：耐髒好清潔？還是設計感（例如特殊漆、跳色）？」
- 「地板你有鎖定超耐磨木地板、SPC，還是還沒決定？」
- 「有預計更換燈具或開關插座嗎？（例如換成隱藏式面板）」
""",
                "stage_4_hidden_risks": """
-------------------------
四、當前任務：【階段 4：釐清隱藏工程與風險】
-------------------------
你的目標是主動把「最常被忽略、施工後才加價」的地方問出來。
請根據對話歷史，向使用者提出下一個最關鍵的問題來收集資訊。一次只問一題。
範例問題：
- 拆除後的找平與修補：「如果拆掉舊地板或磁磚，地面高低差太大，能接受另外按實際狀況報價，還是希望先估一個預算上限？」
- 壁癌與滲水：「有沒有哪幾面牆之前就有壁癌或滲水的記錄？」
- 清潔與收尾：「你期待完工時是『可以直接搬進來』，還是可以接受自己再整理一次？」
""",
                "stage_5_budget_decision": """
-------------------------
四、當前任務：【階段 5：確認預算感與決策方式】
-------------------------
你的目標是了解使用者的預算區間與重視的優先順序（價格、品質、風格）。
請根據對話歷史，向使用者提出下一個最關鍵的問題來收集資訊。一次只問一題。
範例問題：
- 「你心裡有沒有一個大概的預算範圍？比如說 XX–XX 萬？」
- 「在這次工程裡，價格、施工品質、設計感，三個排列順序會是？」
"""
            }
            task_instruction = stage_prompts.get(stage_id, "請繼續與使用者對話，收集裝修相關資訊。")

        return f"{base_prompt}\n{task_instruction}"

    async def _extract_specifications(self, conversation_history: list, current_specs: dict) -> Dict[str, Any]:
        """
        Evaluates if the current conversation stage is complete.
        """
        if not self.enabled or not self.model:
            return {}

        tracker_view = self.spec_tracker.evaluate(current_specs or {})
        missing_fields = tracker_view.get("missing_fields", [])
        if not missing_fields:
            return {} # All done

        next_stage = missing_fields[0]
        stage_id = next_stage['id']
        stage_label = next_stage['label']

        history_text = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in conversation_history])

        prompt = f"""
        **Role:** You are an expert AI assistant reviewing a conversation about interior renovation.
        **Goal:** Determine if the user has provided enough information to complete the current conversation stage.

        **Current Stage to Evaluate:** "{stage_label}" ({stage_id})

        **Conversation History:**
        ---
        {history_text}
        ---

        **Question:** Based *only* on the conversation history provided, has the user given a clear and sufficient answer to satisfy the goal of the "{stage_label}" stage?

        **Answer format:** Respond with a single JSON object with one key: `is_complete`. The value should be `true` or `false`.
        - `true`: If the user's response directly and adequately addresses the core question of the stage.
        - `false`: If the user's response is vague, incomplete, off-topic, or if the AI hasn't even asked the relevant question yet.

        **JSON Response:**
        """

        try:
            response = await self.model.generate_content_async(prompt)
            
            # Extract JSON from the response text
            json_str_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if not json_str_match:
                logger.warning(f"Spec extraction: No JSON found in response for stage {stage_id}.")
                return {}

            result = json.loads(json_str_match.group(0))
            if result.get("is_complete") is True:
                logger.info(f"Stage '{stage_id}' has been completed.")
                return {stage_id: True} # Return the flag to mark stage as complete

        except (json.JSONDecodeError, google_exceptions.GoogleAPICallError, Exception) as e:
            logger.error(f"Error during specification extraction for stage {stage_id}: {e}")

        return {}

    async def generate_response_stream(
        self,
        message: str,
        conversation_history: list,
        context: dict
    ) -> AsyncGenerator[Tuple[str, Optional[Dict[str, Any]]], None]:
        if not self.enabled or not self.model:
            yield ("抱歉，AI 服務目前無法使用。", None)
            return

        try:
            extracted_specs = context.get("extracted_specs", {})
            system_prompt = self._build_dynamic_system_prompt(extracted_specs)

            # Summarization logic is placeholder, using full history for now
            processed_history = await self._get_summarized_history(conversation_history, MAX_HISTORY_TOKENS)

            contents = self._build_gemini_contents(system_prompt, processed_history, message)

            response_stream = await self.model.generate_content_async(contents=contents, stream=True)

            full_response = ""
            async for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    full_response += chunk.text
                    yield (chunk.text, None)
            
            # After streaming, evaluate if the stage is complete
            updated_history = conversation_history + [
                {"sender": "user", "content": message},
                {"sender": "agent", "content": full_response}
            ]
            extracted = await self._extract_specifications(updated_history, extracted_specs)

            if extracted:
                yield ("", extracted)

        except google_exceptions.GoogleAPICallError as e:
            logger.error(f"Google API Call Error in generate_response_stream: {e}")
            yield (f"抱歉，與 AI 服務的通訊發生錯誤: {e.message}", None)
        except Exception as e:
            logger.error(f"Generic Error in generate_response_stream: {e}", exc_info=True)
            yield ("抱歉，AI 服務發生未預期的錯誤。", None)

# Singleton instance
gemini_service = GeminiLLMService()
