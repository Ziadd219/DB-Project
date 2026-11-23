from flask import Flask, render_template, request, redirect
import os
import psycopg2

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host = "localhost",
        database = "student_course_db",
        user = "postgres",
        password = os.environ["DB_PASSWORD"]
    )



@app.route('/')
def home():
    return render_template("index.html")


@app.route('/students')
def students():
    search = request.args.get("search", "").strip()
    conn = get_connection()
    try:
        cursor = conn.cursor()

        if search:
            cursor.execute("""SELECT student_id, first_name, last_name, email, department FROM students 
                              WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s OR department ILIKE %s
                              ORDER BY student_id;""",
                           (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("""SELECT student_id, first_name, last_name, email, department FROM students ORDER BY student_id;""")
        student_data = cursor.fetchall()
        cursor.close()

        return render_template("students.html", students=student_data, search=search)
    finally:
        conn.close()


@app.route("/add_student", methods=["POST"])
def add_student():
    first_name = request.form["first_name"].strip()
    last_name = request.form["last_name"].strip()
    email = request.form["email"].strip()
    department = request.form["department"].strip()

    if not all([first_name, last_name, email, department]):
        return "All fields are required.", 400
    if len(first_name) > 50 or len(last_name) > 50 or len(email) > 100 or len(department) > 50:
        return "Input exceeds maximum length.", 400

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO students (first_name, last_name, email, department) VALUES (%s, %s, %s, %s)""",
                       (first_name, last_name, email, department))
        conn.commit()
        cursor.close()
    except psycopg2.IntegrityError:
        conn.rollback()
        return "Student with this email already exists.", 400
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect("/students")


@app.route("/edit_student/<int:student_id>")
def edit_student(student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT student_id, first_name, last_name, email, department FROM students WHERE student_id = %s""",
                       (student_id,))
        student = cursor.fetchone()
        cursor.close()

        if student is None:
            return "Student not found.", 404

        return render_template("edit_student.html", student=student)
    finally:
        conn.close()


@app.route("/update_student/<int:student_id>", methods=["POST"])
def update_student(student_id):
    first_name = request.form["first_name"].strip()
    last_name = request.form["last_name"].strip()
    email = request.form["email"].strip()
    department = request.form["department"].strip()

    if not all([first_name, last_name, email, department]):
        return "All fields are required.", 400
    if len(first_name) > 50 or len(last_name) > 50 or len(email) > 100 or len(department) > 50:
        return "Input exceeds maximum length.", 400

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""UPDATE students SET first_name = %s, last_name = %s, email = %s, department = %s WHERE student_id = %s""",
                       (first_name, last_name, email, department, student_id))
        if cursor.rowcount == 0:
            conn.rollback()
            return "Student not found.", 404
        
        conn.commit()
        cursor.close()
    except psycopg2.IntegrityError:
        conn.rollback()
        return "Student with this email already exists.", 400
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect("/students")


@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT COUNT(*) FROM enrollments WHERE student_id = %s""", (student_id,))
        enrollment_count = cursor.fetchone()[0]

        if enrollment_count > 0:
            conn.rollback()
            return "Cannot delete student with existing enrollments.", 400

        cursor.execute("""DELETE FROM students WHERE student_id = %s""", (student_id,))
        if cursor.rowcount == 0:
            conn.rollback()
            return "Student not found.", 404
        
        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect("/students")


@app.route('/courses')
def courses():
    search = request.args.get("search", "").strip()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if search:
            cursor.execute("""SELECT course_id, course_code, course_name, credits, department FROM courses
                                WHERE course_code ILIKE %s OR course_name ILIKE %s OR department ILIKE %s
                                ORDER BY course_id;""", (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("""SELECT course_id, course_code, course_name, credits, department FROM courses ORDER BY course_id;""")
        course_data = cursor.fetchall()
        cursor.close()

        return render_template("courses.html", courses=course_data, search=search)
    finally:
        conn.close()

@app.route("/add_course", methods=["POST"])
def add_course():
    course_code = request.form["course_code"].strip()
    course_name = request.form["course_name"].strip()
    credits_text = request.form["credits"].strip()
    department = request.form["department"].strip()

    if not all([course_code, course_name, credits_text, department]):
        return "All fields are required.", 400
    if len(course_code) > 20 or len(course_name) > 100 or len(department) > 50:
        return "Input exceeds maximum length.", 400

    try:
        credits = int(credits_text)
    except ValueError:
        return "Credits must be an integer.", 400
    if credits <= 0:
        return "Credits must be a positive integer.", 400
    
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO courses (course_code, course_name, credits, department) VALUES (%s, %s, %s, %s)""",
                       (course_code, course_name, credits, department))
        conn.commit()
        cursor.close()
    except psycopg2.IntegrityError:
        conn.rollback()
        return "Course with this code already exists.", 400
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect("/courses")

@app.route("/edit_course/<int:course_id>")
def edit_course(course_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT course_id, course_code, course_name, credits, department FROM courses WHERE course_id = %s""",
                       (course_id,))
        course = cursor.fetchone()
        cursor.close()

        if course is None:
            return "Course not found.", 404

        return render_template("edit_course.html", course=course)
    finally:
        conn.close()

@app.route("/update_course/<int:course_id>", methods=["POST"])
def update_course(course_id):
    course_code = request.form["course_code"].strip()
    course_name = request.form["course_name"].strip()
    credits_text = request.form["credits"].strip()
    department = request.form["department"].strip()

    if not all([course_code, course_name, credits_text, department]):
        return "All fields are required.", 400
    if len(course_code) > 20 or len(course_name) > 100 or len(department) > 50:
        return "Input exceeds maximum length.", 400
    try:
        credits = int(credits_text)
    except ValueError:
        return "Credits must be an integer.", 400
    if credits <= 0:
        return "Credits must be a positive integer.", 400
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""UPDATE courses SET course_code = %s, course_name = %s, credits = %s, department = %s WHERE course_id = %s""",
                       (course_code, course_name, credits, department, course_id))
        if cursor.rowcount == 0:
            conn.rollback()
            return "Course not found.", 404
        
        conn.commit()
        cursor.close()

    except psycopg2.IntegrityError:
        conn.rollback()
        return "Course with this code already exists.", 400
    
    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return redirect("/courses")


@app.route("/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT COUNT(*) FROM enrollments WHERE course_id = %s""", (course_id,))
        enrollment_count = cursor.fetchone()[0]

        if enrollment_count > 0:
            conn.rollback()
            return "Cannot delete course with existing enrollments.", 400

        cursor.execute("""DELETE FROM courses WHERE course_id = %s""", (course_id,))
        if cursor.rowcount == 0:
            conn.rollback()
            return "Course not found.", 404
        
        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect("/courses")


@app.route('/enrollments')
def enrollments():
    search = request.args.get("search", "").strip()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        if search:
            cursor.execute("""SELECT e.enrollment_id, s.first_name, s.last_name,
                                     c.course_code, c.course_name, e.enrollment_date, e.status
                              FROM enrollments e
                              JOIN students s ON e.student_id = s.student_id
                              JOIN courses c ON e.course_id = c.course_id
                              WHERE s.first_name ILIKE %s OR s.last_name ILIKE %s OR c.course_code ILIKE %s OR c.course_name ILIKE %s
                              ORDER BY e.enrollment_id;""",
                           (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("""SELECT e.enrollment_id, s.first_name, s.last_name,
                                     c.course_code, c.course_name, e.enrollment_date, e.status
                                     FROM enrollments e
                                     JOIN students s ON e.student_id = s.student_id
                                     JOIN courses c ON e.course_id = c.course_id
                                     ORDER BY e.enrollment_id;""")
        enrollment_data = cursor.fetchall()

        cursor.execute("""SELECT student_id, first_name, last_name FROM students ORDER BY student_id;""")
        student_data = cursor.fetchall()
        cursor.execute("""SELECT course_id, course_code, course_name FROM courses ORDER BY course_id;""")
        course_data = cursor.fetchall()
        cursor.close()

        return render_template("enrollments.html", enrollments=enrollment_data, students=student_data, courses=course_data, search=search)
    finally:
        conn.close()

@app.route("/add_enrollment", methods=["POST"])
def add_enrollment():
    student_id = request.form["student_id"]
    course_id = request.form["course_id"]
    status = request.form["status"].strip()

    if not student_id or not course_id:
        return "Please select a student and a course.", 400
    try:
        student_id = int(student_id)
        course_id = int(course_id)
    except ValueError:
        return "Invalid student or course ID.", 400
    if student_id <= 0 or course_id <= 0:
        return "Student and Course IDs must be positive integers.", 400

    if status not in ["Active", "Completed", "Dropped"]:
        return "Invalid status.", 400

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (%s, %s, CURRENT_DATE, %s)""",
                       (student_id, course_id, status))
        conn.commit()
        cursor.close()
    except psycopg2.IntegrityError:
        conn.rollback()
        return "This student is already enrolled in this course, or invalid enrollment.", 400
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect("/enrollments")

@app.route("/edit_enrollment/<int:enrollment_id>")
def edit_enrollment(enrollment_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT e.enrollment_id, s.first_name, s.last_name, c.course_code, e.status
                          FROM enrollments e
                          JOIN students s ON e.student_id = s.student_id
                          JOIN courses c ON e.course_id = c.course_id
                          WHERE e.enrollment_id = %s""", (enrollment_id,))
        enrollment = cursor.fetchone()
        cursor.close()

        if enrollment is None:
            return "Enrollment not found.", 404
        
        return render_template("edit_enrollment.html", enrollment=enrollment)
    finally:
        conn.close()

@app.route("/update_enrollment/<int:enrollment_id>", methods=["POST"])
def update_enrollment(enrollment_id):
    status = request.form["status"].strip()

    if status not in ["Active", "Completed", "Dropped"]:
        return "Invalid status.", 400

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""UPDATE enrollments SET status = %s WHERE enrollment_id = %s""",
                       (status, enrollment_id))
        if cursor.rowcount == 0:
            conn.rollback()
            return "Enrollment not found.", 404
        
        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect("/enrollments") 


@app.route("/delete_enrollment/<int:enrollment_id>", methods=["POST"])
def delete_enrollment(enrollment_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM enrollments WHERE enrollment_id = %s""", (enrollment_id,))
        if cursor.rowcount == 0:
            conn.rollback()
            return "Enrollment not found.", 404
        
        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect("/enrollments")


if __name__ == '__main__':
    app.run(debug=True)