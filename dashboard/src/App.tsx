import { useState } from "react";
import { DashboardProvider, useDashboardState } from "./features/dashboard/dashboard-provider";
import type { DashboardState } from "./features/dashboard/dashboard-types";

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`badge ${status.toLowerCase()}`}>
      {status}
    </span>
  );
}

function MetricCards({ state }: { state: DashboardState }) {
  return (
    <div className="cards">
      <div className="card">
        <div className="metricLabel">Total Resources</div>
        <div className="metricValue">{state.metrics.totalResources}</div>
        <div className="metricChange">↑ 2 this session</div>
      </div>

      <div className="card">
        <div className="metricLabel">Active Workloads</div>
        <div className="metricValue">{state.metrics.activeWorkloads}</div>
        <div className="metricChange">↑ 16% from last hour</div>
      </div>

      <div className="card">
        <div className="metricLabel">Avg. Latency</div>
        <div className="metricValue">{state.metrics.avgLatency}</div>
        <div className="metricChange">↓ 8% improvement</div>
      </div>

      <div className="card">
        <div className="metricLabel">Resource Utilization</div>
        <div className="metricValue">{state.metrics.resourceUtilization}</div>
        <div className="metricChange">Within optimal range</div>
      </div>
    </div>
  );
}

function ResourcesTable({ state }: { state: DashboardState }) {
  return (
    <section className="section">
      <div className="sectionHeader">
        <div>
          <div className="sectionTitle">Resource Overview</div>
          <div className="sectionSub">
            Available edge and cloud resources
          </div>
        </div>

        <button className="refresh">↻ Refresh</button>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Resource</th>
            <th>CPU</th>
            <th>Memory</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {state.resources.map((resource) => (
            <tr key={resource.name}>
              <td>
                <div className="resourceName">{resource.name}</div>
                <div className="resourceType">{resource.type}</div>
              </td>

              <td>
                <div className="cpuValue">{resource.cpu}%</div>
                <div className="barContainer">
                  <div
                    className="bar"
                    style={{ width: `${resource.cpu}%` }}
                  />
                </div>
              </td>

              <td>{resource.memory}%</td>

              <td>
                <StatusBadge status={resource.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function WorkloadsPanel({ state }: { state: DashboardState }) {
  return (
    <section className="section">
      <div className="sectionHeader">
        <div>
          <div className="sectionTitle">Active Workloads</div>
          <div className="sectionSub">
            Current workload execution
          </div>
        </div>
      </div>

      {state.workloads.map((workload) => (
        <div className="workload" key={workload.name}>
          <div className="workloadTop">
            <div className="workloadName">{workload.name}</div>

            <StatusBadge status={workload.status} />
          </div>

          <div className="workloadMeta">
            <span>{workload.node}</span>
            <span>Latency: {workload.latency}</span>
          </div>
        </div>
      ))}
    </section>
  );
}

function OverviewPage({ state }: { state: DashboardState }) {
  return (
    <>
      <MetricCards state={state} />

      <div className="grid">
        <ResourcesTable state={state} />
        <WorkloadsPanel state={state} />
      </div>
    </>
  );
}

function ResourcesPage({ state }: { state: DashboardState }) {
  return (
    <section className="section fullSection">
      <div className="sectionHeader">
        <div>
          <div className="sectionTitle">All Resources</div>
          <div className="sectionSub">
            Edge devices and cloud resources
          </div>
        </div>

        <button className="refresh">↻ Refresh</button>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Resource</th>
            <th>Type</th>
            <th>CPU</th>
            <th>Memory</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {state.resources.map((resource) => (
            <tr key={resource.name}>
              <td>
                <div className="resourceName">{resource.name}</div>
              </td>

              <td>{resource.type}</td>

              <td>
                <div className="cpuValue">{resource.cpu}%</div>

                <div className="barContainer">
                  <div
                    className="bar"
                    style={{ width: `${resource.cpu}%` }}
                  />
                </div>
              </td>

              <td>{resource.memory}%</td>

              <td>
                <StatusBadge status={resource.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function WorkloadsPage({ state }: { state: DashboardState }) {
  return (
    <>
      <MetricCards state={state} />

      <section className="section fullSection">
        <div className="sectionHeader">
          <div>
            <div className="sectionTitle">Workload Execution</div>
            <div className="sectionSub">
              Current and queued workloads
            </div>
          </div>

          <button className="refresh">↻ Refresh</button>
        </div>

        {state.workloads.map((workload) => (
          <div className="workload largeWorkload" key={workload.name}>
            <div className="workloadTop">
              <div>
                <div className="workloadName">{workload.name}</div>
                <div className="resourceType">
                  Running on {workload.node}
                </div>
              </div>

              <StatusBadge status={workload.status} />
            </div>

            <div className="workloadMeta">
              <span>Node: {workload.node}</span>
              <span>Latency: {workload.latency}</span>
            </div>
          </div>
        ))}
      </section>
    </>
  );
}

function OrchestrationPage({ state }: { state: DashboardState }) {
  return (
    <>
      <MetricCards state={state} />

      <div className="grid">
        <section className="section">
          <div className="sectionHeader">
            <div>
              <div className="sectionTitle">
                Orchestration Decision
              </div>

              <div className="sectionSub">
                Resource allocation overview
              </div>
            </div>
          </div>

          <div className="decisionBox">
            <div className="decisionLabel">
              Current Strategy
            </div>

            <div className="decisionValue">
              {state.orchestration.strategy}
            </div>

            <div className="decisionText">
              Workloads are assigned according to available
              CPU, memory, latency and resource status.
            </div>
          </div>

          <div className="decisionRow">
            <span>Latency Requirement</span>
            <strong>{state.orchestration.latencyRequirement}</strong>
          </div>

          <div className="decisionRow">
            <span>Priority</span>
            <strong>{state.orchestration.priority}</strong>
          </div>

          <div className="decisionRow">
            <span>Model Confidence</span>
            <strong>{state.orchestration.modelConfidence}</strong>
          </div>
        </section>

        <section className="section">
          <div className="sectionHeader">
            <div>
              <div className="sectionTitle">
                Allocation Status
              </div>

              <div className="sectionSub">
                Current resource decisions
              </div>
            </div>
          </div>

          {state.orchestration.allocations.map((allocation) => (
            <div className="allocation" key={allocation.workload}>
              <div className="allocationTitle">
                {allocation.workload}
              </div>

              <div className="allocationMeta">
                <span>{allocation.status}</span>
                <strong>{allocation.node}</strong>
              </div>
            </div>
          ))}
        </section>
      </div>
    </>
  );
}

function App() {
  return (
    <DashboardProvider>
      <Dashboard />
    </DashboardProvider>
  );
}

function Dashboard() {
  const { state } = useDashboardState();
  const [activePage, setActivePage] = useState("Overview");

  return (
    <div className="app">
      <style>{`
        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          font-family: Inter, -apple-system, BlinkMacSystemFont,
            "Segoe UI", sans-serif;
          background: #f5f7fb;
          color: #172033;
        }

        button {
          font-family: inherit;
        }

        .app {
          min-height: 100vh;
          display: flex;
        }

        .sidebar {
          width: 250px;
          min-height: 100vh;
          background: #111827;
          color: white;
          padding: 24px 16px;
          position: fixed;
          left: 0;
          top: 0;
          bottom: 0;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 0 10px 30px;
          font-size: 18px;
          font-weight: 700;
        }

        .logoIcon {
          width: 38px;
          height: 38px;
          border-radius: 11px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #4f46e5;
          font-size: 18px;
        }

        .navTitle {
          color: #6b7280;
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 1px;
          padding: 0 12px;
          margin-bottom: 8px;
        }

        .navItem {
          width: 100%;
          border: none;
          background: transparent;
          color: #9ca3af;
          text-align: left;
          padding: 12px;
          border-radius: 9px;
          margin-bottom: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .navItem:hover {
          background: #1f2937;
          color: white;
        }

        .navItem.active {
          background: #312e81;
          color: white;
        }

        .main {
          margin-left: 250px;
          width: calc(100% - 250px);
          min-height: 100vh;
        }

        .topbar {
          height: 72px;
          background: white;
          border-bottom: 1px solid #e5e7eb;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 32px;
        }

        .pageTitle {
          font-size: 21px;
          font-weight: 700;
        }

        .subtitle {
          color: #6b7280;
          font-size: 12px;
          margin-top: 3px;
        }

        .systemStatus {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #15803d;
          font-size: 13px;
          font-weight: 600;
        }

        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #22c55e;
        }

        .content {
          padding: 30px 32px;
        }

        .cards {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 18px;
          margin-bottom: 24px;
        }

        .card {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 14px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        }

        .metricLabel {
          color: #6b7280;
          font-size: 13px;
        }

        .metricValue {
          font-size: 30px;
          font-weight: 750;
          margin-top: 10px;
        }

        .metricChange {
          color: #16a34a;
          font-size: 12px;
          margin-top: 6px;
        }

        .grid {
          display: grid;
          grid-template-columns: 1.5fr 1fr;
          gap: 20px;
        }

        .section {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 14px;
          overflow: hidden;
        }

        .fullSection {
          width: 100%;
        }

        .sectionHeader {
          padding: 18px 20px;
          border-bottom: 1px solid #e5e7eb;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .sectionTitle {
          font-size: 15px;
          font-weight: 700;
        }

        .sectionSub {
          color: #6b7280;
          font-size: 12px;
          margin-top: 3px;
        }

        .table {
          width: 100%;
          border-collapse: collapse;
        }

        .table th {
          text-align: left;
          color: #6b7280;
          font-size: 11px;
          text-transform: uppercase;
          padding: 13px 20px;
          background: #f9fafb;
        }

        .table td {
          padding: 15px 20px;
          border-top: 1px solid #f0f1f3;
          font-size: 13px;
        }

        .resourceName {
          font-weight: 650;
        }

        .resourceType {
          color: #6b7280;
          font-size: 11px;
          margin-top: 3px;
        }

        .cpuValue {
          margin-bottom: 5px;
        }

        .badge {
          display: inline-flex;
          padding: 5px 9px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 650;
        }

        .online {
          color: #15803d;
          background: #dcfce7;
        }

        .busy {
          color: #b45309;
          background: #fef3c7;
        }

        .offline {
          color: #b91c1c;
          background: #fee2e2;
        }

        .running {
          color: #1d4ed8;
          background: #dbeafe;
        }

        .queued {
          color: #6b7280;
          background: #f3f4f6;
        }

        .completed {
          color: #15803d;
          background: #dcfce7;
        }

        .barContainer {
          width: 90px;
          height: 6px;
          background: #e5e7eb;
          border-radius: 10px;
          overflow: hidden;
        }

        .bar {
          height: 100%;
          background: #4f46e5;
          border-radius: 10px;
        }

        .workload {
          padding: 17px 20px;
          border-bottom: 1px solid #f0f1f3;
        }

        .largeWorkload {
          padding: 22px 24px;
        }

        .workload:last-child {
          border-bottom: none;
        }

        .workloadTop {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .workloadName {
          font-weight: 650;
          font-size: 13px;
        }

        .workloadMeta {
          display: flex;
          justify-content: space-between;
          margin-top: 9px;
          color: #6b7280;
          font-size: 11px;
        }

        .refresh {
          border: 1px solid #e5e7eb;
          background: white;
          padding: 8px 12px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 12px;
        }

        .refresh:hover {
          background: #f9fafb;
        }

        .decisionBox {
          padding: 24px;
          border-bottom: 1px solid #f0f1f3;
        }

        .decisionLabel {
          color: #6b7280;
          font-size: 12px;
        }

        .decisionValue {
          font-size: 17px;
          font-weight: 700;
          margin-top: 7px;
        }

        .decisionText {
          color: #6b7280;
          font-size: 12px;
          line-height: 1.6;
          margin-top: 8px;
        }

        .decisionRow {
          display: flex;
          justify-content: space-between;
          padding: 16px 24px;
          border-bottom: 1px solid #f0f1f3;
          font-size: 13px;
        }

        .decisionRow span {
          color: #6b7280;
        }

        .allocation {
          padding: 20px;
          border-bottom: 1px solid #f0f1f3;
        }

        .allocation:last-child {
          border-bottom: none;
        }

        .allocationTitle {
          font-size: 13px;
          font-weight: 650;
        }

        .allocationMeta {
          display: flex;
          justify-content: space-between;
          margin-top: 8px;
          color: #6b7280;
          font-size: 11px;
        }

        .allocationMeta strong {
          color: #172033;
        }

        @media (max-width: 1000px) {
          .cards {
            grid-template-columns: repeat(2, 1fr);
          }

          .grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 700px) {
          .sidebar {
            width: 70px;
          }

          .logo span,
          .navTitle,
          .navItem span {
            display: none;
          }

          .main {
            margin-left: 70px;
            width: calc(100% - 70px);
          }

          .content {
            padding: 18px;
          }

          .cards {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <aside className="sidebar">
        <div className="logo">
          <div className="logoIcon">⚡</div>
          <span>Edge Orchestrator</span>
        </div>

        <div className="navTitle">Platform</div>

        {[
          "Overview",
          "Resources",
          "Workloads",
          "Orchestration",
        ].map((item) => (
          <button
            key={item}
            className={`navItem ${
              activePage === item ? "active" : ""
            }`}
            onClick={() => setActivePage(item)}
          >
            <span>
              {item === "Overview" && "▣ "}
              {item === "Resources" && "◈ "}
              {item === "Workloads" && "◆ "}
              {item === "Orchestration" && "⚙ "}
              {item}
            </span>
          </button>
        ))}

        <div className="navTitle" style={{ marginTop: 28 }}>
          System
        </div>

        <button className="navItem">
          <span>◉ System Health</span>
        </button>

        <button className="navItem">
          <span>⚙ Settings</span>
        </button>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <div className="pageTitle">{activePage}</div>

            <div className="subtitle">
              I3-IoT Edge Cloud Orchestration Platform
            </div>
          </div>

          <div className="systemStatus">
            <span className="dot"></span>
            System Operational
          </div>
        </header>

        <div className="content">
          {state && activePage === "Overview" && <OverviewPage state={state} />}
          {state && activePage === "Resources" && <ResourcesPage state={state} />}
          {state && activePage === "Workloads" && <WorkloadsPage state={state} />}
          {state && activePage === "Orchestration" && <OrchestrationPage state={state} />}
        </div>
      </main>
    </div>
  );
}

export default App;
