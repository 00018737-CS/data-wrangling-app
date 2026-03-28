🤖 AI Usage Report
Project Name: AI Data Wrangler

Coursework: Data Science & Web Applications

1. 🛠 AI Tools Used
Model: Google Gemini / ChatGPT

Purpose: Code generation, debugging, and UI structuring.

Extent of Use: Approximately 70% of the initial boilerplate and complex logic (JSON parsing for the AI Assistant) was drafted with AI assistance. 30% was manual adjustment, bug fixing, and integration.

2. 📝 Prompts and Interaction
Our team used AI in a "Top-Down" approach. Here are examples of how we interacted with the AI:

Architecture Prompt: "How should I structure a multi-page Streamlit app where data needs to stay in memory between pages? Give me a folder structure for modules."

Logic Prompt: "Create a Python function using Pandas that detects outliers in a specific column using the IQR method and returns a boolean mask."

UI Prompt: "I have a DuplicateID error in Streamlit because I have two toggles with the same name. How do I fix this using keys?"

The AI Sandbox Prompt: "Write a system prompt for a LLM that takes a dataset summary and a user request, then returns ONLY a JSON array of cleaning actions like 'drop_duplicates' or 'fill_nulls'."

3. 🔍 Manual Verification & Corrections
Despite the AI's speed, we spent roughly half of our development time manually verifying and fixing the output. AI is not perfect, and we had to step in frequently:

The "AttributeError" Fix: The AI originally suggested calling functions named render_tab(), but our files used render(). We had to manually trace the traceback and fix the naming across all 8 cleaning modules.

State Persistence: The AI often "forgot" that Streamlit reruns the whole script. We had to manually implement st.session_state checks at the top of every page to prevent the dataset from disappearing when switching tabs.

Data Science Validation: In the "Scaling" module, the AI initially forgot to handle cases where the Standard Deviation is zero (which causes a division-by-zero error). We manually added if std_val != 0 to the Z-score logic.

Regex Debugging: The "Dirty Numeric Cleaning" regex provided by the AI was too aggressive and was removing decimal points. We manually tested and rewrote the regex to [^\d.-] to ensure floats remained valid.

UI Polish: We manually redesigned the "Before/After" preview metrics to ensure they were side-by-side, as the AI-generated code originally stacked them vertically, wasting screen space.

4. 💡 Learning Outcomes
Using AI significantly accelerated our learning because it allowed us to see "Pro-level" Python patterns (like pd.get_dummies or df.eval()) in action immediately. However, the manual verification taught us the most about defensive programming and exception handling. We learned that AI can write code, but humans must architect the safety and the user experience.

5. ✅ Final Human Sign-off
We, the team, have manually tested the following features to ensure 100% functionality:

File uploads for both .csv and .xlsx formats.

Successful execution of all 8 manual cleaning tabs.

The "Undo" logic and "Reset Session" button.

The export of the cleaned CSV file (verified by opening the result in Excel).

📦 Final Checklist for Submission:
You now have all 3 required documents:

Reflection Report (The "Journey" story).

README.md (The "Technical Manual").

AI_USAGE.md (The "Transparency" report).

Is there anything else you need before you zip up your project? I can help with a requirements.txt if you don't have one yet!

