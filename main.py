# main.py - Time Span Estimator
import sys
import subprocess
import importlib.util
import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import csv
from datetime import datetime
import base64

def read_requirements():
    """Read requirements from requirements.txt if it exists"""
    requirements = []
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (remove version specifiers)
                    package = line.split('>=')[0].split('<=')[0].split('==')[0].split('!=')[0].split('~=')[0]
                    requirements.append(package.strip())
    return requirements

def check_and_install_requirements():
    """Check and install required packages"""
    # Get requirements from file or use default
    required_packages = read_requirements()
    if not required_packages:
        required_packages = ['streamlit']  # fallback
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("Installing missing packages...")
        for package in missing_packages:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}. Please install it manually: pip install {package}")
                return False
        print("All packages installed successfully!")
    return True

# Check and install requirements before importing streamlit
if not check_and_install_requirements():
    sys.exit(1)

import streamlit as st

# Embedded questions from questions.py
questions = [
    {
        "text": "You're given a new project. What is your first step?",
        "options": [
            "Make a list of tasks for the week.",
            "Create a 3–6 month project timeline.",
            "Align the project with our 3-year strategic plan.",
            "Evaluate how this project could shape our position over the next 10 years."
        ],
        "levels": [1, 3, 5, 6]
    },
    {
        "text": "A problem arises in your department. How do you approach it?",
        "options": [
            "Fix the immediate issue so operations continue.",
            "Identify patterns to prevent future occurrences.",
            "Assess the systemic causes affecting yearly performance.",
            "Examine how structural changes could influence the next decade."
        ],
        "levels": [1, 2, 4, 6]
    },
    {
        "text": "You're planning for next year. What is most important to you?",
        "options": [
            "Ensure this month's goals are met.",
            "Develop a roadmap for the coming 12 months.",
            "Review alignment with 3–5 year objectives.",
            "Model how today's choices affect future generations."
        ],
        "levels": [1, 3, 5, 7]
    },
    {
        "text": "How do you define success in your current role?",
        "options": [
            "Completing tasks efficiently and on time.",
            "Delivering predictable results over the year.",
            "Driving strategic initiatives over multiple years.",
            "Shaping vision and legacy far beyond your tenure."
        ],
        "levels": [1, 3, 5, 7]
    },
    {
        "text": "You're asked to lead a cross-functional initiative. What do you focus on?",
        "options": [
            "Coordinating tasks and timelines right away.",
            "Facilitating collaboration across teams for the next quarter.",
            "Structuring governance and decision-making for the next few years.",
            "Exploring long-term impacts on culture and external positioning."
        ],
        "levels": [1, 3, 4, 6]
    },
    {
        "text": "A colleague asks for your view on an organizational change. You:",
        "options": [
            "Offer your thoughts based on how it affects daily work.",
            "Share your views on its operational consequences over the year.",
            "Discuss its impact on long-term strategy and leadership.",
            "Reflect on how it connects to institutional legacy and identity."
        ],
        "levels": [1, 2, 5, 7]
    },
    {
        "text": "You are given full autonomy to design a team. Where do you start?",
        "options": [
            "Match people to current tasks and roles.",
            "Define team goals and a 6-month plan.",
            "Design structure and competencies for future growth.",
            "Shape a culture aligned with long-term mission."
        ],
        "levels": [1, 3, 4, 6]
    },
    {
        "text": "You are mentoring a younger colleague. You help them by:",
        "options": [
            "Giving practical tips for immediate challenges.",
            "Helping them map out goals for the next year.",
            "Encouraging reflection on their 3–5 year development.",
            "Guiding them to envision their future legacy and purpose."
        ],
        "levels": [1, 2, 4, 6]
    },
    {
        "text": "Your role is redefined. How do you respond?",
        "options": [
            "Clarify your tasks and responsibilities immediately.",
            "Assess short-term adjustments to your workflow.",
            "Evaluate strategic implications for your function.",
            "Reflect on how this shift may shape the organization's future."
        ],
        "levels": [1, 2, 4, 6]
    },
    {
        "text": "You're designing a new service. What drives your thinking?",
        "options": [
            "What clients expect this week or month.",
            "Trends in user needs over the next 6–12 months.",
            "Positioning in the market over the next 3–5 years.",
            "Disruption, legacy, and long-term system change."
        ],
        "levels": [1, 2, 5, 7]
    },
    {
        "text": "You are asked to contribute to a high-level strategy meeting. What is your approach?",
        "options": [
            "Give input based on recent data and outcomes.",
            "Raise concerns about trends and yearly goals.",
            "Suggest structural improvements over several years.",
            "Bring in thinking about generational or societal impacts."
        ],
        "levels": [1, 3, 5, 7]
    },
    {
        "text": "You are evaluating success of a recent initiative. What matters most?",
        "options": [
            "Whether it was delivered on time and budget.",
            "Whether it achieved quarterly KPIs.",
            "How it shifted long-term organizational behavior.",
            "Whether it changed our position in the broader ecosystem."
        ],
        "levels": [1, 3, 5, 6]
    }
]

# Embedded logic functions from logic.py
def calculate_average_level(levels):
    """Calculate average stratum level (rounded to nearest int)"""
    if not levels:
        return 0
    return round(sum(levels) / len(levels))

def interpret_level(level, purpose):
    """Return short summary and description based on level and use case"""
    stratum_ranges = {
        1: ("Short-term action", "You operate with focus on immediate tasks or daily goals."),
        2: ("Pattern and routine", "You handle recurring issues and short cycles (weeks–months)."),
        3: ("Project cycle focus", "You think in terms of quarters or 1-year execution plans."),
        4: ("Operational systems", "You work with functions, policies, or 2–3 year improvements."),
        5: ("Strategic leadership", "You manage complexity with a 5-year horizon and organizational influence."),
        6: ("Vision and innovation", "You think systemically over 10+ years, shaping structures and culture."),
        7: ("Societal shaping", "You envision transformations over decades, often influencing broader systems.")
    }

    summary, description = stratum_ranges.get(level, ("Undefined", "No clear interpretation."))

    if purpose == "Recruitment / Candidate Assessment":
        description += " This can help estimate alignment with role complexity."
    elif purpose == "Leadership Development":
        description += " Consider this your developmental time horizon — a basis for deeper reflection."
    elif purpose == "Self-reflection":
        description += " Use this insight to reflect on where you thrive and where you may want to grow."

    return summary, description

# Export functions
def categorize_questions():
    """Define categories for each question"""
    return {
        0: "Project Planning",
        1: "Problem Solving", 
        2: "Strategic Planning",
        3: "Success Definition",
        4: "Leadership",
        5: "Organizational Change",
        6: "Team Design",
        7: "Mentoring",
        8: "Role Adaptation",
        9: "Service Design",
        10: "Strategy Contribution",
        11: "Success Evaluation"
    }

def analyze_by_category(answers):
    """Analyze answers by category and identify strengths/weaknesses"""
    categories = categorize_questions()
    category_scores = {}
    
    for i, answer in enumerate(answers):
        category = categories[i]
        if category not in category_scores:
            category_scores[category] = []
        category_scores[category].append(answer)
    
    # Calculate average for each category
    category_averages = {}
    for category, scores in category_scores.items():
        category_averages[category] = sum(scores) / len(scores)
    
    return category_averages

def get_strength_weakness_analysis(category_averages):
    """Identify strongest and weakest categories"""
    sorted_categories = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)
    
    strengths = sorted_categories[:3]  # Top 3
    weaknesses = sorted_categories[-3:]  # Bottom 3
    
    return strengths, weaknesses

def generate_csv_data(answers, avg_level, purpose):
    """Generate CSV data for export"""
    csv_data = []
    
    # Add header
    csv_data.append(["Question", "Category", "Your Answer Level", "Selected Option"])
    
    # Add question data
    categories = categorize_questions()
    for i, (question, answer_level) in enumerate(zip(questions, answers)):
        option_index = question['levels'].index(answer_level)
        csv_data.append([
            f"Question {i+1}",
            categories[i],
            f"Stratum {answer_level}",
            question['options'][option_index]
        ])
    
    # Add summary data
    csv_data.append([])
    csv_data.append(["Summary", "Value"])
    csv_data.append(["Final Stratum Level", f"Level {avg_level}"])
    csv_data.append(["Assessment Purpose", purpose])
    csv_data.append(["Date Completed", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    csv_data.append(["Total Questions", len(answers)])
    csv_data.append(["Average Score", f"{sum(answers)/len(answers):.1f}"])
    
    return csv_data

def generate_json_data(answers, avg_level, purpose):
    """Generate JSON data for export"""
    categories = categorize_questions()
    
    data = {
        "assessment_info": {
            "date_completed": datetime.now().isoformat(),
            "purpose": purpose,
            "total_questions": len(answers),
            "final_stratum_level": avg_level,
            "average_score": round(sum(answers)/len(answers), 1)
        },
        "answers": []
    }
    
    for i, (question, answer_level) in enumerate(zip(questions, answers)):
        option_index = question['levels'].index(answer_level)
        data["answers"].append({
            "question_number": i + 1,
            "category": categories[i],
            "question_text": question['text'],
            "answer_level": answer_level,
            "selected_option": question['options'][option_index]
        })
    
    return data

def create_download_link(data, filename, file_type):
    """Create a download link for the data"""
    if file_type == "csv":
        csv_string = "\n".join([",".join([str(cell) for cell in row]) for row in data])
        b64 = base64.b64encode(csv_string.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    elif file_type == "json":
        json_string = json.dumps(data, indent=2)
        b64 = base64.b64encode(json_string.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}">Download JSON File</a>'
    
    return href

# Setup
st.set_page_config(page_title="Time Span Estimator", layout="centered")
if "page" not in st.session_state:
    st.session_state.page = "start"
if "answers" not in st.session_state:
    st.session_state.answers = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# Page Routing
if st.session_state.page == "start":
    st.title("🕰️ Time Span Estimator")
    st.markdown("""
Welcome!  
This tool estimates your natural time horizon — how far into the future you typically think and act — based on Elliot Jaques' **Stratified Systems Theory**.

Select how you intend to use the tool and begin.
""")
    purpose = st.selectbox("How do you plan to use this tool?", [
        "Self-reflection",
        "Recruitment / Candidate Assessment",
        "Leadership Development"
    ])
    if st.button("Start"):
        st.session_state.purpose = purpose
        st.session_state.page = "questions"
        st.rerun()

elif st.session_state.page == "questions":
    q_index = st.session_state.current_q
    if q_index < len(questions):
        q = questions[q_index]
        
        # Progress bar and indicators
        progress = (q_index + 1) / len(questions)
        st.progress(progress)
        
        # Question completion indicators
        cols = st.columns(len(questions))
        for i, col in enumerate(cols):
            if i < q_index:
                col.markdown("✅")  # Completed
            elif i == q_index:
                col.markdown("🔄")  # Current
            else:
                col.markdown("⭕")  # Not started
        
        # Enhanced question header with progress
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>Question {q_index + 1} of {len(questions)}</h3>
                <p style="color: #666; font-size: 14px;">{int(progress * 100)}% Complete</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Question content
        st.markdown(f"### {q['text']}")
        answer = st.radio("Select your answer:", q["options"], key=f"q_{q_index}")
        
        # Simple navigation button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Next Question", type="primary"):
                selected_index = q["options"].index(answer)
                st.session_state.answers.append(q["levels"][selected_index])
                st.session_state.current_q += 1
                st.rerun()
    else:
        st.session_state.page = "result"
        st.rerun()

elif st.session_state.page == "result":
    avg_level = calculate_average_level(st.session_state.answers)
    summary, description = interpret_level(avg_level, st.session_state.purpose)

    # Main result header
    st.success(f"**Your estimated time span level is: Stratum {avg_level}**")
    st.markdown(f"### {summary}")
    st.write(description)
    
    # Create tabs for different views - NOW WITH 5 TABS INCLUDING EXPORT
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Detailed Analysis", "🎯 Insights", "📋 Summary", "📤 Export"])
    
    with tab1:
        st.markdown("### Your Time Span Profile")
        
        # Gauge chart showing stratum level
        try:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_level,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Stratum Level"},
                delta = {'reference': 4},
                gauge = {
                    'axis': {'range': [None, 7]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 1], 'color': "lightgray"},
                        {'range': [1, 2], 'color': "lightblue"},
                        {'range': [2, 3], 'color': "lightgreen"},
                        {'range': [3, 4], 'color': "yellow"},
                        {'range': [4, 5], 'color': "orange"},
                        {'range': [5, 6], 'color': "red"},
                        {'range': [6, 7], 'color': "darkred"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 7
                    }
                }
            ))
            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
        except Exception as e:
            st.error(f"Chart could not be displayed: {e}")
            st.info("Your stratum level: " + str(avg_level))
        
        # Stratum level comparison
        stratum_info = {
            1: "Short-term action",
            2: "Pattern and routine", 
            3: "Project cycle focus",
            4: "Operational systems",
            5: "Strategic leadership",
            6: "Vision and innovation",
            7: "Societal shaping"
        }
        
        st.markdown("### Stratum Level Comparison")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Your Level:**")
            st.markdown(f"**Stratum {avg_level}** - {stratum_info[avg_level]}")
        with col2:
            st.markdown("**Typical Range:**")
            st.markdown("Most people fall between **Stratum 2-5**")
    
    with tab2:
        st.markdown("### Your Answer Distribution")
        
        # Create histogram of answers
        answer_counts = {}
        for level in st.session_state.answers:
            answer_counts[level] = answer_counts.get(level, 0) + 1
        
        # Bar chart of answer distribution
        levels = list(answer_counts.keys())
        counts = list(answer_counts.values())
        
        try:
            fig_bar = px.bar(
                x=levels, 
                y=counts,
                labels={'x': 'Stratum Level', 'y': 'Number of Answers'},
                title="Distribution of Your Answers Across Stratum Levels",
                color=levels,
                color_continuous_scale="viridis"
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Bar chart could not be displayed: {e}")
            st.write("Answer distribution:", answer_counts)
        
        # Answer pattern analysis
        st.markdown("### Answer Pattern Analysis")
        
        # Calculate statistics
        min_level = min(st.session_state.answers)
        max_level = max(st.session_state.answers)
        level_range = max_level - min_level
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lowest Level", f"Stratum {min_level}")
        with col2:
            st.metric("Highest Level", f"Stratum {max_level}")
        with col3:
            st.metric("Range", f"{level_range} levels")
        
        # Consistency analysis
        if level_range <= 2:
            consistency = "High consistency - you think at similar time horizons across different scenarios"
        elif level_range <= 4:
            consistency = "Moderate consistency - you adapt your thinking based on context"
        else:
            consistency = "High variability - you think very differently depending on the situation"
        
        st.info(f"**Consistency Analysis:** {consistency}")
    
    with tab3:
        st.markdown("### Detailed Insights & Analysis")
        
        # Category analysis
        category_averages = analyze_by_category(st.session_state.answers)
        strengths, weaknesses = get_strength_weakness_analysis(category_averages)
        
        # Category performance chart
        st.markdown("#### Performance by Category")
        categories = list(category_averages.keys())
        scores = list(category_averages.values())
        
        try:
            fig_category = px.bar(
                x=categories,
                y=scores,
                labels={'x': 'Category', 'y': 'Average Stratum Level'},
                title="Your Performance Across Different Thinking Categories",
                color=scores,
                color_continuous_scale="RdYlGn"
            )
            fig_category.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_category, use_container_width=True)
        except Exception as e:
            st.error(f"Category chart could not be displayed: {e}")
        
        # Strengths and weaknesses
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Your Strengths")
            for category, score in strengths:
                st.markdown(f"**{category}** (Stratum {score:.1f})")
                if score >= 5:
                    st.markdown("💪 *Exceptional strategic thinking*")
                elif score >= 4:
                    st.markdown("👍 *Strong operational thinking*")
                else:
                    st.markdown("✅ *Solid foundation*")
        
        with col2:
            st.markdown("#### 📈 Development Areas")
            for category, score in weaknesses:
                st.markdown(f"**{category}** (Stratum {score:.1f})")
                if score <= 2:
                    st.markdown("🎯 *Focus on expanding time horizon*")
                elif score <= 3:
                    st.markdown("🔄 *Develop strategic perspective*")
                else:
                    st.markdown("🔄 *Enhance current approach*")
        
        # Development roadmap
        st.markdown("#### 🗺️ Development Roadmap")
        overall_avg = sum(st.session_state.answers) / len(st.session_state.answers)
        
        if overall_avg <= 3:
            st.markdown("""
            **Next Steps for Growth:**
            1. **Expand Planning Horizons** - Practice thinking 6-12 months ahead
            2. **Strategic Projects** - Take on projects with longer timelines
            3. **Mentorship** - Seek guidance from more experienced strategic thinkers
            """)
        elif overall_avg <= 5:
            st.markdown("""
            **Next Steps for Growth:**
            1. **Systems Thinking** - Consider how decisions impact multiple functions
            2. **Vision Development** - Practice articulating long-term organizational goals
            3. **Cross-functional Leadership** - Lead initiatives across departments
            """)
        else:
            st.markdown("""
            **Next Steps for Growth:**
            1. **Mentorship** - Share your strategic insights with others
            2. **Organizational Influence** - Shape culture and long-term direction
            3. **Industry Leadership** - Consider broader societal impact
            """)
        
        # Original insights
        st.markdown("---")
        st.markdown("### Original Insights")
        
        # Time horizon visualization
        time_horizons = {
            1: "Days to weeks",
            2: "Weeks to months", 
            3: "Months to 1 year",
            4: "1-3 years",
            5: "3-5 years",
            6: "5-10 years",
            7: "10+ years"
        }
        
        st.markdown(f"**Your Natural Time Horizon:** {time_horizons[avg_level]}")
        
        # Development suggestions based on level
        development_tips = {
            1: "Consider expanding your planning horizon to include quarterly goals and project timelines.",
            2: "Try thinking about annual planning and how current patterns affect longer-term outcomes.",
            3: "Explore strategic thinking and how your projects align with organizational objectives.",
            4: "Develop systems thinking and consider how operational changes impact multiple functions.",
            5: "Focus on vision development and how strategic decisions shape organizational culture.",
            6: "Consider broader societal impacts and how your work influences future generations.",
            7: "Your long-term thinking is exceptional. Focus on mentoring others and sharing your vision."
        }
        
        st.markdown("### Development Suggestions")
        st.write(development_tips[avg_level])
        
        # Purpose-specific insights
        if st.session_state.purpose == "Leadership Development":
            st.markdown("### Leadership Development Focus")
            if avg_level <= 3:
                st.write("Focus on developing strategic thinking and long-term planning skills.")
            elif avg_level <= 5:
                st.write("Enhance your ability to think systemically and influence organizational culture.")
            else:
                st.write("Leverage your visionary thinking to mentor others and shape organizational direction.")
        
        elif st.session_state.purpose == "Recruitment / Candidate Assessment":
            st.markdown("### Role Alignment")
            role_suggestions = {
                1: "Individual contributor roles with clear, immediate deliverables",
                2: "Team coordination roles with recurring responsibilities", 
                3: "Project management roles with defined timelines",
                4: "Functional leadership roles with operational oversight",
                5: "Strategic leadership roles with organizational influence",
                6: "Executive roles with vision and innovation focus",
                7: "C-suite or board-level roles with societal impact"
            }
            st.write(f"**Suggested Role Types:** {role_suggestions[avg_level]}")
    
    with tab4:
        st.markdown("### Assessment Summary")
        
        # Summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Final Stratum Level", f"Level {avg_level}")
            st.metric("Questions Completed", f"{len(st.session_state.answers)}/12")
        with col2:
            st.metric("Assessment Purpose", st.session_state.purpose)
            st.metric("Average Score", f"{sum(st.session_state.answers)/len(st.session_state.answers):.1f}")
        
        # Answer breakdown
        st.markdown("### Your Answers by Question")
        for i, (question, answer_level) in enumerate(zip(questions, st.session_state.answers)):
            with st.expander(f"Question {i+1}: {question['text'][:50]}..."):
                st.write(f"**Your Answer Level:** Stratum {answer_level}")
                # Find which option corresponds to this answer level
                option_index = question['levels'].index(answer_level)
                st.write(f"**Selected Option:** {question['options'][option_index]}")
        
        st.markdown("---")
        st.markdown(f"*Assessment completed for: {st.session_state.purpose}*")

    # NEW EXPORT TAB
    with tab5:
        st.markdown("### Export Your Results")
        st.markdown("Download your assessment results for further analysis or record keeping.")
        
        # Generate export data
        csv_data = generate_csv_data(st.session_state.answers, avg_level, st.session_state.purpose)
        json_data = generate_json_data(st.session_state.answers, avg_level, st.session_state.purpose)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 CSV Export")
            st.markdown("**Best for:** Excel analysis, data processing")
            st.markdown("**Includes:** All questions, answers, categories, and summary data")
            
            csv_filename = f"time_span_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_link = create_download_link(csv_data, csv_filename, "csv")
            st.markdown(csv_link, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📄 JSON Export")
            st.markdown("**Best for:** Programmatic analysis, API integration")
            st.markdown("**Includes:** Structured data with metadata and detailed responses")
            
            json_filename = f"time_span_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            json_link = create_download_link(json_data, json_filename, "json")
            st.markdown(json_link, unsafe_allow_html=True)
        
        # Summary report
        st.markdown("---")
        st.markdown("#### 📋 Quick Summary Report")
        
        time_horizons = {
            1: "Days to weeks",
            2: "Weeks to months", 
            3: "Months to 1 year",
            4: "1-3 years",
            5: "3-5 years",
            6: "5-10 years",
            7: "10+ years"
        }
        
        development_tips = {
            1: "Consider expanding your planning horizon to include quarterly goals and project timelines.",
            2: "Try thinking about annual planning and how current patterns affect longer-term outcomes.",
            3: "Explore strategic thinking and how your projects align with organizational objectives.",
            4: "Develop systems thinking and consider how operational changes impact multiple functions.",
            5: "Focus on vision development and how strategic decisions shape organizational culture.",
            6: "Consider broader societal impacts and how your work influences future generations.",
            7: "Your long-term thinking is exceptional. Focus on mentoring others and sharing your vision."
        }
        
        summary_report = f"""
# Time Span Assessment Report

**Assessment Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Assessment Purpose:** {st.session_state.purpose}
**Final Stratum Level:** {avg_level}

## Key Results
- **Your Time Horizon:** {time_horizons[avg_level]}
- **Consistency Range:** {max(st.session_state.answers) - min(st.session_state.answers)} levels
- **Questions Completed:** {len(st.session_state.answers)}/12

## Summary
{summary}

{description}

## Development Focus
{development_tips[avg_level]}
"""
        
        st.text_area("Copy this summary:", summary_report, height=300)
        
        # Copy to clipboard button
        if st.button("📋 Copy Summary to Clipboard"):
            st.success("Summary copied! (Note: You may need to manually copy from the text area above)")

    # Restart button
    if st.button("🔄 Take Assessment Again"):
        for key in ["page", "answers", "current_q"]:
            del st.session_state[key]
        st.rerun()
