/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.11-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: time_tracker
-- ------------------------------------------------------
-- Server version	10.11.11-MariaDB-0ubuntu0.24.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `DPTID` varchar(20) NOT NULL,
  `DPT_NAME` varchar(100) NOT NULL,
  `MANAGERID` varchar(20) DEFAULT NULL,
  `DPT_ACTIVE` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`DPTID`),
  KEY `MANAGERID` (`MANAGERID`),
  CONSTRAINT `fk_dept_manager` FOREIGN KEY (`MANAGERID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`ebrooks23`@`%`*/ /*!50003 TRIGGER before_insert_department
                BEFORE INSERT ON department
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.DPTID IS NULL OR NEW.DPTID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(DPTID, 2) + 0), 1000) + 1
                                    FROM department);
                        SET NEW.DPTID = CONCAT('D', next_id);
                    END IF;
                END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `employee_projects`
--

DROP TABLE IF EXISTS `employee_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee_projects` (
  `EMPID` varchar(20) NOT NULL,
  `PROJECT_ID` varchar(20) NOT NULL,
  PRIMARY KEY (`EMPID`,`PROJECT_ID`),
  KEY `EMPID` (`EMPID`),
  KEY `PROJECT_ID` (`PROJECT_ID`),
  CONSTRAINT `fk_emp_proj_employee` FOREIGN KEY (`EMPID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_emp_proj_project` FOREIGN KEY (`PROJECT_ID`) REFERENCES `projects` (`PROJECTID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `employee_table`
--

DROP TABLE IF EXISTS `employee_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`ebrooks23`@`%`*/ /*!50003 TRIGGER before_insert_employee
                BEFORE INSERT ON employee_table
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.EMPID IS NULL OR NEW.EMPID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(EMPID, 2) + 0), 1000) + 1
                                    FROM employee_table);
                        SET NEW.EMPID = CONCAT('E', next_id);
                    END IF;
                END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `login_table`
--

DROP TABLE IF EXISTS `login_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`ebrooks23`@`%`*/ /*!50003 TRIGGER before_insert_project
                BEFORE INSERT ON projects
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.PROJECTID IS NULL OR NEW.PROJECTID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(PROJECTID, 2) + 0), 10000) + 1
                                    FROM projects);
                        SET NEW.PROJECTID = CONCAT('P', next_id);
                    END IF;
                END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `time`
--

DROP TABLE IF EXISTS `time`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `time` (
  `TIMEID` varchar(20) NOT NULL,
  `EMPID` varchar(20) NOT NULL,
  `START_TIME` datetime NOT NULL,
  `STOP_TIME` datetime NOT NULL,
  `NOTES` text DEFAULT NULL,
  `MANUAL_ENTRY` tinyint(1) DEFAULT 0,
  `TOTAL_MINUTES` int(11) GENERATED ALWAYS AS (timestampdiff(MINUTE,`START_TIME`,`STOP_TIME`)) STORED,
  `PROJECTID` varchar(30) NOT NULL DEFAULT 'TEMP_PROJECT',
  PRIMARY KEY (`TIMEID`),
  KEY `EMPID` (`EMPID`),
  KEY `START_TIME` (`START_TIME`),
  KEY `STOP_TIME` (`STOP_TIME`),
  KEY `fk_time_project` (`PROJECTID`),
  CONSTRAINT `fk_time_employee` FOREIGN KEY (`EMPID`) REFERENCES `employee_table` (`EMPID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_time_project` FOREIGN KEY (`PROJECTID`) REFERENCES `projects` (`PROJECTID`),
  CONSTRAINT `chk_time_valid` CHECK (`STOP_TIME` > `START_TIME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`ebrooks23`@`%`*/ /*!50003 TRIGGER before_insert_time
                BEFORE INSERT ON time
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.TIMEID IS NULL OR NEW.TIMEID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(TIMEID, 2) + 0), 1000) + 1
                                    FROM time);
                        SET NEW.TIMEID = CONCAT('T', next_id);
                    END IF;
                END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-01 17:15:56
