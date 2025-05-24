"""
FORMAT component for transformed content examples output
Part of the 5W modular prompt system for structured AI interactions
"""

CONTENT = """FORMAT: Return a JSON object with this exact structure:
{
  "transformation_results": {
    "total_content_pieces": 0,
    "successful_transformations": 0,
    "transformation_summary": "Overview of transformation outcomes"
  },
  "transformed_content": [
    {
      "content_id": "Unique identifier for tracking",
      "original_content": "The exact original content sample",
      "transformed_content": "The completely rewritten version",
      "content_type": "Type of content (email, social post, blog excerpt, etc)",
      "content_channel": "Where this content appears",
      "voice_traits_applied": [
        {
          "trait_name": "Name of voice trait applied",
          "application_method": "How this trait was implemented",
          "before_example": "Specific phrase from original",
          "after_example": "How it was transformed"
        }
      ],
      "persona_optimizations": [
        {
          "persona_element": "Aspect of persona addressed",
          "optimization_description": "How content was optimized for persona",
          "language_changes": "Specific language modifications made"
        }
      ],
      "competitive_positioning": {
        "differentiation_applied": "How competitive insights were integrated",
        "positioning_elements": ["Key positioning concepts incorporated"]
      },
      "improvement_summary": "Overall description of transformations made",
      "quality_score": 0
    }
  ],
  "transformation_patterns": [
    {
      "pattern_name": "Type of transformation pattern identified",
      "description": "What this pattern addresses",
      "frequency": 0,
      "examples": ["List of specific examples where this pattern was applied"]
    }
  ]
}"""