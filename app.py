"""
Prompt Doctor - Streamlit Application
A prompt engineering learning app with an AI examiner.
"""

import streamlit as st
import json
from datetime import datetime
from levels import (
    LEVELS,
    get_domains_for_level,
    get_task,
    get_sample_input,
    get_principles,
    get_output_schema,
    get_sample_examples,
    get_level_name,
)
from runner import run_prompt
from examiner import grade_prompt

# Page configuration
st.set_page_config(
    page_title="Prompt Doctor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session state
if "current_level" not in st.session_state:
    st.session_state.current_level = 1
if "unlocked_levels" not in st.session_state:
    st.session_state.unlocked_levels = {1}
if "domain" not in st.session_state:
    st.session_state.domain = list(LEVELS[1]["domains"].keys())[0]
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "verdict" not in st.session_state:
    st.session_state.verdict = None
if "model_output" not in st.session_state:
    st.session_state.model_output = None
if "prompt_history" not in st.session_state:
    st.session_state.prompt_history = []
if "error" not in st.session_state:
    st.session_state.error = None
if "show_certificate" not in st.session_state:
    st.session_state.show_certificate = False


def generate_certificate():
    """Generate certificate text for completing all levels."""
    date_str = datetime.now().strftime("%B %d, %Y")
    cert = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                  🏆 CERTIFICATE OF ACHIEVEMENT 🏆            ║
║                                                              ║
║              PROMPT DOCTOR CERTIFICATION                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

                    This certifies that

                    🎓 YOU ARE A PROMPT DOCTOR 🎓

              has successfully completed all 5 levels of
                    Prompt Engineering Mastery

Levels Completed:
  ✅ Level 1: Basic Prompting
  ✅ Level 2: Structured Output
  ✅ Level 3: Few-Shot Learning
  ✅ Level 4: Advanced Techniques
  ✅ Level 5: Expert Prompting

Date of Completion: {date_str}

You have demonstrated excellence in:
• Role assignment and clear instructions
• Structured JSON output generation
• Few-shot learning and example-based prompting
• Advanced prompt engineering techniques
• Expert-level prompt crafting

Congratulations on becoming a Prompt Doctor!
"""
    return cert


def reset_for_new_level():
    """Reset submission state when changing levels."""
    st.session_state.submitted = False
    st.session_state.verdict = None
    st.session_state.model_output = None
    st.session_state.error = None


def change_level(level):
    """Change to a different level."""
    st.session_state.current_level = level
    reset_for_new_level()
    # Update domain to first available for this level
    domains = get_domains_for_level(level)
    if domains:
        st.session_state.domain = domains[0]


def change_domain():
    """Handle domain change."""
    st.session_state.submitted = False
    st.session_state.verdict = None
    st.session_state.model_output = None
    st.session_state.error = None


# Title
st.title("🏥 Prompt Doctor")
st.markdown("### Learn prompt engineering through practice and AI feedback")

# Main layout: two columns
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("## 📋 Task Panel")

    # Level selector
    st.markdown("### Current Level")
    level_cols = st.columns(5)
    for i in range(1, 6):
        with level_cols[i - 1]:
            is_unlocked = i in st.session_state.unlocked_levels
            is_current = i == st.session_state.current_level
            btn_type = "primary" if is_current else "secondary"
            if is_unlocked:
                if st.button(
                    f"L{i}",
                    key=f"level_{i}",
                    type=btn_type,
                    use_container_width=True,
                ):
                    change_level(i)
            else:
                st.button(
                    f"🔒 L{i}",
                    key=f"level_{i}_locked",
                    disabled=True,
                    use_container_width=True,
                )

    level_name = get_level_name(st.session_state.current_level)
    st.markdown(f"**{level_name}**")
    st.markdown(f"*{LEVELS[st.session_state.current_level]['goal']}*")

    # Domain selector
    domains = get_domains_for_level(st.session_state.current_level)
    selected_domain = st.selectbox(
        "Select Domain",
        domains,
        index=domains.index(st.session_state.domain) if st.session_state.domain in domains else 0,
        key="domain_selector",
        on_change=change_domain,
    )
    st.session_state.domain = selected_domain

    # Task description
    task = get_task(st.session_state.current_level, st.session_state.domain)
    sample_input = get_sample_input(st.session_state.current_level, st.session_state.domain)

    st.markdown("### Task")
    st.info(task)

    st.markdown("### Sample Input")
    st.code(sample_input, language="text")

    # Show output schema for Level 2
    output_schema = get_output_schema(st.session_state.current_level, st.session_state.domain)
    if output_schema:
        st.markdown("### Required Output Schema")
        st.json(output_schema)

    # Show examples for Level 3
    examples = get_sample_examples(st.session_state.current_level, st.session_state.domain)
    if examples:
        st.markdown("### Reference Examples")
        for i, ex in enumerate(examples, 1):
            with st.expander(f"Example {i}"):
                st.markdown("**Input:**")
                st.code(ex["input"], language="text")
                st.markdown("**Expected Output:**")
                st.code(ex["output"], language="text")

    # Principles to follow
    principles = get_principles(st.session_state.current_level)
    st.markdown("### Principles to Follow")
    for p in principles:
        st.markdown(f"- {p}")

    # Prompt editor
    st.markdown("### ✍️ Your Prompt")
    prompt = st.text_area(
        "Write your prompt here...",
        height=200,
        placeholder="Write your prompt here. This will be sent to the model along with the sample input.",
        key="prompt_editor",
    )

    # Submit button
    submit_col1, submit_col2 = st.columns([3, 1])
    with submit_col1:
        submitted = st.button(
            "🚀 Submit Prompt",
            type="primary",
            use_container_width=True,
            disabled=not prompt.strip(),
        )
    with submit_col2:
        if st.button("🔄 Reset", use_container_width=True):
            reset_for_new_level()
            st.rerun()

with col_right:
    st.markdown("## 📊 Results Panel")

    if submitted and prompt.strip():
        with st.spinner("Running your prompt..."):
            st.session_state.submitted = True
            st.session_state.error = None

            # Step 1: Run the prompt
            runner_result = run_prompt(prompt, sample_input)

            if runner_result["success"]:
                model_output = runner_result["output"]
                st.session_state.model_output = model_output

                # Step 2: Grade the prompt
                with st.spinner("Examiner is grading your prompt..."):
                    verdict = grade_prompt(
                        level=st.session_state.current_level,
                        principles=principles,
                        student_prompt=prompt,
                        sample_input=sample_input,
                        model_output=model_output,
                    )
                    st.session_state.verdict = verdict

                    # Track history
                    st.session_state.prompt_history.append(
                        {
                            "level": st.session_state.current_level,
                            "domain": st.session_state.domain,
                            "prompt": prompt,
                            "verdict": verdict,
                        }
                    )

                    # Step 3: Handle pass/revise - unlock next level if passed
                    if verdict["verdict"] == "pass":
                        next_level = st.session_state.current_level + 1
                        if next_level <= 5:
                            st.session_state.unlocked_levels.add(next_level)
                        # Check if all levels completed
                        if st.session_state.current_level == 5:
                            st.session_state.show_certificate = True
                        # Rerun so level buttons reflect the new unlock state immediately
                        st.rerun()
            else:
                st.session_state.error = runner_result["error"]
                st.session_state.model_output = None
                st.session_state.verdict = None

    # Display results
    if st.session_state.error:
        st.error(f"❌ Error: {st.session_state.error}")

    # Certificate modal
    if st.session_state.show_certificate:
        st.balloons()
        st.success("🎉 **CONGRATULATIONS!** 🎉")
        st.markdown("### You've completed ALL 5 levels!")
        
        certificate_text = generate_certificate()
        st.code(certificate_text, language="text")
        
        st.download_button(
            label="📥 Download Certificate",
            data=certificate_text,
            file_name=f"prompt_doctor_certificate_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True,
        )
        
        if st.button("Close", use_container_width=True):
            st.session_state.show_certificate = False
            st.rerun()

    if st.session_state.verdict:
        verdict = st.session_state.verdict

        # Verdict banner
        if verdict["verdict"] == "pass":
            st.success("✅ **PASS** — All principles satisfied!")
            next_level = st.session_state.current_level + 1
            if next_level <= 5:
                st.balloons()
                st.info(f"🎉 **Level {next_level} unlocked!** Select it from the level buttons to continue.")
        else:
            st.warning("🔄 **REVISE** — Some principles need improvement.")

        # Examiner ran successfully?
        if not verdict.get("ran_ok", True):
            st.warning("⚠️ Examiner encountered issues. Results may be incomplete.")

        # Principles breakdown
        st.markdown("### 📋 Principle Evaluation")
        for p in verdict["principles"]:
            principle_name = p.get("name", "Unknown")
            passed = p.get("pass", False)
            weakness = p.get("weakness", "")
            question = p.get("question", "")

            if passed:
                st.success(f"✅ **{principle_name}** — Passed")
            else:
                st.error(f"❌ **{principle_name}** — Needs Work")
                if weakness:
                    st.markdown(f"**Weakness:** {weakness}")
                if question:
                    st.markdown(f"**💡 Guiding Question:** {question}")
                st.markdown("---")

        # Model output
        if st.session_state.model_output:
            st.markdown("### 🤖 Model Output")
            with st.expander("View model output", expanded=True):
                st.text(st.session_state.model_output)

        # Raw verdict JSON
        with st.expander("View raw examiner verdict"):
            st.json(verdict)

    elif not submitted and not st.session_state.error:
        # Show placeholder when nothing has been submitted
        st.info("👈 Write a prompt in the left panel and click **Submit Prompt** to get started.")
        st.markdown("""
        ### How it works:
        1. **Select a domain** (Legal, Healthcare, etc.)
        2. **Read the task** and sample input
        3. **Write a prompt** that follows the level principles
        4. **Submit** to run your prompt and get AI examiner feedback
        5. **Revise** based on feedback until you pass
        6. **Unlock** the next level!
        """)

    # Progress tracking
    if st.session_state.prompt_history:
        st.markdown("---")
        st.markdown("### 📈 Progress")
        st.markdown(f"**Current Level:** {st.session_state.current_level} - {level_name}")
        st.markdown(f"**Unlocked Levels:** {', '.join(f'L{i}' for i in sorted(st.session_state.unlocked_levels))}")
        st.markdown(f"**Attempts this session:** {len(st.session_state.prompt_history)}")

        with st.expander("View attempt history"):
            for i, attempt in enumerate(st.session_state.prompt_history, 1):
                v = attempt["verdict"]
                status = "✅ Pass" if v["verdict"] == "pass" else "🔄 Revise"
                st.markdown(f"**Attempt {i}:** L{attempt['level']} - {attempt['domain']} - {status}")
                if i < len(st.session_state.prompt_history):
                    st.markdown("---")


# Footer
st.markdown("---")
st.markdown(
    "Prompt Doctor — Learn prompt engineering through practice | Built with Streamlit + OpenRouter"
)