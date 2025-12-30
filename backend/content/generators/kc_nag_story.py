"""
K.C. Nag Story Context Generator

Uses LLM with Instructor (Pydantic) to generate story contexts that wrap
deterministic math skeletons in engaging, real-world narratives.

Key principle: LLM generates ONLY the story (skin), math is already solved (skeleton).
Uses Structured Outputs to enforce JSON schema compliance.
"""

import json
from typing import Optional, Dict, Any
import httpx
import os
from ..models import KCNagStoryContext, MathSkeleton


class KCNagStoryGenerator:
    """
    Generates K.C. Nag-aligned story contexts for math problems.
    
    K.C. Nag philosophy:
    - Real-world relevance (cooking, sports, shopping)
    - Progressive building (simple → complex)
    - Visual thinking (grids, pictures, patterns)
    - Story-driven (characters and contexts)
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        """
        Initialize with OpenAI API credentials.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: API endpoint (defaults to OpenAI)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.model = "gpt-4o-mini"  # Use efficient model for story generation
        
        # KC Nag themes for different contexts
        self.kc_nag_themes = {
            "factors": [
                "Organizing items into equal groups (cookies, flowers, toys)",
                "Arranging students into teams",
                "Packing items into boxes",
                "Sharing equally among friends",
                "Creating patterns with tiles",
            ],
            "multiples": [
                "Repeating patterns (dance steps, songs)",
                "Skip counting (jumping, climbing stairs)",
                "Regular intervals (time, distance)",
                "Cycles and repetition",
                "Building sequences",
            ],
            "gcd": [
                "Dividing items fairly among groups",
                "Creating the largest equal portions",
                "Finding common measurements",
                "Making equal-sized bundles",
            ],
            "lcm": [
                "Synchronized events (bells ringing together)",
                "Meeting points in cycles",
                "Planning schedules",
                "Creating harmonious patterns",
            ],
        }
    
    def generate_story_context(
        self,
        skeleton: MathSkeleton,
        theme: Optional[str] = None,
    ) -> KCNagStoryContext:
        """
        Generate K.C. Nag story context for a math skeleton.
        
        Args:
            skeleton: Mathematical skeleton from SymPy generator
            theme: Optional theme override (e.g., "cooking", "sports")
        
        Returns:
            KCNagStoryContext with story details
        """
        
        # Select theme based on concept if not provided
        if not theme:
            concept_lower = skeleton.concept.lower()
            if "factor" in concept_lower:
                theme = "Organizing items into groups"
            elif "multiple" in concept_lower:
                theme = "Repeating patterns"
            elif "gcd" in concept_lower:
                theme = "Sharing equally"
            elif "lcm" in concept_lower:
                theme = "Synchronized events"
            else:
                theme = "Real-world mathematics"
        
        # Build prompt for LLM
        prompt = self._build_story_prompt(skeleton, theme)
        
        # Call OpenAI API with structured outputs
        response = self._call_openai_structured(prompt)
        
        return response
    
    def _build_story_prompt(self, skeleton: MathSkeleton, theme: str) -> str:
        """
        Build the prompt for story generation.
        
        The prompt ensures:
        1. LLM knows it should NOT solve the math
        2. LLM knows it should wrap numbers in a story
        3. LLM is constrained to specific JSON format
        """
        
        # Extract parameters for the story
        params = skeleton.parameters
        
        prompt = f"""You are an expert in K.C. Nag pedagogy. Your task is to create a story context 
for a mathematics problem. 

IMPORTANT CONSTRAINTS:
- Do NOT solve any math or calculate answers
- Do NOT change any numbers provided
- Your role is ONLY to create engaging, real-world context
- The story should be appropriate for Grade 5 (age 9-10)
- Focus on the "Skins and Skeletons" approach: you provide the SKIN (story), the math SKELETON is already solved

Mathematical Concept: {skeleton.concept}
Difficulty: {skeleton.difficulty}
Theme: {theme}

The problem involves these parameters:
{json.dumps(params, indent=2)}

Generate a story context with these elements:

1. **story_character**: A relatable Grade 5 character (name + brief description)
   - Examples: "Akshara, a baker in Mumbai", "Raj, a sports coach in Delhi", "Priya, a shopkeeper"
   
2. **story_setting**: The real-world location
   - Should connect to Indian culture/context where possible
   - Examples: "A bakery", "A school sports day", "A vegetable market"
   
3. **story_action**: What the character is doing
   - Should naturally involve the concept
   - Examples: "arranging cookies in boxes", "dividing items fairly", "organizing a group activity"
   
4. **real_world_relevance**: Why this skill matters
   - Connects to student's life
   - Example: "Knowing factors helps arrange items efficiently"
   
5. **visual_hint**: Description of a visual (grid, picture, diagram)
   - Guide for frontend to create visual aids
   - Example: "A 6×4 grid showing arranged items"
   
6. **number_placement**: How the main number appears in the story
   - Use placeholder {'{'}number{'}'} or similar
   - Example: "Total cookies: {'{'}number{'}'}"
   
7. **concept_bridge**: Explicit connection to the math concept
   - One sentence explaining why the story requires this math
   
8. **extension_question**: A follow-up for deeper thinking
   - Slightly harder question using the same concept
   - No numerical answer expected, just extends thinking

Respond ONLY with valid JSON matching the schema exactly. No additional text.
"""
        
        return prompt
    
    def _call_openai_structured(self, prompt: str) -> KCNagStoryContext:
        """
        Call OpenAI API with structured outputs (forces valid JSON response).
        
        Uses JSON schema enforcement to ensure LLM output matches Pydantic model.
        """
        
        # Convert Pydantic model to JSON schema for API
        schema = {
            "type": "object",
            "properties": {
                "story_character": {
                    "type": "string",
                    "description": "Main character in the story"
                },
                "story_setting": {
                    "type": "string",
                    "description": "Real-world context and location"
                },
                "story_action": {
                    "type": "string",
                    "description": "What the character is doing"
                },
                "real_world_relevance": {
                    "type": "string",
                    "description": "Why this matters"
                },
                "visual_hint": {
                    "type": "string",
                    "description": "Description of visual aid"
                },
                "number_placement": {
                    "type": "string",
                    "description": "Where the numbers appear in the story"
                },
                "concept_bridge": {
                    "type": "string",
                    "description": "Connection to mathematical concept"
                },
                "extension_question": {
                    "type": "string",
                    "description": "Follow-up challenge question"
                },
            },
            "required": [
                "story_character",
                "story_setting",
                "story_action",
                "real_world_relevance",
                "visual_hint",
                "number_placement",
                "concept_bridge",
                "extension_question",
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "KCNagStoryContext",
                    "schema": schema,
                    "strict": True,
                }
            },
            "temperature": 0.7,  # Some creativity, but not too much
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
            
            response_data = response.json()
            
            # Extract JSON from response
            content = response_data["choices"][0]["message"]["content"]
            story_dict = json.loads(content)
            
            # Validate with Pydantic
            return KCNagStoryContext(**story_dict)
        
        except Exception as e:
            # If API call fails, return a default story context
            print(f"Warning: Story generation API call failed: {e}")
            return self._get_fallback_story_context()
    
    def _get_fallback_story_context(self) -> KCNagStoryContext:
        """
        Fallback story context if API fails.
        Ensures system continues to work even without LLM access.
        """
        return KCNagStoryContext(
            story_character="Akshara, a young student in Delhi",
            story_setting="Her school's mathematics club",
            story_action="organizing supplies for a project",
            real_world_relevance="Understanding factors helps organize items efficiently",
            visual_hint="A grid showing items arranged in equal groups",
            number_placement="Total items to organize: {number}",
            concept_bridge="To organize items equally, we need to find all possible ways to divide them",
            extension_question="If we have a different number of items, would the factors be the same or different? Why?",
        )


# Simpler version without API dependency for local testing
class KCNagStoryGeneratorLocal:
    """
    Local story generator using templates and rules.
    Useful for development/testing without API costs.
    """
    
    def __init__(self):
        self.stories = {
            "factors": {
                "Organizing cookies": {
                    "character": "Akshara, a baker",
                    "setting": "Her cozy bakery in Mumbai",
                    "action": "arranging cookies in boxes",
                    "relevance": "Knowing factors helps arrange items into equal groups",
                    "visual": "Grid showing cookies arranged in rows and columns",
                    "bridge": "To distribute {number} cookies equally, she needs to find all factors",
                    "extension": "What if she had {number}+1 cookies? Would she have the same ways to arrange them?",
                },
                "Arranging students": {
                    "character": "Raj, a sports coach",
                    "setting": "The school sports ground in Bangalore",
                    "action": "dividing students into equal teams",
                    "relevance": "Factors help create fair teams for games",
                    "visual": "Picture showing students standing in {number} equal groups",
                    "bridge": "To form equal teams from {number} students, find all factors",
                    "extension": "If more students join, what new team arrangements are possible?",
                },
                "Creating patterns": {
                    "character": "Priya, a mathematician",
                    "setting": "Her home in Kolkata",
                    "action": "designing tile patterns for a floor",
                    "relevance": "Factors determine how to arrange tiles symmetrically",
                    "visual": "A rectangular grid showing {number} tiles",
                    "bridge": "To create a rectangle with {number} tiles, we use factors",
                    "extension": "Can you create multiple rectangular patterns with these tiles?",
                },
            },
            "multiples": {
                "Skip counting": {
                    "character": "Amit, a young athlete",
                    "setting": "The track near his home in Delhi",
                    "action": "running in a pattern with friends",
                    "relevance": "Multiples help understand repeating patterns in exercise",
                    "visual": "A number line showing jumps of {number}",
                    "bridge": "Each jump covers {number} meters, so jumps land on multiples of {number}",
                    "extension": "After 10 jumps, how far would you travel?",
                },
                "Repeating patterns": {
                    "character": "Neha, a musician",
                    "setting": "Music class in school",
                    "action": "creating a rhythm pattern",
                    "relevance": "Multiples help create repetitive musical patterns",
                    "visual": "Beats shown as a repeating pattern",
                    "bridge": "A pattern with {number} beats repeats throughout the song",
                    "extension": "How many times does the pattern repeat in a longer song?",
                },
            },
            "gcd": {
                "Sharing equally": {
                    "character": "Arjun, a fair-minded brother",
                    "setting": "His home during snack time",
                    "action": "dividing snacks fairly between friends",
                    "relevance": "GCD helps divide items into equal portions",
                    "visual": "Groups showing fair division",
                    "bridge": "To divide both snack types equally, use GCD of both quantities",
                    "extension": "What's the largest number of friends who can share equally?",
                },
            },
            "lcm": {
                "Synchronized meetings": {
                    "character": "Zara, a bus conductor",
                    "setting": "Two bus stops in Hyderabad",
                    "action": "synchronizing bus timings",
                    "relevance": "LCM helps find when events happen together",
                    "visual": "A timeline showing bus arrivals",
                    "bridge": "Buses meet at times that are multiples of both {number}",
                    "extension": "When will three buses meet at the same time?",
                },
            },
        }
    
    def generate_story_context(
        self,
        skeleton: MathSkeleton,
        theme: Optional[str] = None,
    ) -> KCNagStoryContext:
        """Generate story using local templates"""
        
        concept_type = "factors" if "factor" in skeleton.concept.lower() else \
                      "multiples" if "multiple" in skeleton.concept.lower() else \
                      "gcd" if "gcd" in skeleton.concept.lower().upper() else \
                      "lcm" if "lcm" in skeleton.concept.lower().upper() else \
                      "factors"
        
        stories_for_concept = self.stories.get(concept_type, self.stories["factors"])
        
        # Pick a random story template
        import random
        story_template = random.choice(list(stories_for_concept.values()))
        
        # Get the main parameter
        params = skeleton.parameters
        main_number = params.get("target_number") or params.get("number_1") or params.get("number") or "N"
        
        return KCNagStoryContext(
            story_character=story_template["character"],
            story_setting=story_template["setting"],
            story_action=story_template["action"],
            real_world_relevance=story_template["relevance"],
            visual_hint=story_template["visual"],
            number_placement=story_template["bridge"].replace("{number}", str(main_number)),
            concept_bridge=story_template["bridge"].replace("{number}", str(main_number)),
            extension_question=story_template["extension"].replace("{number}", str(main_number)),
        )
