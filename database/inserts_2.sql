-- First: Insert users (no foreign key dependencies)
INSERT INTO user (id_user, name, lastname, email, password) VALUES
(1, 'Didier', 'Gamboa', 'didier.gamboa@upy.edu.mx', 'didi.er69'),
(2, 'Julian', 'Casablancas', 'julian.casa@upy.edu.mx', 'pass_2233');

-- Second: Insert students (no foreign key dependencies)
INSERT INTO student (id_student, student_name, student_lastname, student_status) VALUES
(2109061, 'Juan', 'Fernandez', 1),
(2109128, 'Juliana', 'Ramayo', 1),
(3847834, 'Paco', 'ElChato', 0);

-- Third: Insert classes (depends on users)
INSERT INTO classes (id_class, id_user, class_name) VALUES
(1, 1, 'Business Intelligence'),
(2, 1, 'English');

-- Finally: Insert assistance (depends on classes and students)
INSERT INTO assistance (assistance_class_id, assistance_date, id_student, assistance_status) VALUES
-- Business Intelligence attendance
(1, '2024-10-22', 2109061, 'P'),
(1, '2024-10-22', 2109128, 'J'),
-- English class attendance
(2, '2024-10-22', 3847834, 'A'),
-- Next day attendance
(1, '2024-10-23', 2109061, 'P'),
(1, '2024-10-23', 2109128, 'P'),
(2, '2024-10-23', 3847834, 'P');