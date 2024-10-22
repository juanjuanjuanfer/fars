-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS fars_db;
USE fars_db;

-- Users table
CREATE TABLE IF NOT EXISTS user (
    id_user INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- Changed to accommodate hashed passwords
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Classes table
CREATE TABLE IF NOT EXISTS classes (
    id_class INT PRIMARY KEY AUTO_INCREMENT,
    id_user INT NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES user(id_user) ON DELETE RESTRICT
);

-- Student table
CREATE TABLE IF NOT EXISTS student (
    id_student INT PRIMARY KEY,
    student_name VARCHAR(50) NOT NULL,
    student_lastname VARCHAR(50) NOT NULL,
    student_status TINYINT(1) DEFAULT 1,  -- Using TINYINT for boolean (0/1)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Class list table (junction table for many-to-many relationship)
CREATE TABLE IF NOT EXISTS class_list (
    id_list INT PRIMARY KEY AUTO_INCREMENT,
    id_class INT NOT NULL,
    id_student INT NOT NULL,  -- Changed from array to individual relationships
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_class) REFERENCES classes(id_class) ON DELETE CASCADE,
    FOREIGN KEY (id_student) REFERENCES student(id_student) ON DELETE CASCADE,
    UNIQUE KEY unique_class_student (id_class, id_student)  -- Prevent duplicate enrollments
);

-- Assistance table
CREATE TABLE IF NOT EXISTS assistance (
    assistance_id INT PRIMARY KEY AUTO_INCREMENT,  -- Added primary key
    assistance_class_id INT NOT NULL,
    assistance_date DATE NOT NULL,
    id_student INT NOT NULL,
    assistance_status CHAR(1) NOT NULL,  -- P: Present, A: Absent, J: Justified
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assistance_class_id) REFERENCES classes(id_class) ON DELETE RESTRICT,
    FOREIGN KEY (id_student) REFERENCES student(id_student) ON DELETE RESTRICT,
    CONSTRAINT valid_assistance_status CHECK (assistance_status IN ('P', 'A', 'J')),
    UNIQUE KEY unique_assistance (assistance_class_id, assistance_date, id_student)  -- Prevent duplicate assistance records
);