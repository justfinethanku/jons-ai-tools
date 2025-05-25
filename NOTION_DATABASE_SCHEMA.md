# Notion Database Schema Reference

This document outlines the complete structure of all Notion databases used in the AI Tools project.

## Database Overview

The system uses three interconnected Notion databases:

1. **AI Client Library** - Main client management database
2. **Content Samples** - Content collection and analysis  
3. **Voice Guidelines** - Final brand voice documentation

## 📋 AI Client Library (Main Database)
**Database ID**: `1fd72022-1e76-81ce-9f16-e77cd8075e3b`  
**Purpose**: Central client management and workflow tracking

### Properties

| Property | Type | Description | Options/Details |
|----------|------|-------------|-----------------|
| **Name** | title | Client company name | Primary identifier |
| **Industry** | select | Business sector | Technology, Healthcare, Finance, Education, Retail, Manufacturing, Professional Services, Non-profit, Other, Web Development and Digital Marketing, Portrait Photography |
| **Website** | url | Company website | |
| **Contact_Email** | email | Primary contact email | |
| **Phone_Number** | phone | Contact phone number | |
| **Location** | rich_text | Company location/address | |
| **Company_Size** | select | Number of employees | 1-10 employees, 11-50 employees, 51-200 employees, 201-500 employees, 501+ employees |
| **Company_Description** | rich_text | What the company does | |
| **Brand_Mission** | rich_text | Company mission statement | |
| **Brand_Values** | rich_text | Core company values | |
| **Value_Proposition** | rich_text | Unique value proposition | |
| **Target_Audience** | rich_text | Current target audience | |
| **Ideal_Target_Audience** | rich_text | Ideal target audience goals | |
| **Communication_Tone** | select | Preferred communication style | Professional, Friendly, Authoritative, Casual, Inspirational |
| **Content_Samples** | relation | Links to Content Samples database | |
| **Voice_Guidelines** | relation | Links to Voice Guidelines database | |
| **Project_Tracker** | relation | Links to project tracking database | |
| **Progress_Average** | rollup | Overall workflow completion % | Calculated from project tracker |
| **Content_Count** | rollup | Number of content samples collected | Calculated from content samples |
| **Voice_Status** | rollup | Voice guidelines completion status | Calculated from voice guidelines |
| **Last_Updated** | last_edited_time | When record was last modified | Auto-generated |
| **Project_Count** | rollup | Number of projects for client | Calculated from project tracker |
| **Last_Project_Update** | rollup | Most recent project activity | Calculated from project tracker |

## 📋 Content Samples Database
**Database ID**: `1fd72022-1e76-8119-9f36-d4ce24c04d86`  
**Purpose**: Store and analyze client content for voice development

### Properties

| Property | Type | Description | Options/Details |
|----------|------|-------------|-----------------|
| **Name** | title | Sample identifier/description | |
| **Client** | relation | Links back to AI Client Library | |
| **Content_Type** | select | Type of content sample | Original Sample, Rewritten Version, Generated Content, Competitor Example |
| **Channel_Type** | select | Source channel/platform | Website Homepage, Website About, Website Services, Instagram, Facebook, LinkedIn, Twitter/X, Email Newsletter, Blog Post, Customer Service, Marketing Material, Other |
| **Sample_Content** | rich_text | The actual content text | |
| **Source_URL** | url | Where content originated | |
| **Collection_Date** | date | When content was collected | |
| **Word_Count** | number | Length of content sample | |
| **Quality_Score** | select | Content quality rating | 5 - Perfect, 4 - Very Good, 3 - Good, 2 - Fair, 1 - Poor |
| **Tone_Assessment** | select | Voice tone evaluation | Excellent, Good, Needs Improvement, Poor, For Review |
| **Notes** | rich_text | Analysis notes and observations | |

## 📋 Voice Guidelines Database
**Database ID**: `1fd72022-1e76-8117-9d2f-ed89252b6bc3`  
**Purpose**: Comprehensive brand voice documentation and guidelines

### Properties

| Property | Type | Description | Options/Details |
|----------|------|-------------|-----------------|
| **Name** | title | Guidelines identifier | |
| **Client** | relation | Links back to AI Client Library | |
| **Status** | select | Development status | Draft, In Progress, Review, Final, Archived |
| **Voice_Characteristics** | multi_select | Key voice traits | (Dynamic - populated during workflow) |
| **Brand_Personality_Traits** | multi_select | Personality descriptors | (Dynamic - populated during workflow) |
| **Tone_Description** | rich_text | How the brand should sound | |
| **Tone_Analysis** | rich_text | Detailed tone breakdown | |
| **Personality_Analysis** | rich_text | Brand personality assessment | |
| **Word_Choice_Guidelines** | rich_text | Preferred language patterns | |
| **Words_To_Avoid** | rich_text | Language to avoid | |
| **Signature_Phrases** | rich_text | Brand-specific phrases | |
| **Audience_Fit_Assessment** | rich_text | How voice fits target audience | |
| **Consistency_Assessment** | rich_text | Voice consistency analysis | |
| **Identified_Gaps** | rich_text | Areas needing improvement | |
| **Word_Choice_Analysis** | rich_text | Language pattern analysis | |
| **Recommendations** | rich_text | Implementation recommendations | |
| **Implementation_Notes** | rich_text | How to use these guidelines | |
| **Last_Updated** | date | When guidelines were last modified | |

## Database Relationships

```
AI Client Library (Main)
├── Content_Samples (relation) → Content Samples Database
├── Voice_Guidelines (relation) → Voice Guidelines Database
└── Project_Tracker (relation) → Project Tracker Database

Content Samples Database
└── Client (relation) → AI Client Library

Voice Guidelines Database
└── Client (relation) → AI Client Library
```

## Workflow Integration

1. **Client Creation**: New clients added to AI Client Library
2. **Content Collection**: Brand Builder collects content → Content Samples Database
3. **Voice Analysis**: Content analyzed to create → Voice Guidelines Database
4. **Progress Tracking**: Rollup fields show completion status in AI Client Library

## Access Configuration

All databases are accessed via the Notion integration configured in `.streamlit/secrets.toml`:

```toml
[notion]
NOTION_API_KEY = "your-notion-integration-token"
NOTION_DATABASE_ID = "1fd72022-1e76-81ce-9f16-e77cd8075e3b"  # AI Client Library
Content_Samples_database_ID = "1fd72022-1e76-8119-9f36-d4ce24c04d86"
voice_guidelines_database_id = "1fd72022-1e76-8117-9d2f-ed89252b6bc3"
```

---

*Last Updated: 2025-05-25*  
*Generated by AI Tools Brand Builder System*