from functools import lru_cache
from typing import List
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate

from utils.logger import logger


@lru_cache(maxsize=1)
def get_qa_prompt() -> ChatPromptTemplate:
    """
    Get the QA prompt template.
    Tries to use LangChain Hub, with fallback to custom prompt.
    Uses LRU cache to avoid creating multiple instances.

    Returns:
        ChatPromptTemplate: The prompt template
    """
    prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    logger.info("Using QA prompt from LangChain Hub")

    return prompt


data_extraction_prompt = """
    SYSTEM INSTRUCTION:
    You are an intelligent data extraction assistant for AI training data preparation. Your task is to analyze web content from blog posts and extract only the high-value information that would be useful for training language models.

    USER CONTEXT:
    I am preparing a dataset to train an AI model and need to extract clean, high-quality content from blog posts. I'm using crawl4AI in a Docker container to fetch the content, but I need you to process each URL and extract only the relevant information.

    EXTRACTION GUIDELINES:
    1. Focus on extracting the main article content only:
    - Skip navigation elements, headers, footers, sidebars, and advertisements
    - Ignore author bios, related posts, and comments sections
    - Exclude social media buttons, sharing options, and calls-to-action

    2. For each article, extract and structure the following:
    - Title: The main headline of the article
    - Summary: A brief 1-2 sentence summary of the content
    - MainContent: The core article text, preserving paragraphs and section headers
    - KeyConcepts: A list of important concepts, terms, or ideas (max 10)
    - PublicationDate: If available

    3. Clean the extracted content:
    - Remove any remaining HTML tags or markdown formatting
    - Preserve important formatting like lists, headers, and emphasis where relevant
    - Fix any obvious OCR or extraction errors
    - Standardize spacing and paragraph breaks

    4. Output the extracted data in this JSON format:
    {
        "title": "Article title",
        "summary": "Brief summary",
        "mainContent": "Full article text with appropriate paragraph breaks",
        "keyConcepts": ["concept1", "concept2", "concept3"],
        "publicationDate": "YYYY-MM-DD or null if unavailable"
    }
"""


def get_forge_blog_prompt(topics: List[str], version: str = "V1") -> str:
    template = ""

    if version == "V1":
        template = """
            You are an expert blog writer specializing in creating SEO-optimized content. You have been given the following topics:

            {topics}

            For each topic, you must generate a separate, complete blog post that is optimized for search engines. For each blog post:

            1. **Title and Meta Description**:
               - Create a title that is attention-grabbing, includes the primary keyword, and is between 50-60 characters long.
               - Include a meta description of 110-150 characters that summarizes the post and includes the primary keyword.

            2. **Content Structure**:
               - Structure the content with an H1 title (the main title), H2 headers for main sections, and H3 headers for subsections.
               - Ensure natural integration of the primary and secondary keywords throughout the text.

            3. **Code Examples**:
               - If the topic is related to programming or technology, include relevant code examples.
               - Format the code using `<pre><code>` tags to present it as a code block.
               - Provide clear explanations of what the code does and how it relates to the topic.

            4. **Images**:
               - Suggest where images should be placed by including placeholders like "Insert image: [description]" with alt text that includes relevant keywords for SEO.
               - For example: "Insert image: a vibrant garden with flowers, alt text: 'colorful flower garden landscaping tips'."

            5. **References**:
               - Support your statements with references to reliable sources, such as academic papers, official documentation, or reputable websites.
               - Mention these sources appropriately within the text, providing their names and, if possible, URLs or other identifiers.
               - Ensure that all references are accurate and correctly cited based on your training data or general knowledge.

            6. **Content Quality**:
               - Ensure the content is informative, engaging, and aims for a word count of 800-1200 words for depth.
               - Leverage your training data on blog posts to provide valuable insights.

            7. **Formatting**:
               - Each blog post should be clearly distinct and formatted as a standalone piece, starting with the title and meta description, followed by the body with image placeholders and code examples as appropriate.

            Provide the output for each topic in a separate section, clearly labeled by the topic name.
        """
    elif version == "V2":
        template = """
            You are an expert AI blog writer specializing in SEO-friendly, informative, and well-structured blog posts. Your task is to generate **multiple** blog posts based on the given topics. Each topic should have its own **separate** blog post following these guidelines:

            ### **Input:**
            - You will receive a **list of topics**. For each topic, generate a unique, high-quality, and SEO-optimized blog post.

            ### **Blog Structure:**

            #### **1. Title & Headings**
               - Create a compelling, click-worthy **title** that includes high-ranking SEO keywords.
               - Use **H1, H2, and H3 headings** to structure the content for readability and SEO.

            #### **2. Introduction**
               - Start with an **engaging hook** to capture the reader’s attention.
               - Clearly state **what the article will cover** and why it is valuable.

            #### **3. Main Content**
               - Provide **in-depth, well-researched, and structured** content.
               - Naturally incorporate **SEO keywords** relevant to the topic without keyword stuffing.
               - Use **bullet points, tables, and lists** to improve readability.
               - **If applicable, include code snippets with proper syntax highlighting** (e.g., Python, JavaScript, HTML).
               - Explain code snippets with **real-world use cases** and step-by-step explanations.

            #### **4. Code Examples (If applicable)**
               - When relevant, include **well-commented code snippets**.
               - Provide **step-by-step explanations** for complex technical topics.
               - Example format:
                 ```python
                 # Example: Function to optimize website SEO with AI
                 def optimize_seo(content: str) -> str:
                     ""\"
                     Uses NLP to improve SEO keyword optimization.
                     ""\"
                     import some_ai_library
                     optimized_content = some_ai_library.optimize(content)
                     return optimized_content
                 ```
               - Explain how the code works and where it should be used.

            #### **5. Images & Media Suggestions**
               - Suggest **relevant, royalty-free images** to enhance the blog post.
               - Provide **alt text descriptions** for better accessibility and SEO.
               - Indicate **where images should be placed** for improved user engagement.

            #### **6. Reference Websites & Documents**
               - Include **reliable sources, official documentation, and useful guides**.
               - Example:
                 - For an AI-related topic: [OpenAI Documentation](https://platform.openai.com/docs)
                 - For SEO: [Moz SEO Guide](https://moz.com/learn/seo)

            #### **7. Call-to-Action (CTA)**
               - End with a **strong CTA** (e.g., encourage readers to comment, share, or subscribe).

            #### **8. SEO Enhancements**
               - Provide a **meta description** (under 160 characters) summarizing the post.
               - Suggest an **SEO-friendly URL slug**.

            ### **Topics to Generate Blogs For:**
         {topics}

         ### **Output Format:**
         For each topic, return a **separate** well-structured blog post in markdown or HTML format.

         #### **Example Output:**
         **Topic:** Example Topic
         **Blog Post:**
         - Title: "Example SEO-Optimized Blog Title"
         - Content: [Complete Blog with Headings, Content, Code Snippets, References, CTA, and SEO Elements]

         Now, generate a **separate** blog post for each topic in the list.
        """
    prompt_template = ChatPromptTemplate.from_template(template)

    formatted_prompt = prompt_template.format(
        topics="\n".join(f"- {topic}" for topic in topics)
    )

    return formatted_prompt
