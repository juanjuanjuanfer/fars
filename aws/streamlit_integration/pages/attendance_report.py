import streamlit as st
import utils
from datetime import datetime, timedelta
import pandas as pd
import io
import calendar
import plotly.graph_objects as go



def get_month_options(first_date, last_date):
    """Generate a list of months between two dates"""
    months = []
    current = first_date.replace(day=1)  # Start at beginning of first month
    last = last_date.replace(day=1)  # Compare with beginning of last month
    
    while current <= last:
        months.append(current)
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            try:
                current = current.replace(month=current.month + 1)
            except ValueError:
                # Handle case where next month has fewer days
                current = current.replace(day=1, month=current.month + 1)
    
    return months

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
        
        # Convert present/absent to P/A in date columns
        date_columns = [col for col in df.columns if col not in ['student_name', 'student_id']]
        for col in date_columns:
            df[col] = df[col].replace({'present': 'P', 'absent': 'A'})
        
        # Calculate attendance statistics
        if len(dates) > 0:
            df['Total Present'] = df.iloc[:, 2:].apply(lambda x: (x == 'P').sum(), axis=1)
            df['Total Absent'] = df.iloc[:, 2:].apply(lambda x: (x == 'A').sum(), axis=1)
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
        months = get_month_options(first_date, last_date)
        
        if not months:
            st.warning("No months available in the date range")
            return
        
        # Display available months with attendance
        st.info(f"Available months: {', '.join(d.strftime('%B %Y') for d in months)}")
        
        selected_months = st.multiselect(
            "Select months to include in report",
            options=months,
            format_func=lambda x: x.strftime('%B %Y'),
            default=[months[-1]] if months else None,
            key="month_selector"
        )
        
        if selected_months:
            # Set date range for selected months
            start_date = min(selected_months).replace(day=1)
            end_date = max(selected_months).replace(
                day=calendar.monthrange(
                    max(selected_months).year,
                    max(selected_months).month
                )[1]
            )
            
            # Show selected date range
            st.write(f"Report will include dates from {start_date} to {end_date}")
    
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

                    # Add this after the dataframe display, inside the if statement where error is None
                    if report_type == "Monthly":
                        st.markdown("### 📈 Attendance Visualizations")
                        
                        # Create tabs for different visualizations
                        plot_tab1, plot_tab2, plot_tab3 = st.tabs([
                            "Daily Attendance Trends", 
                            "Student Performance", 
                            "Attendance Distribution"
                        ])
                        
                        with plot_tab1:
                            # Calculate daily attendance rates
                            date_columns = df.columns[2:-3]  # Exclude name, id, and summary columns
                            daily_attendance = pd.DataFrame({
                                'Date': date_columns,
                                'Present': [
                                    (df[date] == 'present').sum() for date in date_columns
                                ],
                                'Absent': [
                                    (df[date] == 'absent').sum() for date in date_columns
                                ]
                            })
                            daily_attendance['Date'] = pd.to_datetime(daily_attendance['Date'])
                            daily_attendance['Attendance Rate'] = (
                                daily_attendance['Present'] / 
                                (daily_attendance['Present'] + daily_attendance['Absent']) * 100
                            )
                            
                            # Create daily trend plot
                            fig1 = go.Figure()
                            fig1.add_trace(
                                go.Scatter(
                                    x=daily_attendance['Date'],
                                    y=daily_attendance['Attendance Rate'],
                                    mode='lines+markers',
                                    name='Attendance Rate',
                                    line=dict(color='#2E86C1', width=2),
                                    marker=dict(size=8)
                                )
                            )
                            fig1.update_layout(
                                title='Daily Attendance Rate Trend',
                                xaxis_title='Date',
                                yaxis_title='Attendance Rate (%)',
                                hovermode='x unified',
                                yaxis_range=[0, 100]
                            )
                            st.plotly_chart(fig1, use_container_width=True)
                        
                        with plot_tab2:
                            # Create student performance bar chart
                            student_performance = df.sort_values('Attendance Rate', ascending=True)
                            fig2 = go.Figure()
                            fig2.add_trace(
                                go.Bar(
                                    y=student_performance['student_name'],
                                    x=student_performance['Attendance Rate'],
                                    orientation='h',
                                    marker_color='#27AE60'
                                )
                            )
                            fig2.update_layout(
                                title='Student Attendance Rates',
                                xaxis_title='Attendance Rate (%)',
                                yaxis_title='Student Name',
                                xaxis_range=[0, 100],
                                height=max(400, len(df) * 30)  # Adjust height based on number of students
                            )
                            st.plotly_chart(fig2, use_container_width=True)
                        
                        with plot_tab3:
                            # Create attendance distribution chart
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Pie chart of overall attendance
                                total_present = df['Total Present'].sum()
                                total_absent = df['Total Absent'].sum()
                                
                                fig3 = go.Figure(data=[
                                    go.Pie(
                                        labels=['Present', 'Absent'],
                                        values=[total_present, total_absent],
                                        hole=.3,
                                        marker_colors=['#27AE60', '#E74C3C']
                                    )
                                ])
                                fig3.update_layout(title='Overall Attendance Distribution')
                                st.plotly_chart(fig3, use_container_width=True)
                            
                            with col2:
                                # Histogram of attendance rates
                                fig4 = go.Figure(data=[
                                    go.Histogram(
                                        x=df['Attendance Rate'],
                                        nbinsx=10,
                                        marker_color='#3498DB'
                                    )
                                ])
                                fig4.update_layout(
                                    title='Distribution of Attendance Rates',
                                    xaxis_title='Attendance Rate (%)',
                                    yaxis_title='Number of Students',
                                    xaxis_range=[0, 100]
                                )
                                st.plotly_chart(fig4, use_container_width=True)
                                
                        # Add insights section
                        st.markdown("### 📊 Key Insights")
                        
                        # Calculate insights

                        
                        best_students = df[df['Attendance Rate'] >= 95]['student_name'].tolist()
                        attention_needed = df[df['Attendance Rate'] < 80]['student_name'].tolist()
                        
                        col1, col2 = st.columns(2)

                        with col2:
                            st.info(f"""
                            **Perfect/Near Perfect Attendance:** {len(best_students)} students  
                            **Need Attention (<80%):** {len(attention_needed)} students
                            """)
                        
                        # Show detailed lists in expanders
                        if best_students:
                            with st.expander("View Students with Excellent Attendance (≥95%)"):
                                st.write("• " + "\n• ".join(best_students))
                        
                        if attention_needed:
                            with st.expander("View Students Needing Attention (<80%)"):
                                st.write("• " + "\n• ".join(attention_needed))
                    
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