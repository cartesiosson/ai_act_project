from fastapi import FastAPI
from routers import assessments, systems, purposes, criteria, risklevels, compliance

app = FastAPI(
    title="AI Act API",
    description="""
    API para evaluar, clasificar y documentar el riesgo de sistemas de inteligencia artificial conforme al AI Act europeo.
    Permite gestionar propósitos, criterios de riesgo, niveles, requisitos de cumplimiento y evaluaciones específicas.
    """,
    version="0.1.0"
)

app.include_router(
    assessments.router,
    prefix="/assessments",
    tags=["Evaluaciones de Riesgo"]
)

app.include_router(
    systems.router,
    prefix="/systems",
    tags=["Sistemas Inteligentes"]
)

app.include_router(
    purposes.router,
    prefix="/purposes",
    tags=["Propósitos Funcionales"]
)

app.include_router(
    criteria.router,
    prefix="/criteria",
    tags=["Criterios de Riesgo"]
)

app.include_router(
    risklevels.router,
    prefix="/risklevels",
    tags=["Niveles de Riesgo"]
)

app.include_router(
    compliance.router,
    prefix="/compliance",
    tags=["Requisitos de Cumplimiento"]
)