// Dashboard state types shared by the mock and REST adapters.
//
// These mirror the shapes the React UI already consumes (see App.tsx).
// Values are intentionally kept simple: strings, numbers, and unions
// that the existing components render without further transformation.

export type ResourceStatus = "Online" | "Busy" | "Offline";
export type WorkloadStatus = "Running" | "Queued" | "Completed";

export type Resource = {
  name: string;
  type: string;
  cpu: number;
  memory: number;
  status: ResourceStatus;
};

export type Workload = {
  name: string;
  node: string;
  status: WorkloadStatus;
  latency: string;
};

// Orchestration decision view rendered by the Orchestration page.
export type OrchestrationDecision = {
  strategy: string;
  latencyRequirement: string;
  priority: string;
  modelConfidence: string;
  allocations: Array<{
    workload: string;
    status: string;
    node: string;
  }>;
};

// Full dashboard state consumed by every page component.
export type DashboardState = {
  resources: Resource[];
  workloads: Workload[];
  metrics: {
    totalResources: number;
    activeWorkloads: number;
    avgLatency: string;
    resourceUtilization: string;
  };
  orchestration: OrchestrationDecision;
  updatedAt: string;
};

// ---- Backend API shapes -----------------------------------------------
// These mirror the FastAPI /api/state response produced by
// api.state.SimulationState.get_snapshot(). They are kept here so the
// REST adapter can map them into the DashboardState above without the
// UI ever touching raw backend keys.

export type ApiResource = {
  id: string;
  type: string;
  cpu_capacity: number;
  available_cpu: number;
  cpu_utilization: number;
  memory_capacity: number;
  available_memory: number;
  memory_utilization: number;
  latency: number;
  bandwidth: number;
  energy_level: number;
};

export type ApiWorkload = {
  id: string;
  source_device_id: string;
  type: string;
  cpu_required: number;
  memory_required: number;
  data_size: number;
  latency_requirement: number;
  energy_requirement: number;
  priority: number;
  model_confidence: number;
};

export type ApiDecision = {
  workload_id: string;
  destination: string | null;
  score: number;
  reason: string;
};

export type ApiEvent = {
  event_id: string;
  device_id: string;
  event_type: string;
  severity: string;
  temperature: number;
  vibration: number;
  description: string;
};

export type ApiMetric = {
  resource_id: string;
  type: string;
  cpu_utilization: number;
  memory_utilization: number;
};

export type ApiState = {
  resources: ApiResource[];
  workloads: ApiWorkload[];
  decisions: ApiDecision[];
  executionFeedback: unknown[];
  events: ApiEvent[];
  metrics: ApiMetric[];
  updatedAt: string;
};