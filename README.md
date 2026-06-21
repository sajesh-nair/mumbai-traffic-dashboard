Mumbai Commuter Intelligence Dashboard
An interactive data tool that analyzes traffic incident patterns to help corporate commuters optimize their shift timings across Mumbai's primary transit corridors.

Instead of relying on real-time navigation map rerouting, this project uses historical incident data to map network "heartbeats"—allowing drivers to identify precise time windows to completely side-step predictable gridlock.

Key Insights & Features
Predicting the Unavoidable: Focuses on the single variable commuters actually control: Timing.
Targeted Corridor Analysis: Maps high-density incident counts across key routes:

Western Express Highway (WEH) Axis
Sion-Panvel Highway Corridor
Eastern Express Highway (EEH) Axis
South Mumbai Main Trunk Roads
Jogeshwari-Vikhroli Link Road (JVLR)

Incident Trend Profiles: Visualizes diurnal spikes—such as early morning commercial truck breakdowns and mid-day school/delivery surge waves—so users can shift departures by 30–40 minutes to save hours of travel time.

🛠️ Tech Stack
Language: Python
Web Framework: Streamlit
Data Visualization: Plotly

📈 Data Source
The dashboard parses and categorizes ~500 official historical traffic incident logs and alerts broadcasted by the Mumbai Traffic Police data feed.

💻 Installation & Setup
Clone the repository:

Bash
git clone https://github.com/your-username/mumbai-commuter-intelligence.git
cd mumbai-commuter-intelligence

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
Run the application locally:

Bash
streamlit run app.py
