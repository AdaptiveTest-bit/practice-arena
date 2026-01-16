"""
Coverage QA CLI for Phase 2 implementation.
Analyzes template coverage against blueprint targets.
"""

import yaml
import argparse
import sys
from typing import Dict, List, Tuple, Any
from pathlib import Path
from collections import defaultdict
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.content_validation.taxonomy_validator import get_taxonomy_validator
from domain.content_validation.rubric_validator import get_rubric_validator

logger = logging.getLogger(__name__)


class CoverageQACLI:
    """
    Command-line interface for coverage quality assurance.
    
    Analyzes template coverage against blueprint targets and generates reports.
    """
    
    def __init__(self, blueprint_path: str = None):
        """
        Initialize the Coverage QA CLI.
        
        Args:
            blueprint_path: Path to blueprint YAML file
        """
        if blueprint_path is None:
            blueprint_path = Path(__file__).parent.parent / "config" / "content" / "blueprints" / "math" / "class5" / "factors_multiples.yaml"
        
        self.blueprint_path = Path(blueprint_path)
        self.blueprint_data = self._load_blueprint()
        self.taxonomy_validator = get_taxonomy_validator()
        self.rubric_validator = get_rubric_validator()
    
    def _load_blueprint(self) -> Dict:
        """Load blueprint YAML file."""
        try:
            with open(self.blueprint_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError(f"Blueprint file not found: {self.blueprint_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid blueprint YAML: {e}")
    
    def analyze_template_coverage(self, templates: List[Dict]) -> Dict:
        """
        Analyze template coverage against blueprint targets.
        
        Args:
            templates: List of template dictionaries
            
        Returns:
            Coverage analysis report
        """
        coverage_targets = self.blueprint_data.get('coverage_targets', {}).get('by_concept_id', {})
        
        # Count templates by concept_id
        template_counts = defaultdict(int)
        concept_difficulty = defaultdict(list)
        concept_bloom = defaultdict(list)
        
        for template in templates:
            concept_id = template.get('meta', {}).get('concept_id')
            if concept_id:
                template_counts[concept_id] += 1
                
                difficulty = template.get('meta', {}).get('difficulty')
                if difficulty:
                    concept_difficulty[concept_id].append(difficulty)
                
                bloom_level = template.get('meta', {}).get('bloom_level')
                if bloom_level:
                    concept_bloom[concept_id].append(bloom_level)
        
        # Generate coverage report
        report = {
            'summary': {
                'total_concepts': len(coverage_targets),
                'concepts_with_templates': len(template_counts),
                'total_templates': len(templates),
                'coverage_percentage': 0
            },
            'by_concept': {},
            'gaps': [],
            'recommendations': []
        }
        
        concepts_meeting_targets = 0
        
        for concept_id, target in coverage_targets.items():
            template_count = template_counts.get(concept_id, 0)
            min_per_week = target.get('min_per_week', 0)
            priority = target.get('priority', 'medium')
            
            # Calculate coverage percentage for this concept
            coverage_pct = min(100, (template_count / min_per_week) * 100) if min_per_week > 0 else 0
            
            if coverage_pct >= 100:
                concepts_meeting_targets += 1
            
            # Analyze difficulty distribution
            difficulties = concept_difficulty.get(concept_id, [])
            difficulty_dist = self._analyze_difficulty_distribution(difficulties, target.get('difficulty_mix', {}))
            
            # Analyze bloom distribution
            bloom_levels = concept_bloom.get(concept_id, [])
            bloom_dist = self._analyze_bloom_distribution(bloom_levels, target.get('bloom_mix', {}))
            
            concept_report = {
                'template_count': template_count,
                'target_min_per_week': min_per_week,
                'coverage_percentage': coverage_pct,
                'priority': priority,
                'meets_target': template_count >= min_per_week,
                'difficulty_distribution': difficulty_dist,
                'bloom_distribution': bloom_dist,
                'notes': target.get('notes', '')
            }
            
            report['by_concept'][concept_id] = concept_report
            
            # Add to gaps if not meeting target
            if template_count < min_per_week:
                report['gaps'].append({
                    'concept_id': concept_id,
                    'gap_size': min_per_week - template_count,
                    'priority': priority
                })
        
        # Calculate overall coverage percentage
        if len(coverage_targets) > 0:
            report['summary']['coverage_percentage'] = (concepts_meeting_targets / len(coverage_targets)) * 100
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _analyze_difficulty_distribution(self, difficulties: List[int], target_mix: Dict) -> Dict:
        """Analyze difficulty distribution against target mix."""
        if not difficulties:
            return {'actual': {}, 'target': target_mix, 'matches': False}
        
        # Count actual distribution
        actual_dist = {}
        for diff in difficulties:
            actual_dist[str(diff)] = actual_dist.get(str(diff), 0) + 1
        
        total = len(difficulties)
        actual_pct = {k: (v / total) * 100 for k, v in actual_dist.items()}
        
        # Check if distribution roughly matches target (within 20% tolerance)
        matches = True
        for diff_level, target_pct in target_mix.items():
            actual_pct_for_level = actual_pct.get(diff_level, 0)
            if abs(actual_pct_for_level - (target_pct * 100)) > 20:
                matches = False
                break
        
        return {
            'actual': actual_pct,
            'target': {k: v * 100 for k, v in target_mix.items()},
            'matches': matches,
            'sample_size': total
        }
    
    def _analyze_bloom_distribution(self, bloom_levels: List[str], target_mix: Dict) -> Dict:
        """Analyze bloom level distribution against target mix."""
        if not bloom_levels:
            return {'actual': {}, 'target': target_mix, 'matches': False}
        
        # Count actual distribution
        actual_dist = {}
        for bloom in bloom_levels:
            actual_dist[bloom] = actual_dist.get(bloom, 0) + 1
        
        total = len(bloom_levels)
        actual_pct = {k: (v / total) * 100 for k, v in actual_dist.items()}
        
        # Check if distribution roughly matches target (within 20% tolerance)
        matches = True
        for bloom_level, target_pct in target_mix.items():
            actual_pct_for_level = actual_pct.get(bloom_level, 0)
            if abs(actual_pct_for_level - (target_pct * 100)) > 20:
                matches = False
                break
        
        return {
            'actual': actual_pct,
            'target': {k: v * 100 for k, v in target_mix.items()},
            'matches': matches,
            'sample_size': total
        }
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on coverage analysis."""
        recommendations = []
        
        # Overall coverage recommendations
        coverage_pct = report['summary']['coverage_percentage']
        if coverage_pct < 50:
            recommendations.append("CRITICAL: Overall coverage is below 50%. Focus on creating templates for high-priority concepts.")
        elif coverage_pct < 80:
            recommendations.append("WARNING: Overall coverage is below 80%. Prioritize filling gaps in medium and high priority concepts.")
        
        # Priority-based recommendations
        high_priority_gaps = [gap for gap in report['gaps'] if gap.get('priority') == 'high']
        if high_priority_gaps:
            recommendations.append(f"URGENT: {len(high_priority_gaps)} high-priority concepts need templates. Address these first.")
        
        # Difficulty distribution recommendations
        concepts_with_poor_difficulty = []
        for concept_id, concept_report in report['by_concept'].items():
            if not concept_report['difficulty_distribution']['matches']:
                concepts_with_poor_difficulty.append(concept_id)
        
        if concepts_with_poor_difficulty:
            recommendations.append(f"Consider adjusting difficulty distribution for {len(concepts_with_poor_difficulty)} concepts to match targets.")
        
        # Bloom level recommendations
        concepts_with_poor_bloom = []
        for concept_id, concept_report in report['by_concept'].items():
            if not concept_report['bloom_distribution']['matches']:
                concepts_with_poor_bloom.append(concept_id)
        
        if concepts_with_poor_bloom:
            recommendations.append(f"Consider adjusting bloom level distribution for {len(concepts_with_poor_bloom)} concepts to match targets.")
        
        return recommendations
    
    def validate_templates(self, templates: List[Dict]) -> Dict:
        """
        Validate templates against taxonomy and rubrics.
        
        Args:
            templates: List of template dictionaries
            
        Returns:
            Validation report
        """
        validation_report = {
            'total_templates': len(templates),
            'taxonomy_valid': 0,
            'rubric_valid': 0,
            'both_valid': 0,
            'taxonomy_errors': defaultdict(list),
            'rubric_errors': defaultdict(list),
            'quality_scores': []
        }
        
        for i, template in enumerate(templates):
            # Taxonomy validation
            taxonomy_valid, taxonomy_errors = self.taxonomy_validator.validate_template_metadata(
                template.get('meta', {})
            )
            
            # Rubric validation
            rubric_valid, rubric_errors = self.rubric_validator.validate_template_structure(template)
            
            # Quality scoring
            quality_score, quality_level = self.rubric_validator.calculate_quality_score(template)
            validation_report['quality_scores'].append({
                'template_index': i,
                'score': quality_score,
                'level': quality_level
            })
            
            # Update counters
            if taxonomy_valid:
                validation_report['taxonomy_valid'] += 1
            else:
                validation_report['taxonomy_errors'][i] = taxonomy_errors
            
            if rubric_valid:
                validation_report['rubric_valid'] += 1
            else:
                validation_report['rubric_errors'][i] = rubric_errors
            
            if taxonomy_valid and rubric_valid:
                validation_report['both_valid'] += 1
        
        return validation_report
    
    def generate_report(self, templates: List[Dict], output_format: str = 'text') -> str:
        """
        Generate comprehensive coverage and validation report.
        
        Args:
            templates: List of template dictionaries
            output_format: 'text' or 'json'
            
        Returns:
            Formatted report string
        """
        coverage_report = self.analyze_template_coverage(templates)
        validation_report = self.validate_templates(templates)
        
        if output_format == 'json':
            import json
            return json.dumps({
                'coverage': coverage_report,
                'validation': validation_report,
                'blueprint_info': {
                    'file': str(self.blueprint_path),
                    'subject': self.blueprint_data.get('subject'),
                    'grade': self.blueprint_data.get('grade'),
                    'chapter': self.blueprint_data.get('chapter_name')
                }
            }, indent=2)
        
        # Text format
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("COVERAGE QA REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Blueprint: {self.blueprint_data.get('subject')} Grade {self.blueprint_data.get('grade')} - {self.blueprint_data.get('chapter_name')}")
        report_lines.append("")
        
        # Coverage summary
        summary = coverage_report['summary']
        report_lines.append("COVERAGE SUMMARY:")
        report_lines.append(f"  Total Concepts: {summary['total_concepts']}")
        report_lines.append(f"  Concepts with Templates: {summary['concepts_with_templates']}")
        report_lines.append(f"  Total Templates: {summary['total_templates']}")
        report_lines.append(f"  Overall Coverage: {summary['coverage_percentage']:.1f}%")
        report_lines.append("")
        
        # Validation summary
        report_lines.append("VALIDATION SUMMARY:")
        report_lines.append(f"  Total Templates: {validation_report['total_templates']}")
        report_lines.append(f"  Taxonomy Valid: {validation_report['taxonomy_valid']}")
        report_lines.append(f"  Rubric Valid: {validation_report['rubric_valid']}")
        report_lines.append(f"  Both Valid: {validation_report['both_valid']}")
        report_lines.append("")
        
        # Gaps
        if coverage_report['gaps']:
            report_lines.append("COVERAGE GAPS:")
            for gap in coverage_report['gaps']:
                report_lines.append(f"  {gap['concept_id']}: need {gap['gap_size']} more templates (priority: {gap['priority']})")
            report_lines.append("")
        
        # Recommendations
        if coverage_report['recommendations']:
            report_lines.append("RECOMMENDATIONS:")
            for rec in coverage_report['recommendations']:
                report_lines.append(f"  • {rec}")
            report_lines.append("")
        
        # Quality scores summary
        if validation_report['quality_scores']:
            scores = [qs['score'] for qs in validation_report['quality_scores']]
            avg_score = sum(scores) / len(scores) if scores else 0
            report_lines.append("QUALITY SUMMARY:")
            report_lines.append(f"  Average Quality Score: {avg_score:.1f}/100")
            
            # Count by quality level
            level_counts = {}
            for qs in validation_report['quality_scores']:
                level = qs['level']
                level_counts[level] = level_counts.get(level, 0) + 1
            
            for level, count in level_counts.items():
                report_lines.append(f"  {level.title()}: {count} templates")
            report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """Command-line interface entry point."""
    parser = argparse.ArgumentParser(description='Coverage QA CLI for template analysis')
    parser.add_argument('--blueprint', '-b', type=str, help='Path to blueprint YAML file')
    parser.add_argument('--templates', '-t', type=str, help='Path to templates JSON file')
    parser.add_argument('--output', '-o', type=str, choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--output-file', type=str, help='Output file path (default: stdout)')
    
    args = parser.parse_args()
    
    # Initialize CLI
    try:
        qa_cli = CoverageQACLI(args.blueprint)
    except Exception as e:
        print(f"Error initializing QA CLI: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load templates
    templates = []
    if args.templates:
        try:
            import json
            with open(args.templates, 'r') as f:
                templates = json.load(f)
            if not isinstance(templates, list):
                raise ValueError("Templates file must contain a list of template objects")
        except Exception as e:
            print(f"Error loading templates: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No templates file provided. Running with empty template set.", file=sys.stderr)
    
    # Generate report
    try:
        report = qa_cli.generate_report(templates, args.output)
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(report)
            print(f"Report written to: {args.output_file}")
        else:
            print(report)
    
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
