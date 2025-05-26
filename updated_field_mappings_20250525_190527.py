# Updated field mappings based on actual Notion schema


# AI Client Library
CLIENT_LIBRARY_FIELDS = {
    "checkbox": ['Brand_Builder_Complete # TO BE ADDED', 'Content_Collector_Complete # TO BE ADDED', 'Voice_Auditor_Complete # TO BE ADDED', 'Audience_Definer_Complete # TO BE ADDED', 'Voice_Traits_Builder_Complete # TO BE ADDED', 'Gap_Analyzer_Complete # TO BE ADDED', 'Content_Rewriter_Complete # TO BE ADDED', 'Guidelines_Finalizer_Complete # TO BE ADDED'],
    "email": ['Contact_Email'],
    "last_edited_time": ['Last_Updated'],
    "multi_select": ['Desired_Emotional_Impact # TO BE ADDED', 'Brand_Personality # TO BE ADDED'],
    "phone_number": ['Phone_Number'],
    "relation": ['Content_Samples', 'Project_Tracker', 'Voice_Guidelines'],
    "rich_text": ['Brand_Mission', 'Brand_Values', 'Company_Description', 'Ideal_Target_Audience', 'Location', 'Target_Audience', 'Value_Proposition', 'Product_Service_Description # TO BE ADDED', 'LinkedIn_URL # TO BE ADDED', 'Twitter_URL # TO BE ADDED', 'Facebook_URL # TO BE ADDED', 'Instagram_URL # TO BE ADDED', 'Other_Social_Media # TO BE ADDED', 'Deep_Research_Workflow # TO BE ADDED', 'Last_Tool_Completed # TO BE ADDED'],
    "rollup": ['Content_Count', 'Last_Project_Update', 'Progress_Average', 'Project_Count', 'Voice_Status'],
    "select": ['Communication_Tone', 'Company_Size', 'Industry', 'Research_Status # TO BE ADDED'],
    "title": ['Name'],
    "url": ['Website'],
}

# Content Samples
CONTENT_SAMPLES_FIELDS = {
    "checkbox": ['Original_Sample # TO BE ADDED', 'Rewritten_Version # TO BE ADDED'],
    "date": ['Collection_Date'],
    "number": ['Word_Count'],
    "relation": ['Client'],
    "rich_text": ['Notes', 'Sample_Content'],
    "select": ['Channel_Type', 'Content_Type', 'Quality_Score', 'Tone_Assessment'],
    "title": ['Name'],
    "url": ['Source_URL'],
}

# Voice Guidelines
VOICE_GUIDELINES_FIELDS = {
    "date": ['Last_Updated'],
    "multi_select": ['Brand_Personality_Traits', 'Voice_Characteristics'],
    "relation": ['Client'],
    "rich_text": ['Audience_Fit_Assessment', 'Consistency_Assessment', 'Identified_Gaps', 'Implementation_Notes', 'Personality_Analysis', 'Recommendations', 'Signature_Phrases', 'Tone_Analysis', 'Tone_Description', 'Word_Choice_Analysis', 'Word_Choice_Guidelines', 'Words_To_Avoid'],
    "select": ['Status'],
    "title": ['Name'],
}

# Field name mappings (old -> new)
FIELD_MAPPINGS = {
    "AI Client Library": {
        "Current_Target_Audience": "Target_Audience",
        "Address": "Location",
    },
}