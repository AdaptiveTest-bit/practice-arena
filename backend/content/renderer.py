"""
Rich Question Template Renderer

Uses Jinja2 to render complete rich questions from skeleton + skin.
Produces HTML for web display and LaTeX for PDF export.
"""

from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Dict, Any
from .models import RichQuestion, MathSkeleton, KCNagStoryContext


class RichQuestionRenderer:
    """
    Renders rich questions by combining:
    1. Mathematical skeleton (SymPy)
    2. Story skin (K.C. Nag)
    3. Jinja2 templates
    """
    
    def __init__(self, template_dir: str = None):
        """Initialize Jinja2 environment"""
        if template_dir is None:
            template_dir = str(Path(__file__).parent.parent / "templates")
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
        )
        # Add custom filters
        self.env.filters['latex_escape'] = self._latex_escape
    
    def render_rich_question(
        self,
        skeleton: MathSkeleton,
        story: KCNagStoryContext,
        template_name: str = "rich_question.html",
    ) -> Dict[str, str]:
        """
        Render a complete rich question.
        
        Args:
            skeleton: Mathematical skeleton
            story: K.C. Nag story context
            template_name: Name of Jinja2 template to use
        
        Returns:
            Dict with 'html_problem' and 'latex_full' keys
        """
        
        # Build context for Jinja2
        context = {
            "skeleton": skeleton,
            "story": story,
            "parameters": skeleton.parameters,
        }
        
        # Render HTML version
        try:
            html_template = self.env.get_template(template_name)
            html_problem = html_template.render(**context)
        except Exception as e:
            print(f"Warning: Failed to load template {template_name}, using fallback")
            html_problem = self._render_html_fallback(skeleton, story)
        
        # Render LaTeX version
        latex_full = self._render_latex(skeleton, story)
        
        return {
            "html_problem": html_problem,
            "latex_full": latex_full,
        }
    
    def _render_html_fallback(self, skeleton: MathSkeleton, story: KCNagStoryContext) -> str:
        """Fallback HTML rendering if template not found"""
        
        html = f"""
        <div class="rich-question">
            <!-- Story Context -->
            <div class="story-context">
                <h3>📖 The Story</h3>
                <p><strong>{story.story_character}</strong> is {story.story_action} in {story.story_setting}.</p>
                <p class="relevance">🎯 Why this matters: {story.real_world_relevance}</p>
            </div>
            
            <!-- Visual Hint -->
            <div class="visual-hint">
                <p class="hint-label">📐 Visual Hint:</p>
                <p>{story.visual_hint}</p>
            </div>
            
            <!-- The Math Problem -->
            <div class="math-problem">
                <h3>❓ The Problem</h3>
                <div class="problem-text">
                    {story.number_placement}
                </div>
                <div class="latex-display">
                    <p>{skeleton.latex_problem}</p>
                </div>
            </div>
            
            <!-- Concept Bridge -->
            <div class="concept-bridge">
                <p class="bridge-label">🔗 How it connects:</p>
                <p>{story.concept_bridge}</p>
            </div>
            
            <!-- Extension -->
            <div class="extension">
                <p class="extension-label">🚀 Think deeper:</p>
                <p>{story.extension_question}</p>
            </div>
            
            <!-- Answer Area -->
            <div class="answer-area">
                <input type="text" placeholder="Your answer..." id="student_answer" />
                <button onclick="checkAnswer()">Check Answer</button>
            </div>
            
            <!-- Steps (collapsible) -->
            <details class="solution-steps">
                <summary>📚 Solution Steps</summary>
                <ol>
        """
        
        for step in skeleton.steps:
            html += f"<li>{step}</li>\n"
        
        html += f"""
                </ol>
                <p class="explanation">{skeleton.explanation}</p>
            </details>
        </div>
        """
        
        return html
    
    def _render_latex(self, skeleton: MathSkeleton, story: KCNagStoryContext) -> str:
        """Render LaTeX version for PDF export"""
        
        latex = f"""
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}
\\usepackage{{xcolor}}

\\title{{{skeleton.concept}}}
\\author{{K.C. Nag Inspired Problem}}
\\date{{}}

\\begin{{document}}

\\maketitle

\\section*{{📖 The Story}}

\\textbf{{{story.story_character}}} is {story.story_action} in {story.story_setting}.

\\textit{{{story.real_world_relevance}}}

\\section*{{❓ The Problem}}

{story.number_placement}

\\[
{skeleton.latex_problem}
\\]

\\section*{{🔗 How it Connects}}

{story.concept_bridge}

\\section*{{📚 Solution Steps}}

\\begin{{enumerate}}
"""
        
        for step in skeleton.steps:
            latex += f"\\item {step}\n"
        
        latex += f"""
\\end{{enumerate}}

\\section*{{Explanation}}

{skeleton.explanation}

\\section*{{🚀 Extension Question}}

{story.extension_question}

\\end{{document}}
"""
        
        return latex
    
    @staticmethod
    def _latex_escape(text: str) -> str:
        """Escape special LaTeX characters"""
        special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
        }
        for char, escaped in special_chars.items():
            text = text.replace(char, escaped)
        return text
