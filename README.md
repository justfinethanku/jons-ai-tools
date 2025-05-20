

Jon’s AI Tools

Overview

Jon’s AI Tools is a modular, AI-powered content and workflow toolkit for content creators, video producers, marketers, and prompt engineers. It leverages large language models (OpenAI GPT-4 and Google PaLM/Gemini) through Streamlit to assist with prompt engineering and content generation tasks.

The toolkit refines rough prompts into polished ones, explains complex prompts, generates social media copy across multiple platforms, and more – all while maintaining each client’s unique brand voice and tone.

By integrating with a Notion database called the AI Client Library for client profiles, the tools can automatically tailor outputs to a selected client’s industry, style, and keywords, ensuring consistency and personalization in generated content.

⸻

What Can You Do with This Toolkit?
	•	Prompt Refiner:
Improve any AI prompt iteratively. Enter a rough draft prompt and get back a clearer, more effective version. Request specific revisions (e.g. “make it shorter”, “add a friendly tone”) and the tool will refine the prompt in real-time.
Ideal for prompt engineers optimizing prompts for better AI responses.
	•	Coder Helper:
Similar to Prompt Refiner but geared toward coding scenarios or technical prompts. Refines prompts for clarity and can provide an explanation of what the prompt does.
Great for understanding complex prompts or improving instructions for code generation.
	•	Copy Generator:
Turn a video script, podcast outline, or any content notes into ready-to-use social media posts for every major platform in one click. Provide your notes or upload a text file, and the tool produces platform-optimized copy for Facebook, LinkedIn, TikTok, YouTube, and a generic version.
Each post adheres to best practices (character limits, hashtag style, tone), saving hours of work.
	•	Extensible Modules:
More modules are coming (and you can extend it yourself). Future additions may include an email/newsletter generator, SEO content optimizer, or analytics insights tool.
Design is modular – each tool is a self-contained script that plugs into the Streamlit app, so new features can be added without affecting existing ones.

⸻

Who Is It For?

This repository is for creators and teams who regularly produce content and interact with AI. If you’re a video producer needing social copy, a marketing agency personalizing content for multiple clients, or a prompt engineer refining prompts for reliable AI output, Jon’s AI Tools can help.
	•	Control: You review and edit AI outputs before using them.
	•	Agencies & Freelancers: Use the Notion integration to keep a database of client profiles (brand voice, audience, etc.) and generate on-brand content instantly.
	•	Technical Teams: The prompt engineering tools help document and fine-tune prompts for internal AI tools.

⸻

Real-World Example Workflow
	1.	Prep Your Client Profiles:
Use the provided Notion template or script to set up your “AI Client Library” database. Add each client’s details (Brand Voice, Tone, Industry, Keywords).
Example:

Acme Corp – Voice: Professional, Tone: Authoritative, Industry: Tech


	2.	Refine a Prompt:
Suppose you have a rough prompt for a video editing AI:

Make a highlight reel from my footage.

Use Prompt Refiner: paste your draft and click Refine. The tool returns a structured, detailed prompt (role, steps, format) for better AI results. If it’s not perfect, ask for a revision (“focus on a playful tone”) and the tool will iterate.

	3.	Generate Social Media Copy:
After producing a new YouTube video, use Copy Generator. Paste your summary or transcript, select the client profile (so the AI knows the brand voice), and hit Generate Copy.
You get:
	•	A Facebook post (punchy hook and hashtags)
	•	A LinkedIn post (professional angle)
	•	A TikTok caption (casual, trendy language)
	•	More
Review, tweak, and publish or schedule as needed.
	4.	Iterate and Save:
If the client wants changes, refine the copy or prompts using the tools. Download all generated text results in one click. The Notion integration could be extended so that with one command, you save the final copy back to the client’s page for record-keeping.

⸻

Why Use Jon’s AI Tools?
	•	Save Time, Improve Quality:
Automate the grunt work of content creation and prompt tuning. Instead of writing 5 separate social media posts or endlessly tweaking prompts by hand, get AI-generated drafts in seconds. Faster turnaround for campaigns, more time for strategy and creativity.
	•	Consistency at Scale:
By centralizing client profile data, the toolkit ensures the tone and voice stay on-brand across all platforms and clients. The tools apply the same guidelines everywhere automatically.
	•	Higher Engagement:
Social prompts are crafted with best practices to boost engagement (hooks, questions, keywords). Encapsulate expert copywriting tips so even non-writers can produce strong marketing copy.
	•	Transparency and Control:
Unlike black-box content generators, this toolkit lets you see and edit the prompts guiding the AI. Refine instructions, add your twist, or intervene at any time. AI assistance with human oversight.
	•	Scalability:
Whether you manage 2 clients or 20, the same tools scale with you. Adding a new client is as simple as a new Notion entry. Adding a new platform or content format is as simple as writing a new prompt template file and maybe a small tool script.

