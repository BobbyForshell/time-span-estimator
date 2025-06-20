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

# Import multi-language support
from config.languages import LANGUAGES, get_text
from questions_multilingual import QUESTIONS_MULTILINGUAL

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

# Embedded logic functions from logic.py
def calculate_average_level(levels):
    """Calculate average stratum level (rounded to nearest int)"""
    if not levels:
        return 0
    return round(sum(levels) / len(levels))

def interpret_level(level, purpose, language="en"):
    """Return short summary and description based on level and use case"""
    stratum_ranges = {
        1: (get_text("stratum_1", language), get_text("stratum_desc_1", language)),
        2: (get_text("stratum_2", language), get_text("stratum_desc_2", language)),
        3: (get_text("stratum_3", language), get_text("stratum_desc_3", language)),
        4: (get_text("stratum_4", language), get_text("stratum_desc_4", language)),
        5: (get_text("stratum_5", language), get_text("stratum_desc_5", language)),
        6: (get_text("stratum_6", language), get_text("stratum_desc_6", language)),
        7: (get_text("stratum_7", language), get_text("stratum_desc_7", language))
    }

    summary, description = stratum_ranges.get(level, ("Undefined", "No clear interpretation."))

    if purpose == get_text("purpose_recruitment", language):
        description += get_text("purpose_add_recruitment", language)
    elif purpose == get_text("purpose_leadership", language):
        description += get_text("purpose_add_leadership", language)
    elif purpose == get_text("purpose_self", language):
        description += get_text("purpose_add_self", language)

    return summary, description

# Export functions
def categorize_questions(language="en"):
    """Define categories for each question"""
    return {
        0: get_text("category_project_planning", language),
        1: get_text("category_problem_solving", language), 
        2: get_text("category_strategic_planning", language),
        3: get_text("category_success_definition", language),
        4: get_text("category_leadership", language),
        5: get_text("category_organizational_change", language),
        6: get_text("category_team_design", language),
        7: get_text("category_mentoring", language),
        8: get_text("category_role_adaptation", language),
        9: get_text("category_service_design", language),
        10: get_text("category_strategy_contribution", language),
        11: get_text("category_success_evaluation", language)
    }

def analyze_by_category(answers, language="en"):
    """Analyze answers by category and identify strengths/weaknesses"""
    categories = categorize_questions(language)
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

def generate_csv_data(answers, avg_level, purpose, language="en"):
    """Generate CSV data for export"""
    csv_data = []
    
    # Add header
    csv_data.append(["Question", "Category", "Your Answer Level", "Selected Option"])
    
    # Add question data
    categories = categorize_questions(language)
    for i, (question, answer_level) in enumerate(zip(QUESTIONS_MULTILINGUAL, answers)):
        option_index = question['levels'].index(answer_level)
        csv_data.append([
            f"Question {i+1}",
            categories[i],
            f"Stratum {answer_level}",
            question['options'][language][option_index]
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

def generate_json_data(answers, avg_level, purpose, language="en"):
    """Generate JSON data for export"""
    categories = categorize_questions(language)
    
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
    
    for i, (question, answer_level) in enumerate(zip(QUESTIONS_MULTILINGUAL, answers)):
        option_index = question['levels'].index(answer_level)
        data["answers"].append({
            "question_number": i + 1,
            "category": categories[i],
            "question_text": question['text'][language],
            "answer_level": answer_level,
            "selected_option": question['options'][language][option_index]
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
if "language" not in st.session_state:
    st.session_state.language = "en"

# Language selector (always visible)
language = st.sidebar.selectbox("🌐 Language / Språk", list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], key="language_selector")
if language != st.session_state.language:
    st.session_state.language = language
    st.rerun()

# Page Routing
if st.session_state.page == "start":
    st.title(get_text("title", language))
    st.markdown(get_text("description", language))
    
    purpose = st.selectbox(get_text("purpose_label", language), [
        get_text("purpose_self", language),
        get_text("purpose_recruitment", language),
        get_text("purpose_leadership", language)
    ])
    
    if st.button(get_text("start_button", language)):
        st.session_state.purpose = purpose
        st.session_state.page = "questions"
        st.rerun()

elif st.session_state.page == "questions":
    q_index = st.session_state.current_q
    if q_index < len(QUESTIONS_MULTILINGUAL):
        q = QUESTIONS_MULTILINGUAL[q_index]
        
        # Progress bar and indicators
        progress = (q_index + 1) / len(QUESTIONS_MULTILINGUAL)
        st.progress(progress)
        
        # Question completion indicators
        cols = st.columns(len(QUESTIONS_MULTILINGUAL))
        for i, col in enumerate(cols):
            if i < q_index:
                col.markdown(get_text("completed", language))  # Completed
            elif i == q_index:
                col.markdown(get_text("current", language))  # Current
            else:
                col.markdown(get_text("not_started", language))  # Not started
        
        # Enhanced question header with progress
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>{get_text('question_progress', language).format(q_index + 1, len(QUESTIONS_MULTILINGUAL))}</h3>
                <p style="color: #666; font-size: 14px;">{get_text('percent_complete', language).format(int(progress * 100))}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Question content
        st.markdown(f"### {q['text'][language]}")
        answer = st.radio("Select your answer:", q["options"][language], key=f"q_{q_index}")
        
        # Simple navigation button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(get_text("next_question", language), type="primary"):
                selected_index = q["options"][language].index(answer)
                st.session_state.answers.append(q["levels"][selected_index])
                st.session_state.current_q += 1
                st.rerun()
    else:
        st.session_state.page = "result"
        st.rerun()

elif st.session_state.page == "result":
    avg_level = calculate_average_level(st.session_state.answers)
    summary, description = interpret_level(avg_level, st.session_state.purpose, language)

    # Main result header
    st.success(f"**{get_text('result_title', language).format(avg_level)}**")
    st.markdown(f"### {summary}")
    st.write(description)
    
    # Create tabs for different views - NOW WITH 5 TABS INCLUDING EXPORT
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        get_text("overview_tab", language), 
        get_text("analysis_tab", language), 
        get_text("insights_tab", language), 
        get_text("summary_tab", language), 
        get_text("export_tab", language)
    ])
    
    with tab1:
        st.markdown(f"### {get_text('time_span_profile', language)}")
        
        # Gauge chart showing stratum level
        try:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_level,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': get_text("stratum_level", language)},
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
            1: get_text("stratum_1", language),
            2: get_text("stratum_2", language), 
            3: get_text("stratum_3", language),
            4: get_text("stratum_4", language),
            5: get_text("stratum_5", language),
            6: get_text("stratum_6", language),
            7: get_text("stratum_7", language)
        }
        
        st.markdown(f"### {get_text('stratum_level_comparison', language)}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{get_text('your_level', language)}**")
            st.markdown(f"**Stratum {avg_level}** - {stratum_info[avg_level]}")
        with col2:
            st.markdown(f"**{get_text('typical_range', language)}**")
            st.markdown(get_text("most_people_range", language))
    
    with tab2:
        st.markdown(f"### {get_text('answer_distribution', language)}")
        
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
                labels={'x': get_text('stratum_level_label', language), 'y': get_text('number_of_answers', language)},
                title=get_text("distribution_title", language),
                color=levels,
                color_continuous_scale="viridis"
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Bar chart could not be displayed: {e}")
            st.write("Answer distribution:", answer_counts)
        
        # Answer pattern analysis
        st.markdown(f"### {get_text('answer_pattern_analysis', language)}")
        
        # Calculate statistics
        min_level = min(st.session_state.answers)
        max_level = max(st.session_state.answers)
        level_range = max_level - min_level
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(get_text("lowest_level", language), f"Stratum {min_level}")
        with col2:
            st.metric(get_text("highest_level", language), f"Stratum {max_level}")
        with col3:
            st.metric(get_text("range", language), f"{level_range} {get_text('levels', language)}")
        
        # Consistency analysis
        if level_range <= 2:
            consistency = get_text("high_consistency", language)
        elif level_range <= 4:
            consistency = get_text("moderate_consistency", language)
        else:
            consistency = get_text("high_variability", language)
        
        st.info(f"**{get_text('consistency_analysis', language)}** {consistency}")
    
    with tab3:
        st.markdown(f"### {get_text('detailed_insights', language)}")
        
        # Category analysis
        category_averages = analyze_by_category(st.session_state.answers, language)
        strengths, weaknesses = get_strength_weakness_analysis(category_averages)
        
        # Category performance chart
        st.markdown(f"#### {get_text('performance_by_category', language)}")
        categories = list(category_averages.keys())
        scores = list(category_averages.values())
        
        try:
            fig_category = px.bar(
                x=categories,
                y=scores,
                labels={'x': get_text('category_label', language), 'y': get_text('average_stratum_level', language)},
                title=get_text("category_performance_title", language),
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
            st.markdown(f"#### {get_text('your_strengths', language)}")
            for category, score in strengths:
                st.markdown(f"**{category}** (Stratum {score:.1f})")
                if score >= 5:
                    st.markdown(get_text("exceptional_strategic", language))
                elif score >= 4:
                    st.markdown(get_text("strong_operational", language))
                else:
                    st.markdown(get_text("solid_foundation", language))
        
        with col2:
            st.markdown(f"#### {get_text('development_areas', language)}")
            for category, score in weaknesses:
                st.markdown(f"**{category}** (Stratum {score:.1f})")
                if score <= 2:
                    st.markdown(get_text("focus_expanding", language))
                elif score <= 3:
                    st.markdown(get_text("develop_strategic", language))
                else:
                    st.markdown(get_text("enhance_approach", language))
        
        # Development roadmap
        st.markdown(f"#### {get_text('development_roadmap', language)}")
        overall_avg = sum(st.session_state.answers) / len(st.session_state.answers)
        
        if overall_avg <= 3:
            st.markdown(f"""
            {get_text('next_steps_growth', language)}
            {get_text('expand_planning', language)}
            {get_text('strategic_projects', language)}
            {get_text('mentorship_guidance', language)}
            """)
        elif overall_avg <= 5:
            st.markdown(f"""
            {get_text('next_steps_growth', language)}
            {get_text('systems_thinking', language)}
            {get_text('vision_development', language)}
            {get_text('cross_functional', language)}
            """)
        else:
            st.markdown(f"""
            {get_text('next_steps_growth', language)}
            {get_text('mentorship_share', language)}
            {get_text('organizational_influence', language)}
            {get_text('industry_leadership', language)}
            """)
        
        # Original insights
        st.markdown("---")
        st.markdown(f"### {get_text('original_insights', language)}")
        
        # Time horizon visualization
        time_horizons = {
            1: get_text("time_horizon_1", language),
            2: get_text("time_horizon_2", language), 
            3: get_text("time_horizon_3", language),
            4: get_text("time_horizon_4", language),
            5: get_text("time_horizon_5", language),
            6: get_text("time_horizon_6", language),
            7: get_text("time_horizon_7", language)
        }
        
        st.markdown(f"**{get_text('natural_time_horizon', language)}** {time_horizons[avg_level]}")
        
        # Development suggestions based on level
        development_tips = {
            1: get_text("dev_tip_1", language),
            2: get_text("dev_tip_2", language),
            3: get_text("dev_tip_3", language),
            4: get_text("dev_tip_4", language),
            5: get_text("dev_tip_5", language),
            6: get_text("dev_tip_6", language),
            7: get_text("dev_tip_7", language)
        }
        
        st.markdown(f"### {get_text('development_suggestions', language)}")
        st.write(development_tips[avg_level])
        
        # Purpose-specific insights
        if st.session_state.purpose == get_text("purpose_leadership", language):
            st.markdown(f"### {get_text('leadership_development_focus', language)}")
            if avg_level <= 3:
                st.write(get_text("focus_strategic", language))
            elif avg_level <= 5:
                st.write(get_text("enhance_systemic", language))
            else:
                st.write(get_text("leverage_visionary", language))
        
        elif st.session_state.purpose == get_text("purpose_recruitment", language):
            st.markdown(f"### {get_text('role_alignment', language)}")
            role_suggestions = {
                1: get_text("individual_contributor", language),
                2: get_text("team_coordination", language), 
                3: get_text("project_management", language),
                4: get_text("functional_leadership", language),
                5: get_text("strategic_leadership_roles", language),
                6: get_text("executive_roles", language),
                7: get_text("c_suite_roles", language)
            }
            st.write(f"**{get_text('suggested_role_types', language)}** {role_suggestions[avg_level]}")
    
    with tab4:
        st.markdown(f"### {get_text('assessment_summary', language)}")
        
        # Summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(get_text("final_stratum_level", language), f"Level {avg_level}")
            st.metric(get_text("questions_completed", language), f"{len(st.session_state.answers)}/12")
        with col2:
            st.metric(get_text("assessment_purpose", language), st.session_state.purpose)
            st.metric(get_text("average_score", language), f"{sum(st.session_state.answers)/len(st.session_state.answers):.1f}")
        
        # Answer breakdown
        st.markdown(f"### {get_text('answers_by_question', language)}")
        for i, (question, answer_level) in enumerate(zip(QUESTIONS_MULTILINGUAL, st.session_state.answers)):
            with st.expander(f"Question {i+1}: {question['text'][language][:50]}..."):
                st.write(f"**{get_text('your_answer_level', language)}** Stratum {answer_level}")
                # Find which option corresponds to this answer level
                option_index = question['levels'].index(answer_level)
                st.write(f"**{get_text('selected_option', language)}** {question['options'][language][option_index]}")
        
        st.markdown("---")
        st.markdown(f"*{get_text('assessment_completed', language)} {st.session_state.purpose}*")

    # NEW EXPORT TAB
    with tab5:
        st.markdown(f"### {get_text('export_title', language)}")
        st.markdown(get_text("export_description", language))
        
        # Generate export data
        csv_data = generate_csv_data(st.session_state.answers, avg_level, st.session_state.purpose, language)
        json_data = generate_json_data(st.session_state.answers, avg_level, st.session_state.purpose, language)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### {get_text('csv_export', language)}")
            st.markdown(f"**{get_text('csv_description', language)}**")
            st.markdown(get_text("includes_all", language))
            
            csv_filename = f"time_span_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_link = create_download_link(csv_data, csv_filename, "csv")
            st.markdown(csv_link, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"#### {get_text('json_export', language)}")
            st.markdown(f"**{get_text('json_description', language)}**")
            st.markdown(get_text("includes_structured", language))
            
            json_filename = f"time_span_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            json_link = create_download_link(json_data, json_filename, "json")
            st.markdown(json_link, unsafe_allow_html=True)
        
        # Summary report
        st.markdown("---")
        st.markdown(f"#### {get_text('summary_report', language)}")
        
        time_horizons = {
            1: get_text("time_horizon_1", language),
            2: get_text("time_horizon_2", language), 
            3: get_text("time_horizon_3", language),
            4: get_text("time_horizon_4", language),
            5: get_text("time_horizon_5", language),
            6: get_text("time_horizon_6", language),
            7: get_text("time_horizon_7", language)
        }
        
        development_tips = {
            1: get_text("dev_tip_1", language),
            2: get_text("dev_tip_2", language),
            3: get_text("dev_tip_3", language),
            4: get_text("dev_tip_4", language),
            5: get_text("dev_tip_5", language),
            6: get_text("dev_tip_6", language),
            7: get_text("dev_tip_7", language)
        }
        
        summary_report = f"""
# {get_text('report_title', language)}

**{get_text('assessment_date', language)}** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**{get_text('assessment_purpose', language)}** {st.session_state.purpose}
**{get_text('final_stratum_level', language)}** {avg_level}

## {get_text('key_results', language)}
- **{get_text('your_time_horizon', language)}** {time_horizons[avg_level]}
- **{get_text('consistency_range', language)}** {max(st.session_state.answers) - min(st.session_state.answers)} {get_text('levels', language)}
- **{get_text('questions_completed_report', language)}** {len(st.session_state.answers)}/12

## {get_text('summary_section', language)}
{summary}

{description}

## {get_text('development_focus', language)}
{development_tips[avg_level]}
"""
        
        st.text_area(get_text("copy_summary", language), summary_report, height=300)
        
        # Copy to clipboard button
        if st.button(get_text("copy_button", language)):
            st.success(get_text("summary_copied", language))

    # Restart button
    if st.button(get_text("restart_button", language)):
        for key in ["page", "answers", "current_q"]:
            del st.session_state[key]
        st.rerun()
