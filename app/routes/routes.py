from fastapi import APIRouter, HTTPException

from app.schemas.schemas import InquiryRequest, InquiryResponse
from app.utils.sanitizer import PiiSanitizer
from app.services.ai_service import AiService
from app.services.audit_service import AuditService
from app.utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

router = APIRouter()

# Shared circuit breaker instance (guards the mock AI call)
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

@router.post("/secure-inquiry", response_model=InquiryResponse)
async def secure_inquiry(payload: InquiryRequest):
    # Step 1: Sanitization
    try:
        sanitized_message, redactions = PiiSanitizer.sanitize(payload.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sanitization failed: {str(e)}")

    # Step 2: AI Call with Circuit Breaker
    try:
        generated_answer = await circuit_breaker.call(
            AiService.generate_answer, sanitized_message
        )
    except CircuitBreakerOpenError:
        # Circuit is OPEN → instant fallback, no 2-second timeout wait
        generated_answer = "Service Busy"
    except Exception as e:
        # AI call failed (circuit not yet open) — propagate as 502
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    # Step 3: Audit Log (encrypted original + plaintext sanitized)
    try:
        audit_id = await AuditService.log_inquiry(
            user_id=payload.userId,
            original_message=payload.message,
            sanitized_message=sanitized_message,
            redactions=redactions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit logging failed: {str(e)}")


    return InquiryResponse(
        userId=payload.userId,
        original_message=payload.message,
        sanitized_message=sanitized_message,
        redactions_found=redactions,
        generated_answer=generated_answer,
        audit_id=audit_id 
    )


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/")
async def root():
    return {"message": "Welcome to the Secure Inquiry API"}