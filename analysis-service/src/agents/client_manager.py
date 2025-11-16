"""
Client Manager Agent - 客戶經理 Agent

This agent serves as the primary interface between users and the interior design AI system.
It conducts structured interviews following the construction sequence to gather comprehensive
project requirements.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class QuestionCategory(str, Enum):
    """Categories following the construction sequence"""
    INITIAL_INFO = "基本資訊"
    SPACE_STATUS = "空間現況與使用目的"
    BUDGET_EXPECTATIONS = "預算與期望"
    DEMOLITION = "拆除與保護工程"
    WATERPROOFING = "防水工程"
    WATER_ELECTRIC = "水電工程"
    MECHANICAL = "機電整合"
    MASONRY = "泥作工程"
    TILE_STONE = "磁磚石材工程"
    WOODWORK = "木作工程"
    METAL = "金屬工程"
    PAINT = "油漆工程"
    CABINET_SYSTEM = "系統櫃與廚具"
    FLOOR = "地板工程"
    GLASS = "玻璃與鏡面"
    HARDWARE = "五金配件"
    DESIGN_STYLE = "設計與風格偏好"
    CONSTRUCTION_CONDITIONS = "施工與維護條件"
    MATERIAL_BRANDS = "材料與品牌選擇"
    COMPLETION = "驗收與保固"

class Question:
    """Represents a single question in the interview"""
    def __init__(
        self,
        id: str,
        category: QuestionCategory,
        question_text: str,
        options: Optional[List[str]] = None,
        requires_clarification: bool = False,
        follow_up_trigger: Optional[Dict[str, str]] = None,
        info_purpose: str = "",
        can_skip: bool = False,
        skip_suggestion: str = "",
        empathy_message: str = "",
        clarification_questions: Optional[List[str]] = None
    ):
        self.id = id
        self.category = category
        self.question_text = question_text
        self.options = options or []
        self.requires_clarification = requires_clarification
        self.follow_up_trigger = follow_up_trigger or {}
        self.info_purpose = info_purpose
        self.can_skip = can_skip  # 是否可以跳過此問題
        self.skip_suggestion = skip_suggestion  # 建議跳過時的說法
        self.empathy_message = empathy_message  # 同理心訊息
        self.clarification_questions = clarification_questions or []  # 追問選項

class ClientManagerAgent:
    """
    客戶經理 Agent - Manages the entire customer interaction flow

    Responsibilities:
    1. Welcome users and collect initial information (name, quote upload)
    2. Conduct structured interviews following construction sequence
    3. Generate style reference images during style discussion
    4. Compile comprehensive project brief for other agents
    5. Present final results to users
    """

    def __init__(self):
        self.questions = self._initialize_questions()
        self.current_question_index = 0

    def _initialize_questions(self) -> List[Question]:
        """Initialize all questions following the construction sequence and best practices"""

        questions = [
            # ===== 基本資訊 =====
            Question(
                id="basic_001",
                category=QuestionCategory.INITIAL_INFO,
                question_text="您好！我是您的專屬客戶經理。首先，請問我該如何稱呼您呢？",
                info_purpose="建立個人化服務體驗",
                empathy_message="很高興認識您！讓我們一起為您的家打造理想的樣貌。"
            ),

            # ===== 空間現況與使用目的 =====
            Question(
                id="space_001",
                category=QuestionCategory.SPACE_STATUS,
                question_text="請問這個空間目前的使用情況是什麼？",
                options=["自住", "出租", "短租", "家人使用", "其他"],
                info_purpose="決定工程預算取向（自住重品質，出租重耐用性）"
            ),

            Question(
                id="space_002",
                category=QuestionCategory.SPACE_STATUS,
                question_text="原先的裝潢做了多久？空間目前有沒有漏水、壁癌、或結構裂縫等問題？",
                options=["全新屋況，無問題", "5年內，狀況良好", "5-10年，有輕微問題", "10年以上，有明顯問題", "不確定，需要專業評估"],
                requires_clarification=True,
                info_purpose="評估是否需額外修繕工程與防水補強費",
                empathy_message="了解房屋狀況能幫我們更準確地評估預算，也能避免施工時才發現問題。",
                can_skip=True,
                skip_suggestion="如果您不太確定，沒關係！我們的設計師到現場丈量時會仔細檢查，給您專業建議。",
                clarification_questions=[
                    "浴室或廚房有發現漏水痕跡嗎？",
                    "牆面有潮濕或脫落的情況嗎？",
                    "您最擔心哪個區域的狀況？"
                ]
            ),

            Question(
                id="space_003",
                category=QuestionCategory.SPACE_STATUS,
                question_text="您有既有的平面圖或丈量圖嗎？",
                options=["有完整平面圖", "只有簡易草圖", "沒有任何圖面"],
                info_purpose="若無圖面，丈量工時需估入報價"
            ),

            Question(
                id="space_004",
                category=QuestionCategory.SPACE_STATUS,
                question_text="本次改裝的範圍到哪裡？",
                options=["只要油漆", "油漆+地板", "油漆+地板+櫃體", "全室裝修（包含水電、衛浴）", "其他"],
                info_purpose="劃清工程範圍，避免估價遺漏"
            ),

            # ===== 預算與期望 =====
            Question(
                id="budget_001",
                category=QuestionCategory.BUDGET_EXPECTATIONS,
                question_text="關於預算，我完全理解這是很實際的考量。您心中的預算區間大約是多少？",
                options=["50萬以內", "50-100萬", "100-200萬", "200萬以上", "希望先了解行情再決定"],
                info_purpose="決定報價深度與材質等級",
                empathy_message="預算規劃很重要，我會根據您的預算提供最合適的方案。如果預算有彈性，我也會提供不同等級的選擇讓您參考。",
                can_skip=False,
                clarification_questions=[
                    "這個預算是否包含家電和家具？",
                    "如果有特別想投資的項目（如廚房、主臥），可以讓我知道嗎？"
                ]
            ),

            Question(
                id="budget_002",
                category=QuestionCategory.BUDGET_EXPECTATIONS,
                question_text="施工期有沒有時間壓力？例如入住前或出租檔期？",
                options=["非常急（1個月內）", "有點趕（2-3個月）", "時間充裕（3個月以上）", "配合您的建議"],
                info_purpose="影響工期壓力與工班排程成本"
            ),

            Question(
                id="budget_003",
                category=QuestionCategory.BUDGET_EXPECTATIONS,
                question_text="對於品質、外觀、預算三者，您的優先順序是什麼？",
                options=["品質第一", "外觀美感優先", "預算控制最重要", "品質與美感並重", "需要建議"],
                info_purpose="建立溝通基準，避免後續糾紛"
            ),

            # ===== 設計與風格偏好 =====
            Question(
                id="design_001",
                category=QuestionCategory.DESIGN_STYLE,
                question_text="您想保留現有的風格還是全面更新？",
                options=["全面更新", "保留部分家具/裝潢", "微調即可"],
                info_purpose="若保留部分，影響施工順序與保護成本"
            ),

            Question(
                id="design_002",
                category=QuestionCategory.DESIGN_STYLE,
                question_text="您心中期待的風格是什麼？（可複選或描述）",
                options=["北歐風（簡約、明亮、木質感）", "現代風（簡潔線條、黑白灰）", "無印風（自然、純白、收納）",
                        "工業風（水泥、鐵件、磚牆）", "美式風（溫馨、木作、深色）", "混搭風", "其他/不確定"],
                info_purpose="幫助理解顏色、光線、質感方向，需搭配參考圖"
            ),

            Question(
                id="design_003",
                category=QuestionCategory.DESIGN_STYLE,
                question_text="是否希望同時改善照明或增加收納空間？",
                options=["需要加強照明", "需要增加收納", "兩者都需要", "目前足夠"],
                info_purpose="若需調整，報價需整合水電與木作"
            ),

            # ===== 拆除與保護工程 =====
            Question(
                id="demolition_001",
                category=QuestionCategory.DEMOLITION,
                question_text="現場需要拆除哪些項目？",
                options=["舊磁磚/地板", "舊天花板", "舊廚具/衛浴", "隔間牆", "全室拆除", "不需拆除"],
                info_purpose="確定拆除範圍與費用",
                empathy_message="拆除工程是裝修的第一步，做好規劃很重要。"
            ),

            Question(
                id="demolition_002",
                category=QuestionCategory.DEMOLITION,
                question_text="您的報價單有沒有明確標示「垃圾清運費」？這是很容易被遺漏的項目。",
                options=["報價已包含", "報價標示為「贈送」", "報價沒提到", "不確定"],
                info_purpose="確認清運費用歸屬，避免施工後才有爭議",
                empathy_message="垃圾清運費常常被遺漏或標示不清。如果是「贈送」，建議還是請業者明訂在合約中，才能避免後續糾紛。",
                can_skip=True,
                skip_suggestion="這個我們的設計師會在報價時特別確認，確保您的權益。",
                clarification_questions=[
                    "如果報價寫「贈送」，您希望我們建議業者改成明確收費項目嗎？（這樣後續才有保障）"
                ]
            ),

            Question(
                id="demolition_003",
                category=QuestionCategory.DEMOLITION,
                question_text="拆除後的現場保護和清潔，報價有包含嗎？",
                options=["有包含施工後保護與清潔", "只包含保護，不包含清潔", "都沒包含", "不確定"],
                info_purpose="確認是否含施工後保護、清潔，這會影響總價",
                empathy_message="施工保護（如電梯、公共區域）和每日清潔，都是容易被忽略但很重要的項目。",
                can_skip=True,
                skip_suggestion="我們會在報價中明確列出保護與清潔費用。"
            ),

            # ===== 防水工程 =====
            Question(
                id="waterproof_001",
                category=QuestionCategory.WATERPROOFING,
                question_text="浴室或廚房需要重做防水嗎？",
                options=["需要（浴室）", "需要（廚房）", "都需要", "不需要"],
                info_purpose="防水是隱蔽工程的重點項目"
            ),

            # ===== 水電工程 =====
            Question(
                id="electric_001",
                category=QuestionCategory.WATER_ELECTRIC,
                question_text="電路與給排水是否需要更新？（房齡超過10年建議更新）",
                options=["全部重拉", "部分更新", "維持現況", "需要評估建議"],
                info_purpose="老屋建議重拉電線與防漏測試"
            ),

            Question(
                id="electric_002",
                category=QuestionCategory.WATER_ELECTRIC,
                question_text="有沒有特殊的電器設備需要規劃？（如智能家居、烘衣機、洗碗機等）",
                info_purpose="特殊設備需預留電源與空間"
            ),

            # ===== 機電整合 =====
            Question(
                id="mechanical_001",
                category=QuestionCategory.MECHANICAL,
                question_text="冷氣、熱水器、排風系統是否需要更新或新增？",
                options=["全新規劃", "更換設備", "維持現有", "需要建議"],
                info_purpose="涉及天花板施工與管線配置"
            ),

            # ===== 泥作工程 =====
            Question(
                id="masonry_001",
                category=QuestionCategory.MASONRY,
                question_text="地面是否需要重新整平或加高？",
                options=["需要整平", "需要加高", "不需要"],
                info_purpose="影響後續地板工程"
            ),

            # ===== 磁磚石材 =====
            Question(
                id="tile_001",
                category=QuestionCategory.TILE_STONE,
                question_text="浴室、廚房的磁磚有特定喜好嗎？",
                options=["拋光石英磚", "霧面磚", "復古磚", "大理石紋", "交給設計師建議"],
                info_purpose="磁磚等級影響價格差異大"
            ),

            # ===== 木作工程 =====
            Question(
                id="wood_001",
                category=QuestionCategory.WOODWORK,
                question_text="天花板需要做造型還是平釘即可？",
                options=["造型天花板（含間接照明）", "平釘天花板", "不做天花板", "需要建議"],
                info_purpose="天花板固著於構造體，依法規需要報審",
                empathy_message="天花板如果固著於建築結構體，依《建築物室內裝修管理辦法》需要申請許可。我們會協助確認是否需要報審。"
            ),

            Question(
                id="wood_002",
                category=QuestionCategory.WOODWORK,
                question_text="報價單有沒有「贈送」的項目？（如床框、軌道等）",
                options=["有贈送項目", "沒有贈送項目", "不確定"],
                info_purpose="了解是否有贈送項目及其風險",
                empathy_message="「贈送」的東西聽起來很划算，但有個重點要特別注意：贈送的項目，您無法要求廠商完善或負責。如果是很重要的東西，建議還是改成「收費項目」，這樣後續才有義務幫您處理問題。",
                can_skip=False,
                clarification_questions=[
                    "哪些項目是贈送的？",
                    "這些贈送項目對您來說重要嗎？（如果重要，建議改成收費）"
                ]
            ),

            # ===== 系統櫃與廚具 =====
            Question(
                id="cabinet_001",
                category=QuestionCategory.CABINET_SYSTEM,
                question_text="系統櫃或廚具有品牌偏好嗎？",
                options=["指定品牌（如IKEA、綠的）", "重視環保板材（E0/E1）", "以預算為主", "需要建議"],
                info_purpose="系統櫃品牌與板材等級影響價格"
            ),

            # ===== 油漆工程 =====
            Question(
                id="paint_001",
                category=QuestionCategory.PAINT,
                question_text="您的報價單有標示油漆品牌嗎？不同品牌價差很大。",
                options=["有標示品牌", "沒有標示，只寫乳膠漆", "不確定"],
                info_purpose="油漆品牌會大幅影響價格，例如 ICI 約1500/坪、班傑明約3200/坪",
                empathy_message="油漆品牌的價差可以很大，了解品牌才能判斷報價是否合理。",
                can_skip=False,
                clarification_questions=[
                    "如果有標示，是哪個品牌？（如得利Dulux、ICI、虹牌、立邦、班傑明等）",
                    "您有偏好的品牌嗎？或是重視環保低VOC？"
                ]
            ),

            Question(
                id="paint_002",
                category=QuestionCategory.PAINT,
                question_text="油漆報價是用「坪數」還是「一式」計價？",
                options=["用坪數或平方米", "用一式（整間或整層）", "不確定"],
                info_purpose="「一式」計價難以跨廠商比價，坪數計價較透明",
                empathy_message="用「一式」計價的原因可能是：數量太少、工法複雜（如跳色、特殊工序）、或包含多項施工。但最好還是要求提供施工面積明細。",
                can_skip=True,
                skip_suggestion="我們會協助您取得更詳細的坪數與單價明細。",
                clarification_questions=[
                    "如果是「一式」，有包含哪些項目？（如跳色、地板收邊打silicon、保護等）",
                    "每間房間的施工面積（牆+天花）大約多少坪？"
                ]
            ),

            Question(
                id="paint_003",
                category=QuestionCategory.PAINT,
                question_text="油漆工法的細節，報價有說明嗎？（這會影響品質和價格）",
                options=["有詳細說明", "只寫「油漆」兩個字", "有部分說明", "不確定"],
                info_purpose="工法細節決定品質，如批土程度、底漆、面漆道數",
                empathy_message="油漆的價差很大原因之一就是「批土程度」。一般批土只處理凹洞，但「透批」是全室都批土。如果要求燈照無陰影，費用會更高。",
                can_skip=True,
                skip_suggestion="我們會在報價中明確標示工法細節，包括底漆、批土、面漆道數。",
                clarification_questions=[
                    "報價有提到「透批」（全室批土）嗎？",
                    "有說明批土標準嗎？（如一般平整或燈照無陰影）",
                    "有標示底漆幾道、面漆幾道嗎？"
                ]
            ),

            Question(
                id="paint_004",
                category=QuestionCategory.PAINT,
                question_text="如果您的房子有貼過壁紙，報價有包含壁紙與底膠的「完整去除」嗎？",
                options=["房子沒有壁紙", "有包含壁紙去除", "不確定是否完整去除", "報價沒提到"],
                info_purpose="壁紙去除不完整會造成後續脫落問題，不應用批土來掩蓋",
                empathy_message="壁紙去除很重要！底紙沒去乾淨的話，不能只用批土蓋過，會造成後續脫落。正確做法是完整去除壁紙和底膠，才能重新上漆。",
                can_skip=True,
                skip_suggestion="如果有壁紙，我們的師傅會確保完整去除，不會用批土掩蓋。"
            ),

            # ===== 地板工程 =====
            Question(
                id="floor_001",
                category=QuestionCategory.FLOOR,
                question_text="地板材質有什麼偏好？",
                options=["實木地板", "海島型木地板", "超耐磨木地板", "SPC石塑地板", "磁磚", "需要建議"],
                info_purpose="地板材質影響質感與預算"
            ),

            # ===== 施工條件 =====
            Question(
                id="construction_001",
                category=QuestionCategory.CONSTRUCTION_CONDITIONS,
                question_text="您的社區或大樓有特殊的施工規定嗎？",
                options=["有，社區管委會有規範", "沒有特殊規定", "不確定"],
                info_purpose="每個社區的自治管理辦法可能有不同規定",
                empathy_message="有些社區會規定陽台不能加裝鐵窗、陽台燈色不能更改（維持大樓外觀）、或限制施工時間等。了解這些規定可以避免施工後被要求拆除。",
                can_skip=True,
                skip_suggestion="我們會協助您向管委會確認相關施工規範。",
                clarification_questions=[
                    "社區對陽台有特殊規定嗎？（如不能加鐵窗、燈色限制等）",
                    "施工時間有限制嗎？（如只能平日、不能週末等）",
                    "需要向管委會申請施工許可嗎？"
                ]
            ),

            Question(
                id="construction_002",
                category=QuestionCategory.CONSTRUCTION_CONDITIONS,
                question_text="施工現場的出入與電梯狀況如何？",
                options=["有貨梯可用", "只有客梯", "需爬樓梯", "不確定"],
                info_purpose="決定搬運與工期成本",
                can_skip=True,
                skip_suggestion="這個我們的工班會提前確認。"
            ),

            Question(
                id="construction_003",
                category=QuestionCategory.CONSTRUCTION_CONDITIONS,
                question_text="會有其他廠商同步進場嗎？（如窗簾、冷氣、家具）",
                options=["會，需要協調", "不會，全部統包", "還沒確定"],
                info_purpose="避免工序打架與責任爭議"
            ),

            # ===== 驗收與保固 =====
            Question(
                id="completion_001",
                category=QuestionCategory.COMPLETION,
                question_text="期望工程結束後多久可以入住？",
                options=["立即入住", "通風1週", "通風2週以上", "配合工程建議"],
                info_purpose="決定油漆選用（水性vs油性乾燥期）"
            ),

            Question(
                id="completion_002",
                category=QuestionCategory.COMPLETION,
                question_text="是否希望提供每日施工照片紀錄？",
                options=["需要", "不需要", "重要階段即可"],
                info_purpose="建立信任與透明度"
            ),

            Question(
                id="completion_003",
                category=QuestionCategory.COMPLETION,
                question_text="對於保固條款，您最重視哪個項目？",
                options=["防水保固", "櫃體五金", "油漆修補", "整體保固", "需要了解標準"],
                info_purpose="工程契約條列化"
            ),
        ]

        return questions

    def get_welcome_message(self) -> str:
        """Generate welcome message"""
        return "歡迎來到 Nooko 裝潢 AI 夥伴！我是您的專屬客戶經理，將協助您分析報價單並了解您的裝潢需求。讓我們開始吧！"

    def get_next_question(self, context: Dict[str, Any]) -> Optional[Question]:
        """
        Get the next question based on current context and previous answers

        Args:
            context: Dictionary containing previous answers and state

        Returns:
            Next Question object or None if interview is complete
        """
        if self.current_question_index >= len(self.questions):
            return None

        question = self.questions[self.current_question_index]
        self.current_question_index += 1

        return question

    def process_answer(
        self,
        question_id: str,
        answer: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user's answer and update context

        Args:
            question_id: ID of the question being answered
            answer: User's answer
            context: Current conversation context

        Returns:
            Updated context with processed answer
        """
        # Store the answer
        context.setdefault("answers", {})[question_id] = answer

        # Find the question
        question = next((q for q in self.questions if q.id == question_id), None)

        if question and question.requires_clarification:
            # Check if we need to ask follow-up questions
            if answer in question.follow_up_trigger:
                context.setdefault("pending_follow_ups", []).append(
                    question.follow_up_trigger[answer]
                )

        # Check if we need to generate style reference images
        if question_id == "design_002" and answer:
            context["generate_style_images"] = True
            context["style_preference"] = answer

        return context

    def compile_project_brief(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile all collected information into a structured project brief
        for contractor and designer agents

        Args:
            context: Complete conversation context with all answers

        Returns:
            Structured project brief
        """
        answers = context.get("answers", {})

        # Extract key information
        user_profile = {
            "name": answers.get("basic_001", ""),
            "space_usage": answers.get("space_001", ""),
            "property_age": answers.get("space_002", ""),
            "has_floor_plan": answers.get("space_003", ""),
            "renovation_scope": answers.get("space_004", ""),
        }

        budget_info = {
            "budget_range": answers.get("budget_001", ""),
            "timeline_pressure": answers.get("budget_002", ""),
            "priority": answers.get("budget_003", ""),
        }

        style_preferences = {
            "keep_existing": answers.get("design_001", ""),
            "style": answers.get("design_002", ""),
            "lighting_storage": answers.get("design_003", ""),
        }

        construction_requirements = {
            category.value: {
                q.id: answers.get(q.id, "")
                for q in self.questions
                if q.category == category
            }
            for category in QuestionCategory
        }

        project_brief = {
            "project_id": context.get("project_id", ""),
            "user_profile": user_profile,
            "budget_info": budget_info,
            "style_preferences": style_preferences,
            "construction_requirements": construction_requirements,
            "original_quote_analysis": context.get("quote_analysis", {}),
            "compiled_at": datetime.utcnow().isoformat(),
        }

        return project_brief

    def generate_summary_message(self, project_brief: Dict[str, Any]) -> str:
        """
        Generate a friendly summary message for the user

        Args:
            project_brief: Compiled project brief

        Returns:
            Summary message string
        """
        user_name = project_brief["user_profile"].get("name", "")
        style = project_brief["style_preferences"].get("style", "")
        budget = project_brief["budget_info"].get("budget_range", "")

        message = f"""
{user_name}，感謝您提供這麼詳細的資訊！

根據您的需求，我已經為您整理出完整的專案簡報：
• 裝修風格：{style}
• 預算範圍：{budget}
• 工程範圍：{project_brief["user_profile"].get("renovation_scope", "")}

現在我會將這份資料交給我們的專業統包商和設計師團隊，他們將為您：
1. 產出詳細的規格報價單（包含可能遺漏的項目與風險評估）
2. 設計符合您風格的概念渲染圖

請稍候片刻，我們很快就會為您呈現專業的分析結果！
"""
        return message.strip()

    def should_generate_style_images(self, context: Dict[str, Any]) -> bool:
        """Check if we should generate style reference images"""
        return context.get("generate_style_images", False)

    def get_progress_percentage(self) -> int:
        """Calculate current progress percentage"""
        if len(self.questions) == 0:
            return 100
        return int((self.current_question_index / len(self.questions)) * 100)
