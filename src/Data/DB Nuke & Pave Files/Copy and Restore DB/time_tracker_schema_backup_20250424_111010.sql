-- MariaDB Schema Backup for database: time_tracker
-- Generated on: 2025-04-24 11:10:10
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
  KEY `fk_dept_manager` (`MANAGERID`),
  CONSTRAINT `fk_dept_manager` FOREIGN KEY (`MANAGERID`) REFERENCES `employee_table` (`EMPID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Structure for table `employee_table`
DROP TABLE IF EXISTS `employee_table`;
CREATE TABLE `employee_table` (
  `EMPID` varchar(20) NOT NULL,
  `FIRST_NAME` varchar(50) NOT NULL,
  `LAST_NAME` varchar(50) NOT NULL,
  `DPTID` varchar(20) NOT NULL,
  `EMAIL_ADDRESS` varchar(100) DEFAULT NULL,
  `MGR_EMPID` varchar(20) DEFAULT NULL,
  `EMP_ACTIVE` tinyint(1) DEFAULT 1,
  `EMP_ROLE` varchar(50) NOT NULL DEFAULT 'individual',
  PRIMARY KEY (`EMPID`),
  UNIQUE KEY `EMAIL_ADDRESS` (`EMAIL_ADDRESS`),
  KEY `fk_emp_manager` (`MGR_EMPID`),
  KEY `idx_employee_dept` (`DPTID`),
  CONSTRAINT `fk_emp_dept` FOREIGN KEY (`DPTID`) REFERENCES `department` (`DPTID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_emp_manager` FOREIGN KEY (`MGR_EMPID`) REFERENCES `employee_table` (`EMPID`) ON DELETE SET NULL ON UPDATE CASCADE
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
  KEY `fk_login_emp` (`EMPID`),
  CONSTRAINT `fk_login_emp` FOREIGN KEY (`EMPID`) REFERENCES `employee_table` (`EMPID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Structure for table `projects`
DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects` (
  `PROJECTID` varchar(30) NOT NULL,
  `PROJECT_NAME` varchar(100) NOT NULL,
  `CREATED_BY` varchar(20) NOT NULL,
  `DATE_CREATED` datetime NOT NULL,
  `PRIOR_PROJECTID` varchar(30) DEFAULT NULL,
  `PROJECT_ACTIVE` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`PROJECTID`),
  KEY `fk_project_prior` (`PRIOR_PROJECTID`),
  KEY `idx_project_creator` (`CREATED_BY`),
  CONSTRAINT `fk_project_creator` FOREIGN KEY (`CREATED_BY`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_project_prior` FOREIGN KEY (`PRIOR_PROJECTID`) REFERENCES `projects` (`PROJECTID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Structure for table `time`
DROP TABLE IF EXISTS `time`;
CREATE TABLE `time` (
  `TIMEID` int(11) NOT NULL AUTO_INCREMENT,
  `EMPID` varchar(20) NOT NULL,
  `PROJECTID` varchar(30) NOT NULL,
  `START_TIME` datetime NOT NULL,
  `STOP_TIME` datetime DEFAULT NULL,
  `NOTES` text DEFAULT NULL,
  `MANUAL_ENTRY` tinyint(1) DEFAULT 0,
  `TOTAL_MINUTES` int(11) DEFAULT NULL,
  PRIMARY KEY (`TIMEID`),
  KEY `fk_time_project` (`PROJECTID`),
  KEY `idx_time_emp_project` (`EMPID`,`PROJECTID`),
  CONSTRAINT `fk_time_emp` FOREIGN KEY (`EMPID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_time_project` FOREIGN KEY (`PROJECTID`) REFERENCES `projects` (`PROJECTID`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table data statistics
-- Table `department`: ~4 rows, Data: 0.02MB, Indexes: 0.02MB
-- Table `employee_table`: ~16 rows, Data: 0.02MB, Indexes: 0.05MB
-- Table `login_table`: ~16 rows, Data: 0.02MB, Indexes: 0.02MB
-- Table `projects`: ~4 rows, Data: 0.02MB, Indexes: 0.03MB
-- Table `time`: ~17 rows, Data: 0.02MB, Indexes: 0.03MB

-- Triggers

DELIMITER $$

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

-- Structure for trigger `calculate_total_minutes_insert`
DROP TRIGGER IF EXISTS `calculate_total_minutes_insert`$$
CREATE DEFINER=`root`@`localhost` TRIGGER calculate_total_minutes_insert BEFORE INSERT ON time
FOR EACH ROW
BEGIN
    IF NEW.STOP_TIME IS NULL THEN
        SET NEW.TOTAL_MINUTES = TIMESTAMPDIFF(MINUTE, NEW.START_TIME, NOW());
    ELSE
        SET NEW.TOTAL_MINUTES = TIMESTAMPDIFF(MINUTE, NEW.START_TIME, NEW.STOP_TIME);
    END IF;
END$$

DELIMITER ;

-- User privileges (current connection user only)
-- GRANT USAGE ON *.* TO `ebrooks23`@`%` IDENTIFIED BY PASSWORD '*D37C49F9CBEFBF8B6F4B165AC703AA271E079004'
-- GRANT ALL PRIVILEGES ON `time_tracker`.* TO `ebrooks23`@`%`

-- Foreign key information
-- FK: department.MANAGERID -> employee_table.EMPID (fk_dept_manager)
-- FK: employee_table.DPTID -> department.DPTID (fk_emp_dept)
-- FK: employee_table.MGR_EMPID -> employee_table.EMPID (fk_emp_manager)
-- FK: login_table.EMPID -> employee_table.EMPID (fk_login_emp)
-- FK: projects.CREATED_BY -> employee_table.EMPID (fk_project_creator)
-- FK: projects.PRIOR_PROJECTID -> projects.PROJECTID (fk_project_prior)
-- FK: time.EMPID -> employee_table.EMPID (fk_time_emp)
-- FK: time.PROJECTID -> projects.PROJECTID (fk_time_project)

-- Index information
-- INDEX: department.fk_dept_manager (MANAGERID)
-- UNIQUE: employee_table.EMAIL_ADDRESS (EMAIL_ADDRESS)
-- INDEX: employee_table.fk_emp_manager (MGR_EMPID)
-- INDEX: employee_table.idx_employee_dept (DPTID)
-- INDEX: login_table.fk_login_emp (EMPID)
-- INDEX: projects.fk_project_prior (PRIOR_PROJECTID)
-- INDEX: projects.idx_project_creator (CREATED_BY)
-- INDEX: time.fk_time_project (PROJECTID)
-- INDEX: time.idx_time_emp_project (EMPID,PROJECTID)

