"""
Prompt Optimizer Microservice
Runs as independent HTTP server on port 8001
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
import hashlib
from typing import Dict, Any, List, Tuple
from datetime import datetime
import redis
import logging
from dataclasses import asdict

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis for caching (optional)
try:
    cache = redis.Redis(host='localhost', port=6379, decode_responses=True)
    cache.ping()
    CACHE_ENABLED = True
    logger.info("✅ Redis cache connected")
except:
    CACHE_ENABLED = False
    logger.warning("⚠️ Redis not available, running without cache")


class PromptOptimizerService:
    """Core prompt optimization logic"""
    
    def __init__(self):
        self.max_prompt_length = 500
        self.banned_terms = self._load_banned_terms()
        self.safe_keywords = ["cinematic", "professional", "4K", "artistic", "beautiful"]
        self.optimization_count = 0
        self.success_count = 0
    
    def optimize(self, prompt: Any, level: str = "moderate") -> Dict[str, Any]:
        """Optimize a prompt"""
        start_time = datetime.now()
        self.optimization_count += 1
        
        # Check cache
        cache_key = self._generate_cache_key(prompt, level)
        if CACHE_ENABLED:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for {cache_key}")
                return json.loads(cached)
        
        # Perform optimization
        optimized = self._apply_optimization(prompt, level)
        
        # Validate safety
        is_safe, issues = self.validate_safety(optimized)
        
        # Calculate success probability
        success_prob = self._calculate_success_probability(optimized, is_safe)
        
        if success_prob > 0.5:
            self.success_count += 1
        
        result = {
            "optimized_prompt": optimized,
            "original_length": len(str(prompt)),
            "optimized_length": len(optimized),
            "is_safe": is_safe,
            "safety_issues": issues,
            "success_probability": success_prob,
            "optimization_level": level,
            "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
        }
        
        # Cache result
        if CACHE_ENABLED and is_safe:
            cache.setex(cache_key, 3600, json.dumps(result))
        
        return result
    
    def validate_safety(self, prompt: str) -> Tuple[bool, List[str]]:
        """Validate prompt safety"""
        issues = []
        prompt_lower = prompt.lower()
        
        # Check banned terms
        found_banned = [term for term in self.banned_terms if term in prompt_lower]
        if found_banned:
            issues.append(f"Contains banned terms: {', '.join(found_banned[:3])}")
        
        # Check length
        if len(prompt) > self.max_prompt_length:
            issues.append(f"Too long: {len(prompt)} chars")
        
        # Check patterns
        if re.search(r'\d{4}-\d{2}-\d{2}', prompt):
            issues.append("Contains date patterns")
        
        return len(issues) == 0, issues
    
    def _apply_optimization(self, prompt: Any, level: str) -> str:
        """Apply optimization based on level"""
        if isinstance(prompt, dict):
            prompt_str = self._dict_to_text(prompt)
        else:
            prompt_str = str(prompt)
        
        if level == "minimal":
            return self._minimal_optimization(prompt_str)
        elif level == "moderate":
            return self._moderate_optimization(prompt_str)
        elif level == "aggressive":
            return self._aggressive_optimization(prompt_str)
        else:
            return self._extreme_optimization(prompt_str)
    
    def _minimal_optimization(self, text: str) -> str:
        """Remove banned terms only"""
        for term in self.banned_terms:
            text = re.sub(r'\b' + re.escape(term) + r'\b', '', text, flags=re.IGNORECASE)
        return ' '.join(text.split())
    
    def _moderate_optimization(self, text: str) -> str:
        """Simplify and clean"""
        text = self._minimal_optimization(text)
        text = re.sub(r'\([^)]+\)', '', text)
        text = re.sub(r'"[^"]+"', '', text)
        if len(text) > 500:
            text = text[:497] + "..."
        return text
    
    def _aggressive_optimization(self, text: str) -> str:
        """Keep essentials only"""
        text = self._moderate_optimization(text)
        sentences = text.split('.')[:3]
        text = '. '.join(sentences)
        if len(text) > 300:
            text = text[:297] + "..."
        return text
    
    def _extreme_optimization(self, text: str) -> str:
        """Bare minimum"""
        keywords = []
        text_lower = text.lower()
        if "scene" in text_lower or "view" in text_lower:
            keywords.append("scenic view")
        if "person" in text_lower or "people" in text_lower:
            keywords.append("person walking")
        keywords.extend(self.safe_keywords[:3])
        return " ".join(keywords)
    
    def _dict_to_text(self, prompt_dict: Dict[str, Any]) -> str:
        """Convert dict to text"""
        parts = []
        for key in ['scene', 'subject', 'style', 'description']:
            if key in prompt_dict:
                value = prompt_dict[key]
                if isinstance(value, dict):
                    parts.append(value.get('description', ''))
                else:
                    parts.append(str(value))
        return ". ".join(filter(None, parts))
    
    def _calculate_success_probability(self, prompt: str, is_safe: bool) -> float:
        """Calculate success probability"""
        if not is_safe:
            return 0.1
        
        score = 0.9
        if len(prompt) > 400:
            score -= 0.2
        elif len(prompt) > 300:
            score -= 0.1
        
        # Bonus for safe keywords
        for keyword in self.safe_keywords:
            if keyword in prompt.lower():
                score += 0.02
        
        return min(1.0, max(0.1, score))
    
    def _generate_cache_key(self, prompt: Any, level: str) -> str:
        """Generate cache key"""
        key_data = f"{prompt}_{level}"
        return f"prompt_opt:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _load_banned_terms(self) -> List[str]:
        """Load banned terms"""
        return [
            "war", "soldier", "military", "weapon", "gun", "rifle", "combat",
            "fight", "battle", "violence", "blood", "explosion", "bomb",
            "terrorist", "enemy", "kill", "death", "ptsd", "trauma",
            "israel", "palestinian", "lebanon", "gaza", "hamas", "october"
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "total_optimizations": self.optimization_count,
            "successful_optimizations": self.success_count,
            "success_rate": self.success_count / max(1, self.optimization_count),
            "cache_enabled": CACHE_ENABLED
        }


# Initialize service
optimizer_service = PromptOptimizerService()


# ============= HTTP API Endpoints =============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "prompt-optimizer",
        "timestamp": datetime.now().isoformat(),
        "cache": "connected" if CACHE_ENABLED else "disabled"
    })


@app.route('/optimize', methods=['POST'])
def optimize_prompt():
    """Optimize a prompt"""
    try:
        data = request.json
        prompt = data.get('prompt')
        level = data.get('level', 'moderate')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        result = optimizer_service.optimize(prompt, level)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/validate', methods=['POST'])
def validate_prompt():
    """Validate prompt safety"""
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        is_safe, issues = optimizer_service.validate_safety(prompt)
        
        return jsonify({
            "is_safe": is_safe,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get service statistics"""
    return jsonify(optimizer_service.get_stats())


@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear the cache"""
    if CACHE_ENABLED:
        try:
            cache.flushdb()
            return jsonify({"message": "Cache cleared"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"message": "Cache not enabled"}), 400


if __name__ == '__main__':
    logger.info("🚀 Starting Prompt Optimizer Service on port 8001")
    app.run(host='0.0.0.0', port=8001, debug=False)