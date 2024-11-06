import streamlit as st
import pandas as pd
import os
import numpy as np
import pickle
import subprocess  
from datetime import datetime
import time
import csv
from twilio.rest import Client  

account_sid = 'add your ssid'                                         ## you should make the changes here               
auth_token = 'add your token which will get in the twilio'            ## you should make the changes here
twilio_number = 'add the number which will be given by twillo'        ## you should make the changes here


def send_sms(to_number, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=twilio_number,
        to=to_number
    )
    return message.sid


def get_absent_students(total_students, present_students):
    return [student for student in total_students if student not in present_students]


def load_attendance():
    attendance_files = [f for f in os.listdir("Attendance") if f.endswith('.csv')]
    all_data = []

    for file in attendance_files:
        df = pd.read_csv(f"Attendance/{file}")
        df['Date'] = file.split('_')[1].replace('.csv', '')
        all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return None


def load_faces_data():
    if os.path.exists('data/faces_data.pkl') and os.path.exists('data/names.pkl'):
        with open('data/faces_data.pkl', 'rb') as f:
            faces_data = pickle.load(f)
        with open('data/names.pkl', 'rb') as f:
            names = pickle.load(f)
        return faces_data, names
    return None, None


def remove_face(name):
    faces_data, names = load_faces_data()
    if faces_data is not None and names is not None:
        if name in names:
            indices = [i for i, n in enumerate(names) if n == name]
            faces_data = np.delete(faces_data, indices, axis=0)
            names = [n for i, n in enumerate(names) if n != name]

            with open('data/faces_data.pkl', 'wb') as f:
                pickle.dump(faces_data, f)
            with open('data/names.pkl', 'wb') as f:
                pickle.dump(names, f)

            st.success(f"Removed all entries for {name}")
        else:
            st.error(f"Name {name} not found in data.")
    else:
        st.error("Faces data not found.")

def mark_present(name):
    ts = time.time()
    timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    date = datetime.fromtimestamp(ts).strftime("%d-%m-%y")

    attendance = [name, timestamp, "Button"]

    if os.path.exists(f"Attendance/Attendance_{date}.csv"):
        with open(f"Attendance/Attendance_{date}.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow(attendance)
    else:
        with open(f"Attendance/Attendance_{date}.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow(['NAME', 'TIME', 'Method']) 
            writer.writerow(attendance)

    df_all_attendance = load_attendance()
    if df_all_attendance is not None:
        df_all_attendance.loc[df_all_attendance['NAME'] == name, 'Method'] = 'Button'
        df_all_attendance.to_csv(f"Attendance/Attendance_{date}.csv", index=False)

    st.success(f"Marked {name} as present via Button")

df_all_attendance = load_attendance()

if df_all_attendance is None:
    st.error("No attendance data found.")
else:
    st.title("Attendance Dashboard")

    st.sidebar.header("Total Classes")
    total_classes = st.sidebar.number_input("Enter Total Number of Classes", min_value=1, value=10)

    st.subheader(f"Attendance Records")

    numeric_columns = df_all_attendance.select_dtypes(include=['number']).columns
    if 'Method' not in df_all_attendance.columns:
        df_all_attendance['Method'] = np.nan  


    st.dataframe(df_all_attendance[['NAME', 'TIME', 'Date', 'Method']])

    
    student_data = {
        "shashi": {"parent_phone": "+91add the number you want to send the message"},   ## you should make the changes here
        "keerthan": {"parent_phone": "+91add the number you want to send the message"}, ## you should make the changes here##
        "amruth": {"parent_phone": "+91add the number you want to send the message"},## you should make the changes here
        "prajwal": {"parent_phone": "+91add the number you want to send the message"},## you should make the changes here
        "sutheej": {"parent_phone": "+91add the number you want to send the message"},## you should make the changes here
        "kiran": {"parent_phone": "+91add the number you want to send the message"},## you should make the changes here
        "shreevanth": {"parent_phone": "+91add the number you want to send the message"},## you should make the changes here
    }

    total_students = list(student_data.keys())

    present_students = df_all_attendance[df_all_attendance['Date'] == datetime.now().strftime("%d-%m-%y")]["NAME"].unique().tolist()

    absent_students = get_absent_students(total_students, present_students)

    st.subheader("Individual Attendance Percentage")

    attendance_summary = []
    for name in total_students:
        attendance_count = df_all_attendance[df_all_attendance["NAME"] == name].shape[0]
        attendance_percentage = (attendance_count / total_classes) * 100
        attendance_summary.append({"Name": name, "Attendance Count": attendance_count, "Attendance Percentage": attendance_percentage})

    attendance_df = pd.DataFrame(attendance_summary)

    st.table(attendance_df[['Name', 'Attendance Count', 'Attendance Percentage']])

    if st.button("Download Attendance Summary"):
        attendance_df.to_csv("attendance_summary.csv", index=False)
        st.success("Attendance summary saved as 'attendance_summary.csv'.")

    st.sidebar.header("Admin Actions")
    remove_name = st.sidebar.text_input("Enter name to remove")
    if st.sidebar.button("Remove Face"):
        if remove_name:
            remove_face(remove_name)
        else:
            st.sidebar.error("Please enter a name.")

    st.subheader("Absent Students")

    for student in absent_students:
        col1, col2 = st.columns([2, 1])
        col1.write(student)
        if col2.button(f"Mark {student} Present"):
            mark_present(student)

    if st.sidebar.button("Send SMS to Parents"):
        if absent_students:
            for student in absent_students:
                parent_phone = student_data[student]["parent_phone"]
                sms_message = f"Dear Parent, your child {student} was absent today."
                try:
                    sms_sid = send_sms(parent_phone, sms_message)
                    st.success(f"SMS sent to parent of {student} (SID: {sms_sid})")
                except Exception as e:
                    st.error(f"Failed to send SMS to parent of {student}: {e}")
        else:
            st.info("No absent students to notify.")

    st.sidebar.header("Take Attendance")
    if st.sidebar.button("Take Attendance (Face Recognition)"):
        try:
            subprocess.Popen(['python', 'test.py'])
            st.sidebar.success("Attendance is being taken via face recognition...")
        except Exception as e:
            st.sidebar.error(f"Failed to take attendance: {e}")
