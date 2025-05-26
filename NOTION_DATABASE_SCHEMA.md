# Notion Database Schema Reference

*Auto-generated on: 2025-05-25 21:27:18*

## Database Overview

The system uses three interconnected Notion databases:

1. **AI Client Library** - Central client management and workflow tracking
2. **Content Samples** - Store and analyze client content for voice development
3. **Voice Guidelines** - Comprehensive brand voice documentation and guidelines

## 📋 AI Client Library
**Database ID**: `1fd72022-1e76-81ce-9f16-e77cd8075e3b`  
**Purpose**: Central client management and workflow tracking

### Properties

| Property | Type | Description | Options/Details |
|----------|------|-------------|-----------------|
| **Audience_Definer_Complete** | checkbox |  |  |
| **Brand_Builder_Complete** | checkbox |  |  |
| **Brand_Mission** | rich_text |  |  |
| **Brand_Personality** | rich_text |  |  |
| **Brand_Values** | rich_text |  |  |
| **Communication_Tone** | rich_text |  |  |
| **Company_Description** | rich_text |  |  |
| **Company_Size** | select |  | 1-10 employees, 11-50 employees, 51-200 employees, 201-500 employees, 501+ employees |
| **Contact_Email** | email |  |  |
| **Content_Collector_Complete** | checkbox |  |  |
| **Content_Count** | rollup |  | Calculated from Content_Samples |
| **Content_Rewriter_Complete** | checkbox |  |  |
| **Content_Samples** | relation |  | Links to Content Samples |
| **Deep_Research_Workflow** | rich_text |  |  |
| **Desired_Emotional_Impact** | rich_text |  |  |
| **Facebook_URL** | rich_text |  |  |
| **Gap_Analyzer_Complete** | checkbox |  |  |
| **Guidelines_Finalizer_Complete** | checkbox |  |  |
| **Ideal_Target_Audience** | rich_text |  |  |
| **Industry** | rich_text | Business sector |  |
| **Instagram_URL** | rich_text |  |  |
| **Last_Project_Update** | rollup |  | Calculated from Project_Tracker |
| **Last_Tool_Completed** | rich_text |  |  |
| **Last_Updated** | last_edited_time | Last modification date | Auto-generated |
| **LinkedIn_URL** | rich_text |  |  |
| **Location** | rich_text |  |  |
| **Name** | title | Primary identifier | Primary identifier |
| **Other_Social_Media** | rich_text |  |  |
| **Phone_Number** | phone_number |  |  |
| **Product_Service_Description** | rich_text |  |  |
| **Progress_Average** | rollup |  | Calculated from Project_Tracker |
| **Project_Count** | rollup |  | Calculated from Project_Tracker |
| **Project_Tracker** | relation |  | Links to Unknown |
| **Research_Status** | select |  | In Progress |
| **Target_Audience** | rich_text |  |  |
| **Twitter_URL** | rich_text |  |  |
| **Value_Proposition** | rich_text |  |  |
| **Voice_Auditor_Complete** | checkbox |  |  |
| **Voice_Guidelines** | relation |  | Links to Voice Guidelines |
| **Voice_Status** | rollup |  | Calculated from Voice_Guidelines |
| **Voice_Traits_Builder_Complete** | checkbox |  |  |
| **Website** | url | Company website URL |  |

## 📋 Content Samples
**Database ID**: `1fd72022-1e76-8119-9f36-d4ce24c04d86`  
**Purpose**: Store and analyze client content for voice development

### Properties

| Property | Type | Description | Options/Details |
|----------|------|-------------|-----------------|
| **Channel_Type** | select |  | Website Homepage, Website About, Website Services, Instagram, Facebook, LinkedIn, Twitter/X, Email Newsletter, Blog Post, Customer Service, Marketing Material, Other |
| **Client** | relation | Links to client record | Links to AI Client Library |
| **Collection_Date** | date |  |  |
| **Content_Type** | select |  | Original Sample, Rewritten Version, Generated Content, Competitor Example |
| **Name** | title | Primary identifier | Primary identifier |
| **Notes** | rich_text |  |  |
| **Original_Sample** | checkbox |  |  |
| **Quality_Score** | select |  | 5 - Perfect, 4 - Very Good, 3 - Good, 2 - Fair, 1 - Poor |
| **Rewritten_Version** | checkbox |  |  |
| **Sample_Content** | rich_text |  |  |
| **Source_URL** | url |  |  |
| **Tone_Assessment** | select |  | Excellent, Good, Needs Improvement, Poor, For Review |
| **Word_Count** | number |  |  |

## 📋 Voice Guidelines
**Database ID**: `1fd72022-1e76-8117-9d2f-ed89252b6bc3`  
**Purpose**: Comprehensive brand voice documentation and guidelines

### Properties

| Property | Type | Description | Options/Details |
|----------|------|-------------|-----------------|
| **Audience_Fit_Assessment** | rich_text |  |  |
| **Brand_Personality_Traits** | multi_select |  |  |
| **Client** | relation | Links to client record | Links to AI Client Library |
| **Consistency_Assessment** | rich_text |  |  |
| **Identified_Gaps** | rich_text |  |  |
| **Implementation_Notes** | rich_text |  |  |
| **Last_Updated** | date | Last modification date |  |
| **Name** | title | Primary identifier | Primary identifier |
| **Personality_Analysis** | rich_text |  |  |
| **Recommendations** | rich_text |  |  |
| **Signature_Phrases** | rich_text |  |  |
| **Status** | select | Current status | Draft, In Progress, Review, Final, Archived |
| **Tone_Analysis** | rich_text |  |  |
| **Tone_Description** | rich_text |  |  |
| **Voice_Characteristics** | multi_select |  |  |
| **Word_Choice_Analysis** | rich_text |  |  |
| **Word_Choice_Guidelines** | rich_text |  |  |
| **Words_To_Avoid** | rich_text |  |  |

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

## Access Configuration

All databases are accessed via the Notion integration:

```toml
[notion]
NOTION_API_KEY = "your-notion-integration-token"
NOTION_DATABASE_ID = "1fd72022-1e76-81ce-9f16-e77cd8075e3b"  # AI Client Library
Content_Samples_database_ID = "1fd72022-1e76-8119-9f36-d4ce24c04d86"
voice_guidelines_database_id = "1fd72022-1e76-8117-9d2f-ed89252b6bc3"
```

---

*Last Updated: 2025-05-25*  
*Generated by Notion Schema Puller*