-- Insert example users
INSERT INTO user (id_user, name, lastname, email, password) VALUES
(1, 'Didier', 'Gamboa', 'didier.gamboa@upy.edu.mx', 'didi123*'),
(2, 'Julian', 'Casablancas', 'julian.casa@upy.edu.mx', 'the_strokes'),
(3, 'Ajo', 'Amadeus Wolfgang', 'ajo.admin@upy.edu.mx', 'admin');

-- Insert example classes
INSERT INTO classes (id_class, id_user, class_name) VALUES
(1, 3, 'Business Intelligence'),
(2, 1, 'English'),
(3, 2, 'Data Science'),
(4, 3, 'Web Development');

-- Insert example students
INSERT INTO student (id_student, student_name, student_lastname, student_status) VALUES
(2109061, 'Juan', 'Fernandez', 1),
(2109128, 'Juliana', 'Ramayo', 1),
(2109058, 'Carlo', 'Ek', 0),
(2109456, 'Ana', 'Martinez', 1),
(2109789, 'Carlos', 'Lopez', 1);

-- Insert example class_list entries
INSERT INTO class_list (id_class, id_student) VALUES
-- Business Intelligence students
(1, 2109061),
(1, 2109128),
-- English class students
(2, 2109058),
(2, 2109456),
-- Data Science students
(3, 2109061),
(3, 2109789);

-- Insert example assistance records
INSERT INTO assistance (assistance_class_id, assistance_date, id_student, assistance_status) VALUES
-- Business Intelligence attendance
(1, '2024-10-22', 2109061, 'P'),
(1, '2024-10-22', 2109128, 'A'),
-- English class attendance
(2, '2024-10-22', 2109058, 'P'),
(2, '2024-10-22', 2109456, 'J'),
-- Next day attendance
(1, '2024-10-23', 2109061, 'P'),
(1, '2024-10-23', 2109128, 'P'),
-- Data Science attendance
(3, '2024-10-22', 2109061, 'P'),
(3, '2024-10-22', 2109789, 'A');