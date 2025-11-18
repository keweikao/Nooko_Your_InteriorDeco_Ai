"""
Client Manager Agent V2 - 以消費者視角設計的智能問卷系統

核心設計理念：
1. 從「生活需求」出發，而非「工程項目」
2. 支援局部裝修的彈性分流
3. 用視覺化引導，而非專業術語
4. Agent 自動將需求翻譯成工程規格
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class QuestionCategory(str, Enum):
    """以消費者思考邏輯分類"""
    BASIC_INFO = "認識您"
    RENOVATION_SCOPE = "裝修範圍"
    LIFESTYLE_NEEDS = "生活需求"
    STYLE_PREFERENCE = "風格喜好"
    BUDGET_PLANNING = "預算規劃"
    SPACE_DETAILS = "空間細節"
    TIMELINE_CONDITIONS = "時程與條件"

class QuestionType(str, Enum):
    """問題類型"""
    SINGLE_CHOICE = "單選"
    MULTIPLE_CHOICE = "複選"
    TEXT_INPUT = "文字輸入"
    IMAGE_CHOICE = "圖片選擇"
    RANGE_SLIDER = "區間滑桿"
    CONDITIONAL = "條件式問題"  # 根據前面答案決定是否顯示

class VisualReference:
    """視覺化參考資料"""
    def __init__(
        self,
        image_url: str,
        title: str,
        description: str = "",
        price_indicator: str = ""  # 例如："$$"表示中等價位
    ):
        self.image_url = image_url
        self.title = title
        self.description = description
        self.price_indicator = price_indicator

class Question:
    """問題定義"""
    def __init__(
        self,
        id: str,
        category: QuestionCategory,
        question_text: str,
        question_type: QuestionType = QuestionType.SINGLE_CHOICE,
        options: Optional[List[str]] = None,
        visual_references: Optional[List[VisualReference]] = None,

        # 消費者友善設計
        why_we_ask: str = "",  # 為什麼問這個問題（透明化）
        helper_text: str = "",  # 輔助說明
        placeholder: str = "",  # 輸入框提示

        # 同理心與彈性
        empathy_message: str = "",
        can_skip: bool = False,
        skip_suggestion: str = "",
        default_for_partial: bool = False,  # 局部裝修時是否預設跳過

        # 條件邏輯
        show_if: Optional[Dict[str, Any]] = None,  # 顯示條件 {"question_id": "expected_answer"}
        triggers_follow_up: Optional[List[str]] = None,  # 觸發後續問題ID

        # Agent 專業知識映射
        maps_to_construction: List[str] = None,  # 對應到哪些工程項目
        professional_notes: str = ""  # Agent 內部專業註解
    ):
        self.id = id
        self.category = category
        self.question_text = question_text
        self.question_type = question_type
        self.options = options or []
        self.visual_references = visual_references or []
        self.why_we_ask = why_we_ask
        self.helper_text = helper_text
        self.placeholder = placeholder
        self.empathy_message = empathy_message
        self.can_skip = can_skip
        self.skip_suggestion = skip_suggestion
        self.default_for_partial = default_for_partial
        self.show_if = show_if or {}
        self.triggers_follow_up = triggers_follow_up or []
        self.maps_to_construction = maps_to_construction or []
        self.professional_notes = professional_notes

class ClientManagerAgentV2:
    """
    智能客戶經理 Agent - 以消費者視角設計

    特色：
    1. 根據「裝修範圍」動態調整問卷
    2. 用「生活場景」問題取代「工程術語」
    3. 視覺化引導材質選擇
    4. Agent 自動翻譯成專業規格
    """

    def __init__(self):
        self.questions = self._initialize_questions()
        self.answers = {}
        self.renovation_scope = []  # 裝修範圍（動態）

    def _initialize_questions(self) -> List[Question]:
        """初始化問卷 - 以消費者視角設計"""

        questions = [
            # ========================================
            # 第一階段：認識您（6題）
            # ========================================

            Question(
                id="basic_001",
                category=QuestionCategory.BASIC_INFO,
                question_text="您好！我是您的專屬客戶經理。請問我該如何稱呼您呢？",
                question_type=QuestionType.TEXT_INPUT,
                placeholder="例如：陳先生、小美",
                why_we_ask="讓我們的服務更有溫度",
                empathy_message="很高興認識您！接下來我會問一些問題，幫助我們更了解您的需求。"
            ),

            Question(
                id="basic_002",
                category=QuestionCategory.BASIC_INFO,
                question_text="這次裝修的空間，您打算如何使用？",
                options=["自己住", "家人住", "出租", "短租（如Airbnb）", "辦公/工作室", "其他"],
                why_we_ask="使用目的會影響材料選擇和設計方向",
                empathy_message="不同的使用目的，我們會給您不同的建議。例如自住會注重舒適度，出租則會考慮耐用性和維護成本。"
            ),

            Question(
                id="basic_003",
                category=QuestionCategory.BASIC_INFO,
                question_text="會有哪些人經常使用這個空間？",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["我自己", "伴侶/配偶", "學齡前小孩", "國小到高中的孩子", "長輩", "寵物（貓狗）", "其他"],
                why_we_ask="家庭成員會影響空間規劃和安全考量",
                helper_text="可以複選",
                empathy_message="了解家庭成員，能幫我們設計更貼心的細節。例如有小孩會建議圓角設計，有長輩會注重防滑。"
            ),

            # ========================================
            # 第二階段：裝修範圍（關鍵分流點！）
            # ========================================

            Question(
                id="scope_001",
                category=QuestionCategory.RENOVATION_SCOPE,
                question_text="這次您想要裝修的是？",
                options=[
                    "整個家（全室裝修）",
                    "只有某幾個空間",
                    "只想局部翻新（例如換地板、重新油漆）",
                    "還沒決定，想聽建議"
                ],
                why_we_ask="這會決定我們後續詢問的重點",
                empathy_message="不用擔心，無論大小規模，我們都能協助。如果還沒確定範圍，我們也可以根據您的需求和預算給建議。",
                triggers_follow_up=["scope_002", "scope_003"]
            ),

            Question(
                id="scope_002",
                category=QuestionCategory.RENOVATION_SCOPE,
                question_text="請勾選這次要裝修的空間（可複選）",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "客廳/餐廳",
                    "主臥室",
                    "次臥/小孩房",
                    "書房/工作區",
                    "廚房",
                    "衛浴（主衛）",
                    "衛浴（客衛）",
                    "陽台",
                    "玄關/走廊",
                    "儲藏室"
                ],
                show_if={"scope_001": ["只有某幾個空間", "還沒決定，想聽建議"]},
                why_we_ask="確認裝修範圍，才能精準估價",
                helper_text="選擇您想要改造的空間"
            ),

            Question(
                id="scope_003",
                category=QuestionCategory.RENOVATION_SCOPE,
                question_text="這個空間大約多大呢？",
                options=[
                    "10坪以下（約30平方公尺）",
                    "10-20坪",
                    "20-30坪",
                    "30-40坪",
                    "40-50坪",
                    "50坪以上",
                    "不太確定"
                ],
                why_we_ask="坪數影響材料用量和預算估算",
                empathy_message="如果不確定實際坪數，可以先估個大概。我們會在丈量時確認精確數字。",
                can_skip=True,
                skip_suggestion="如果不確定也沒關係，我們丈量時會確認。"
            ),

            Question(
                id="scope_004",
                category=QuestionCategory.RENOVATION_SCOPE,
                question_text="這個空間目前的狀況是？",
                options=[
                    "全新屋（剛交屋，沒裝潢過）",
                    "5年內的裝潢，狀況還不錯",
                    "5-10年了，有些地方想更新",
                    "10年以上，很多地方都舊了",
                    "中古屋，需要重新整理",
                    "不確定，需要專業評估"
                ],
                why_we_ask="屋況會影響是否需要額外的修繕工程",
                empathy_message="老房子的基礎工程（水電、防水）會需要特別注意，這影響後續的施工規劃。",
                can_skip=True
            ),

            # ========================================
            # 第三階段：生活需求（而非工程項目！）
            # ========================================

            Question(
                id="lifestyle_001",
                category=QuestionCategory.LIFESTYLE_NEEDS,
                question_text="目前這個空間有什麼困擾您的地方？（可複選）",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "收納空間不夠，東西都塞不下",
                    "採光不好，白天也很暗",
                    "動線不順，走來走去很卡",
                    "廚房不好用（太小、設備舊、油煙問題）",
                    "浴室有漏水或發霉",
                    "隔音不好，會聽到外面聲音",
                    "冷氣效果差或電費很高",
                    "牆面髒舊、地板刮傷",
                    "沒有什麼大問題，只想更新風格",
                    "其他"
                ],
                why_we_ask="了解痛點，才能對症下藥",
                helper_text="選出您最困擾的問題，我們會優先解決",
                empathy_message="您說的這些問題，我們都遇過很多次。每個問題都有對應的解決方案，待會我會針對您的狀況提供建議。",
                maps_to_construction=["收納→木作/系統櫃", "採光→照明/窗戶", "動線→格局/拆除", "廚房→廚具/水電", "浴室→防水/磁磚", "隔音→隔音工程", "冷氣→機電", "牆面地板→油漆/地板"]
            ),

            Question(
                id="lifestyle_002",
                category=QuestionCategory.LIFESTYLE_NEEDS,
                question_text="在家最常做的事情是什麼？（可複選）",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "在家工作/視訊會議（需要獨立工作空間）",
                    "下廚做飯（廚房很重要）",
                    "在家運動/瑜伽（需要空間）",
                    "看電影/打電動（客廳影音設備）",
                    "閱讀/安靜休息",
                    "陪小孩玩耍/做功課",
                    "朋友常來作客（需要待客空間）",
                    "有收藏/興趣需要展示空間",
                    "其他"
                ],
                why_we_ask="生活習慣會影響空間配置",
                helper_text="了解您的生活型態，才能設計最適合的空間",
                maps_to_construction=["WFH→書房/隔音", "下廚→廚房設備", "運動→地板/隔音", "影音→客廳/照明/電源", "收藏→展示櫃/照明"]
            ),

            Question(
                id="lifestyle_003",
                category=QuestionCategory.LIFESTYLE_NEEDS,
                question_text="您最希望改善的是哪個空間？",
                options=[
                    "客廳 - 希望更舒適、更有質感",
                    "廚房 - 想要好用、好清理",
                    "主臥 - 想要放鬆、好睡",
                    "衛浴 - 想要乾淨、舒服",
                    "書房/工作區 - 需要專注、有效率",
                    "小孩房 - 安全、方便收納",
                    "每個空間都一樣重要",
                    "還沒想清楚"
                ],
                why_we_ask="如果預算有限，可以優先投資最重要的空間",
                can_skip=True
            ),

            # ========================================
            # 第四階段：風格喜好（用圖片，不用術語）
            # ========================================

            Question(
                id="style_001",
                category=QuestionCategory.STYLE_PREFERENCE,
                question_text="下面這些空間風格，哪一種最接近您的喜好？",
                question_type=QuestionType.IMAGE_CHOICE,
                options=[
                    "簡約明亮（北歐風）",
                    "溫暖木質（無印風）",
                    "現代俐落（現代風）",
                    "個性工業（工業風）",
                    "經典溫馨（美式風）",
                    "都不太喜歡，我想看其他的"
                ],
                visual_references=[
                    # 實際部署時這裡會是真實圖片URL
                    VisualReference(
                        image_url="placeholder_nordic.jpg",
                        title="簡約明亮（北歐風）",
                        description="白色系、木質地板、大量採光、簡單線條"
                    ),
                    VisualReference(
                        image_url="placeholder_muji.jpg",
                        title="溫暖木質（無印風）",
                        description="原木色、米白色、收納整齊、自然材質"
                    ),
                    VisualReference(
                        image_url="placeholder_modern.jpg",
                        title="現代俐落（現代風）",
                        description="黑白灰、俐落線條、金屬材質、簡潔設計"
                    ),
                    VisualReference(
                        image_url="placeholder_industrial.jpg",
                        title="個性工業（工業風）",
                        description="水泥、磚牆、鐵件、裸露管線、復古燈具"
                    ),
                    VisualReference(
                        image_url="placeholder_american.jpg",
                        title="經典溫馨（美式風）",
                        description="深木色、線板、古典燈具、溫暖色調"
                    )
                ],
                why_we_ask="風格決定了材料、顏色、家具的選擇方向",
                helper_text="如果都不太確定，也可以選「都不太喜歡」，我們再提供更多選項",
                empathy_message="風格沒有對錯，重要的是您住得舒服。如果還沒想法，我們可以先聊聊您喜歡的顏色、材質感覺。"
            ),

            Question(
                id="style_002",
                category=QuestionCategory.STYLE_PREFERENCE,
                question_text="您偏好的整體色調是？",
                options=[
                    "明亮白色系（白牆、淺色地板）",
                    "溫暖木質調（木地板、米白牆）",
                    "中性灰色調（灰牆、深色地板）",
                    "大膽深色系（深色牆面或地板）",
                    "還沒想法，想看建議"
                ],
                why_we_ask="色調影響油漆和地板的選擇"
            ),

            # ========================================
            # 第五階段：預算規劃（教育+引導）
            # ========================================

            Question(
                id="budget_001",
                category=QuestionCategory.BUDGET_PLANNING,
                question_text="為了提供最適合您的方案，想了解您的預算規劃。根據市場行情：\n\n• 基礎翻新：每坪 3-5萬（油漆、地板、基本櫃體）\n• 中等裝修：每坪 6-9萬（設計感、客製化）\n• 高品質裝修：每坪 10萬以上（進口建材、精緻工法）\n\n您的總預算大約是？",
                options=[
                    "30萬以內",
                    "30-50萬",
                    "50-80萬",
                    "80-120萬",
                    "120-200萬",
                    "200萬以上",
                    "希望先了解需要多少再決定"
                ],
                why_we_ask="預算幫助我們提供最符合您期待的方案",
                empathy_message="預算規劃很重要，我會根據您的預算提供最合適的材料和工法建議。如果預算有彈性，我也會提供不同等級的選擇讓您參考。",
                helper_text="如果還不確定預算，可以選「希望先了解需要多少再決定」"
            ),

            Question(
                id="budget_002",
                category=QuestionCategory.BUDGET_PLANNING,
                question_text="這個預算是否包含以下項目？（可複選）",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "大型家電（冰箱、洗衣機、冷氣）",
                    "活動家具（沙發、床、餐桌椅）",
                    "軟裝佈置（窗簾、掛畫、抱枕、擺飾）",
                    "都不包含，純裝修工程"
                ],
                why_we_ask="釐清預算範圍，避免誤會",
                helper_text="很多人會把家電家具算進總預算，這裡幫您分清楚"
            ),

            Question(
                id="budget_003",
                category=QuestionCategory.BUDGET_PLANNING,
                question_text="如果有特別想投資的項目，請告訴我（可複選）",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "廚房設備要好用、好清理",
                    "衛浴要舒適、高品質",
                    "主臥要特別用心",
                    "收納空間要夠、要聰明",
                    "客廳要有設計感",
                    "地板要耐用、好保養",
                    "照明要舒服、有氛圍",
                    "沒有特別偏好，平均分配",
                    "其他"
                ],
                why_we_ask="了解優先順序，預算配置更聰明",
                can_skip=True,
                empathy_message="預算有限是正常的，我們會幫您把錢花在刀口上。"
            ),

            Question(
                id="budget_004",
                category=QuestionCategory.BUDGET_PLANNING,
                question_text="關於品質、美感、預算三者，您的優先順序是？",
                options=[
                    "品質第一（寧願少做一點，但做好）",
                    "美感優先（希望有設計感，質感到位）",
                    "預算控制最重要（CP值高、經濟實惠）",
                    "品質和美感都重要（預算可以配合）",
                    "需要您的建議"
                ],
                why_we_ask="這會影響材料和工法的選擇方向",
                empathy_message="沒有絕對的對錯，了解您的優先順序，我才能提供最適合的建議。"
            ),

            # ========================================
            # 第六階段：空間細節（條件式展開，只問相關的）
            # ========================================

            # --- 廚房細節（只有選了廚房才問）---
            Question(
                id="kitchen_001",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="關於廚房，您希望做到什麼程度？",
                options=[
                    "整個打掉重做（櫥櫃、檯面、設備全換）",
                    "更換檯面和水槽",
                    "只換廚具設備（爐具、抽油煙機）",
                    "重新油漆和整理就好",
                    "需要建議"
                ],
                show_if={"scope_002": ["廚房"]},
                why_we_ask="廚房工程費用差異大，確認需求很重要",
                default_for_partial=True
            ),

            # --- 衛浴細節（只有選了衛浴才問）---
            Question(
                id="bathroom_001",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="衛浴有沒有漏水、發霉、排水不良的問題？",
                options=[
                    "有漏水問題",
                    "有發霉或壁癌",
                    "排水很慢或會堵塞",
                    "都沒有，狀況良好",
                    "不確定，需要檢查"
                ],
                show_if={"scope_002": ["衛浴（主衛）", "衛浴（客衛）"]},
                why_we_ask="衛浴問題需要優先處理防水和排水",
                empathy_message="衛浴問題如果不處理，之後會越來越麻煩，建議優先解決。",
                maps_to_construction=["漏水→防水工程", "發霉→防水+通風", "排水→水電管線"]
            ),

            Question(
                id="bathroom_002",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="衛浴您想做到什麼程度？",
                options=[
                    "全部打掉重做（含防水、磁磚、衛浴設備）",
                    "更新衛浴設備（馬桶、洗手台、淋浴設備）",
                    "重新貼磁磚和做防水",
                    "簡單整理就好",
                    "需要建議"
                ],
                show_if={"scope_002": ["衛浴（主衛）", "衛浴（客衛）"]},
                why_we_ask="衛浴整修範圍影響預算很大"
            ),

            # --- 地板（所有空間都可能需要）---
            Question(
                id="floor_001",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="地板您想怎麼處理？",
                options=[
                    "全部重做",
                    "保留原本地板",
                    "部分區域更換",
                    "還沒想好"
                ],
                why_we_ask="地板工程會影響整體預算和工期",
                triggers_follow_up=["floor_002"]
            ),

            Question(
                id="floor_002",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="您比較喜歡哪種地板的感覺？（用圖片選擇）",
                question_type=QuestionType.IMAGE_CHOICE,
                options=[
                    "溫暖木地板",
                    "明亮磁磚",
                    "質感石紋磚",
                    "其他/不確定"
                ],
                visual_references=[
                    VisualReference(
                        image_url="placeholder_wood_floor.jpg",
                        title="溫暖木地板",
                        description="觸感溫暖、適合臥室客廳",
                        price_indicator="$$-$$$"
                    ),
                    VisualReference(
                        image_url="placeholder_tile_floor.jpg",
                        title="明亮磁磚",
                        description="好清潔、適合廚房衛浴",
                        price_indicator="$-$$"
                    ),
                    VisualReference(
                        image_url="placeholder_stone_floor.jpg",
                        title="質感石紋磚",
                        description="耐用大氣、適合客廳餐廳",
                        price_indicator="$$-$$$$"
                    )
                ],
                show_if={"floor_001": ["全部重做", "部分區域更換"]},
                helper_text="不用擔心專業名詞，選您喜歡的感覺就好",
                empathy_message="地板的選擇會影響整個家的感覺。木地板溫暖但需要保養，磁磚耐用但較冷硬，各有優缺點。",
                can_skip=True,
                skip_suggestion="如果還沒想法，我們會在丈量時帶樣品給您參考。",
                professional_notes="根據選擇建議：木地板→超耐磨木地板/海島型/實木；磁磚→拋光磚/霧面磚；需要追問：直鋪/打底/架高"
            ),

            # --- 牆面與油漆 ---
            Question(
                id="paint_001",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="牆面和天花板需要重新處理嗎？",
                options=[
                    "需要，牆面有髒污、裂痕或掉漆",
                    "需要，想換個顏色或風格",
                    "狀況還好，可以保留",
                    "不確定，需要現場看"
                ],
                why_we_ask="油漆是改變空間最快的方式",
                triggers_follow_up=["paint_002"]
            ),

            Question(
                id="paint_002",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="關於油漆品質，您的想法是？",
                options=[
                    "要好一點的（無甲醛、防霉、品牌漆）",
                    "一般品質就好（經濟實惠）",
                    "需要建議（不知道差在哪）"
                ],
                show_if={"paint_001": ["需要，牆面有髒污、裂痕或掉漆", "需要，想換個顏色或風格"]},
                why_we_ask="油漆品質影響健康和耐用度",
                helper_text="好的油漆（如ICI、得利）比一般漆貴約20-30%，但比較環保、耐用",
                empathy_message="如果家裡有小孩或長輩，建議用好一點的環保漆。如果是出租，一般漆就夠用了。",
                can_skip=True,
                professional_notes="根據選擇建議品牌和價位：高階→ICI約1500/坪、Benjamin約3200/坪；中階→得利、虹牌；經濟→青葉"
            ),

            # --- 收納需求 ---
            Question(
                id="storage_001",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="收納空間目前夠用嗎？",
                options=[
                    "完全不夠，東西到處堆",
                    "勉強夠用，但想更有系統",
                    "目前足夠",
                    "不確定，想聽建議"
                ],
                why_we_ask="收納規劃影響木作和系統櫃的需求",
                triggers_follow_up=["storage_002"]
            ),

            Question(
                id="storage_002",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="您希望增加哪些收納？（可複選）",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "衣櫃（臥室收納）",
                    "電視櫃/展示櫃（客廳）",
                    "餐櫃/電器櫃（餐廳廚房）",
                    "書櫃/書桌（書房）",
                    "鞋櫃/儲物櫃（玄關）",
                    "雜物儲藏空間",
                    "其他"
                ],
                show_if={"storage_001": ["完全不夠，東西到處堆", "勉強夠用，但想更有系統"]},
                why_we_ask="確認收納需求，才能規劃櫃體",
                maps_to_construction=["系統櫃 vs 木作櫃體"]
            ),

            # --- 照明 ---
            Question(
                id="lighting_001",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="空間的採光和照明如何？",
                options=[
                    "白天也很暗，採光不好",
                    "採光還可以，但晚上燈光不夠",
                    "照明足夠，只是想更有氛圍",
                    "目前滿意"
                ],
                why_we_ask="照明影響生活品質和空間感",
                empathy_message="好的照明設計可以讓空間看起來更大、更舒服。如果採光不好，我們可以用燈光來補強。",
                triggers_follow_up=["lighting_002"]
            ),

            Question(
                id="lighting_002",
                category=QuestionCategory.SPACE_DETAILS,
                question_text="您希望照明達到什麼效果？（可複選）",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "明亮實用（主要照明加強）",
                    "有氣氛（間接照明、調光）",
                    "分區照明（閱讀、用餐、休息不同需求）",
                    "省電節能（LED燈具）",
                    "需要建議"
                ],
                show_if={"lighting_001": ["白天也很暗，採光不好", "採光還可以，但晚上燈光不夠", "照明足夠，只是想更有氛圍"]},
                why_we_ask="照明規劃會影響電路配置",
                maps_to_construction=["水電工程→迴路規劃", "木作→間接照明", "燈具選擇"]
            ),

            # ========================================
            # 第七階段：時程與條件
            # ========================================

            Question(
                id="timeline_001",
                category=QuestionCategory.TIMELINE_CONDITIONS,
                question_text="您希望什麼時候完工？",
                options=[
                    "很急，1個月內",
                    "2-3個月內",
                    "3-6個月都可以",
                    "時間充裕，配合您的安排",
                    "還沒決定"
                ],
                why_we_ask="工期影響工班安排和成本",
                empathy_message="如果時間很趕，我們會優先安排，但可能會有趕工費用。如果時間充裕，我們可以幫您談到更好的價格。"
            ),

            Question(
                id="timeline_002",
                category=QuestionCategory.TIMELINE_CONDITIONS,
                question_text="施工期間，您會住在這裡嗎？",
                options=[
                    "會，會繼續住",
                    "不會，會搬出去",
                    "還沒決定"
                ],
                why_we_ask="如果繼續住，會影響施工時間和方式",
                helper_text="如果繼續住，工班通常只能白天施工，工期會拉長一些"
            ),

            Question(
                id="timeline_003",
                category=QuestionCategory.TIMELINE_CONDITIONS,
                question_text="有沒有確認過社區管理規定？（施工時間、垃圾清運、電梯使用）",
                options=[
                    "有確認過，沒問題",
                    "還沒確認，需要協助",
                    "不確定要確認什麼"
                ],
                why_we_ask="社區規定會影響施工安排",
                empathy_message="很多社區有施工時間限制（例如平日9-5點），也可能要求保護電梯、公共區域。我們會協助您確認這些細節。",
                can_skip=True,
                skip_suggestion="這個我們會在簽約前協助您確認。"
            ),

            # ========================================
            # 第八階段：既有報價檢查（如果有上傳）
            # ========================================

            Question(
                id="quote_001",
                category=QuestionCategory.TIMELINE_CONDITIONS,
                question_text="您的報價單有沒有以下容易被遺漏的項目？（可複選）",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "垃圾清運費（明確金額）",
                    "施工保護費（電梯、公共區域、地板）",
                    "每日清潔費",
                    "拆除後的泥作修補",
                    "管線測試費（水電壓力測試）",
                    "監工費用",
                    "保固條款",
                    "我沒有報價單",
                    "不確定，需要幫我檢查"
                ],
                why_we_ask="這些是最常被遺漏或標示不清的項目",
                empathy_message="很多報價單會把這些項目標示為「贈送」或根本不列出來，後續容易產生爭議。我們會幫您仔細檢查。",
                helper_text="如果您有上傳報價單，我們會特別注意這些細節"
            ),

            # ========================================
            # 最後：確認與總結
            # ========================================

            Question(
                id="final_001",
                category=QuestionCategory.TIMELINE_CONDITIONS,
                question_text="最後，有沒有什麼特別想告訴我們的？或是特別在意的細節？",
                question_type=QuestionType.TEXT_INPUT,
                placeholder="例如：對環保材料特別重視、家裡有過敏兒、希望保留某個舊家具等等",
                why_we_ask="這些細節能讓我們的建議更貼近您的需求",
                can_skip=True,
                empathy_message="謝謝您耐心回答這些問題！接下來我會整理您的需求，並準備專業的分析和建議。"
            )
        ]

        return questions

    def get_next_question(self, current_answers: Dict[str, Any]) -> Optional[Question]:
        """
        智能取得下一題（根據已回答的答案決定）

        核心邏輯：
        1. 檢查 show_if 條件
        2. 檢查 default_for_partial（局部裝修自動跳過）
        3. 支援動態分流
        """
        self.answers = current_answers

        for question in self.questions:
            # 已經回答過，跳過
            if question.id in self.answers:
                continue

            # 檢查顯示條件
            if question.show_if:
                should_show = True
                for condition_q_id, expected_answers in question.show_if.items():
                    user_answer = self.answers.get(condition_q_id)
                    if user_answer not in expected_answers:
                        should_show = False
                        break

                if not should_show:
                    continue

            # 局部裝修跳過某些問題
            if question.default_for_partial:
                scope_answer = self.answers.get("scope_001")
                if scope_answer == "只想局部翻新（例如換地板、重新油漆）":
                    continue

            # 這就是下一題
            return question

        # 沒有下一題了
        return None

    def translate_to_construction_spec(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent 的專業能力：將消費者的回答翻譯成專業工程規格

        這是 Agent 1 的核心價值！
        """
        spec = {
            "renovation_scope": [],
            "construction_items": {},
            "budget_allocation": {},
            "material_suggestions": {},
            "risk_alerts": [],
            "professional_recommendations": []
        }

        # 範例：從生活需求推導工程項目
        lifestyle_needs = answers.get("lifestyle_001", [])

        if "收納空間不夠，東西都塞不下" in lifestyle_needs:
            spec["construction_items"]["storage"] = {
                "required": True,
                "options": ["系統櫃", "木作櫃體", "訂製收納"],
                "priority": "high",
                "estimated_budget": "依坪數和材質，約20-40萬"
            }
            spec["professional_recommendations"].append(
                "根據您的收納需求，建議優先規劃：\n"
                "1. 玄關鞋櫃（建議深度35-40cm）\n"
                "2. 主臥衣櫃（建議至少一面牆）\n"
                "3. 客廳展示收納櫃"
            )

        if "浴室有漏水或發霉" in lifestyle_needs:
            spec["construction_items"]["waterproofing"] = {
                "required": True,
                "priority": "critical",
                "note": "必須優先處理，否則影響後續工程"
            }
            spec["risk_alerts"].append(
                "⚠️ 浴室漏水問題必須優先處理！\n"
                "建議工序：\n"
                "1. 拆除舊磁磚和防水層\n"
                "2. 重做防水（至少兩次）\n"
                "3. 48小時試水測試\n"
                "4. 確認無滲漏再貼磁磚"
            )

        if "廚房不好用" in lifestyle_needs:
            kitchen_detail = answers.get("kitchen_001")
            if kitchen_detail == "整個打掉重做（櫥櫃、檯面、設備全換）":
                spec["construction_items"]["kitchen"] = {
                    "scope": "full_renovation",
                    "includes": ["拆除", "水電管線", "櫥櫃", "檯面", "廚具設備"],
                    "estimated_budget": "依尺寸和設備，約15-40萬",
                    "duration": "約2-3週"
                }

        # 預算分配建議
        total_budget = answers.get("budget_001")
        priority_items = answers.get("budget_003", [])

        if total_budget and priority_items:
            spec["budget_allocation"] = self._suggest_budget_allocation(
                total_budget,
                priority_items,
                spec["construction_items"]
            )

        return spec

    def _suggest_budget_allocation(self, total_budget: str, priorities: List[str], construction_items: Dict) -> Dict:
        """預算分配建議"""
        # 這裡會有複雜的預算分配邏輯
        # 根據優先順序、必要工程、空間大小等因素
        return {
            "total": total_budget,
            "allocation": {
                "基礎工程（拆除、水電、防水）": "25-30%",
                "主要工程（泥作、木作、油漆）": "40-45%",
                "設備與材料（廚具、衛浴、地板）": "20-25%",
                "軟裝與雜項": "5-10%"
            },
            "priority_adjustment": "根據您特別重視的項目，建議調整配置..."
        }

    def generate_questionnaire_summary(self, answers: Dict[str, Any]) -> str:
        """生成問卷摘要（給客戶看的）"""
        summary = "# 您的裝修需求摘要\n\n"

        # 基本資訊
        name = answers.get("basic_001", "")
        purpose = answers.get("basic_002", "")
        summary += f"## 基本資訊\n"
        summary += f"- 稱呼：{name}\n"
        summary += f"- 使用目的：{purpose}\n\n"

        # 裝修範圍
        scope = answers.get("scope_001", "")
        spaces = answers.get("scope_002", [])
        summary += f"## 裝修範圍\n"
        summary += f"- 範圍：{scope}\n"
        if spaces:
            summary += f"- 空間：{', '.join(spaces)}\n\n"

        # 主要需求
        needs = answers.get("lifestyle_001", [])
        if needs:
            summary += f"## 主要需求\n"
            for need in needs:
                summary += f"- {need}\n"
            summary += "\n"

        # 風格偏好
        style = answers.get("style_001", "")
        if style:
            summary += f"## 風格偏好\n"
            summary += f"- {style}\n\n"

        # 預算
        budget = answers.get("budget_001", "")
        if budget:
            summary += f"## 預算規劃\n"
            summary += f"- 總預算：{budget}\n\n"

        summary += "---\n\n"
        summary += "接下來我會根據這些資訊，為您準備：\n"
        summary += "1. 詳細的工程規劃建議\n"
        summary += "2. 預算分配建議\n"
        summary += "3. 材料與工法選擇\n"
        summary += "4. 報價單分析（如果您有上傳）\n"

        return summary
