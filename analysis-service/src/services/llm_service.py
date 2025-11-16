import logging
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)

class MockLLMService:
    """
    A mock LLM service that simulates calls to a real language model like Gemini.
    This is used for local development without needing live API keys.
    """

    async def generate_response(self, prompt: str, context: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Simulates generating a response from an LLM.
        Can return a string for conversational responses or a dict for structured data.

        :param prompt: The prompt to send to the LLM.
        :param context: The context for the generation (e.g., conversation history).
        :return: A hardcoded, realistic response.
        """
        logger.info(f"--- MOCK LLM SERVICE CALLED ---")
        logger.info(f"Prompt: {prompt[:200]}...") # Log first 200 chars of prompt
        logger.info(f"-----------------------------")

        if "present the final quote" in prompt.lower():
            return (
                "感謝您的耐心等候！我們的設計師和專業統包商團隊已經為您準備好了初步的設計方案。\n\n"
                "**設計方面**，我們根據您喜愛的北歐風格，為您製作了一張概念渲染圖，您可以看到整體空間明亮、簡潔，並運用了大量的木質元素，希望能符合您的想像。\n\n"
                "**工程方面**，我們的統包商仔細評估了您的需求和屋況，擬定了一份詳細的規格報價單。其中，我們特別標示了幾個『建議項目』，例如全室電線更新和浴室防水加強，這些對於中古屋的居住安全和長期考量非常重要。\n\n"
                "請您參考下方的渲染圖和報價單，看看是否符合您的期待，或是有任何想要調整的地方，我們都可以隨時討論！"
            )
        elif "generate_quote" in prompt.lower():
            # Simulate generating a structured quote
            return {
                "source": "generated_by_contractor_agent",
                "total_price": 1450000.0,
                "line_items": [
                    {
                        "item_name": "全室電線重拉", "spec": "太平洋電纜 2.0mm 單芯線",
                        "quantity": 1, "unit": "式", "unit_price": 80000, "total_price": 80000,
                        "is_suggestion": True
                    },
                    {
                        "item_name": "浴室防水工程", "spec": "彈性水泥施作，高度 180cm",
                        "quantity": 1, "unit": "間", "unit_price": 25000, "total_price": 25000,
                        "is_suggestion": True
                    },
                    {
                        "item_name": "開放式廚房-拆除牆面", "spec": "含清運",
                        "quantity": 1, "unit": "式", "unit_price": 15000, "total_price": 15000,
                        "is_suggestion": False
                    },
                    {
                        "item_name": "超耐磨木地板", "spec": "Pergo 森系列",
                        "quantity": 20, "unit": "坪", "unit_price": 5500, "total_price": 110000,
                        "is_suggestion": False
                    }
                ]
            }
        elif "summarize" in prompt.lower():
            # Simulate summarizing the conversation into a ProjectBrief
            return {
                "project_id": context.get("project_id", "dummy_project_id"),
                "user_profile": {
                    "house_type": "中古屋",
                    "budget": "100-150萬",
                    "family_size": 2
                },
                "style_preferences": ["北歐風", "明亮", "木質"],
                "key_requirements": [
                    "需要一個開放式廚房",
                    "主臥室要有更衣間",
                    "浴室需要乾濕分離"
                ],
                "original_quote_analysis": {
                    "missing_items": ["全室電線重拉", "浴室防水工程"],
                    "total_price": 1200000
                }
            }
        elif "analyze" in prompt.lower():
            return (
                "感謝您提供報價單！我初步看了一下，有些細節想跟您請教。"
                "請問您這次裝修的是新成屋還是中古屋呢？這會影響到基礎工程的評估喔。"
            )
        else:
            return (
                "了解了。那關於風格方面，您有沒有特別喜歡的感覺呢？"
                "例如是喜歡簡約的無印風，還是溫暖的北歐風，或是有其他想法？"
            )

# Singleton instance
mock_llm_service = MockLLMService()
