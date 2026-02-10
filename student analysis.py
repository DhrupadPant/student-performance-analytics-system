#-----------------------------------------------------------imports and database connection-----------------------------------------------------------------
import mysql.connector
import statistics
from datetime import date

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bolt@2009",
    database="student_analysis"
)
cursor = conn.cursor()

#--------------------------------------------------------------------------sign up----------------------------------------------------------------------------------
def sign_up():
    print("\n--- SIGN UP ---")
    username = input("Enter username: ")

    cursor.execute(
        "select user_id from users where username=%s",
        (username,)
    )
    if cursor.fetchone():
        print("Username already exists")
        return

    password = input("Enter password: ")

    while True:
        confirm = input("Confirm password: ")
        if confirm == password:
            break
        print("Passwords do not match.")

    role = "teacher" if username.startswith("t_") else "student"

    cursor.execute(
        "insert into users (username, password, role) values (%s, %s, %s)",
        (username, password, role)
    )
    conn.commit()

    print("Signup successful.")


# ------------------------------------------------------------------------login--------------------------------------------------------------------------------------
def login():
    print("\n--- LOGIN ---")
    username = input("Username: ")
    password = input("Password: ")

    cursor.execute(
        "select user_id, role from users where username=%s and password=%s",
        (username, password)
    )
    result = cursor.fetchone()

    if not result:
        print("Invalid credentials")
        return None, None

    return result[0], result[1]

#-----------------------------------------------------------------student menu-----------------------------------------------------------------------------------
def student_menu(user_id):
    while True:
        print("\n--- STUDENT DASHBOARD ---")
        print("1. Enter Subjects and Difficulty.")
        print("2. Enter Marks")
        print("3. View Performance Report")
        print("4. Logout")

        choice = input("Choose to navigate(1/2/3/4): ")

        if choice == "1":
            enter_subjects_and_difficulty(user_id)
        elif choice == "2":
            enter_marks(user_id)
        elif choice == "3":
            view_performance(user_id)
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
#-----------------------------------------------------------------teacher menu-----------------------------------------------------------------------------------
def teacher_menu():
    while True:
        print("\n--- TEACHER DASHBOARD ---")
        print("1. View student performance")
        print("2. logout")

        choice = input("Choose option: ")

        if choice == "1":
            select_student_and_view()
        elif choice == "2":
            break
        else:
            print("Invalid choice")

def select_student_and_view():
    cursor.execute(
        "select user_id, username from users where role='student'"
    )
    students = cursor.fetchall()

    if not students:
        print("No students found")
        return

    print("\n--- STUDENT LIST ---")
    for uid, uname in students:
        print(uid, "-", uname)

    while True:
        try:
            chosen_id = int(input("Enter student user_id (Enter 0 to cancel): "))
            if chosen_id == 0:
                return
            break
        except:
            print("Enter valid user_id.")

    cursor.execute(
        "select 1 from users where user_id=%s and role='student'",
        (chosen_id,)
    )
    if not cursor.fetchone():
        print("Invalid student selection.")
        return

    view_performance(chosen_id)


#--------------------------------------------------------subject selection and difficulty input----------------------------------------------------------------
def enter_subjects_and_difficulty(user_id):
    print("\nEnter Subjects (type 'exit' to stop): ")

    while True:
        subject_name = input("Enter subject name: ").strip().title()

        if subject_name.lower() == "exit":
            break

        difficulty = int(input("Enter difficulty (1-5): "))

        cursor.execute(
            "select subject_id from subjects where subject_name=%s",
            (subject_name,)
        )
        result = cursor.fetchone()

        if result:
            subject_id = result[0]
        else:
            cursor.execute(
                "insert into subjects (subject_name) values (%s)",
                (subject_name,)
            )
            conn.commit()
            subject_id = cursor.lastrowid

        cursor.execute(
            "select * from student_subjects where user_id=%s and subject_id=%s",
            (user_id, subject_id)
        )
        if cursor.fetchone():
            print("Subject already added for you")
            continue

        cursor.execute(
            "insert into student_subjects (user_id, subject_id, difficulty) values (%s, %s, %s)",
            (user_id, subject_id, difficulty)
        )
        conn.commit()

        print(f"{subject_name} Added Successfully")
#---------------------------------------------------------------------------marks entry----------------------------------------------------------------------------
def enter_marks(user_id):
    cursor.execute(
        """select ss.subject_id, s.subject_name
           from student_subjects ss
           join subjects s on ss.subject_id=s.subject_id
           where ss.user_id=%s""",
        (user_id,)
    )
    subjects = cursor.fetchall()

    if not subjects:
        print("No subjects found.")
        return

    cursor.execute("select exam_id, exam_name from exams")
    exams = cursor.fetchall()

    for subject_id, subject_name in subjects:
        print(f"\nSubject: {subject_name}")

        for exam_id, exam_name in exams:
            choice = input(f"Did you give {exam_name}? (y/n): ").lower()
            if choice != "y":
                continue

            while True:
                try:
                    percentage = float(input("Enter percentage (0-100): "))
                    if 0 <= percentage <= 100:
                        break
                    print("Invalid range.")
                except:
                    print("Invalid input.")

            cursor.execute(
                "insert into scores (user_id, subject_id, exam_id, percentage) values (%s, %s, %s, %s)",
                (user_id, subject_id, exam_id, percentage)
            )
            conn.commit()

            print("Marks saved.")
            
#----------------------------------------------------performance analysis, trend and scale-------------------------------------------------------------------
def view_performance(user_id):
    cursor.execute(
        """select s.subject_id, s.subject_name, e.exam_name, sc.percentage
           from scores sc
           join subjects s on sc.subject_id=s.subject_id
           join exams e on sc.exam_id=e.exam_id
           where sc.user_id=%s
           order by s.subject_id, e.exam_id""",
        (user_id,)
    )
    data = cursor.fetchall()

    if not data:
        print("No data available.")
        return

    subject_data = {}

    for subject_id, subject_name, exam, pct in data:
        subject_data.setdefault(subject_name, []).append(pct)

    print("\n--- PERFORMANCE REPORT ---")

    for subject, values in subject_data.items():
        avg = sum(values) / len(values)
        scale = performance_scale(avg)
        trend = compute_trend(values)

        print(f"\nSubject: {subject}")
        print("Average:", round(avg, 2), "%")
        print("Level:", scale)
        print("Trend:", trend)
        if avg < 55:
            cursor.execute(
                "select 1 from weak_areas where user_id=%s and subject_id=%s",
                (user_id, subject_id)
            )
        if not cursor.fetchone():
            cursor.execute(
                "insert into weak_areas (user_id, subject_id, weak_area) values (%s, %s, %s)",
                (user_id, subject_id, f"low average {round(avg,2)}%")
            )
        suggest_remedial(avg)

#--------------------------------------------------------------------Advice after analyzing----------------------------------------------------------------------
def performance_scale(score):
    if score >= 85:
        return "Excellent."
    elif score >= 70:
        return "Good."
    elif score >= 55:
        return "Average."
    else:
        return "Needs improvement."


def compute_trend(values):
    if len(values) < 2:
        return "Insufficient data"
    if values[-1] > values[0]:
        return "Improving"
    elif values[-1] < values[0]:
        return "Declining"
    else:
        return "Stable"


def suggest_remedial(avg):
    print("--- Suggested Actions ---")
    if avg < 55:
        print("Book remedial classes.")
        print("Revise fundamentals weekly.")
    elif avg < 70:
        print("Increase question practice.")
    else:
        print("Maintain consistency.")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
while True:
    print("\n1. Sign up")
    print("2. Log in")
    print("3. Exit")

    choice = input("choose: ")

    if choice == "1":
        sign_up()
    elif choice == "2":
        user_id, role = login()
        if role == "student":
            student_menu(user_id)
        elif role == "teacher":
            teacher_menu()

    elif choice == "3":
        break
    else:
        print("Invalid choice.")
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
