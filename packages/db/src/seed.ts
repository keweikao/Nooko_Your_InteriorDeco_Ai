/**
 * Seed script for House IQ - WBS Tags and Global Rules
 * Run with: bun run packages/db/src/seed.ts
 */
import "dotenv/config";
import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import { wbsTag, rule } from "./schema/house-iq";

const sql = neon(process.env.DATABASE_URL!);
const db = drizzle(sql);

// ─── WBS Tags (標準工項分類) ─────────────────────────────────────────────────

const wbsTags = [
  // 水電
  { code: "PLUMBING-WATER-MAIN", category: "水電", nameTw: "自來水管配管", description: "主水管配置" },
  { code: "PLUMBING-HOT-WATER", category: "水電", nameTw: "熱水管配管", description: "熱水管路配置" },
  { code: "PLUMBING-DRAIN", category: "水電", nameTw: "排水管配管", description: "排水管路配置" },
  { code: "KITCHEN-WATER-FILTER", category: "水電", nameTw: "廚下式濾水機", description: "廚房淨水設備安裝" },
  { code: "COUNTERTOP-DRILLING", category: "水電", nameTw: "流理臺洗洞", description: "檯面鑽孔加工" },
  { code: "ELECTRIC-PANEL", category: "水電", nameTw: "配電盤更換", description: "主配電盤更新" },
  { code: "ELECTRIC-CIRCUIT", category: "水電", nameTw: "迴路配線", description: "電力迴路配置" },
  { code: "ELECTRIC-OUTLET", category: "水電", nameTw: "插座安裝", description: "電源插座安裝" },
  { code: "ELECTRIC-SWITCH", category: "水電", nameTw: "開關安裝", description: "電燈開關安裝" },
  { code: "ELECTRIC-220V", category: "水電", nameTw: "220V 專用迴路", description: "冷氣/電熱水器專用迴路" },
  { code: "ELECTRIC-GROUND", category: "水電", nameTw: "接地線施工", description: "接地線配置" },
  { code: "WATER-HEATER-INSTALL", category: "水電", nameTw: "熱水器安裝", description: "電熱水器或瓦斯熱水器安裝" },
  { code: "BATHROOM-FAN", category: "水電", nameTw: "浴室抽風機", description: "浴室換氣扇安裝" },

  // 泥作
  { code: "TILE-FLOOR", category: "泥作", nameTw: "地磚鋪設", description: "地板磁磚施工" },
  { code: "TILE-WALL", category: "泥作", nameTw: "壁磚鋪設", description: "牆面磁磚施工" },
  { code: "LARGE-TILE-240CM", category: "泥作", nameTw: "大板磚鋪設（240cm）", description: "240cm 大板磁磚" },
  { code: "CRANE-FEE", category: "泥作", nameTw: "吊車費", description: "大型材料吊運費用" },
  { code: "TILE-WATERPROOF", category: "泥作", nameTw: "防水工程", description: "浴室/陽台防水施工" },
  { code: "TILE-DEMOLISH", category: "泥作", nameTw: "磁磚拆除", description: "舊有磁磚拆除" },
  { code: "WALL-PLASTER", category: "泥作", nameTw: "粉光打底", description: "牆面水泥粉光" },
  { code: "FLOOR-LEVEL", category: "泥作", nameTw: "地面整平", description: "地板水平整平" },
  { code: "THRESHOLD", category: "泥作", nameTw: "門檻石安裝", description: "浴室門檻石" },
  { code: "DRAIN-SLOPE", category: "泥作", nameTw: "洩水坡度", description: "浴室/陽台洩水坡度" },

  // 木作
  { code: "CABINET-SYSTEM", category: "木作", nameTw: "系統櫃", description: "系統櫥櫃製作" },
  { code: "CABINET-CUSTOM", category: "木作", nameTw: "木作櫃", description: "訂製木作櫥櫃" },
  { code: "CEILING-FLAT", category: "木作", nameTw: "平釘天花板", description: "平面天花板施工" },
  { code: "CEILING-INDIRECT", category: "木作", nameTw: "間接照明天花", description: "含燈槽天花板" },
  { code: "CEILING-MOLDING", category: "木作", nameTw: "天花板線板", description: "天花板裝飾線板" },
  { code: "PARTITION-WALL", category: "木作", nameTw: "隔間牆", description: "輕隔間施工" },
  { code: "DOOR-FRAME", category: "木作", nameTw: "門框安裝", description: "門框製作安裝" },
  { code: "DOOR-INSTALL", category: "木作", nameTw: "門片安裝", description: "門片製作安裝" },
  { code: "WOOD-FLOOR", category: "木作", nameTw: "木地板鋪設", description: "超耐磨/實木地板" },
  { code: "BASEBOARD", category: "木作", nameTw: "踢腳板", description: "踢腳板安裝" },
  { code: "WINDOW-SILL", category: "木作", nameTw: "窗台板", description: "窗台板安裝" },

  // 油漆
  { code: "PAINT-WALL", category: "油漆", nameTw: "牆面油漆", description: "牆面乳膠漆施工" },
  { code: "PAINT-CEILING", category: "油漆", nameTw: "天花板油漆", description: "天花板乳膠漆" },
  { code: "PAINT-PRIMER", category: "油漆", nameTw: "底漆批土", description: "批土打底上底漆" },
  { code: "PAINT-WOOD", category: "油漆", nameTw: "木作噴漆", description: "木作面噴漆處理" },
  { code: "PAINT-SPECIAL", category: "油漆", nameTw: "特殊漆", description: "珪藻土/藝術漆/礦物漆" },
  { code: "WALLPAPER", category: "油漆", nameTw: "壁紙", description: "壁紙施工" },

  // 拆除
  { code: "DEMOLISH-WALL", category: "拆除", nameTw: "牆面拆除", description: "隔間牆拆除" },
  { code: "DEMOLISH-CEILING", category: "拆除", nameTw: "天花板拆除", description: "舊天花板拆除" },
  { code: "DEMOLISH-FLOOR", category: "拆除", nameTw: "地板拆除", description: "舊地板拆除" },
  { code: "DEMOLISH-CABINET", category: "拆除", nameTw: "櫃體拆除", description: "舊櫃子拆除" },
  { code: "DEMOLISH-BATHROOM", category: "拆除", nameTw: "浴室拆除", description: "衛浴設備+磁磚全拆" },
  { code: "DEMOLISH-KITCHEN", category: "拆除", nameTw: "廚房拆除", description: "廚具+磁磚拆除" },
  { code: "WASTE-DISPOSAL", category: "拆除", nameTw: "廢棄物清運", description: "拆除廢料清運" },

  // 衛浴
  { code: "TOILET-INSTALL", category: "衛浴", nameTw: "馬桶安裝", description: "馬桶安裝配管" },
  { code: "VANITY-INSTALL", category: "衛浴", nameTw: "洗手台安裝", description: "面盆/洗手台安裝" },
  { code: "SHOWER-INSTALL", category: "衛浴", nameTw: "淋浴設備安裝", description: "花灑/淋浴柱安裝" },
  { code: "BATHTUB-INSTALL", category: "衛浴", nameTw: "浴缸安裝", description: "浴缸安裝" },
  { code: "SHOWER-DOOR", category: "衛浴", nameTw: "淋浴拉門", description: "玻璃淋浴門安裝" },
  { code: "BATHROOM-ACCESSORY", category: "衛浴", nameTw: "衛浴五金配件", description: "毛巾架/置物架等" },

  // 廚房
  { code: "KITCHEN-CABINET", category: "廚房", nameTw: "廚具安裝", description: "廚房櫥櫃安裝" },
  { code: "KITCHEN-COUNTERTOP", category: "廚房", nameTw: "檯面安裝", description: "廚房檯面施工" },
  { code: "KITCHEN-HOOD", category: "廚房", nameTw: "排油煙機", description: "排油煙機安裝" },
  { code: "KITCHEN-STOVE", category: "廚房", nameTw: "瓦斯爐安裝", description: "瓦斯爐安裝配管" },
  { code: "KITCHEN-SINK", category: "廚房", nameTw: "廚房水槽", description: "水槽安裝" },

  // 空調
  { code: "AC-INSTALL", category: "空調", nameTw: "冷氣安裝", description: "分離式冷氣安裝" },
  { code: "AC-DRAIN", category: "空調", nameTw: "冷氣排水管", description: "冷氣冷凝水排水" },
  { code: "AC-ELECTRIC", category: "空調", nameTw: "冷氣專用迴路", description: "冷氣 220V 電源" },
  { code: "AC-CONCEALED", category: "空調", nameTw: "冷媒管包覆", description: "冷媒管隱藏施工" },

  // 其他
  { code: "WINDOW-REPLACE", category: "其他", nameTw: "窗戶更換", description: "鋁窗/氣密窗更換" },
  { code: "CURTAIN-BOX", category: "其他", nameTw: "窗簾盒", description: "窗簾盒製作" },
  { code: "CURTAIN-INSTALL", category: "其他", nameTw: "窗簾安裝", description: "窗簾軌道+窗簾安裝" },
  { code: "LIGHTING-INSTALL", category: "其他", nameTw: "燈具安裝", description: "各式燈具安裝" },
  { code: "CLEAN-FINAL", category: "其他", nameTw: "完工清潔", description: "全室完工清潔" },
  { code: "PROTECTION-FLOOR", category: "其他", nameTw: "地板保護", description: "施工期間地板保護" },
  { code: "PROTECTION-ELEVATOR", category: "其他", nameTw: "電梯保護", description: "電梯內部保護" },
];

// ─── Global Rules (通用規則) ─────────────────────────────────────────────────

const globalRules = [
  // 水電相關
  {
    triggerWbs: "KITCHEN-WATER-FILTER",
    relatedWbs: "COUNTERTOP-DRILLING",
    ruleType: "dependency" as const,
    message: "安裝廚下式濾水機，是否需要流理臺洗洞？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "WATER-HEATER-INSTALL",
    relatedWbs: "ELECTRIC-220V",
    ruleType: "dependency" as const,
    message: "安裝電熱水器，是否需要 220V 專用迴路？",
    severity: "critical" as const,
  },
  {
    triggerWbs: "ELECTRIC-PANEL",
    relatedWbs: "ELECTRIC-GROUND",
    ruleType: "dependency" as const,
    message: "更換配電盤，是否需要接地線施工？",
    severity: "critical" as const,
  },
  {
    triggerWbs: "ELECTRIC-OUTLET",
    relatedWbs: "ELECTRIC-CIRCUIT",
    ruleType: "dependency" as const,
    message: "新增插座，是否需要增加迴路配線？",
    severity: "warning" as const,
  },

  // 泥作相關
  {
    triggerWbs: "LARGE-TILE-240CM",
    relatedWbs: "CRANE-FEE",
    ruleType: "dependency" as const,
    message: "使用 240cm 大板磚，是否需要吊車費？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "TILE-FLOOR",
    relatedWbs: "FLOOR-LEVEL",
    ruleType: "dependency" as const,
    message: "鋪設地磚前，是否需要地面整平？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "TILE-WALL",
    relatedWbs: "WALL-PLASTER",
    ruleType: "dependency" as const,
    message: "鋪設壁磚前，是否需要粉光打底？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "TILE-FLOOR",
    relatedWbs: "TILE-DEMOLISH",
    ruleType: "dependency" as const,
    message: "鋪設新地磚，是否需要先拆除舊磁磚？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "TILE-WATERPROOF",
    relatedWbs: "DRAIN-SLOPE",
    ruleType: "dependency" as const,
    message: "防水工程完成後，是否需要洩水坡度施工？",
    severity: "critical" as const,
  },
  {
    triggerWbs: "TILE-WATERPROOF",
    relatedWbs: "THRESHOLD",
    ruleType: "dependency" as const,
    message: "浴室防水工程，是否需要門檻石安裝？",
    severity: "warning" as const,
  },

  // 木作相關
  {
    triggerWbs: "CEILING-INDIRECT",
    relatedWbs: "LIGHTING-INSTALL",
    ruleType: "dependency" as const,
    message: "間接照明天花板，是否需要燈具安裝？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "CEILING-FLAT",
    relatedWbs: "PAINT-CEILING",
    ruleType: "dependency" as const,
    message: "施作天花板後，是否需要天花板油漆？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "PARTITION-WALL",
    relatedWbs: "PAINT-WALL",
    ruleType: "dependency" as const,
    message: "新做隔間牆後，是否需要牆面油漆？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "CABINET-CUSTOM",
    relatedWbs: "PAINT-WOOD",
    ruleType: "dependency" as const,
    message: "木作櫃完成後，是否需要木作噴漆？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "WOOD-FLOOR",
    relatedWbs: "BASEBOARD",
    ruleType: "dependency" as const,
    message: "鋪設木地板，是否需要踢腳板？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "DOOR-FRAME",
    relatedWbs: "DOOR-INSTALL",
    ruleType: "dependency" as const,
    message: "安裝門框後，是否需要門片安裝？",
    severity: "warning" as const,
  },

  // 油漆相關
  {
    triggerWbs: "PAINT-WALL",
    relatedWbs: "PAINT-PRIMER",
    ruleType: "dependency" as const,
    message: "牆面油漆前，是否需要底漆批土？",
    severity: "warning" as const,
  },

  // 拆除相關
  {
    triggerWbs: "DEMOLISH-WALL",
    relatedWbs: "WASTE-DISPOSAL",
    ruleType: "dependency" as const,
    message: "牆面拆除後，是否需要廢棄物清運？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "DEMOLISH-BATHROOM",
    relatedWbs: "WASTE-DISPOSAL",
    ruleType: "dependency" as const,
    message: "浴室拆除後，是否需要廢棄物清運？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "DEMOLISH-BATHROOM",
    relatedWbs: "TILE-WATERPROOF",
    ruleType: "dependency" as const,
    message: "浴室拆除後，是否需要重做防水工程？",
    severity: "critical" as const,
  },
  {
    triggerWbs: "DEMOLISH-BATHROOM",
    relatedWbs: "PLUMBING-DRAIN",
    ruleType: "dependency" as const,
    message: "浴室拆除後，是否需要重新配排水管？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "DEMOLISH-KITCHEN",
    relatedWbs: "WASTE-DISPOSAL",
    ruleType: "dependency" as const,
    message: "廚房拆除後，是否需要廢棄物清運？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "DEMOLISH-CEILING",
    relatedWbs: "WASTE-DISPOSAL",
    ruleType: "dependency" as const,
    message: "天花板拆除後，是否需要廢棄物清運？",
    severity: "warning" as const,
  },

  // 衛浴相關
  {
    triggerWbs: "TOILET-INSTALL",
    relatedWbs: "PLUMBING-DRAIN",
    ruleType: "dependency" as const,
    message: "安裝馬桶，是否需要排水管配管？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "SHOWER-INSTALL",
    relatedWbs: "TILE-WATERPROOF",
    ruleType: "dependency" as const,
    message: "安裝淋浴設備，是否已完成防水工程？",
    severity: "critical" as const,
  },
  {
    triggerWbs: "BATHTUB-INSTALL",
    relatedWbs: "PLUMBING-DRAIN",
    ruleType: "dependency" as const,
    message: "安裝浴缸，是否需要排水管配管？",
    severity: "warning" as const,
  },

  // 空調相關
  {
    triggerWbs: "AC-INSTALL",
    relatedWbs: "AC-ELECTRIC",
    ruleType: "dependency" as const,
    message: "安裝冷氣，是否需要冷氣專用迴路（220V）？",
    severity: "critical" as const,
  },
  {
    triggerWbs: "AC-INSTALL",
    relatedWbs: "AC-DRAIN",
    ruleType: "dependency" as const,
    message: "安裝冷氣，是否需要冷氣排水管？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "AC-INSTALL",
    relatedWbs: "AC-CONCEALED",
    ruleType: "dependency" as const,
    message: "安裝冷氣，是否需要冷媒管包覆（隱藏管線）？",
    severity: "warning" as const,
  },

  // 廚房相關
  {
    triggerWbs: "KITCHEN-CABINET",
    relatedWbs: "KITCHEN-COUNTERTOP",
    ruleType: "dependency" as const,
    message: "安裝廚具，是否需要檯面安裝？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "KITCHEN-STOVE",
    relatedWbs: "KITCHEN-HOOD",
    ruleType: "dependency" as const,
    message: "安裝瓦斯爐，是否需要排油煙機？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "KITCHEN-CABINET",
    relatedWbs: "KITCHEN-SINK",
    ruleType: "dependency" as const,
    message: "安裝廚具，是否需要水槽安裝？",
    severity: "warning" as const,
  },

  // 其他
  {
    triggerWbs: "WINDOW-REPLACE",
    relatedWbs: "CURTAIN-BOX",
    ruleType: "dependency" as const,
    message: "更換窗戶後，是否需要窗簾盒？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "CURTAIN-BOX",
    relatedWbs: "CURTAIN-INSTALL",
    ruleType: "dependency" as const,
    message: "安裝窗簾盒後，是否需要窗簾安裝？",
    severity: "warning" as const,
  },

  // 保護工程（施工前必做）
  {
    triggerWbs: "DEMOLISH-WALL",
    relatedWbs: "PROTECTION-FLOOR",
    ruleType: "dependency" as const,
    message: "進行拆除工程前，是否需要地板保護？",
    severity: "warning" as const,
  },
  {
    triggerWbs: "DEMOLISH-WALL",
    relatedWbs: "PROTECTION-ELEVATOR",
    ruleType: "dependency" as const,
    message: "進行拆除工程，是否需要電梯保護？",
    severity: "warning" as const,
  },

  // 完工清潔
  {
    triggerWbs: "PAINT-WALL",
    relatedWbs: "CLEAN-FINAL",
    ruleType: "dependency" as const,
    message: "油漆完工後，是否需要完工清潔？",
    severity: "warning" as const,
  },
];

async function seed() {
  console.log("Seeding WBS tags...");
  await db.insert(wbsTag).values(wbsTags).onConflictDoNothing();
  console.log(`  Inserted ${wbsTags.length} WBS tags`);

  console.log("Seeding global rules...");
  const rulesWithDefaults = globalRules.map((r) => ({
    ...r,
    scope: "global" as const,
    source: "manual" as const,
    isActive: true,
    confidence: 1.0,
  }));
  await db.insert(rule).values(rulesWithDefaults).onConflictDoNothing();
  console.log(`  Inserted ${globalRules.length} global rules`);

  console.log("Seed complete!");
}

seed().catch((err) => {
  console.error("Seed failed:", err);
  process.exit(1);
});
