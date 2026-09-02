from fastapi import APIRouter, HTTPException

from app.schemas import InquiryRequest, InquiryResponse
from app.sanitizer import PiiSanitizer
from app.ai_service import AiService
from app.audit_service import AuditService

router = APIRouter()


@router.post("/secure-inquiry", response_model=InquiryResponse)
async def secure_inquiry(payload: InquiryRequest):
    # Step 1: Sanitization
    try:
        sanitized_message, redactions = PiiSanitizer.sanitize(payload.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sanitization failed: {str(e)}")

    # Step 2: Mock AI Call (2-second simulated delay)
    try:
        generated_answer = await AiService.generate_answer(sanitized_message)
    except Exception as e:
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