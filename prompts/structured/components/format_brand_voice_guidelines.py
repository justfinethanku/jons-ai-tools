"""
FORMAT component for comprehensive brand voice guidelines output
Part of the 5W modular prompt system for structured AI interactions
"""

CONTENT = """FORMAT: Return a JSON object with this exact structure:
{
  "brand_voice_guidelines": {
    "document_overview": {
      "title": "Brand Voice Guidelines for [Client Name]",
      "version": "1.0",
      "created_date": "YYYY-MM-DD",
      "executive_summary": "Comprehensive overview of brand voice strategy and implementation approach",
      "usage_instructions": "How to use this document effectively"
    },
    "brand_foundation": {
      "mission_statement": "Clear brand mission",
      "core_values": ["Value 1", "Value 2", "Value 3"],
      "value_proposition": "Unique positioning statement",
      "brand_personality": ["Trait 1", "Trait 2", "Trait 3"],
      "competitive_differentiation": "How we stand apart from competitors"
    },
    "target_persona": {
      "persona_name": "Primary persona name and title",
      "demographic_summary": "Key demographic and professional characteristics",
      "communication_preferences": "How they prefer to receive information",
      "decision_making_factors": "What influences their choices",
      "pain_points": ["Challenge 1", "Challenge 2", "Challenge 3"],
      "success_metrics": "What defines success for them"
    },
    "voice_traits": [
      {
        "trait_name": "Core voice trait name",
        "definition": "What this trait means in practice",
        "do_guidelines": ["Specific do example 1", "Specific do example 2", "Specific do example 3"],
        "dont_guidelines": ["Specific don't example 1", "Specific don't example 2", "Specific don't example 3"],
        "persona_rationale": "Why this trait resonates with our target persona",
        "application_contexts": ["When and where to emphasize this trait"]
      }
    ],
    "channel_adaptations": {
      "website_content": {
        "voice_emphasis": "Which traits to emphasize on website",
        "tone_guidelines": "Specific tone recommendations",
        "language_level": "Appropriate complexity level",
        "content_themes": ["Theme 1", "Theme 2", "Theme 3"]
      },
      "social_media": {
        "voice_emphasis": "Which traits work best on social platforms",
        "tone_guidelines": "Social media tone approach",
        "engagement_style": "How to interact with audience",
        "content_themes": ["Theme 1", "Theme 2", "Theme 3"]
      },
      "email_marketing": {
        "voice_emphasis": "Email-specific voice traits",
        "tone_guidelines": "Email communication tone",
        "personalization_approach": "How to personalize while maintaining voice",
        "content_themes": ["Theme 1", "Theme 2", "Theme 3"]
      }
    },
    "competitive_positioning": {
      "market_landscape": "Overview of competitive environment",
      "differentiation_strategy": "How our voice sets us apart",
      "messaging_priorities": ["Priority message 1", "Priority message 2", "Priority message 3"],
      "competitive_advantages": ["Advantage 1", "Advantage 2", "Advantage 3"],
      "positioning_statements": ["Statement 1", "Statement 2"]
    },
    "reference_examples": [
      {
        "content_type": "Type of content sample",
        "original_content": "Before transformation example",
        "improved_content": "After transformation example",
        "voice_traits_demonstrated": ["Trait 1", "Trait 2"],
        "improvement_rationale": "Why this transformation works better"
      }
    ],
    "implementation_framework": {
      "step_by_step_guide": [
        {
          "step_number": 1,
          "step_title": "Implementation step title",
          "step_description": "Detailed instructions for this step",
          "deliverables": ["What to produce in this step"]
        }
      ],
      "quality_assurance": {
        "voice_checklist": ["Checkpoint 1", "Checkpoint 2", "Checkpoint 3"],
        "common_mistakes": ["Mistake 1", "Mistake 2", "Mistake 3"],
        "approval_criteria": "What makes content ready for publication"
      },
      "maintenance_guidelines": {
        "regular_reviews": "How often to review voice guidelines",
        "update_triggers": "When to update guidelines",
        "consistency_monitoring": "How to maintain voice consistency over time"
      }
    },
    "quick_reference": {
      "voice_traits_summary": ["Trait 1: Brief description", "Trait 2: Brief description"],
      "persona_key_points": ["Key point 1", "Key point 2", "Key point 3"],
      "dos_and_donts": {
        "always_do": ["Do 1", "Do 2", "Do 3"],
        "never_do": ["Don't 1", "Don't 2", "Don't 3"]
      },
      "emergency_guidelines": "Quick guidance for urgent content needs"
    }
  }
}"""