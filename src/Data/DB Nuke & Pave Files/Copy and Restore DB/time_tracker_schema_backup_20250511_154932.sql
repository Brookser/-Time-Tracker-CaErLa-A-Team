-- MariaDB Schema Backup for database: time_tracker
-- Generated on: 2025-05-11 15:49:32
-- This script contains all necessary information to recreate the database structure

-- Database recreation statement
DROP DATABASE IF EXISTS `time_tracker`;
CREATE DATABASE `time_tracker` CHARACTER SET utf8mb4 COLLATION utf8mb4_general_ci;

USE `time_tracker`;

-- Important server variables
-- character_set_server = utf8mb4
-- collation_server = utf8mb4_general_ci
-- innodb_buffer_pool_size = 134217728
-- innodb_file_per_table = ON
-- innodb_flush_log_at_trx_commit = 1
-- innodb_log_file_size = 100663296
-- max_allowed_packet = 16777216
-- max_connections = 151
-- sql_mode = STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION
-- sync_binlog = 0

-- Table structure

-- Structure for table `department`
DROP TABLE IF EXISTS `department`;
CREATE TABLE `department` (
  `DPTID` varchar(20) NOT NULL,
  `DPT_NAME` varchar(100) NOT NULL,
  `MANAGERID` varchar(20) DEFAULT NULL,
  `DPT_ACTIVE` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`DPTID`),
  KEY `MANAGERID` (`MANAGERID`),
  CONSTRAINT `fk_dept_manager` FOREIGN KEY (`MANAGERID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Structure for table `employee_projects`
DROP TABLE IF EXISTS `employee_projects`;
CREATE TABLE `employee_projects` (
  `EMPID` varchar(20) NOT NULL,
  `PROJECT_ID` varchar(20) NOT NULL,
  PRIMARY KEY (`EMPID`,`PROJECT_ID`),
  KEY `EMPID` (`EMPID`),
  KEY `PROJECT_ID` (`PROJECT_ID`),
  CONSTRAINT `fk_emp_proj_employee` FOREIGN KEY (`EMPID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_emp_proj_project` FOREIGN KEY (`PROJECT_ID`) REFERENCES `projects` (`PROJECTID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Structure for table `employee_table`
DROP TABLE IF EXISTS `employee_table`;
CREATE TABLE `employee_table` (
  `EMPID` varchar(20) NOT NULL,
  `FIRST_NAME` varchar(50) NOT NULL,
  `LAST_NAME` varchar(50) NOT NULL,
  `DPTID` varchar(20) NOT NULL,
  `EMAIL_ADDRESS` varchar(100) NOT NULL,
  `MGR_EMPID` varchar(20) DEFAULT NULL,
  `EMP_ACTIVE` tinyint(1) DEFAULT 1,
  `EMP_ROLE` varchar(20) NOT NULL,
  PRIMARY KEY (`EMPID`),
  UNIQUE KEY `EMAIL_ADDRESS` (`EMAIL_ADDRESS`),
  KEY `DPTID` (`DPTID`),
  KEY `MGR_EMPID` (`MGR_EMPID`),
  CONSTRAINT `fk_employee_dept` FOREIGN KEY (`DPTID`) REFERENCES `department` (`DPTID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_employee_manager` FOREIGN KEY (`MGR_EMPID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Structure for table `login_table`
DROP TABLE IF EXISTS `login_table`;
CREATE TABLE `login_table` (
  `LOGINID` varchar(50) NOT NULL,
  `EMPID` varchar(20) NOT NULL,
  `PASSWORD` varchar(255) NOT NULL,
  `LAST_RESET` datetime DEFAULT NULL,
  `FORCE_RESET` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`LOGINID`),
  KEY `EMPID` (`EMPID`),
  CONSTRAINT `fk_login_employee` FOREIGN KEY (`EMPID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Structure for table `projects`
DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects` (
  `PROJECTID` varchar(20) NOT NULL,
  `PROJECT_NAME` varchar(100) NOT NULL,
  `CREATED_BY` varchar(20) NOT NULL,
  `DATE_CREATED` datetime NOT NULL DEFAULT current_timestamp(),
  `PRIOR_PROJECTID` varchar(20) DEFAULT NULL,
  `PROJECT_ACTIVE` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`PROJECTID`),
  KEY `CREATED_BY` (`CREATED_BY`),
  KEY `PRIOR_PROJECTID` (`PRIOR_PROJECTID`),
  CONSTRAINT `fk_project_creator` FOREIGN KEY (`CREATED_BY`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_project_parent` FOREIGN KEY (`PRIOR_PROJECTID`) REFERENCES `projects` (`PROJECTID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Structure for table `time`
DROP TABLE IF EXISTS `time`;
CREATE TABLE `time` (
  `TIMEID` varchar(20) NOT NULL,
  `EMPID` varchar(20) NOT NULL,
  `START_TIME` datetime NOT NULL,
  `STOP_TIME` datetime DEFAULT NULL,
  `NOTES` text DEFAULT NULL,
  `MANUAL_ENTRY` tinyint(1) DEFAULT 0,
  `PROJECTID` varchar(30) NOT NULL DEFAULT 'TEMP_PROJECT',
  `TOTAL_MINUTES` int(11) GENERATED ALWAYS AS (timestampdiff(MINUTE,`START_TIME`,`STOP_TIME`)) STORED,
  PRIMARY KEY (`TIMEID`),
  KEY `EMPID` (`EMPID`),
  KEY `START_TIME` (`START_TIME`),
  KEY `STOP_TIME` (`STOP_TIME`),
  KEY `fk_time_new_project` (`PROJECTID`),
  CONSTRAINT `fk_time_employee` FOREIGN KEY (`EMPID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_time_project` FOREIGN KEY (`PROJECTID`) REFERENCES `projects` (`PROJECTID`),
  CONSTRAINT `chk_time_valid` CHECK (`STOP_TIME` > `START_TIME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table data statistics
-- Table `department`: ~12 rows, Data: 0.02MB, Indexes: 0.02MB
-- Table `employee_projects`: ~98 rows, Data: 0.02MB, Indexes: 0.03MB
-- Table `employee_table`: ~40 rows, Data: 0.02MB, Indexes: 0.05MB
-- Table `login_table`: ~40 rows, Data: 0.02MB, Indexes: 0.02MB
-- Table `projects`: ~84 rows, Data: 0.02MB, Indexes: 0.03MB
-- Table `time`: ~249 rows, Data: 0.05MB, Indexes: 0.06MB

-- Triggers

DELIMITER $$

-- Structure for trigger `before_insert_department`
DROP TRIGGER IF EXISTS `before_insert_department`$$
CREATE DEFINER=`ebrooks23`@`%` TRIGGER before_insert_department
                BEFORE INSERT ON department
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.DPTID IS NULL OR NEW.DPTID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(DPTID, 2) + 0), 1000) + 1
                                    FROM department);
                        SET NEW.DPTID = CONCAT('D', next_id);
                    END IF;
                END$$

-- Structure for trigger `before_insert_employee`
DROP TRIGGER IF EXISTS `before_insert_employee`$$
CREATE DEFINER=`ebrooks23`@`%` TRIGGER before_insert_employee
                BEFORE INSERT ON employee_table
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.EMPID IS NULL OR NEW.EMPID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(EMPID, 2) + 0), 1000) + 1
                                    FROM employee_table);
                        SET NEW.EMPID = CONCAT('E', next_id);
                    END IF;
                END$$

-- Structure for trigger `before_insert_project`
DROP TRIGGER IF EXISTS `before_insert_project`$$
CREATE DEFINER=`ebrooks23`@`%` TRIGGER before_insert_project
                BEFORE INSERT ON projects
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.PROJECTID IS NULL OR NEW.PROJECTID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(PROJECTID, 2) + 0), 10000) + 1
                                    FROM projects);
                        SET NEW.PROJECTID = CONCAT('P', next_id);
                    END IF;
                END$$

DELIMITER ;

-- User privileges (current connection user only)
-- GRANT USAGE ON *.* TO `ebrooks23`@`%` IDENTIFIED BY PASSWORD '*D37C49F9CBEFBF8B6F4B165AC703AA271E079004'
-- GRANT ALL PRIVILEGES ON `time_tracker`.* TO `ebrooks23`@`%`

-- Foreign key information
-- FK: department.MANAGERID -> employee_table.EMPID (fk_dept_manager)
-- FK: employee_projects.EMPID -> employee_table.EMPID (fk_emp_proj_employee)
-- FK: employee_projects.PROJECT_ID -> projects.PROJECTID (fk_emp_proj_project)
-- FK: employee_table.DPTID -> department.DPTID (fk_employee_dept)
-- FK: employee_table.MGR_EMPID -> employee_table.EMPID (fk_employee_manager)
-- FK: login_table.EMPID -> employee_table.EMPID (fk_login_employee)
-- FK: projects.CREATED_BY -> employee_table.EMPID (fk_project_creator)
-- FK: projects.PRIOR_PROJECTID -> projects.PROJECTID (fk_project_parent)
-- FK: time.EMPID -> employee_table.EMPID (fk_time_employee)
-- FK: time.PROJECTID -> projects.PROJECTID (fk_time_project)

-- Index information
-- INDEX: department.MANAGERID (MANAGERID)
-- INDEX: employee_projects.EMPID (EMPID)
-- INDEX: employee_projects.PROJECT_ID (PROJECT_ID)
-- INDEX: employee_table.DPTID (DPTID)
-- UNIQUE: employee_table.EMAIL_ADDRESS (EMAIL_ADDRESS)
-- INDEX: employee_table.MGR_EMPID (MGR_EMPID)
-- INDEX: login_table.EMPID (EMPID)
-- INDEX: projects.CREATED_BY (CREATED_BY)
-- INDEX: projects.PRIOR_PROJECTID (PRIOR_PROJECTID)
-- INDEX: time.EMPID (EMPID)
-- INDEX: time.fk_time_new_project (PROJECTID)
-- INDEX: time.START_TIME (START_TIME)
-- INDEX: time.STOP_TIME (STOP_TIME)

