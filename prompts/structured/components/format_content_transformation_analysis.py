"""
FORMAT component for content transformation analysis output
Part of the 5W modular prompt system for structured AI interactions
"""

CONTENT = """FORMAT: Return a JSON object with this exact structure:
{
  "transformation_analysis": {
    "analysis_summary": "Overall assessment of transformation opportunities",
    "content_samples_analyzed": 0,
    "total_improvements_identified": 0
  },
  "content_transformations": [
    {
      "original_content": "The exact original content sample",
      "content_type": "Type of content (email, social post, blog excerpt, etc)",
      "content_channel": "Where this content appears (website, LinkedIn, etc)",
      "improvement_opportunities": [
        {
          "category": "voice_trait_alignment|persona_optimization|competitive_positioning|tone_consistency",
          "description": "What needs to be improved",
          "current_issue": "Specific problem with current content",
          "target_improvement": "What the improved version should achieve"
        }
      ],
      "priority_score": 0,
      "transformation_complexity": "low|medium|high"
    }
  ],
  "strategic_recommendations": [
    {
      "theme": "Overarching improvement theme",
      "description": "Strategic recommendation for content transformation",
      "applies_to_content_types": ["list of content types this affects"],
      "implementation_priority": "high|medium|low"
    }
  ]
}"""