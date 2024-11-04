import streamlit as st
import utils
from datetime import datetime, timedelta
import pandas as pd
import io
import calendar

def get_available_dates(course_id):
    """Get all dates that have attendance records for the course"""
    connection = utils.get_db_connection()
    if not connection:
        return []
        
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT attendance_date 
            FROM attendance 
            WHERE attendance_class_id = %s 
            ORDER BY attendance_date
        """, (course_id,))
        
        dates = [row[0] for row in cursor.fetchall()]
        return dates
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_attendance_report(course_id, start_date, end_date):
    """Generate attendance report for date range"""
    connection = utils.get_db_connection()
    if not connection:
        return None, "Database connection failed"
        
    try:
        cursor = connection.cursor()
        
        # Get all dates in range that have attendance
        cursor.execute("""
            SELECT DISTINCT attendance_date 
            FROM attendance 
            WHERE attendance_class_id = %s 
            AND attendance_date BETWEEN %s AND %s 
            ORDER BY attendance_date
        """, (course_id, start_date, end_date))
        
        dates = [row[0] for row in cursor.fetchall()]
        
        if not dates:
            return None, "No attendance records found for selected date range"
            
        # Construct dynamic SQL query
        date_columns = []
        for date in dates:
            formatted_date = date.strftime('%Y-%m-%d')
            date_columns.append(f"""
                MAX(CASE WHEN attendance.attendance_date = '{formatted_date}' 
                    THEN COALESCE(attendance.attendance_status, 'N/A') 
                END) AS '{formatted_date}'
            """)
        
        date_columns_sql = ", ".join(date_columns)
        
        query = f"""
            SELECT 
                students.student_name,
                students.student_id,
                {date_columns_sql}
            FROM 
                students
            LEFT JOIN 
                lists ON students.student_id = lists.list_student_id
            LEFT JOIN 
                attendance ON students.student_id = attendance.attendance_student_id
                AND attendance.attendance_date BETWEEN %s AND %s
                AND attendance.attendance_class_id = %s
            WHERE 
                lists.list_course_id = %s
            GROUP BY 
                students.student_name,
                students.student_id
            ORDER BY 
                students.student_name
        """
        
        cursor.execute(query, (start_date, end_date, course_id, course_id))
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=columns)
        
        # Calculate attendance statistics
        if len(dates) > 0:
            df['Total Present'] = df.iloc[:, 2:].apply(lambda x: (x == 'present').sum(), axis=1)
            df['Total Absent'] = df.iloc[:, 2:].apply(lambda x: (x == 'absent').sum(), axis=1)
            df['Attendance Rate'] = (df['Total Present'] / len(dates) * 100).round(2)
        
        return df, None
        
    except Exception as e:
        return None, f"Error generating report: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    st.title("Attendance Report Generator")
    
    # Verify course selection
    if 'selected_course' not in st.session_state:
        st.warning("Please select a course first")
        if st.button("Go to Course Selection"):
            st.switch_page("pages/courses.py")
        return
        
    course = st.session_state.selected_course
    st.write(f"📊 Generating report for: **{course['course_name']}**")
    
    # Get available dates
    available_dates = get_available_dates(course['course_id'])
    if not available_dates:
        st.warning("No attendance records found for this course")
        return
        
    first_date = min(available_dates)
    last_date = max(available_dates)
    
    # Date range selection
    st.markdown("### Select Report Type")
    report_type = st.radio(
        "Choose report period:",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True
    )
    
    start_date = None
    end_date = None
    
    if report_type == "Daily":
        selected_date = st.date_input(
            "Select date",
            min_value=first_date,
            max_value=last_date,
            value=last_date
        )
        start_date = selected_date
        end_date = selected_date
        
    elif report_type == "Weekly":
        # Get all weeks between first and last date
        weeks = []
        current = first_date
        while current <= last_date:
            week_start = current - timedelta(days=current.weekday())
            week_end = week_start + timedelta(days=7)
            weeks.append((week_start, week_end))
            current += timedelta(days=7)
            
        selected_weeks = st.multiselect(
            "Select weeks",
            options=weeks,
            format_func=lambda x: f"{x[0].strftime('%Y-%m-%d')} to {x[1].strftime('%Y-%m-%d')}"
        )
        
        if selected_weeks:
            start_date = min(week[0] for week in selected_weeks)
            end_date = max(week[1] for week in selected_weeks)
            
    else:  # Monthly
        months = []
        current = first_date
        while current <= last_date:
            months.append(current.replace(day=1))
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
                
        selected_months = st.multiselect(
            "Select months",
            options=months,
            format_func=lambda x: x.strftime('%B %Y'),
            default=[months[-1]]
        )
        
        if selected_months:
            start_date = min(selected_months)
            end_date = max(selected_months)
            # Set end date to last day of month
            end_date = end_date.replace(
                day=calendar.monthrange(end_date.year, end_date.month)[1]
            )
    
    if start_date and end_date:
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                df, error = generate_attendance_report(
                    course['course_id'],
                    start_date,
                    end_date
                )
                
                if error:
                    st.error(error)
                else:
                    # Display report
                    st.markdown("### Attendance Report")
                    st.dataframe(df)
                    
                    # Show summary statistics
                    st.markdown("### Summary Statistics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_attendance = df['Attendance Rate'].mean()
                        st.metric("Average Attendance Rate", f"{avg_attendance:.1f}%")
                    with col2:
                        perfect_attendance = (df['Attendance Rate'] == 100).sum()
                        st.metric("Perfect Attendance", perfect_attendance)
                    with col3:
                        low_attendance = (df['Attendance Rate'] < 80).sum()
                        st.metric("Low Attendance (<80%)", low_attendance)
                    
                    # Download options
                    st.markdown("### Download Report")
                    
                    # Excel download
                    excel_buffer = io.BytesIO()
                    df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_buffer,
                        file_name=f"attendance_report_{start_date}_to_{end_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # CSV download
                    csv_buffer = io.BytesIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download CSV Report",
                        data=csv_buffer,
                        file_name=f"attendance_report_{start_date}_to_{end_date}.csv",
                        mime="text/csv"
                    )

if __name__ == "__main__":
    main()