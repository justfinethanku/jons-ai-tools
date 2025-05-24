# Jon's AI Tools

## Overview

Jon's AI Tools is a comprehensive AI-powered brand research and content creation toolkit designed for marketers, agencies, and content creators. Built with Streamlit and powered by Google Gemini 2.5 Flash, it provides sophisticated brand voice analysis, automated content generation, and advanced prompt engineering capabilities.

The toolkit combines intelligent website analysis, brand voice development, and multi-platform content creation—all while maintaining each client's unique brand identity through integration with a Notion-based AI Client Library.

---

## 🚀 What Can You Do with This Toolkit?

### **Context Gatherer** - Advanced Brand Research
*The foundation of all brand-focused content creation*

- **Two-Step AI Analysis**: Automatically extracts company data from websites and develops comprehensive brand voice profiles
- **Multi-Page Website Scraping**: Intelligently crawls homepage, about, contact, mission, and services pages for complete company insights  
- **30+ Data Points Extracted**: Industry, target audiences, brand values, personality traits, competitive differentiation, messaging priorities, and contact information
- **Professional Role-Based AI**: Uses business analyst and brand strategist personas for accurate, strategic insights
- **Notion Integration**: Automatically populates client profiles with extracted data for immediate use across all tools

**Real Output Example:**
- **Industry**: "Artificial Intelligence Safety and Research"
- **Brand Values**: ['Safety', 'Responsibility', 'Transparency', 'Human-centricity', 'Innovation']
- **Target Audience**: "Leading AI researchers, policymakers, enterprise decision-makers..."
- **Brand Personality**: ['Intelligent', 'Trustworthy', 'Forward-thinking', 'Ethical', 'Collaborative']

### **Copy Generator** - Multi-Platform Content Creation
*Transform any content into platform-optimized social media posts*

- **Universal Input**: Upload scripts, paste transcripts, or provide content notes
- **Platform Optimization**: Generates Facebook, LinkedIn, TikTok, YouTube, and generic social posts
- **Client-Aware Generation**: Automatically applies selected client's brand voice, tone, and keywords
- **Best Practice Implementation**: Follows character limits, hashtag strategies, and engagement optimization
- **Batch Export**: Download all generated content in organized text files

### **Prompt Refiner** - Advanced Prompt Engineering
*Iteratively improve AI prompts for better results*

- **Intelligent Refinement**: Transform rough prompt ideas into structured, effective instructions
- **Role-Based Enhancement**: Adds appropriate roles, contexts, and formatting for optimal AI performance
- **Revision Requests**: Request specific changes ("make it shorter", "add examples") for real-time improvements
- **Technical Focus**: Specialized mode for coding and technical prompt optimization

### **Coder Helper** - Technical Prompt Assistance
*Specialized tool for development and technical scenarios*

- **Code-Focused Refinement**: Optimizes prompts for programming tasks and technical documentation
- **Explanation Generation**: Provides clear explanations of complex technical prompts
- **Development Workflow**: Streamlined interface for rapid prompt iteration in technical contexts

---

## 🎯 Who Is It For?

### **Marketing Agencies & Freelancers**
- Manage multiple client brand voices from a centralized Notion database
- Generate on-brand content across all platforms instantly
- Scale content production without losing brand consistency
- Comprehensive client research and brand development

### **Content Creators & Video Producers**
- Transform video content into multi-platform social media campaigns
- Maintain consistent brand voice across all content
- Automate the repetitive aspects of content adaptation

### **Prompt Engineers & Technical Teams**
- Document and refine prompts for internal AI tools
- Iteratively improve prompt effectiveness
- Build libraries of tested, optimized prompts

### **Small Businesses & Startups**
- Develop professional brand voice profiles from just a website URL
- Create comprehensive content strategies without hiring agencies
- Maintain professional brand presence across all channels

---

## 🔄 Real-World Workflow Example

### 1. **Automated Brand Research**
Start with just a company website:
```
Input: https://anthropic.com
Output: Complete brand profile with 30+ fields including:
- Industry analysis
- Target audience segmentation
- Brand values and mission
- Personality traits
- Competitive positioning
- Contact information
- Social media presence
```

### 2. **Content Creation Pipeline**
```
Video Script/Transcript → Copy Generator → Platform-Optimized Posts

Input: "Today we're launching our new AI safety research initiative..."

Output:
- Facebook: Engaging hook with visual call-to-action
- LinkedIn: Professional thought leadership angle  
- TikTok: Trendy, accessible explanation
- YouTube: Descriptive with keyword optimization
```

### 3. **Prompt Engineering Workflow**
```
Rough Idea → Prompt Refiner → Optimized Instruction

Input: "Make a summary of this article"

Output: "You are a professional content strategist. Analyze the provided article and create a comprehensive summary that includes: [detailed role, steps, and format specifications]"
```

---

## ✨ Why Choose Jon's AI Tools?

### **🤖 Advanced AI Integration**
- **Google Gemini 2.5 Flash**: Latest AI model for superior analysis and generation
- **Temperature Optimization**: Precise control (0.3 for extraction, 0.7 for creativity)
- **Structured JSON Outputs**: Reliable, consistent data extraction
- **Multi-step Analysis**: Complex workflows broken into manageable, accurate steps

### **🎨 Brand-First Approach**
- **Comprehensive Brand Analysis**: Goes beyond basic demographics to strategic positioning
- **Voice Consistency**: Maintains brand identity across all content and platforms
- **Professional Methodology**: Uses proven brand strategy frameworks
- **Scalable Profiles**: Manage unlimited client brands with consistent quality

### **🔧 Technical Excellence**
- **Robust Error Handling**: Multiple fallback strategies for reliable operation
- **Notion Integration**: Seamless database management for client profiles
- **Modular Architecture**: Easy to extend with new tools and capabilities
- **Production Ready**: Built for scale with proper error handling and validation

### **💡 Transparency & Control**
- **Editable Prompts**: Full visibility and control over AI instructions
- **Human Oversight**: Review and edit all outputs before use
- **Iterative Refinement**: Continuous improvement of prompts and processes
- **Data Ownership**: Your client data stays in your Notion workspace

---

## 🚀 Getting Started

1. **Clone the Repository**
2. **Set Up Secrets**: Copy `.streamlit/secrets.toml.template` to `secrets.toml` and add your API keys
3. **Configure Notion**: Set up the AI Client Library database using the provided schema
4. **Launch**: `streamlit run app.py`
5. **Create Clients**: Use Context Gatherer to automatically research and profile new clients
6. **Generate Content**: Select clients and create platform-optimized content instantly

---

## 🛡️ Security & Best Practices

- **Secret Management**: API keys stored securely in `.streamlit/secrets.toml` (git-ignored)
- **No Data Persistence**: Your sensitive data never leaves your local environment
- **Notion Integration**: Client data stored in your own Notion workspace
- **Template Files**: Secure setup guides for API key management

---

*Built for creators who demand both AI efficiency and brand authenticity.*