Jon’s AI Tools
Overview
Jon’s AI Tools is a modular AI-powered content and workflow toolkit for content creators, video producers, marketers, and prompt engineers. It leverages large language models (OpenAI GPT-4 and Google PaLM/Gemini) through Streamlit to assist with prompt engineering and content generation tasks
github.com
. The toolkit refines rough prompts into polished ones, explains complex prompts, generates social media copy across multiple platforms, and more – all while maintaining each client’s unique brand voice and tone. By integrating with a Notion database called the “AI Client Library” for client profiles, the tools can automatically tailor outputs to a selected client’s industry, style, and keywords, ensuring consistency and personalization in generated content
github.com
github.com
.
What Can You Do with This Toolkit?
Prompt Refiner: Improve any AI prompt iteratively. Enter a rough draft prompt and get back a clearer, more effective version. You can then request specific revisions (e.g. “make it shorter”, “add a friendly tone”) and the tool will refine the prompt further in real-time
github.com
github.com
. This is ideal for prompt engineers looking to optimize prompts for better AI responses.
Coder Helper: Similar to Prompt Refiner but geared toward coding scenarios or technical prompts. It refines a given prompt for clarity and can also provide an explanation of what the prompt does
github.com
github.com
. Great for understanding complex prompts or improving instructions for code generation.
Copy Generator: Turn a video script, podcast outline, or any content notes into ready-to-use social media posts for every major platform in one click. Provide your notes or upload a text file, and the tool will produce platform-optimized copy for Facebook, LinkedIn, TikTok, YouTube, and a generic version
github.com
github.com
. Each post adheres to the best practices of its platform (e.g. character limits, hashtag style, tone), saving social media managers and creators hours of work.
More modules are coming (and you can extend it yourself): for example, future additions might include an email/newsletter generator, SEO content optimizer, or analytics insights tool. The design is modular – each tool is a self-contained script that plugs into the Streamlit app, so new features can be added without affecting existing ones.
Who Is It For?
This repository is for creators and teams who regularly produce content and interact with AI. If you’re a video producer needing social copy, a marketing agency personalizing content for multiple clients, or a prompt engineer refining prompts for reliable AI output, Jon’s AI Tools can help. It’s meant to assist in brainstorming, drafting, and refining content, not completely replace human creativity. You maintain control by reviewing and editing AI outputs. Agencies and freelancers can especially benefit: the Notion integration means you can maintain a database of client profiles (brand voice, audience, etc.) and quickly generate on-brand content for each client. The prompt engineering tools help technical teams document and fine-tune prompts for internal AI tools.
Real-World Example Workflow
Prep Your Client Profiles: Use the provided Notion template or script to set up your “AI Client Library” database. Add each client’s details (Brand Voice, Tone, Industry, Keywords). For instance, create entries like Acme Corp – Voice: Professional, Tone: Authoritative, Industry: Tech
github.com
.
Refine a Prompt: Suppose you have a rough prompt for a video editing AI: “Make a highlight reel from my footage.” Using Prompt Refiner, you’d paste that in and click Refine. The tool might return a structured, detailed prompt (with role, steps, format) that yields better AI results. If it’s not perfect, ask for a revision (e.g. “focus on a playful tone”) – the tool will iterate until you’re happy.
Generate Social Media Copy: After producing a new YouTube video, use Copy Generator. Paste your video’s summary or transcript, select the client profile (so the AI knows the brand voice to use), and hit Generate Copy. In seconds, you’ll get a Facebook post (with a punchy hook and hashtags), a LinkedIn post (with a professional angle), a TikTok caption (casual, trendy language), etc., each in the proper format
github.com
github.com
. Review and tweak if needed, then publish or schedule the posts.
Iterate and Save: If the client wants changes, refine the copy or prompts using the tools. You can download all generated text results in one click
github.com
. The Notion integration could be extended so that with one command, you save the final copy back to the client’s page for record-keeping.

Save Time, Improve Quality: Jon’s AI Tools automate the grunt work of content creation and prompt tuning. Instead of writing 5 separate social media posts or endlessly tweaking a prompt by hand, you get AI-generated drafts in seconds. This means faster turnaround for content campaigns and more time to focus on strategy and creativity. Consistency at Scale: By centralizing client profile data, the toolkit ensures that whether you’re writing a tweet or a LinkedIn post, the tone and voice stay on-brand for that client. This consistency is hard to maintain manually across many platforms and clients. The tools apply the same profile guidelines everywhere automatically
github.com
github.com
. Higher Engagement: The social prompts are crafted with best practices to boost engagement (e.g. hooks, questions, keywords). They encapsulate expert copywriting tips, so even non-writers can produce decent marketing copy. This can lead to better audience engagement and potentially more conversions or followers. Transparency and Control: Unlike black-box content generators, this toolkit lets you see and edit the prompts guiding the AI. You can refine the instructions, add your own twist to the templates, or intervene at any time. It’s AI assistance with human oversight, which means the final output can meet high quality standards required in professional settings. Scalability: Whether you manage 2 clients or 20, the same tools can scale with you. Adding a new client is as simple as a new Notion entry. Adding a new platform or content format is as simple as writing a new prompt template file and maybe a small tool script. The modular design means you can plug in new features (say, an email generator or an SEO auditor) without overhauling the whole system.