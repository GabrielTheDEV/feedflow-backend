from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/ingest", tags=["widget"])


@router.post("/widget")
async def ingest_widget(
    payload: WidgetIngestPayload,
    request: Request,
    collection_service: CollectionService = Depends(...),
    domain_service: DomainService = Depends(...),
):
    # 1. validar api_key
    try:
        collection = collection_service.get_active_by_api_key(
            payload.api_key
        )
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # 2. pegar origin
    origin = request.headers.get("origin") or request.headers.get("referer")

    if not origin:
        raise HTTPException(status_code=403, detail="Origin missing")

    # 3. validar domínio
    if not domain_service.is_domain_allowed(collection.id, origin):
        raise HTTPException(status_code=403, detail="Domain not allowed")

    return {"status": "ok"}