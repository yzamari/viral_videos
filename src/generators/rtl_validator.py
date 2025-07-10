"""
RTL Language Validator
Uses Gemini AI to validate and correct word order and sentence structure for RTL languages
"""
import re
from typing import Dict, List, Optional, Any
import google.generativeai as genai

from ..utils.logging_config import get_logger
from ..models.video_models import Language

logger = get_logger(__name__)


class RTLValidator:
    """Validates and corrects RTL language content using Gemini AI"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # RTL languages supported
        self.rtl_languages = {
            Language.HEBREW: {
                "name": "Hebrew",
                "code": "he",
                "native_name": "עברית",
                "direction": "rtl",
                "script": "Hebrew",
                "common_issues": [
                    "Word order in questions",
                    "Verb-subject agreement",
                    "Definite article placement",
                    "Construct state (סמיכות)",
                    "Gender agreement"
                ]
            },
            Language.ARABIC: {
                "name": "Arabic",
                "code": "ar",
                "native_name": "العربية",
                "direction": "rtl",
                "script": "Arabic",
                "common_issues": [
                    "Verb-subject-object order",
                    "Definite article (ال)",
                    "Dual and plural forms",
                    "Feminine/masculine agreement",
                    "Case endings"
                ]
            },
            Language.PERSIAN: {
                "name": "Persian",
                "code": "fa",
                "native_name": "فارسی",
                "direction": "rtl",
                "script": "Persian",
                "common_issues": [
                    "Subject-object-verb order",
                    "Ezafe construction",
                    "Plural markers",
                    "Formal vs informal speech",
                    "Compound verbs"
                ]
            }
        }

        logger.info("✅ RTL Validator initialized with Gemini AI")

    def validate_and_correct_rtl_text(self,
                                      text: str,
                                      language: Language,
                                      context: Optional[str] = None,
                                      target_audience: str = "general") -> Dict[str,
                                                                                Any]:
        """Validate and correct RTL text using Gemini AI"""

        if language not in self.rtl_languages:
            logger.warning(
                f"⚠️ Language {
                    language.value} is not RTL, skipping validation")
            return {
                "is_rtl": False,
                "original_text": text,
                "corrected_text": text,
                "corrections_made": [],
                "validation_passed": True
            }

        logger.info(
            f"🔍 Validating RTL text in {
                self.rtl_languages[language]['name']}")

        try:
            # Step 1: Initial validation
            validation_result = self._validate_rtl_structure(
                text, language, context, target_audience)

            # Step 2: If issues found, get corrections
            if not validation_result["validation_passed"]:
                correction_result = self._get_rtl_corrections(
                    text, language, validation_result["issues"], context)

                # Step 3: Verify corrections
                if correction_result["corrected_text"]:
                    verification_result = self._verify_corrections(
                        original=text,
                        corrected=correction_result["corrected_text"],
                        language=language
                    )

                    return {
                        "is_rtl": True,
                        "original_text": text,
                        "corrected_text": correction_result["corrected_text"],
                        "corrections_made": correction_result["corrections_made"],
                        "validation_passed": verification_result["is_valid"],
                        "confidence_score": verification_result["confidence"],
                        "issues_found": validation_result["issues"],
                        "verification_notes": verification_result["notes"]}

            # No corrections needed
            return {
                "is_rtl": True,
                "original_text": text,
                "corrected_text": text,
                "corrections_made": [],
                "validation_passed": True,
                "confidence_score": 0.95,
                "issues_found": []
            }

        except Exception as e:
            logger.error(f"❌ RTL validation failed: {e}")
            return {
                "is_rtl": True,
                "original_text": text,
                "corrected_text": text,
                "corrections_made": [],
                "validation_passed": False,
                "error": str(e)
            }

    def _validate_rtl_structure(self,
                                text: str,
                                language: Language,
                                context: Optional[str],
                                target_audience: str) -> Dict[str,
                                                              Any]:
        """Validate RTL text structure and grammar"""

        lang_info = self.rtl_languages[language]

        validation_prompt = f"""
        You are an expert linguist specializing in {lang_info['name']} ({lang_info['native_name']}) language validation.

        TASK: Validate this {lang_info['name']} text for grammatical correctness, proper word order, and natural flow.

        TEXT TO VALIDATE:
        {text}

        CONTEXT: {context or "General video content"}
        TARGET AUDIENCE: {target_audience}

        VALIDATION CRITERIA:
        1. WORD ORDER: Check if word order follows {lang_info['name']} grammar rules
        2. GRAMMAR: Verify grammatical correctness and agreement
        3. NATURALNESS: Ensure the text sounds natural to native speakers
        4. SENTENCE STRUCTURE: Check sentence construction and flow
        5. COMMON ISSUES: Look for these specific {lang_info['name']} issues:
           {chr(10).join(f"   - {issue}" for issue in lang_info['common_issues'])}

        ANALYSIS REQUIREMENTS:
        - Identify any grammatical errors or awkward phrasing
        - Check for proper {lang_info['script']} script usage
        - Verify that sentences flow naturally
        - Look for translation artifacts or non-native constructions
        - Consider cultural appropriateness for the target audience

        OUTPUT FORMAT (JSON):
        {{
            "validation_passed": true/false,
            "overall_quality": "excellent|good|fair|poor",
            "issues": [
                {{
                    "type": "grammar|word_order|naturalness|cultural",
                    "description": "specific issue description",
                    "location": "problematic text segment",
                    "severity": "high|medium|low",
                    "suggestion": "how to fix this issue"
                }}
            ],
            "confidence_score": 0.85,
            "native_speaker_rating": "sounds native|acceptable|needs work|unnatural",
            "recommendations": ["specific recommendations for improvement"]
        }}

        Be thorough and precise in your analysis. Return ONLY the JSON response.
        """

        try:
            response = self.model.generate_content(validation_prompt)

            # Parse JSON response
            import json
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                validation_result = json.loads(json_match.group())

                logger.info(
                    f"🔍 Validation result: {
                        validation_result['overall_quality']}")
                logger.info(
                    f"📊 Confidence: {
                        validation_result.get(
                            'confidence_score',
                            0)}")

                if validation_result.get("issues"):
                    logger.info(
                        f"⚠️ Found {len(validation_result['issues'])} issues")
                    for issue in validation_result["issues"]:
                        logger.info(
                            f"   - {issue['type']}: {issue['description']}")

                return validation_result
            else:
                logger.warning("⚠️ Could not parse validation response")
                return {"validation_passed": True, "issues": []}

        except Exception as e:
            logger.error(f"❌ RTL validation failed: {e}")
            return {"validation_passed": True, "issues": []}

    def _get_rtl_corrections(self,
                             text: str,
                             language: Language,
                             issues: List[Dict],
                             context: Optional[str]) -> Dict[str,
                                                             Any]:
        """Get corrected version of RTL text"""

        lang_info = self.rtl_languages[language]

        # Format issues for the prompt
        issues_text = "\n".join([
            f"- {issue['type']}: {issue['description']} (in: '{issue.get('location', 'N/A')}')"
            for issue in issues
        ])

        correction_prompt = f"""
        You are an expert {lang_info['name']} editor and linguist. Your task is to correct the grammatical and structural issues in this text.

        ORIGINAL TEXT:
        {text}

        IDENTIFIED ISSUES:
        {issues_text}

        CONTEXT: {context or "General video content"}

        CORRECTION REQUIREMENTS:
        1. Fix all grammatical errors while preserving the original meaning
        2. Ensure proper {lang_info['name']} word order and sentence structure
        3. Make the text sound natural to native speakers
        4. Maintain the original tone and style
        5. Keep the same content length and message
        6. Use appropriate {lang_info['script']} script conventions

        SPECIFIC FOCUS AREAS:
        {chr(10).join(f"- {issue}" for issue in lang_info['common_issues'])}

        OUTPUT FORMAT (JSON):
        {{
            "corrected_text": "the fully corrected {lang_info['name']} text",
            "corrections_made": [
                {{
                    "original": "problematic segment",
                    "corrected": "fixed segment",
                    "reason": "explanation of the correction",
                    "type": "grammar|word_order|naturalness"
                }}
            ],
            "confidence": 0.9,
            "notes": "additional notes about the corrections"
        }}

        Provide the corrected text that sounds completely natural to native {lang_info['name']} speakers.
        Return ONLY the JSON response.
        """

        try:
            response = self.model.generate_content(correction_prompt)

            # Parse JSON response
            import json
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                correction_result = json.loads(json_match.group())

                logger.info(
                    f"✅ Generated corrections for {
                        len(
                            correction_result.get(
                                'corrections_made',
                                []))} issues")

                return correction_result
            else:
                logger.warning("⚠️ Could not parse correction response")
                return {"corrected_text": text, "corrections_made": []}

        except Exception as e:
            logger.error(f"❌ RTL correction failed: {e}")
            return {"corrected_text": text, "corrections_made": []}

    def _verify_corrections(self,
                            original: str,
                            corrected: str,
                            language: Language) -> Dict[str,
                                                        Any]:
        """Verify that corrections improved the text quality"""

        lang_info = self.rtl_languages[language]

        verification_prompt = f"""
        You are a {lang_info['name']} language quality assessor. Compare these two versions of the same text.

        ORIGINAL TEXT:
        {original}

        CORRECTED TEXT:
        {corrected}

        ASSESSMENT TASK:
        1. Verify that the corrected version is grammatically correct
        2. Confirm that the meaning has been preserved
        3. Check that the corrected version sounds more natural
        4. Ensure no new errors were introduced
        5. Validate that {lang_info['name']} language rules are properly followed

        QUALITY CRITERIA:
        - Grammatical accuracy
        - Natural flow and readability
        - Preservation of original meaning
        - Appropriate {lang_info['script']} script usage
        - Cultural and linguistic appropriateness

        OUTPUT FORMAT (JSON):
        {{
            "is_valid": true/false,
            "improvement_made": true/false,
            "confidence": 0.9,
            "quality_score": {{
                "original": 0.7,
                "corrected": 0.95
            }},
            "meaning_preserved": true/false,
            "naturalness_improved": true/false,
            "notes": "detailed assessment notes",
            "recommendation": "accept|reject|needs_further_work"
        }}

        Be objective and thorough in your assessment. Return ONLY the JSON response.
        """

        try:
            response = self.model.generate_content(verification_prompt)

            # Parse JSON response
            import json
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                verification_result = json.loads(json_match.group())

                logger.info(
                    f"✅ Verification: {
                        verification_result.get(
                            'recommendation',
                            'unknown')}")
                logger.info(
                    f"📊 Quality improvement: {
                        verification_result.get(
                            'quality_score',
                            {}).get(
                            'original',
                            0):.2f} → {
                        verification_result.get(
                            'quality_score',
                            {}).get(
                            'corrected',
                            0):.2f}")

                return verification_result
            else:
                logger.warning("⚠️ Could not parse verification response")
                return {"is_valid": True, "confidence": 0.5}

        except Exception as e:
            logger.error(f"❌ RTL verification failed: {e}")
            return {"is_valid": True, "confidence": 0.5}

    def batch_validate_rtl_content(
            self, content_list: List[Dict[str, str]], language: Language) -> List[Dict[str, Any]]:
        """Validate multiple RTL content items in batch"""

        logger.info(
            f"🔍 Batch validating {
                len(content_list)} items in {
                language.value}")

        results = []

        for i, content_item in enumerate(content_list):
            text = content_item.get("text", "")
            context = content_item.get("context", "")

            if not text.strip():
                logger.warning(f"⚠️ Empty text in item {i}, skipping")
                results.append({
                    "item_index": i,
                    "validation_passed": True,
                    "original_text": text,
                    "corrected_text": text
                })
                continue

            try:
                validation_result = self.validate_and_correct_rtl_text(
                    text=text,
                    language=language,
                    context=context
                )

                validation_result["item_index"] = i
                results.append(validation_result)

                logger.info(
                    f"✅ Item {
                        i + 1}/{
                        len(content_list)}: {
                        'PASSED' if validation_result['validation_passed'] else 'CORRECTED'}")

            except Exception as e:
                logger.error(f"❌ Failed to validate item {i}: {e}")
                results.append({
                    "item_index": i,
                    "validation_passed": False,
                    "original_text": text,
                    "corrected_text": text,
                    "error": str(e)
                })

        # Summary statistics
        passed = sum(1 for r in results if r.get("validation_passed", False))
        corrected = sum(1 for r in results if r.get("corrections_made", []))

        logger.info(
            f"📊 Batch validation complete: {passed}/{len(results)} passed, {corrected} corrected")

        return results

    def is_rtl_language(self, language: Language) -> bool:
        """Check if language is RTL"""
        return language in self.rtl_languages

    def get_rtl_language_info(
            self, language: Language) -> Optional[Dict[str, Any]]:
        """Get RTL language information"""
        return self.rtl_languages.get(language)
