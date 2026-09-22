import type { DashboardState } from "./dashboard-types";

const resources = [
  { name: "Edge Node 01", type: "Edge Device", cpu: 42, memory: 58, status: "Online" as const },
  { name: "Edge Node 02", type: "Edge Device", cpu: 76, memory: 71, status: "Busy" as const },
  { name: "Cloud Node 01", type: "Cloud", cpu: 31, memory: 45, status: "Online" as const },
  { name: "Edge Node 03", type: "Edge Device", cpu: 12, memory: 24, status: "Offline" as const },
];

const workloads = [
  { name: "Video Processing", node: "Edge Node 02", status: "Running" as const, latency: "42 ms" },
  { name: "Sensor Analytics", node: "Edge Node 01", status: "Running" as const, latency: "18 ms" },
  { name: "ML Inference", node: "Cloud Node 01", status: "Queued" as const, latency: "--" },
];

const orchestration: DashboardState["orchestration"] = {
  strategy: "Edge-first workload placement",
  latencyRequirement: "100 ms",
  priority: "8 / 10",
  modelConfidence: "92%",
  allocations: [
    { workload: "Video Processing", status: "Assigned", node: "Edge Node 02" },
    { workload: "Sensor Analytics", status: "Assigned", node: "Edge Node 01" },
    { workload: "ML Inference", status: "Queued", node: "Cloud Node 01" },
  ],
};

export async function fetchMockDashboard(): Promise<DashboardState> {
  return {
    resources,
    workloads,
    metrics: {
      totalResources: 12,
      activeWorkloads: 7,
      avgLatency: "28 ms",
      resourceUtilization: "64%",
    },
    orchestration,
    updatedAt: new Date().toISOString(),
  };
}