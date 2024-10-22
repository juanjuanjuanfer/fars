-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS fars_db;
USE fars_db;

-- Users table
CREATE TABLE IF NOT EXISTS user (
    id_user INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
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
    student_status TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Assistance table
CREATE TABLE IF NOT EXISTS assistance (
    assistance_id INT PRIMARY KEY AUTO_INCREMENT,
    assistance_class_id INT NOT NULL,
    assistance_date DATE NOT NULL,
    id_student INT NOT NULL,
    assistance_status CHAR(1) NOT NULL,  -- P: Present, A: Absent, J: Justified
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assistance_class_id) REFERENCES classes(id_class) ON DELETE RESTRICT,
    FOREIGN KEY (id_student) REFERENCES student(id_student) ON DELETE RESTRICT,
    CONSTRAINT valid_assistance_status CHECK (assistance_status IN ('P', 'A', 'J')),
    UNIQUE KEY unique_assistance (assistance_class_id, assistance_date, id_student)
);

-- Add an index to improve queries for finding all students in a class
CREATE INDEX idx_class_student ON assistance (assistance_class_id, id_student);