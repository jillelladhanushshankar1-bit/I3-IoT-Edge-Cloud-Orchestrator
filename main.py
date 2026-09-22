from dataclasses import asdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.schemas import Workload
from infrastructure.resources import EdgeNode, CloudServer
from infrastructure.resource_manager import InfrastructureResourceManager
from orchestrator import Orchestrator, ScoringConfig


app = FastAPI(
    title="I3-IoT Edge Cloud Orchestrator",
    version="1.0.0",
)

# Allow React/Vite dashboard to communicate with Python backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Infrastructure setup
# ---------------------------------------------------------

resource_manager = InfrastructureResourceManager()

resource_manager.register_resource(
    EdgeNode(
        id="Edge Node 01",
        cpu_capacity=8,
        memory_capacity=16000,
        latency=18,
        bandwidth=500,
        energy_level=82,
    )
)

resource_manager.register_resource(
    EdgeNode(
        id="Edge Node 02",
        cpu_capacity=16,
        memory_capacity=32000,
        latency=42,
        bandwidth=1000,
        energy_level=70,
    )
)

resource_manager.register_resource(
    CloudServer(
        id="Cloud Node 01",
        cpu_capacity=32,
        memory_capacity=64000,
        latency=65,
        bandwidth=5000,
        energy_level=95,
    )
)


orchestrator = Orchestrator(
    ScoringConfig()
)


# ---------------------------------------------------------
# API
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "I3-IoT Edge Cloud Orchestrator",
        "status": "operational",
    }


@app.get("/api/health")
def health():
    return {
        "status": "operational",
        "resources": len(resource_manager.get_all_resources()),
    }


@app.get("/api/resources")
def get_resources():
    resources = resource_manager.get_all_resources()

    return [
        {
            "name": resource.id,
            "type": resource.type,
            "cpu": round(
                (
                    1
                    - resource.available_cpu / resource.cpu_capacity
                )
                * 100,
                1,
            ),
            "memory": round(
                (
                    1
                    - resource.available_memory
                    / resource.memory_capacity
                )
                * 100,
                1,
            ),
            "status": (
                "Offline"
                if resource.available_cpu <= 0
                or resource.available_memory <= 0
                else "Online"
            ),
            "latency": resource.latency,
            "bandwidth": resource.bandwidth,
            "energy": resource.energy_level,
        }
        for resource in resources
    ]


@app.post("/api/orchestrate")
def orchestrate():
    workload = Workload(
        id="demo-workload-001",
        source_device_id="IoT-Device-01",
        type="image_processing",
        cpu_required=4,
        memory_required=4000,
        data_size=5,
        latency_requirement=100,
        energy_requirement=10,
        priority=8,
        model_confidence=0.92,
    )

    resources = resource_manager.get_available_resources()

    decision = orchestrator.decide(
        workload,
        resources,
    )

    return {
        "workload": asdict(workload),
        "decision": asdict(decision),
    }