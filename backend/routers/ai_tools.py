"""AI-powered features for lawyers and judges — case briefs, precedent finding, argument analysis."""

from typing import Optional, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, status

from backend.dependencies import require_current_user, require_role
from backend.models.user import User, Role, AITier, TIER_LIMITS
from backend.services.law import law_service
from backend.services.related import find_related_provisions

router = APIRouter(prefix="/ai", tags=["AI Tools"])

# 20MB max upload
MAX_UPLOAD_SIZE = 20 * 1024 * 1024
ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "txt",
    "text/markdown": "txt",
    "image/png": "image",
    "image/jpeg": "image",
    "image/webp": "image",
}


# ─── Schemas ──────────────────────────────────────────────────────────────

class CaseBriefRequest(BaseModel):
    case_description: str = Field(..., min_length=10, max_length=5000, description="Description of the case or legal situation")
    country: Optional[str] = Field(None, pattern="^(nepal|india)$")
    legal_areas: Optional[List[str]] = Field(None, description="Specific legal areas to focus on")

class CaseBriefResponse(BaseModel):
    summary: str
    key_issues: List[str]
    relevant_laws: List[dict]
    recommended_actions: List[str]
    strengths: List[str]
    weaknesses: List[str]
    precedents: List[dict]

class PrecedentRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=2000, description="Legal question or case description")
    country: Optional[str] = Field(None, pattern="^(nepal|india)$")
    max_results: int = Field(10, ge=1, le=50)

class PrecedentResponse(BaseModel):
    query: str
    precedents: List[dict]
    cross_country_matches: List[dict]
    legal_principles: List[str]

class ArgumentAnalysisRequest(BaseModel):
    argument: str = Field(..., min_length=10, max_length=5000, description="Legal argument to analyze")
    country: Optional[str] = Field(None, pattern="^(nepal|india)$")
    opposing_view: Optional[str] = Field(None, description="Opposing argument if available")
    document_text: Optional[str] = Field(None, max_length=10000, description="Extracted text from uploaded document")

class ArgumentAnalysisResponse(BaseModel):
    strength_score: int = Field(..., ge=0, le=100, description="Argument strength score 0-100")
    strength_level: str
    supporting_laws: List[dict]
    counterarguments: List[str]
    recommendations: List[str]
    risk_factors: List[str]

class DocumentUploadResponse(BaseModel):
    filename: str
    file_type: str
    text: str
    page_count: Optional[int] = None
    char_count: int

class AITierInfoResponse(BaseModel):
    tier: str
    daily_limit: int
    features: List[str]


# ─── Tier Info ────────────────────────────────────────────────────────────

TIER_FEATURES = {
    AITier.FREE: [],
    AITier.BASIC: ["case_brief", "precedent_finder"],
    AITier.PRO: ["case_brief", "precedent_finder", "argument_analysis", "document_upload"],
    AITier.ENTERPRISE: ["case_brief", "precedent_finder", "argument_analysis", "document_upload", "priority_processing"],
}

@router.get("/tier-info", response_model=AITierInfoResponse)
async def get_tier_info(user: User = Depends(require_role(Role.LAWYER, Role.JUDGE))):
    """Get current user's AI tier information and limits."""
    limit = TIER_LIMITS.get(user.ai_tier, 0)
    features = TIER_FEATURES.get(user.ai_tier, [])
    return AITierInfoResponse(
        tier=user.ai_tier.value,
        daily_limit=limit,
        features=features,
    )


# ─── Helpers ──────────────────────────────────────────────────────────────

def _check_ai_tier(user: User):
    """Check if user's AI tier allows access."""
    if user.role in (Role.ADMIN, Role.JUDGE):
        return  # Judges and admins bypass tier limits
    if user.role == Role.PUBLIC:
        raise HTTPException(status_code=403, detail="AI tools require a lawyer or judge account")
    limit = TIER_LIMITS.get(user.ai_tier, 0)
    if limit == 0:
        raise HTTPException(
            status_code=403,
            detail=f"Your current plan ({user.ai_tier.value}) does not include AI tools. Please upgrade."
        )


def _extract_pdf_text(content: bytes) -> tuple[str, int]:
    """Extract text from PDF. Returns (text, page_count)."""
    import io
    import pdfplumber
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pdf.pages[i].extract_text() or "" for i in range(len(pdf.pages))), len(pdf.pages)


def _extract_image_info(content: bytes, filename: str) -> str:
    """Extract metadata from image (no OCR without tesseract). Returns description."""
    import io
    from PIL import Image
    img = Image.open(io.BytesIO(content))
    w, h = img.size
    fmt = img.format or "unknown"
    mode = img.mode
    return f"[Image: {filename} — {fmt} format, {w}x{h} pixels, {mode} color mode. Note: OCR is not available on this server. Please paste the document text manually for analysis.]"


# ─── Document Upload ──────────────────────────────────────────────────────

@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(require_role(Role.LAWYER, Role.JUDGE)),
):
    """Upload a document (PDF, TXT, image) and extract text for AI analysis."""
    _check_ai_tier(user)

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024*1024)}MB.")

    content_type = file.content_type or ""
    file_type = ALLOWED_TYPES.get(content_type)

    if not file_type:
        # Fallback: check filename extension
        name = (file.filename or "").lower()
        if name.endswith(".pdf"):
            file_type = "pdf"
        elif name.endswith((".txt", ".md")):
            file_type = "txt"
        elif name.endswith((".png", ".jpg", ".jpeg", ".webp")):
            file_type = "image"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}. Accepted: PDF, TXT, PNG, JPG, WEBP.")

    try:
        if file_type == "pdf":
            text, page_count = _extract_pdf_text(content)
            return DocumentUploadResponse(
                filename=file.filename or "document.pdf",
                file_type="pdf",
                text=text[:10000],
                page_count=page_count,
                char_count=len(text),
            )
        elif file_type == "txt":
            text = content.decode("utf-8", errors="replace")
            return DocumentUploadResponse(
                filename=file.filename or "document.txt",
                file_type="txt",
                text=text[:10000],
                char_count=len(text),
            )
        elif file_type == "image":
            desc = _extract_image_info(content, file.filename or "image")
            return DocumentUploadResponse(
                filename=file.filename or "image",
                file_type="image",
                text=desc,
                char_count=len(desc),
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to process file: {str(e)}")

    raise HTTPException(status_code=400, detail="Unable to process uploaded file.")


# ─── Case Brief Generator ────────────────────────────────────────────────

@router.post("/case-brief", response_model=CaseBriefResponse)
async def generate_case_brief(
    request: CaseBriefRequest,
    user: User = Depends(require_role(Role.LAWYER, Role.JUDGE)),
):
    """Generate a structured case brief with relevant laws and analysis."""
    _check_ai_tier(user)
    
    # Search for relevant laws based on case description
    results = law_service.search(
        request.case_description,
        country=request.country,
        top_k=20,
        sort="relevance"
    )
    
    # Categorize results
    relevant_laws = []
    legal_areas_found = set()
    
    for r in results[:15]:
        article = r["article"]
        law_info = {
            "id": article.get("id", ""),
            "title": article.get("title", ""),
            "article_number": article.get("article_number", ""),
            "source_document": article.get("source_document", ""),
            "country": article.get("country", ""),
            "category": article.get("category", ""),
            "relevance_score": r["score"],
            "key_text": article.get("full_text", "")[:300] + "..." if len(article.get("full_text", "")) > 300 else article.get("full_text", ""),
        }
        relevant_laws.append(law_info)
        legal_areas_found.add(article.get("category", "general"))
    
    # Generate case brief structure
    case_words = request.case_description.lower().split()
    
    # Extract key issues from description
    key_issues = []
    issue_keywords = ["dispute", "violation", "breach", "claim", "allegation", "rights", "contract", "agreement"]
    for keyword in issue_keywords:
        if keyword in request.case_description.lower():
            key_issues.append(f"Issue related to {keyword}")
    
    if not key_issues:
        key_issues = [
            "Identification of applicable legal provisions",
            "Jurisdiction and venue considerations",
            "Statute of limitations analysis"
        ]
    
    # Generate recommended actions
    recommended_actions = [
        "Review all cited provisions in detail",
        "Gather supporting documentation and evidence",
        "Consult with subject matter expert if needed",
        "Prepare preliminary legal memorandum"
    ]
    
    # Analyze strengths and weaknesses
    strengths = []
    weaknesses = []
    
    if len(relevant_laws) > 5:
        strengths.append("Strong statutory support with multiple applicable provisions")
    else:
        weaknesses.append("Limited direct statutory support found")
    
    if request.country:
        strengths.append(f"Focused jurisdiction ({request.country}) provides clarity")
    else:
        weaknesses.append("Multi-jurisdictional analysis may be required")
    
    # Find related precedents
    precedents = []
    if relevant_laws:
        top_law = relevant_laws[0]
        related = find_related_provisions(
            top_law["article_number"],
            country=request.country,
            limit=5
        )
        for rel in related:
            precedents.append({
                "id": rel.get("id", ""),
                "title": rel.get("title", ""),
                "article_number": rel.get("article_number", ""),
                "relationship": rel.get("relationship_type", "related"),
                "country": rel.get("country", ""),
            })
    
    return CaseBriefResponse(
        summary=f"Case analysis based on {len(relevant_laws)} relevant legal provisions across {len(legal_areas_found)} legal areas.",
        key_issues=key_issues,
        relevant_laws=relevant_laws,
        recommended_actions=recommended_actions,
        strengths=strengths,
        weaknesses=weaknesses,
        precedents=precedents,
    )


# ─── Precedent Finder ────────────────────────────────────────────────────

@router.post("/find-precedent", response_model=PrecedentResponse)
async def find_precedent(
    request: PrecedentRequest,
    user: User = Depends(require_role(Role.LAWYER, Role.JUDGE)),
):
    """Find similar legal precedents and cross-country matches."""
    _check_ai_tier(user)
    
    # Search for relevant provisions
    results = law_service.search(
        request.query,
        country=request.country,
        top_k=request.max_results,
        sort="relevance"
    )
    
    precedents = []
    for r in results:
        article = r["article"]
        precedents.append({
            "id": article.get("id", ""),
            "title": article.get("title", ""),
            "article_number": article.get("article_number", ""),
            "source_document": article.get("source_document", ""),
            "country": article.get("country", ""),
            "category": article.get("category", ""),
            "relevance_score": r["score"],
            "excerpt": article.get("full_text", "")[:200] + "..." if len(article.get("full_text", "")) > 200 else article.get("full_text", ""),
        })
    
    # Find cross-country matches
    cross_country_matches = []
    if not request.country:
        nepal_results = law_service.search(request.query, country="nepal", top_k=5)
        india_results = law_service.search(request.query, country="india", top_k=5)
        
        for nr in nepal_results[:3]:
            cross_country_matches.append({
                "id": nr["article"].get("id", ""),
                "title": nr["article"].get("title", ""),
                "country": "nepal",
                "article_number": nr["article"].get("article_number", ""),
                "relevance_score": nr["score"],
            })
        
        for ir in india_results[:3]:
            cross_country_matches.append({
                "id": ir["article"].get("id", ""),
                "title": ir["article"].get("title", ""),
                "country": "india",
                "article_number": ir["article"].get("article_number", ""),
                "relevance_score": ir["score"],
            })
    
    # Extract legal principles
    legal_principles = []
    categories_found = set()
    for r in results:
        cat = r["article"].get("category", "")
        if cat and cat not in categories_found:
            categories_found.add(cat)
            legal_principles.append(f"Principle related to {cat.replace('_', ' ')}")
    
    if not legal_principles:
        legal_principles = ["Legal principle identification requires further analysis"]
    
    return PrecedentResponse(
        query=request.query,
        precedents=precedents,
        cross_country_matches=cross_country_matches,
        legal_principles=legal_principles,
    )


# ─── Argument Analysis ───────────────────────────────────────────────────

@router.post("/analyze-argument", response_model=ArgumentAnalysisResponse)
async def analyze_argument(
    request: ArgumentAnalysisRequest,
    user: User = Depends(require_role(Role.LAWYER, Role.JUDGE)),
):
    """Analyze the strength of a legal argument with supporting laws."""
    _check_ai_tier(user)
    
    # Combine argument with any extracted document text
    search_query = request.argument
    if request.document_text:
        # Use first 500 chars of document text as additional context
        doc_excerpt = request.document_text[:500]
        search_query = f"{request.argument} {doc_excerpt}"
    
    # Search for supporting laws
    results = law_service.search(
        search_query,
        country=request.country,
        top_k=15,
        sort="relevance"
    )
    
    supporting_laws = []
    for r in results[:10]:
        article = r["article"]
        supporting_laws.append({
            "id": article.get("id", ""),
            "title": article.get("title", ""),
            "article_number": article.get("article_number", ""),
            "source_document": article.get("source_document", ""),
            "country": article.get("country", ""),
            "relevance_score": r["score"],
            "key_text": article.get("full_text", "")[:200] + "..." if len(article.get("full_text", "")) > 200 else article.get("full_text", ""),
        })
    
    # Calculate strength score
    strength_score = 50  # Base score
    
    # Adjust based on number of supporting laws
    if len(supporting_laws) > 10:
        strength_score += 20
    elif len(supporting_laws) > 5:
        strength_score += 10
    elif len(supporting_laws) < 3:
        strength_score -= 15
    
    # Adjust based on relevance scores
    avg_relevance = sum(r["score"] for r in results[:5]) / min(5, len(results)) if results else 0
    if avg_relevance > 0.8:
        strength_score += 15
    elif avg_relevance > 0.6:
        strength_score += 5
    elif avg_relevance < 0.3:
        strength_score -= 10
    
    # Adjust for country specificity
    if request.country:
        strength_score += 5
    
    strength_score = max(0, min(100, strength_score))
    
    # Determine strength level
    if strength_score >= 80:
        strength_level = "Strong"
    elif strength_score >= 60:
        strength_level = "Moderate"
    elif strength_score >= 40:
        strength_level = "Weak"
    else:
        strength_level = "Very Weak"
    
    # Generate counterarguments
    counterarguments = []
    if request.opposing_view:
        counterarguments.append(f"Opposing view: {request.opposing_view}")
    
    counterarguments.extend([
        "Consider alternative interpretations of cited provisions",
        "Examine potential jurisdictional challenges",
        "Review recent amendments or judicial interpretations"
    ])
    
    # Generate recommendations
    recommendations = [
        "Strengthen argument with additional supporting precedents",
        "Address potential counterarguments proactively",
        "Consider seeking expert opinion on complex legal issues"
    ]
    
    if strength_score < 60:
        recommendations.append("Consider alternative legal theories or approaches")
    
    # Identify risk factors
    risk_factors = []
    if len(supporting_laws) < 5:
        risk_factors.append("Limited supporting legislation")
    
    if not request.country:
        risk_factors.append("Multi-jurisdictional uncertainty")
    
    risk_factors.extend([
        "Potential for judicial discretion in application",
        "Evolving legal standards in this area"
    ])
    
    return ArgumentAnalysisResponse(
        strength_score=strength_score,
        strength_level=strength_level,
        supporting_laws=supporting_laws,
        counterarguments=counterarguments,
        recommendations=recommendations,
        risk_factors=risk_factors,
    )
