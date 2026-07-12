🎓 University Academic Command Center
A real-time academic analytics dashboard built with Python & Streamlit, connected live to Google Sheets.

🔗 Live App: https://live-student-tracker-kzxsmllzw6ojiyrbihvhtv.streamlit.app/

📌 Overview:-
This dashboard gives faculty and administrators a single unified view of student academic performance (SGPA/CGPA) across departments and colleges — with interactive charts, 
live KPIs, and a searchable student registry. Data syncs automatically every 60 seconds from a connected Google Sheet.


🚀 Features

- **Live Google Sheets sync** — no manual uploads, data refreshes every 60 seconds
- **4 navigation pages** — Overview, Overall Pass Rate, Avg Campus CGPA, Records
- **5 KPI cards** — Top Department, Overall Pass Rate, Avg Campus CGPA, Total Students, At-Risk count
- **Interactive charts** — Bar, Pie, Scatter, Heatmap
- **Student search** — search by Name or Registration Number
- **At-risk detection** — automatically flags students with SGPA below 6.0

🗂️ Navigation

| Page | Description |
|---|---|
| 📊 Overview | Department & college charts, SGPA heatmap, at-risk student list |
| 📈 Overall Pass Rate | Pass/fail breakdown by department, college, and study year |
| 🎓 Avg Campus CGPA | CGPA analysis by department, year, and CGPA band |
| 📋 Records | Department leaderboard and searchable student registry |

 📊 Charts Used

| Chart Type | Used For |
|---|---|
| Bar Chart | SGPA by dept, pass rate by dept/college/year, CGPA by dept/year |
| Pie Chart | Enrollment by dept/college, pass vs fail, CGPA bands |
| Scatter Plot | SGPA vs student count per dept, per-student CGPA distribution |
| Heatmap | SGPA across department × college grid |

🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web app framework |
| Plotly | Interactive charts |
| Pandas | Data processing |
| streamlit-gsheets-connection | Live Google Sheets connection |
