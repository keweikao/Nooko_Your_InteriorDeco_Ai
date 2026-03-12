import { authClient } from "@/lib/auth-client";
import { trpc, queryClient } from "@/utils/trpc";
import { useMutation, useQuery } from "@tanstack/react-query";
import { createFileRoute, redirect, Link } from "@tanstack/react-router";
import { useState, useCallback } from "react";
import { Button } from "@my-better-t-app/ui/components/button";
import { Input } from "@my-better-t-app/ui/components/input";

export const Route = createFileRoute("/quotations/$quotationId")({
  component: QuotationEditorPage,
  beforeLoad: async () => {
    const session = await authClient.getSession();
    if (!session.data) {
      redirect({ to: "/login", throw: true });
    }
    return { session };
  },
});

type Alert = {
  ruleId: string;
  message: string;
  severity: "warning" | "critical";
  relatedWbs: string;
  scope: "global" | "company";
  source: "manual" | "ai_suggested" | "learned";
  confidence: number | null;
  triggerItemId: string;
  triggerItemName: string;
};

function QuotationEditorPage() {
  const { quotationId } = Route.useParams();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showAddItem, setShowAddItem] = useState(false);

  const quotation = useQuery(
    trpc.quotation.get.queryOptions({ id: quotationId }),
  );

  const wbsTags = useQuery(trpc.wbs.list.queryOptions());

  // Check all existing rules on load
  const rulesCheck = useQuery({
    ...trpc.rules.check.queryOptions({ quotationId }),
    enabled: !!quotation.data,
  });

  // Merge loaded alerts with new alerts from item additions
  const allAlerts = [
    ...alerts,
    ...(rulesCheck.data ?? []).filter(
      (a) => !alerts.some((existing) => existing.ruleId === a.ruleId),
    ),
  ];

  const invalidateQuotation = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: trpc.quotation.get.queryOptions({ id: quotationId }).queryKey,
    });
    queryClient.invalidateQueries({
      queryKey: trpc.rules.check.queryOptions({ quotationId }).queryKey,
    });
  }, [quotationId]);

  const addItem = useMutation(
    trpc.item.add.mutationOptions({
      onSuccess: (data) => {
        setAlerts((prev) => [
          ...prev,
          ...data.alerts.filter(
            (a) => !prev.some((existing) => existing.ruleId === a.ruleId),
          ),
        ]);
        invalidateQuotation();
        setShowAddItem(false);
      },
    }),
  );

  const removeItem = useMutation(
    trpc.item.remove.mutationOptions({
      onSuccess: () => invalidateQuotation(),
    }),
  );

  const respondToAlert = useMutation(
    trpc.rules.respond.mutationOptions({
      onSuccess: () => invalidateQuotation(),
    }),
  );

  const updateStatus = useMutation(
    trpc.quotation.update.mutationOptions({
      onSuccess: () => invalidateQuotation(),
    }),
  );

  if (quotation.isLoading) {
    return <div className="p-4 text-muted-foreground">載入中...</div>;
  }

  if (!quotation.data) {
    return <div className="p-4 text-red-500">報價單不存在</div>;
  }

  const q = quotation.data;

  return (
    <div className="container mx-auto max-w-7xl px-4 py-4">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <Link
            to="/quotations"
            className="text-sm text-muted-foreground hover:underline"
          >
            &larr; 返回列表
          </Link>
          <h1 className="text-xl font-bold">{q.projectName}</h1>
          {q.projectAddress && (
            <p className="text-sm text-muted-foreground">{q.projectAddress}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={q.status} />
          {q.status === "draft" && (
            <Button
              variant="outline"
              className="text-sm"
              onClick={() =>
                updateStatus.mutate({ id: q.id, status: "completed" })
              }
            >
              標記完成
            </Button>
          )}
        </div>
      </div>

      {/* Main layout: items table + alert panel */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Left: Items Table */}
        <div className="lg:col-span-2">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="font-medium">工項列表</h2>
            <Button
              onClick={() => setShowAddItem(!showAddItem)}
              className="text-sm"
            >
              {showAddItem ? "取消" : "+ 新增工項"}
            </Button>
          </div>

          {showAddItem && (
            <AddItemForm
              wbsTags={wbsTags.data ?? []}
              onAdd={(data) => addItem.mutate({ ...data, quotationId })}
              isPending={addItem.isPending}
            />
          )}

          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-muted/50">
                <tr>
                  <th className="px-3 py-2 text-left font-medium">分類</th>
                  <th className="px-3 py-2 text-left font-medium">工項名稱</th>
                  <th className="px-3 py-2 text-left font-medium">WBS</th>
                  <th className="px-3 py-2 text-left font-medium">單位</th>
                  <th className="px-3 py-2 text-right font-medium">數量</th>
                  <th className="px-3 py-2 text-left font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                {q.items.length === 0 && (
                  <tr>
                    <td
                      colSpan={6}
                      className="px-3 py-8 text-center text-muted-foreground"
                    >
                      尚無工項，請點擊「新增工項」開始。
                    </td>
                  </tr>
                )}
                {q.items.map((item) => (
                  <tr key={item.id} className="border-b hover:bg-muted/30">
                    <td className="px-3 py-2">{item.category}</td>
                    <td className="px-3 py-2 font-medium">{item.itemName}</td>
                    <td className="px-3 py-2 text-xs text-muted-foreground">
                      {item.wbsCode || "—"}
                    </td>
                    <td className="px-3 py-2">{item.unit}</td>
                    <td className="px-3 py-2 text-right">{item.quantity}</td>
                    <td className="px-3 py-2">
                      <Button
                        variant="outline"
                        className="h-6 px-2 text-xs"
                        onClick={() =>
                          removeItem.mutate({
                            id: item.id,
                            quotationId: q.id,
                          })
                        }
                      >
                        刪除
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Alert Panel */}
        <div className="lg:col-span-1">
          <AlertPanel
            alerts={allAlerts}
            wbsTags={wbsTags.data ?? []}
            quotationId={quotationId}
            onRespond={(alert, response) => {
              // Find the trigger item for this alert
              respondToAlert.mutate({
                quotationItemId: alert.triggerItemId,
                ruleId: alert.ruleId,
                response,
              });

              if (response === "added_item") {
                // Auto-add the related item
                const relatedTag = (wbsTags.data ?? []).find(
                  (t) => t.code === alert.relatedWbs,
                );
                if (relatedTag) {
                  addItem.mutate({
                    quotationId,
                    category: relatedTag.category,
                    itemName: relatedTag.nameTw,
                    wbsCode: relatedTag.code,
                    unit: "式",
                    quantity: 1,
                  });
                }
              }

              // Remove this alert from local state
              setAlerts((prev) =>
                prev.filter((a) => a.ruleId !== alert.ruleId),
              );
            }}
          />
        </div>
      </div>
    </div>
  );
}

// ─── Sub-components ──────────────────────────────────────────────────────────

type WbsTag = {
  id: string;
  code: string;
  category: string;
  nameTw: string;
  description: string | null;
};

function AddItemForm({
  wbsTags,
  onAdd,
  isPending,
}: {
  wbsTags: WbsTag[];
  onAdd: (data: {
    category: string;
    itemName: string;
    wbsCode?: string;
    unit: string;
    quantity: number;
  }) => void;
  isPending: boolean;
}) {
  const [selectedWbs, setSelectedWbs] = useState("");
  const [category, setCategory] = useState("");
  const [itemName, setItemName] = useState("");
  const [unit, setUnit] = useState("式");
  const [quantity, setQuantity] = useState(1);

  // Group tags by category
  const categories = [...new Set(wbsTags.map((t) => t.category))];

  const handleWbsSelect = (code: string) => {
    setSelectedWbs(code);
    const tag = wbsTags.find((t) => t.code === code);
    if (tag) {
      setCategory(tag.category);
      setItemName(tag.nameTw);
    }
  };

  return (
    <div className="mb-3 rounded-lg border bg-muted/20 p-3">
      <div className="mb-2">
        <label className="mb-1 block text-xs font-medium">
          從標準工項選擇（或手動輸入）
        </label>
        <select
          value={selectedWbs}
          onChange={(e) => handleWbsSelect(e.target.value)}
          className="w-full rounded-md border bg-background px-3 py-1.5 text-sm"
        >
          <option value="">-- 選擇標準工項 --</option>
          {categories.map((cat) => (
            <optgroup key={cat} label={cat}>
              {wbsTags
                .filter((t) => t.category === cat)
                .map((t) => (
                  <option key={t.code} value={t.code}>
                    {t.nameTw}
                  </option>
                ))}
            </optgroup>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="mb-1 block text-xs font-medium">分類 *</label>
          <Input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="例：水電"
            className="text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium">工項名稱 *</label>
          <Input
            value={itemName}
            onChange={(e) => setItemName(e.target.value)}
            placeholder="例：廚下式濾水機"
            className="text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium">單位 *</label>
          <Input
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
            placeholder="式"
            className="text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium">數量 *</label>
          <Input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            min={0.1}
            step={0.1}
            className="text-sm"
          />
        </div>
      </div>

      <div className="mt-2">
        <Button
          className="text-sm"
          disabled={isPending || !category.trim() || !itemName.trim()}
          onClick={() =>
            onAdd({
              category: category.trim(),
              itemName: itemName.trim(),
              wbsCode: selectedWbs || undefined,
              unit: unit.trim(),
              quantity,
            })
          }
        >
          {isPending ? "新增中..." : "新增工項"}
        </Button>
      </div>
    </div>
  );
}

function AlertPanel({
  alerts,
  wbsTags,
  quotationId,
  onRespond,
}: {
  alerts: Alert[];
  wbsTags: WbsTag[];
  quotationId: string;
  onRespond: (alert: Alert, response: "accepted" | "dismissed" | "added_item") => void;
}) {
  return (
    <div>
      <h2 className="mb-2 font-medium">
        關聯提醒{" "}
        {alerts.length > 0 && (
          <span className="text-sm font-normal text-yellow-600 dark:text-yellow-400">
            ({alerts.length})
          </span>
        )}
      </h2>

      {alerts.length === 0 && (
        <div className="rounded-lg border border-dashed p-4 text-center text-sm text-muted-foreground">
          目前沒有關聯提醒
        </div>
      )}

      <div className="space-y-2">
        {alerts.map((alert) => {
          const relatedTag = wbsTags.find((t) => t.code === alert.relatedWbs);
          return (
            <div
              key={`${alert.ruleId}-${alert.triggerItemId}`}
              className={`rounded-lg border p-3 ${
                alert.severity === "critical"
                  ? "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950"
                  : "border-yellow-300 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950"
              }`}
            >
              <div className="mb-1 flex items-start gap-1">
                <span className="text-base">
                  {alert.severity === "critical" ? "!" : "?"}
                </span>
                <p className="text-sm">{alert.message}</p>
              </div>

              {relatedTag && (
                <p className="mb-2 text-xs text-muted-foreground">
                  建議工項：{relatedTag.nameTw} ({relatedTag.category})
                </p>
              )}

              <div className="flex items-center gap-2">
                <span
                  className={`text-xs ${
                    alert.scope === "company"
                      ? "text-blue-600 dark:text-blue-400"
                      : "text-gray-500"
                  }`}
                >
                  {alert.scope === "company" ? "公司規則" : "通用規則"}
                </span>
                {alert.source === "ai_suggested" && (
                  <span className="text-xs text-purple-600 dark:text-purple-400">
                    AI 建議
                  </span>
                )}
              </div>

              <div className="mt-2 flex gap-2">
                <Button
                  className="h-7 px-3 text-xs"
                  onClick={() => onRespond(alert, "added_item")}
                >
                  加入
                </Button>
                <Button
                  variant="outline"
                  className="h-7 px-3 text-xs"
                  onClick={() => onRespond(alert, "dismissed")}
                >
                  不需要
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    draft: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
    reviewing:
      "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
    completed:
      "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  };
  const labels: Record<string, string> = {
    draft: "草稿",
    reviewing: "審核中",
    completed: "已完成",
  };
  return (
    <span
      className={`inline-block rounded-full px-2 py-0.5 text-xs ${styles[status] ?? ""}`}
    >
      {labels[status] ?? status}
    </span>
  );
}
