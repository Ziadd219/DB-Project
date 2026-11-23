CREATE TABLE enrollments (
	enrollment_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	student_id INTEGER NOT NULL REFERENCES students(student_id),
	course_id INTEGER NOT NULL REFERENCES courses(course_id),
	enrollment_date DATE NOT NULL,
	status VARCHAR(20) NOT NULL
		CHECK (status IN ('Active', 'Completed', 'Dropped')),
	UNIQUE (student_id, course_id)
);