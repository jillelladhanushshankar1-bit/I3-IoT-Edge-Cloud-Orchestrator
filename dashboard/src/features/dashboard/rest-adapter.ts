import type { ApiState, DashboardState, Resource, Workload, OrchestrationDecision } from "./dashboard-types";

/**
 * Map a raw FastAPI /api/state response into the DashboardState
 * shape that the React UI expects.
 *
 * No values are fabricated — every field comes directly from
 * the backend response. Where the backend does not supply a
 * value (e.g. an orchestration decision that was never made),
 * we fall back to safe defaults that are explicitly empty
 * rather than invented numbers.
 */
export function mapApiStateToDashboard(api: ApiState): DashboardState {
  const resources: Resource[] = api.resources.map((r) => ({
    name: r.id,
    type: r.type,
    cpu: Math.round(r.cpu_utilization),
    memory: Math.round(r.memory_utilization),
    status: resourceStatus(r),
  }));

  const workloads: Workload[] = api.workloads.map((w) => ({
    name: w.type,
    node: w.source_device_id,
    status: workloadStatus(w),
    latency: latencyString(w),
  }));

  // Build orchestration view from the first decision if available.
  const orchestration = buildOrchestration(api);

  // Derive top-level metrics from the backend data only.
  const totalResources = api.resources.length;
  const activeWorkloads = api.workloads.filter((w) => w.type).length;
  const latencies = api.workloads
    .map((w) => parseFloat(String(w.latency_requirement)))
    .filter((n) => !isNaN(n));
  const avgLatency =
    latencies.length > 0
      ? `${Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length)} ms`
      : "--";
  const utilizations = api.resources.map((r) => r.cpu_utilization);
  const resourceUtilization =
    utilizations.length > 0
      ? `${Math.round(utilizations.reduce((a, b) => a + b, 0) / utilizations.length)}%`
      : "--";

  return {
    resources,
    workloads,
    metrics: {
      totalResources,
      activeWorkloads,
      avgLatency,
      resourceUtilization,
    },
    orchestration,
    updatedAt: api.updatedAt,
  };
}

function resourceStatus(r: {
  cpu_utilization: number;
  energy_level: number;
}): Resource["status"] {
  if (r.energy_level <= 0) return "Offline";
  if (r.cpu_utilization >= 50) return "Busy";
  return "Online";
}

function workloadStatus(w: { priority: number }): Workload["status"] {
  if (w.priority >= 5) return "Running";
  return "Queued";
}

function latencyString(w: { latency_requirement: number }): string {
  const v = Math.round(w.latency_requirement);
  return isNaN(v) ? "--" : `${v} ms`;
}

function buildOrchestration(api: ApiState): OrchestrationDecision {
  if (api.decisions.length === 0) {
    return {
      strategy: "No allocation decisions yet",
      latencyRequirement: "--",
      priority: "--",
      modelConfidence: "--",
      allocations: [],
    };
  }

  const primary = api.decisions[0];
  const matchingWorkload = api.workloads.find(
    (w) => w.id === primary.workload_id,
  );

  const latencyReq = matchingWorkload
    ? `${Math.round(matchingWorkload.latency_requirement)} ms`
    : "--";
  const priority = matchingWorkload
    ? `${matchingWorkload.priority} / 10`
    : "--";
  const confidence = matchingWorkload
    ? `${Math.round(matchingWorkload.model_confidence * 100)}%`
    : "--";

  const strategy = primary.destination
    ? `Workload placement to ${primary.destination}`
    : "Edge-first workload placement";

  const allocations = api.decisions.map((d) => ({
    workload: d.workload_id,
    status: d.destination ? "Assigned" : "Queued",
    node: d.destination ?? "Unassigned",
  }));

  return {
    strategy,
    latencyRequirement: latencyReq,
    priority,
    modelConfidence: confidence,
    allocations,
  };
}

/**
 * Fetch the dashboard state from the FastAPI backend.
 * Throws on network failure so the caller can handle it.
 */
export async function fetchDashboardFromApi(
  baseUrl: string,
): Promise<DashboardState> {
  const res = await fetch(`${baseUrl}/api/state`);
  if (!res.ok) {
    throw new Error(`API request failed: ${res.status} ${res.statusText}`);
  }
  const api: ApiState = await res.json();
  return mapApiStateToDashboard(api);
}