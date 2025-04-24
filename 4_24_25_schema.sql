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
  KEY `fk_dept_manager` (`MANAGERID`),
  CONSTRAINT `fk_dept_manager` FOREIGN KEY (`MANAGERID`) REFERENCES `employee_table` (`EMPID`) ON DELETE SET NULL ON UPDATE CASCADE
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
  KEY `fk_login_emp` (`EMPID`),
  CONSTRAINT `fk_login_emp` FOREIGN KEY (`EMPID`) REFERENCES `employee_table` (`EMPID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb3 */ ;
/*!50003 SET character_set_results = utf8mb3 */ ;
/*!50003 SET collation_connection  = utf8mb3_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER calculate_total_minutes_insert BEFORE INSERT ON time
FOR EACH ROW
BEGIN
    IF NEW.STOP_TIME IS NULL THEN
        SET NEW.TOTAL_MINUTES = TIMESTAMPDIFF(MINUTE, NEW.START_TIME, NOW());
    ELSE
        SET NEW.TOTAL_MINUTES = TIMESTAMPDIFF(MINUTE, NEW.START_TIME, NEW.STOP_TIME);
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

-- Dump completed on 2025-04-24  7:17:25
