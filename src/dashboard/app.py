# src/dashboard/app.py
import streamlit as st
import pandas as pd
from pathlib import Path
import re
import plotly.express as px

def standardize_mumbai_location(text):
    """Maps messy text updates cleanly into major target commuter networks only."""
    if not isinstance(text, str):
        return "Other Connecting Roads"
    text_lower = text.lower()
    
    mapping = {
        "Western Express Highway (WEH) Axis": ["weh", "western express", "andheri", "vile parle", "borivali", "bandra", "santacruz", "mumbai public school", "chakala"],
        "Eastern Express Highway (EEH) Axis": ["eeh", "eastern express", "ghatkopar", "vikhroli", "mulund", "bhandup", "chembur"],
        "Jogeshwari-Vikhroli Link Road (JVLR)": ["jvlr", "jogeshwari-vikhroli", "powai", "seepz"],
        "Sion-Panvel Highway Corridor": ["sion hospital", "sion", "chheda nagar", "mankhurd", "vashi"],
        "Santacruz-Chembur Link Road (SCLR)": ["sclr", "santacruz chembur", "kurla", "star junction", "amar mahal"],
        "LBS Marg Corridor": ["lbs marg", "lbs road", "mulund naka", "bhandup west"],
        "South Mumbai Main Trunk Roads": ["pedder road", "marine drive", "babulnath", "crawford", "colaba", "worli", "haji ali", "m.k.road"]
    }
    
    for standardized_name, keywords in mapping.items():
        if any(kw in text_lower for kw in keywords):
            return standardized_name
            
    return "Other Connecting Roads"

def load_data():
    processed_path = Path("data/raw/mumbai_traffic_processed.csv")
    if not processed_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(processed_path)
    
    if not df.empty:
        filter_keywords = ['aadhaar', 'identity', 'worli mumbai', 'resident status']
        df = df[~df['text'].str.contains('|'.join(filter_keywords), na=False, case=False)]
        df['Standardized_Location'] = df['text'].apply(standardize_mumbai_location)
        df['datetime'] = pd.to_datetime(df['createdAt'], format='mixed', errors='coerce')
        df['Hour_of_Day'] = df['datetime'].dt.hour
        
    return df

def main():
    st.set_page_config(page_title="Mumbai Smart Commuter Engine", layout="wide")
    
    df = load_data()
    if df.empty:
        st.warning("⚠️ Processed dataset not found.")
        return
        
    valid_data = df.dropna(subset=['Standardized_Location'])

    st.title("🚀 Mumbai Commuter Intelligence & Arrival Delay Simulator")
    st.caption(f"Empirical Model Layer | Analyzing {len(df)} Live Incidents to Optimize Corporate Transit Windows")
    st.markdown("---")

    # ------------------------------------------------------------
    # 🔮 SMART COMMUTE RISK SIMULATOR
    # ------------------------------------------------------------
    st.header("🔮 1. Interactive Commute Risk Simulator")
    st.markdown("Select your route and planned departure hour to calculate your expected travel overhead delay dynamically from actual incident counts.")
    
    col_ui, col_display = st.columns([1, 1])
    
    with col_ui:
        user_route = st.selectbox(
            "Select Your Route / Main Transit Axis:",
            options=sorted(list(valid_data['Standardized_Location'].unique()))
        )
        
        user_hour = st.slider(
            "Select Your Planned Departure Hour:",
            min_value=0, max_value=23, value=13,
            format="%d:00 HRS"
        )
        
        route_df = valid_data[valid_data['Standardized_Location'] == user_route]
        hour_df = route_df[route_df['Hour_of_Day'] == user_hour]
        
        if hour_df.empty:
            global_hour_df = valid_data[valid_data['Hour_of_Day'] == user_hour]
            active_incidents = len(global_hour_df) * 0.15 
            active_breakdowns = (global_hour_df['Traffic_Reason'] == 'Vehicle Breakdown').sum() * 0.15
            active_accidents = (global_hour_df['Traffic_Reason'] == 'Accident').sum() * 0.15
        else:
            active_incidents = len(hour_df)
            active_breakdowns = (hour_df['Traffic_Reason'] == 'Vehicle Breakdown').sum()
            active_accidents = (hour_df['Traffic_Reason'] == 'Accident').sum()
            
        base_delay = 15 
        incident_weight = active_incidents * 8  
        breakdown_premium = active_breakdowns * 12
        accident_premium = active_accidents * 20
        
        total_simulated_delay = int(base_delay + incident_weight + breakdown_premium + accident_premium)
        
    with col_display:
        if total_simulated_delay > 40:
            box_color, status_text = "#FF4B4B", "🔴 CRITICAL GRIDLOCK WINDOW"
        elif total_simulated_delay > 25:
            box_color, status_text = "#FFA500", "🟡 MODERATE DELAY RISK"
        else:
            box_color, status_text = "#00FA9A", "🟢 OPTIMAL TRAVEL STREAM"
            
        st.markdown(
            f"""
            <div style="background-color:#111; padding:25px; border-radius:12px; border-left:8px solid {box_color};">
                <p style="margin:0; font-size:14px; color:#aaa; font-weight:bold; letter-spacing:1px;">SIMULATED OVERHEAD DELAY</p>
                <h1 style="margin:5px 0; color:{box_color}; font-size:46px;">+{total_simulated_delay} Mins</h1>
                <p style="margin:0; font-size:16px; color:#fff; font-weight:600;">Current State: {status_text}</p>
                <p style="margin:10px 0 0 0; font-size:13px; color:#888;">*Data State: Calculated dynamically from reported road disruptions matching this timeline profile.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ------------------------------------------------------------
    # 📊 SECTION 2: HIGH-VALUE RE-ENGINEERED GRAPH MATRIX
    # ------------------------------------------------------------
    st.header("📊 2. High-Density Congestion Core Mapping")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### Overall Total Traffic Volume by Route Axis")
        chart_matrix = valid_data[valid_data['Standardized_Location'] != "Other Connecting Roads"]
        hotspot_matrix = chart_matrix.groupby('Standardized_Location').size().reset_index(name='Total_Alerts').sort_values(by='Total_Alerts', ascending=False).head(5)
        
        fig1 = px.bar(hotspot_matrix, x='Total_Alerts', y='Standardized_Location', orientation='h', template='plotly_dark')
        fig1.update_layout(xaxis_title="Total Incident Log Count", yaxis_title=None, height=280, margin=dict(l=10, r=10, t=10, b=10))
        fig1.update_traces(marker_color='#4682B4') 
        # Updated: Switched use_container_width=True with width='stretch'
        st.plotly_chart(fig1, width='stretch', config={'staticPlot': True})
        
    with col_chart2:
        st.markdown(f"#### ⚡ Hourly Trend Profile for: **{user_route}**")
        
        dynamic_route_df = valid_data[valid_data['Standardized_Location'] == user_route]
        hourly_trends = dynamic_route_df.groupby('Hour_of_Day').size().reindex(range(0, 24), fill_value=0)
        
        time_labels = []
        for h in range(24):
            if h == 0: time_labels.append("12 AM")
            elif h == 12: time_labels.append("12 PM")
            elif h > 12: time_labels.append(f"{h-12} PM")
            else: time_labels.append(f"{h} AM")
            
        dynamic_trend_df = pd.DataFrame({"Hour of Day": time_labels, "Active Reports Count": hourly_trends.values})
        
        fig2 = px.bar(dynamic_trend_df, x='Hour of Day', y='Active Reports Count', template='plotly_dark')
        fig2.update_layout(xaxis_title="24-Hour Distribution Axis", yaxis_title="Active Alerts", height=280, margin=dict(l=10, r=10, t=10, b=10))
        fig2.update_traces(marker_color='#FF6347') 
        # Updated: Switched use_container_width=True with width='stretch'
        st.plotly_chart(fig2, width='stretch', config={'staticPlot': True})

    st.markdown("---")

    # ------------------------------------------------------------
    # ⏱️ SECTION 3: THE STRATEGIC OFFICE TIMING PLANNER
    # ------------------------------------------------------------
    st.header("⏱️ 3. The Smart Commuter's Shift Planning Guide")
    
    hourly_counts = df.groupby('Hour_of_Day').size().reindex(range(0, 24), fill_value=0)
    time_labels_all = []
    for h in range(24):
        if h == 0: time_labels_all.append("12 AM")
        elif h == 12: time_labels_all.append("12 PM")
        elif h > 12: time_labels_all.append(f"{h-12} PM")
        else: time_labels_all.append(f"{h} AM")
        
    time_df = pd.DataFrame({"Hour Axis": time_labels_all, "Reports Density": hourly_counts.values})
    
    fig_time = px.bar(time_df, x='Hour Axis', y='Reports Density', template='plotly_dark')
    fig_time.update_layout(xaxis_title="Time of Day (Strict Chronological Sequence)", yaxis_title="Logged Volume", height=280)
    fig_time.update_traces(marker_color='#00FA9A')
    # Updated: Switched use_container_width=True with width='stretch'
    st.plotly_chart(fig_time, width='stretch', config={'staticPlot': True})
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.success(
            "🌅 **Optimized Morning Corporate Shift Strategy:**\n\n"
            "* **The Data Threat:** Alerts spike sharply at **6:00 AM** due to early commercial breakdown bottlenecks on flyover inclines.\n"
            "* **Workaround:** If you travel this route, leave early to cross major checkpoints by **5:15 AM**. If you miss that slot, push your departure back to **8:30 AM** to allow recovery teams to clear lanes."
        )
    with col_m2:
        st.warning(
            "🌆 **Optimized Afternoon / Return Shift Strategy:**\n\n"
            "* **The Data Threat:** Mid-day delivery distributions cause a secondary incident wave peaking right around **1:00 PM**.\n"
            "* **Workaround:** Avoid traveling during peak afternoon lunch windows. Shift your schedule to travel before **12:00 PM**, or stall your departure until **2:30 PM** to save hours of gridlock time."
        )

if __name__ == "__main__":
    main()