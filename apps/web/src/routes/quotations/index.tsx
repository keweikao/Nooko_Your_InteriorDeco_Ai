import { authClient } from "@/lib/auth-client";
import { trpc } from "@/utils/trpc";
import { useMutation, useQuery } from "@tanstack/react-query";
import { createFileRoute, Link, redirect, useNavigate } from "@tanstack/react-router";
import { queryClient } from "@/utils/trpc";
import { useState } from "react";
import { Button } from "@my-better-t-app/ui/components/button";
import { Input } from "@my-better-t-app/ui/components/input";

export const Route = createFileRoute("/quotations/")({
  component: QuotationsPage,
  beforeLoad: async () => {
    const session = await authClient.getSession();
    if (!session.data) {
      redirect({ to: "/login", throw: true });
    }
    return { session };
  },
});

function QuotationsPage() {
  const { session } = Route.useRouteContext();
  const navigate = useNavigate();
  const [showNewForm, setShowNewForm] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [projectAddress, setProjectAddress] = useState("");

  const activeOrg = authClient.useActiveOrganization();
  const orgs = authClient.useListOrganizations();

  // Organization setup state
  const [orgName, setOrgName] = useState("");
  const [creatingOrg, setCreatingOrg] = useState(false);

  const quotations = useQuery({
    ...trpc.quotation.list.queryOptions(),
    enabled: !!activeOrg.data,
  });

  const createQuotation = useMutation(
    trpc.quotation.create.mutationOptions({
      onSuccess: (data) => {
        queryClient.invalidateQueries({ queryKey: trpc.quotation.list.queryOptions().queryKey });
        navigate({ to: "/quotations/$quotationId", params: { quotationId: data.id } });
      },
    }),
  );

  const deleteQuotation = useMutation(
    trpc.quotation.delete.mutationOptions({
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: trpc.quotation.list.queryOptions().queryKey });
      },
    }),
  );

  // If user has no organization, show setup UI
  if (orgs.data && orgs.data.length === 0) {
    return (
      <div className="container mx-auto max-w-lg px-4 py-8">
        <div className="rounded-lg border p-6">
          <h1 className="mb-4 text-xl font-bold">建立公司</h1>
          <p className="mb-4 text-sm text-muted-foreground">
            開始使用前，請先建立您的公司組織。
          </p>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              if (!orgName.trim()) return;
              setCreatingOrg(true);
              try {
                const result = await authClient.organization.create({
                  name: orgName.trim(),
                  slug: orgName.trim().toLowerCase().replace(/\s+/g, "-"),
                });
                if (result.data) {
                  await authClient.organization.setActive({
                    organizationId: result.data.id,
                  });
                  window.location.reload();
                }
              } finally {
                setCreatingOrg(false);
              }
            }}
          >
            <Input
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              placeholder="公司名稱"
              className="mb-3"
            />
            <Button type="submit" disabled={creatingOrg || !orgName.trim()}>
              {creatingOrg ? "建立中..." : "建立公司"}
            </Button>
          </form>
        </div>
      </div>
    );
  }

  // Auto-set active org if user has orgs but none is active
  if (orgs.data && orgs.data.length > 0 && !activeOrg.data) {
    authClient.organization.setActive({ organizationId: orgs.data[0].id });
  }

  return (
    <div className="container mx-auto max-w-4xl px-4 py-4">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">報價單列表</h1>
        <Button onClick={() => setShowNewForm(!showNewForm)}>
          {showNewForm ? "取消" : "新增報價單"}
        </Button>
      </div>

      {showNewForm && (
        <form
          className="mb-4 rounded-lg border p-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (!projectName.trim()) return;
            createQuotation.mutate({
              projectName: projectName.trim(),
              projectAddress: projectAddress.trim() || undefined,
            });
          }}
        >
          <div className="mb-3">
            <label className="mb-1 block text-sm font-medium">案件名稱 *</label>
            <Input
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="例：王先生住宅裝修"
            />
          </div>
          <div className="mb-3">
            <label className="mb-1 block text-sm font-medium">施工地址</label>
            <Input
              value={projectAddress}
              onChange={(e) => setProjectAddress(e.target.value)}
              placeholder="例：台北市大安區..."
            />
          </div>
          <Button type="submit" disabled={createQuotation.isPending || !projectName.trim()}>
            {createQuotation.isPending ? "建立中..." : "建立"}
          </Button>
        </form>
      )}

      {quotations.isLoading && <p className="text-muted-foreground">載入中...</p>}

      {quotations.data && quotations.data.length === 0 && (
        <p className="text-muted-foreground">尚無報價單，請點擊「新增報價單」開始。</p>
      )}

      {quotations.data && quotations.data.length > 0 && (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="px-4 py-2 text-left font-medium">案件名稱</th>
                <th className="px-4 py-2 text-left font-medium">地址</th>
                <th className="px-4 py-2 text-left font-medium">狀態</th>
                <th className="px-4 py-2 text-left font-medium">建立者</th>
                <th className="px-4 py-2 text-left font-medium">建立時間</th>
                <th className="px-4 py-2 text-left font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              {quotations.data.map((q) => (
                <tr key={q.id} className="border-b hover:bg-muted/30">
                  <td className="px-4 py-2">
                    <Link
                      to="/quotations/$quotationId"
                      params={{ quotationId: q.id }}
                      className="font-medium text-blue-600 hover:underline dark:text-blue-400"
                    >
                      {q.projectName}
                    </Link>
                  </td>
                  <td className="px-4 py-2 text-muted-foreground">
                    {q.projectAddress || "—"}
                  </td>
                  <td className="px-4 py-2">
                    <StatusBadge status={q.status} />
                  </td>
                  <td className="px-4 py-2">{q.createdByUser.name}</td>
                  <td className="px-4 py-2 text-muted-foreground">
                    {new Date(q.createdAt).toLocaleDateString("zh-TW")}
                  </td>
                  <td className="px-4 py-2">
                    <Button
                      variant="outline"
                      className="h-7 px-2 text-xs"
                      onClick={() => {
                        if (confirm("確定要刪除此報價單？")) {
                          deleteQuotation.mutate({ id: q.id });
                        }
                      }}
                    >
                      刪除
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
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
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs ${styles[status] ?? ""}`}>
      {labels[status] ?? status}
    </span>
  );
}
