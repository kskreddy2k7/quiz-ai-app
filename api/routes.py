import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from .models import TopicQuizRequest, TeacherHelpRequest, AIHelpRequest
from services.ai_service import ai_service
from services.file_service import file_service
from utils.helpers import get_random_quote

from utils.limiter import limiter

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "ai_status": ai_service.status,
        "provider": ai_service.provider
    }

@router.post("/generate_topic")
@limiter.limit("5/minute")
async def generate_topic(req: TopicQuizRequest, request: Request):
    if not ai_service.has_ai:
        raise HTTPException(status_code=400, detail="AI not configured")
    
    # Map user-facing question types to strict modes
    MODE_MAPPING = {
        "Single Choice": "single_only",
        "Multiple Choice": "multi_only",
        "True/False": "truefalse_only",
        "Mixed": "mixed"
    }
    
    mode = MODE_MAPPING.get(req.question_type, "single_only")
    
    # Generate strict mode-specific prompts
    if mode == "single_only":
        prompt = f"""
        Generate {req.num_questions} HIGH-QUALITY SINGLE-CHOICE questions about "{req.topic}" in {req.language}.
        Difficulty: {req.difficulty}
        
        QUALITY STANDARDS (CRITICAL):
        ✓ Questions must be CLEAR, UNAMBIGUOUS, and PROFESSIONALLY WRITTEN
        ✓ Test UNDERSTANDING and APPLICATION, not just memorization
        ✓ Use REAL-WORLD scenarios and practical examples when possible
        ✓ Avoid trick questions or unnecessarily confusing wording
        ✓ All wrong options (distractors) must be PLAUSIBLE but clearly incorrect
        ✓ Options should be similar in length and complexity
        ✓ No "All of the above" or "None of the above" options
        
        TECHNICAL RULES:
        1. Each question MUST have EXACTLY ONE correct answer
        2. Set "type": "single" for ALL questions
        3. Provide exactly 4 well-crafted options per question
        4. Use "answer": "exact option text" (string, NOT array)
        5. DO NOT include "correct_answers" field
        6. DO NOT generate multiple-choice or True/False questions
        
        EXPLANATION REQUIREMENTS:
        - Write 2-3 clear, educational sentences
        - Explain WHY the correct answer is right
        - Explain the key concept being tested
        - Help students understand and remember the principle
        
        Return ONLY a valid JSON array:
        [
            {{
                "type": "single",
                "prompt": "Clear, professional question in {req.language}...",
                "choices": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A",
                "explanation": "Comprehensive explanation covering why this is correct and the underlying concept..."
            }}
        ]
        """
    
    elif mode == "multi_only":
        prompt = f"""
        Generate {req.num_questions} HIGH-QUALITY MULTIPLE-CHOICE questions about "{req.topic}" in {req.language}.
        Difficulty: {req.difficulty}
        
        QUALITY STANDARDS (CRITICAL):
        ✓ Questions must be CLEAR and test DEEP UNDERSTANDING
        ✓ Multiple correct answers should be LOGICALLY RELATED
        ✓ Use scenarios that require ANALYSIS and CRITICAL THINKING
        ✓ Wrong options must be plausible but clearly incorrect
        ✓ Avoid making it too easy to guess by elimination
        
        TECHNICAL RULES:
        1. Each question MUST have TWO OR MORE correct answers (typically 2-3)
        2. Set "type": "multi" for ALL questions
        3. Provide 4-6 well-crafted options per question
        4. Use "correct_answers": ["option1", "option2"] (array with 2+ items)
        5. DO NOT include "answer" field
        6. DO NOT generate single-choice or True/False questions
        
        EXPLANATION REQUIREMENTS:
        - Explain WHY each correct answer is right
        - Explain WHY incorrect options are wrong
        - Help students understand the underlying pattern
        
        Return ONLY a valid JSON array:
        [
            {{
                "type": "multi",
                "prompt": "Professional question requiring analysis in {req.language}...",
                "choices": ["Option A", "Option B", "Option C", "Option D", "Option E"],
                "correct_answers": ["Option A", "Option C"],
                "explanation": "Comprehensive explanation of why A and C are correct and why others are not..."
            }}
        ]
        """
    
    elif mode == "truefalse_only":
        prompt = f"""
        Generate {req.num_questions} HIGH-QUALITY TRUE/FALSE questions about "{req.topic}" in {req.language}.
        Difficulty: {req.difficulty}
        
        QUALITY STANDARDS (CRITICAL):
        ✓ Statements must be PRECISE and UNAMBIGUOUS
        ✓ Test FACTUAL KNOWLEDGE and CONCEPTUAL UNDERSTANDING
        ✓ Avoid overly simple or obvious statements
        ✓ Use specific facts, dates, or technical details when appropriate
        ✓ Make statements challenging but fair
        
        TECHNICAL RULES:
        1. Each question MUST have EXACTLY TWO options: "True" and "False"
        2. Set "type": "truefalse" for ALL questions
        3. Use "answer": "True" or "answer": "False" (string)
        4. DO NOT include "correct_answers" field
        5. DO NOT generate MCQs with 3+ options
        
        EXPLANATION REQUIREMENTS:
        - Explain WHY the statement is true or false
        - Provide supporting facts, evidence, or reasoning
        - Clarify any nuances or common misconceptions
        
        Return ONLY a valid JSON array:
        [
            {{
                "type": "truefalse",
                "prompt": "Precise, factual statement in {req.language}...",
                "choices": ["True", "False"],
                "answer": "True",
                "explanation": "Clear explanation with supporting facts and reasoning..."
            }}
        ]
        """
    
    else:  # mixed mode
        # Calculate distribution for mixed mode
        num_single = max(1, int(req.num_questions * 0.4))
        num_multi = max(1, int(req.num_questions * 0.4))
        num_tf = max(1, req.num_questions - num_single - num_multi)
        
        prompt = f"""
        Generate EXACTLY {req.num_questions} questions in MIXED mode about "{req.topic}" in {req.language}.
        Difficulty: {req.difficulty}
        
        CRITICAL DISTRIBUTION REQUIREMENT - YOU MUST FOLLOW THIS EXACTLY:
        - Generate EXACTLY {num_single} "single" type questions (one correct answer)
        - Generate EXACTLY {num_multi} "multi" type questions (2+ correct answers)
        - Generate EXACTLY {num_tf} "truefalse" type questions (True/False only)
        
        TOTAL: {num_single} + {num_multi} + {num_tf} = {req.num_questions} questions
        
        CRITICAL RULES - DO NOT BREAK:
        1. You MUST generate ALL THREE types of questions in the exact quantities specified above
        2. DO NOT generate all questions as the same type
        3. MUST set "type" field correctly for EACH question
        4. Each question MUST follow its type's rules exactly:
           
           For "single" type ({num_single} questions):
           - Set "type": "single"
           - Provide exactly 4 choices
           - Use "answer": "exact option text" (string, NOT array)
           - DO NOT include "correct_answers" field
           
           For "multi" type ({num_multi} questions):
           - Set "type": "multi"
           - Provide 4-6 choices
           - Use "correct_answers": ["option1", "option2"] (array with 2+ items)
           - DO NOT include "answer" field
           
           For "truefalse" type ({num_tf} questions):
           - Set "type": "truefalse"
           - Provide EXACTLY 2 choices: ["True", "False"]
           - Use "answer": "True" or "answer": "False" (string)
           - DO NOT include "correct_answers" field
        
        Return ONLY a valid JSON array with ALL THREE types mixed:
        [
            {{
                "type": "single",
                "prompt": "Question in {req.language}...",
                "choices": ["A", "B", "C", "D"],
                "answer": "A",
                "explanation": "..."
            }},
            {{
                "type": "multi",
                "prompt": "Question in {req.language}...",
                "choices": ["A", "B", "C", "D"],
                "correct_answers": ["A", "C"],
                "explanation": "..."
            }},
            {{
                "type": "truefalse",
                "prompt": "Statement in {req.language}...",
                "choices": ["True", "False"],
                "answer": "True",
                "explanation": "..."
            }}
        ]
        
        REMINDER: Generate {num_single} single + {num_multi} multi + {num_tf} truefalse = {req.num_questions} total questions
        """
    
    try:
        questions = await ai_service.generate_quiz(prompt)
        
        # Validate and enforce question types
        questions = ai_service.validate_question_types(questions, mode)
        
        # CRITICAL: Ensure we have the requested number of questions
        if len(questions) < req.num_questions:
            print(f"⚠️ AI generated only {len(questions)} questions, requested {req.num_questions}. Padding...")
            
            # Pad with additional questions using offline generator
            needed = req.num_questions - len(questions)
            padding_questions = ai_service.generate_offline_quiz(req.topic, needed, req.difficulty, mode)
            questions.extend(padding_questions)
        
        # Trim if AI generated too many
        questions = questions[:req.num_questions]
        
        return {"questions": questions}
    except Exception as e:
        print(f"Error in generate_topic: {e}") # Debug log
        # Fallback to offline quiz
        offline_questions = ai_service.generate_offline_quiz(req.topic, req.num_questions, req.difficulty, mode)
        return {"questions": offline_questions}

@router.post("/generate_file")
@limiter.limit("3/minute")
async def generate_file(
    request: Request,
    file: UploadFile = File(...),
    difficulty: str = Form("Medium"),
    num_questions: int = Form(5),
    question_type: str = Form("Single Choice"),
    language: str = Form("English")
):
    if not ai_service.has_ai:
        raise HTTPException(status_code=400, detail="AI not configured")
    
    # Limit question count
    num_questions = min(max(num_questions, 1), 20)
    
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extract text from file
        text = await file_service.extract_text(filepath)
        if text.startswith("Error"):
             # Print error for debugging
             print(f"❌ TEXT EXTRACTION ERROR: {text}")
             raise HTTPException(status_code=400, detail=text)
        
        # DEBUG LOGGING - See what is actually extracted
        print(f"📄 EXTRACTED TEXT SAMPLE (Len: {len(text)}):\n{text[:500]}...")
        
        # VALIDATE TEXT CONTENT - Increased to 300 chars to ensure minimal context
        if len(text.strip()) < 300:
            print(f"⚠️ REJECTED: Text too short ({len(text.strip())} chars)")
            detailed_msg = f"File contains insufficient text ({len(text.strip())} characters). Extracted: {text[:100]}..."
            raise HTTPException(status_code=400, detail=f"File content is to short or unreadable. It might be scanned/image-based. Please use a text-based PDF/DOCX.\n\nDebug: {detailed_msg}")
            
        # Limit text length for processing
        text_excerpt = text[:8000]  # Increased from 5000 for better context
        
        # Map user-facing question types to strict modes
        MODE_MAPPING = {
            "Single Choice": "single_only",
            "Multiple Choice": "multi_only",
            "True/False": "truefalse_only",
            "Mixed": "mixed"
        }
        
        mode = MODE_MAPPING.get(question_type, "single_only")
        
        # Generate strict mode-specific prompts (same quality as topic generation)
        if mode == "single_only":
            prompt = f"""
            Based on the following text, generate {num_questions} HIGH-QUALITY SINGLE-CHOICE questions in {language}.
            Difficulty: {difficulty}
            
            QUALITY STANDARDS (CRITICAL):
            ✓ Questions MUST be based on the TEXT CONTENT provided
            ✓ Test UNDERSTANDING of the material, not just memorization
            ✓ Use CLEAR, PROFESSIONAL wording
            ✓ All wrong options must be PLAUSIBLE but clearly incorrect
            ✓ Questions should cover KEY CONCEPTS from the text
            
            TECHNICAL RULES:
            1. Each question MUST have EXACTLY ONE correct answer
            2. Set "type": "single" for ALL questions
            3. Provide exactly 4 well-crafted options per question
            4. Use "answer": "exact option text" (string, NOT array)
            5. DO NOT include "correct_answers" field
            
            EXPLANATION REQUIREMENTS:
            - Explain WHY the answer is correct based on the text
            - Reference specific information from the material
            - Help students understand the concept
            
            Text: {text_excerpt}
            
            Return ONLY a valid JSON array.
            """
        
        elif mode == "multi_only":
            prompt = f"""
            Based on the following text, generate {num_questions} HIGH-QUALITY MULTIPLE-CHOICE questions in {language}.
            Difficulty: {difficulty}
            
            QUALITY STANDARDS (CRITICAL):
            ✓ Questions must be based on the TEXT CONTENT provided
            ✓ Test DEEP UNDERSTANDING of the material
            ✓ Multiple correct answers should be LOGICALLY RELATED
            ✓ Wrong options must be plausible but clearly incorrect
            
            TECHNICAL RULES:
            1. Each question MUST have TWO OR MORE correct answers (typically 2-3)
            2. Set "type": "multi" for ALL questions
            3. Provide 4-6 well-crafted options per question
            4. Use "correct_answers": ["option1", "option2"] (array with 2+ items)
            5. DO NOT include "answer" field
            
            EXPLANATION REQUIREMENTS:
            - Explain WHY each correct answer is right based on the text
            - Reference specific details from the material
            - Help students understand the full concept
            
            Text: {text_excerpt}
            
            Return ONLY a valid JSON array.
            """
        
        elif mode == "truefalse_only":
            prompt = f"""
            Based on the following text, generate {num_questions} HIGH-QUALITY TRUE/FALSE questions in {language}.
            Difficulty: {difficulty}
            
            QUALITY STANDARDS (CRITICAL):
            ✓ Statements must be derived directly from the TEXT CONTENT
            ✓ Test FACTUAL ACCURACY and COMPREHENSION
            ✓ Avoid ambiguous or opinion-based statements
            ✓ Use specific facts from the text
            
            TECHNICAL RULES:
            1. Each question MUST have EXACTLY TWO options: "True" and "False"
            2. Set "type": "truefalse" for ALL questions
            3. Use "answer": "True" or "answer": "False" (string)
            4. DO NOT include "correct_answers" field
            
            EXPLANATION REQUIREMENTS:
            - Explain WHY the statement is true or false based on the text
            - Cite the specific part of the text that supports the answer
            - Clarify the correct fact if the statement is false
            
            Text: {text_excerpt}
            
            Return ONLY a valid JSON array.
            """
        
        else:  # mixed mode
            num_single = max(1, int(num_questions * 0.4))
            num_multi = max(1, int(num_questions * 0.4))
            num_tf = max(1, num_questions - num_single - num_multi)
            
            prompt = f"""
            Based on the following text, generate EXACTLY {num_questions} HIGH-QUALITY questions in MIXED mode in {language}.
            Difficulty: {difficulty}
            
            QUALITY STANDARDS (CRITICAL):
            ✓ Questions must be based on the TEXT CONTENT provided
            ✓ Test DEEP UNDERSTANDING of the material
            ✓ Use CLEAR, PROFESSIONAL wording
            
            CRITICAL DISTRIBUTION REQUIREMENT:
            - Generate EXACTLY {num_single} "single" type questions (High Quality)
            - Generate EXACTLY {num_multi} "multi" type questions (High Quality)
            - Generate EXACTLY {num_tf} "truefalse" type questions (High Quality)
            
            TOTAL: {num_single} + {num_multi} + {num_tf} = {num_questions} questions
            
            EXPLANATION REQUIREMENTS:
            - Explain WHY each answer is correct based on the text
            - Reference specific details from the material
            - Help students understand the full concept
            
            Text: {text_excerpt}
            
            Return ONLY a valid JSON array with ALL THREE types mixed.
            REMINDER: Generate {num_single} single + {num_multi} multi + {num_tf} truefalse = {num_questions} total questions
            """
        
        # Generate quiz with NO FALLBACK (we want error if AI fails, not generic questions)
        questions = await ai_service.generate_quiz(prompt, allow_fallback=False)
        
        # Validate and enforce question types
        questions = ai_service.validate_question_types(questions, mode)
        
        # Ensure correct number of questions
        if len(questions) < num_questions:
            print(f"⚠️ AI generated only {len(questions)} questions from file, requested {num_questions}. Padding...")
            needed = num_questions - len(questions)
            padding_questions = ai_service.generate_offline_quiz(f"Content from {file.filename}", needed, difficulty, mode)
            questions.extend(padding_questions)
        
        # Trim if too many
        questions = questions[:num_questions]
        
        return {
            "questions": questions,
            "filename": file.filename,
            "text_length": len(text),
            "mode": mode
        }
    except Exception as e:
        error_msg = str(e)
        print(f"❌ GENERATION ERROR: {error_msg}")
        
        # Friendly error messages
        if "Quota exceeded" in error_msg or "429" in error_msg:
            detail = "AI Limit Reached. Please try again in a few minutes or use a different API key."
        elif "AI Generation Failed" in error_msg:
             detail = f"Could not generate questions from this text. The AI service failed: {error_msg}"
        else:
            detail = f"Processing Error: {error_msg}"
            
        raise HTTPException(status_code=500, detail=detail)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@router.post("/teacher_help")
@limiter.limit("5/minute")
async def teacher_help(req: TeacherHelpRequest, request: Request):
    if not ai_service.has_ai:
         raise HTTPException(status_code=400, detail="AI not configured")
    
    prompt = f"Task: {req.task}. Topic: {req.topic}. Details: {req.details}"
    try:
        response = await ai_service.generate_text(prompt)
        return {"response": response}
    except Exception as e:
        print(f"Error in teacher_help: {e}") # Debug log
        # Fallback to offline notes
        fallback_notes = ai_service.generate_offline_notes(req.topic)
        return {"response": fallback_notes}

@router.post("/ai_help")
@limiter.limit("5/minute")
async def ai_help(req: AIHelpRequest, request: Request):
    if not ai_service.has_ai:
         raise HTTPException(status_code=400, detail="AI not configured")
    
    prompt = f"Style: {req.style}. Question: {req.question}"
    try:
        response = await ai_service.generate_text(prompt)
        return {"response": response}
    except Exception as e:
        print(f"Error in ai_help: {e}")
        return {"response": "🤖 **AI Tutor Offline**: I'm having trouble connecting to the brain right now. Please check your internet or try again later."}
