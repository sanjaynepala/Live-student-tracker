🎓 Academic Command Center

A real-time Streamlit dashboard that connects to a live Google Sheet to track student CGPA, pass rates, and departmental performance across a university campus.

🔗 Live App: https://live-student-tracker-kzxsmllzw6ojiyrbihvhtv.streamlit.app/


✨ Features


📊 Overview — Enrollment by department, avg CGPA by department, CGPA vs. student-count scatter, top 10 students, and at-risk students (based on Result = Fail).
📈 Overall Pass Rate — Pass/fail distribution, pass rate by department and by study year, with a 75% target line.
🎓 Avg Campus CGPA — Campus-wide, department-wise, and year-wise CGPA breakdowns.
📋 Records — Department leaderboard + searchable, filterable full student registry (auto-sorted by Redg. No. when a department is selected).
Live sync — Refreshes from Google Sheets every 60 seconds.
Filters — Study Year and Department, applied globally across all views.


🗂️ Data Source

Reads directly from a connected Google Sheet via streamlit-gsheets. Required columns are documented in table_column.txt — key ones include Name, programme, college, overall sgp, study year, result, and a registration-number column (any header containing "redg").

🛠️ Tech Stack

ComponentToolUI / App frameworkStreamlitData sourceGoogle Sheets (streamlit-gsheets)Data handlingPandasChartsPlotly (Express & Graph Objects)
