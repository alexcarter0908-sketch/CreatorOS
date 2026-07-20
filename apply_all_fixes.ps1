# ======================================================================
# Creator OS - Complete Fix Script
# Run this from the project root directory: CreatorOS-main
# ======================================================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Creator OS - Complete Fix Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------
# FIX 1: Frontend - Remove invalid 'provider' field from API call
# ---------------------------------------------------------------
Write-Host "[FIX 1] Fixing Frontend: Removing invalid 'provider' field..." -ForegroundColor Yellow

$frontendFile = "frontend\features\command-center\components\CommandInput.tsx"
if (Test-Path $frontendFile) {
    $content = Get-Content $frontendFile -Raw
    $content = $content -replace ',\s*provider:\s*"openai"', ''
    $content | Set-Content $frontendFile
    Write-Host "  DONE: Removed 'provider: openai' from API payload" -ForegroundColor Green
} else {
    Write-Host "  WARNING: File not found: $frontendFile" -ForegroundColor Red
}

# ---------------------------------------------------------------
# FIX 2: Frontend - Fix updateCommand -> updateMessage
# ---------------------------------------------------------------
Write-Host ""
Write-Host "[FIX 2] Fixing Frontend: updateCommand -> updateMessage..." -ForegroundColor Yellow

if (Test-Path $frontendFile) {
    $content = Get-Content $frontendFile -Raw
    $content = $content -replace '\bupdateCommand\b', 'updateMessage'
    $content | Set-Content $frontendFile
    Write-Host "  DONE: Replaced 'updateCommand' with 'updateMessage'" -ForegroundColor Green
} else {
    Write-Host "  WARNING: File not found: $frontendFile" -ForegroundColor Red
}

# ---------------------------------------------------------------
# FIX 3: Backend - Add Smart Intent Routing to commands.py
# ---------------------------------------------------------------
Write-Host ""
Write-Host "[FIX 3] Fixing Backend: Adding Smart Intent Routing..." -ForegroundColor Yellow

$backendFile = "backend\app\api\v1\endpoints\commands.py"
if (Test-Path $backendFile) {
    $content = Get-Content $backendFile -Raw

    # 3a: Add detect_intent function after detect_asset_type
    $intentFunction = @"

def detect_intent(command: str) -> str:
    """
    Lightweight intent router. Uses keyword/pattern matching instead of LLM to keep speed high.
    Returns: 'conversation', 'search', 'create', or 'code'.

    - conversation: "Hi", "Hello", "How are you", "Good morning", "thanks", "ok", etc.
    - search: "What is...", "Who is...", "Find...", "Search for...", "latest news on..."
    - create: "Write a script", "Make a video", "Create thumbnail", "Generate..."
    - code: "Write code", "Fix bug", "Python script", "React component", etc.
    """
    cmd = command.lower().strip()

    # 1. CODE intent - only if explicitly about coding/building
    code_keywords = ["write code", "python script", "javascript code", "typescript code",
                     "react component", "html page", "css style", "debug this", "build a script",
                     "code a", "program", "algorithm", "function", "class"]
    if any(k in cmd for k in code_keywords):
        return "code"

    # 2. CREATE intent - asset generation requests
    create_keywords = ["write a script", "create a script", "make a video", "make a reel",
                       "make a thumbnail", "create thumbnail", "design a thumbnail",
                       "generate a video", "generate a script", "write a blog",
                       "write an article", "write a post", "make a poster", "make a banner",
                       "create a logo", "design a logo", "voiceover", "tts", "text to speech",
                       "make a photo", "generate an image", "make a photo", "create a photo",
                       "video ban", "thumbnail ban", "script likh", "seo karo"]
    if any(k in cmd for k in create_keywords):
        return "create"

    # 3. SEARCH intent - factual/research questions
    search_keywords = ["what is", "who is", "how to", "where is", "when did",
                       "why does", "latest news", "current state", "find out",
                       "search for", "trending", "market analysis", "research about",
                       "statistics", "data about", "comparison", "review of"]
    if any(k in cmd for k in search_keywords):
        return "search"

    # 4. CONVERSATION intent (default fallback) - casual chat
    return "conversation"

"@

    # Find the position after detect_asset_type function and insert detect_intent
    $lines = $content -split "`n"
    $insertIndex = -1
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match '^\s*return "text"\s*$') {
            # Check if next few lines are empty (end of function)
            if ($i + 1 -lt $lines.Length -and $lines[$i+1] -match '^\s*$') {
                $insertIndex = $i + 2
                break
            }
        }
    }

    if ($insertIndex -gt 0) {
        $newLines = @()
        $newLines += $lines[0..($insertIndex - 1)]
        $newLines += $intentFunction -split "`n"
        $newLines += ""
        $newLines += $lines[$insertIndex..($lines.Length - 1)]
        $content = $newLines -join "`n"
        Write-Host "  DONE: Added detect_intent() function" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Could not find insert point for detect_intent" -ForegroundColor Red
    }

    # 3b: Replace the asset creation block in /run endpoint with intent-aware routing
    $oldBlock = '    asset_type = detect_asset_type(request.command)'
    $newBlock = @"    intent = detect_intent(request.command)

    # CONVERSATION: reply directly without asset pipeline (instant response)
    if intent == "conversation":
        try:
            from app.services.providers.implementations.groq.groq_provider import GroqProvider
            groq = GroqProvider()

            # Build chat prompt with system instruction for conversational mode
            system_instruction = (
                "You are the AI assistant for Creator OS, a complete AI video creation operating system. "
                "Keep your replies conversational, concise, and friendly. "
                "Do NOT perform web searches unless the user explicitly asks a factual question. "
                "Do NOT generate scripts, videos, or assets unless the user explicitly asks you to create something. "
                "If the user says hello, greets you, or asks how you are, respond warmly and briefly. "
                "If the user asks about your capabilities, explain that you can create scripts, videos, thumbnails, "
                "voiceovers, SEO content, and publish directly to YouTube and social media."
            )

            # Build full prompt with history
            chat_messages = []
            chat_messages.append({"role": "system", "content": system_instruction})

            if history:
                for msg in history:
                    chat_messages.append(msg)

            chat_messages.append({"role": "user", "content": request.command})

            # Use Groq's chat completion for fast conversational response
            reply_text = await groq.complete_chat(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                prompt=chat_messages,
            )

            convo_repo.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=reply_text,
                status="completed",
                asset_id=None,
                extra_metadata=None,
            )

            return {
                "message": reply_text,
                "conversation_id": conversation.id,
                "intent": "conversation"
            }
        except Exception as e:
            convo_repo.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content="",
                status="failed",
                error_message=str(e),
            )
            raise HTTPException(status_code=500, detail=str(e)) from e

    # SEARCH: use web search before going through orchestrator
    if intent == "search":
        try:
            from app.services.research.web_search import web_search_with_sources

            search_context, sources = web_search_with_sources(
                request.command,
                max_results=6,
                deep=False,
            )

            from app.services.providers.implementations.groq.groq_provider import GroqProvider
            groq = GroqProvider()

            search_instruction = (
                "You are the AI assistant for Creator OS. "
                "You have web search results below. Provide a concise, accurate answer based on these results. "
                "Cite your sources at the end. Keep the response helpful and to the point."
            )

            chat_prompt = f"{search_instruction}\n\nSearch Results:\n{search_context}\n\nUser question: {request.command}"

            if history:
                for msg in history:
                    chat_prompt += f"\n{msg['role']}: {msg['content']}"

            reply_text = await groq.complete_chat(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                prompt=chat_prompt,
            )

            convo_repo.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=reply_text,
                status="completed",
                asset_id=None,
                extra_metadata={"sources": sources} if sources else None,
            )

            return {
                "message": reply_text,
                "conversation_id": conversation.id,
                "intent": "search",
                "sources": sources
            }
        except Exception as e:
            convo_repo.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content="",
                status="failed",
                error_message=str(e),
            )
            raise HTTPException(status_code=500, detail=str(e)) from e

    # CREATE or CODE: go through normal asset pipeline
    asset_type = detect_asset_type(request.command)"@

    $content = $content.Replace($oldBlock, $newBlock)

    # Save the modified file
    $content | Set-Content $backendFile
    Write-Host "  DONE: Replaced asset block with intent-aware routing" -ForegroundColor Green
} else {
    Write-Host "  WARNING: File not found: $backendFile" -ForegroundColor Red
}

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  All fixes applied successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Changes made:" -ForegroundColor White
Write-Host "  1. Frontend: Removed invalid 'provider' field" -ForegroundColor Green
Write-Host "  2. Frontend: Fixed updateCommand -> updateMessage" -ForegroundColor Green
Write-Host "  3. Backend: Added Smart Intent Routing" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  - Restart your backend server" -ForegroundColor White
Write-Host "  - Restart your frontend (or hard refresh browser)" -ForegroundColor White
Write-Host "  - Test with: 'Hi', 'Write a script for a video about AI', 'What is quantum computing?'" -ForegroundColor White
