INSERT INTO students (first_name, last_name, email, department) 
VALUES
('Ziad', 'Samer', 'ziad.samer@uni.com', 'Computer Engineering'),
('Ahmed', 'Hassan', 'ahmed.has@uni.com', 'Economics'),
('Sara', 'Mohamed', 'sara.moh@uni.com', 'Software Engineering');

SELECT * FROM students;

INSERT INTO courses (course_code, course_name, credits, department)
VALUES
('COM301','Computer Programming I', 4, 'Computer Engineering'),
('MED212', 'Dynamics', 5, 'Mechanical Engineering'),
('COM304', 'Data Structure & Algorithms', 5, 'Software Engineering');

SELECT * FROM courses;


INSERT INTO enrollments (student_id, course_id, enrollment_date, status)
VALUES
((SELECT student_id FROM students where email = 'ziad.samer@uni.com'),
 (SELECT course_id FROM courses WHERE course_code = 'COM301'),
 CURRENT_DATE, 'Active'),
((SELECT student_id FROM students WHERE email = 'ahmed.has@uni.com'),
 (SELECT course_id FROM courses WHERE course_code = 'MED212'),
 CURRENT_DATE, 'Active'),
((SELECT student_id FROM students WHERE email = 'sara.moh@uni.com'),
 (SELECT course_id FROM courses WHERE course_code = 'COM304'),
 CURRENT_DATE, 'Active');

SELECT
	students.first_name,
	students.last_name,
	courses.course_name,
	enrollments.status
FROM enrollments 
JOIN students ON enrollments.student_id = students.student_id
JOIN courses ON enrollments.course_id = courses.course_id;

