-- MySQL dump 10.13  Distrib 9.3.0, for macos15.2 (arm64)
--
-- Host: localhost    Database: testmanager
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Folders`
--

DROP TABLE IF EXISTS `Folders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Folders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `folder_name` varchar(255) NOT NULL,
  `parent_folder_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_folder_id` (`parent_folder_id`),
  CONSTRAINT `folders_ibfk_1` FOREIGN KEY (`parent_folder_id`) REFERENCES `Folders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Folders`
--

LOCK TABLES `Folders` WRITE;
/*!40000 ALTER TABLE `Folders` DISABLE KEYS */;
/*!40000 ALTER TABLE `Folders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PerformanceTestResults`
--

DROP TABLE IF EXISTS `PerformanceTestResults`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PerformanceTestResults` (
  `id` int NOT NULL AUTO_INCREMENT,
  `performance_test_id` int DEFAULT NULL,
  `execution_time` datetime DEFAULT NULL,
  `response_time_avg` float DEFAULT NULL,
  `response_time_p95` float DEFAULT NULL,
  `throughput` float DEFAULT NULL,
  `error_rate` float DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `report_path` varchar(512) DEFAULT NULL,
  `result_data` text,
  PRIMARY KEY (`id`),
  KEY `performance_test_id` (`performance_test_id`),
  CONSTRAINT `performancetestresults_ibfk_1` FOREIGN KEY (`performance_test_id`) REFERENCES `PerformanceTests` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PerformanceTestResults`
--

LOCK TABLES `PerformanceTestResults` WRITE;
/*!40000 ALTER TABLE `PerformanceTestResults` DISABLE KEYS */;
/*!40000 ALTER TABLE `PerformanceTestResults` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PerformanceTests`
--

DROP TABLE IF EXISTS `PerformanceTests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PerformanceTests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text,
  `k6_script_path` varchar(512) NOT NULL,
  `environment` varchar(100) DEFAULT NULL,
  `parameters` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PerformanceTests`
--

LOCK TABLES `PerformanceTests` WRITE;
/*!40000 ALTER TABLE `PerformanceTests` DISABLE KEYS */;
/*!40000 ALTER TABLE `PerformanceTests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (1,'테스트 프로젝트','테스트 케이스 관리 시스템');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Screenshots`
--

DROP TABLE IF EXISTS `Screenshots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Screenshots` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_case_id` int DEFAULT NULL,
  `screenshot_path` varchar(512) NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_case_id` (`test_case_id`),
  CONSTRAINT `screenshots_ibfk_1` FOREIGN KEY (`test_case_id`) REFERENCES `TestCases` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Screenshots`
--

LOCK TABLES `Screenshots` WRITE;
/*!40000 ALTER TABLE `Screenshots` DISABLE KEYS */;
/*!40000 ALTER TABLE `Screenshots` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_result`
--

DROP TABLE IF EXISTS `test_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_result` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_case_id` int DEFAULT NULL,
  `result` varchar(10) DEFAULT NULL,
  `executed_at` datetime DEFAULT NULL,
  `notes` text,
  `screenshot` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_case_id` (`test_case_id`),
  CONSTRAINT `test_result_ibfk_1` FOREIGN KEY (`test_case_id`) REFERENCES `TestCases` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_result`
--

LOCK TABLES `test_result` WRITE;
/*!40000 ALTER TABLE `test_result` DISABLE KEYS */;
INSERT INTO `test_result` VALUES (1,1,'Pass','2025-08-01 06:30:56','',NULL),(2,2,'Pass','2025-08-01 06:31:08','',NULL),(3,3,'Pass','2025-08-01 06:31:14','',NULL),(4,4,'Fail','2025-08-01 06:31:19','',NULL),(5,5,'N/A','2025-08-01 06:31:26','',NULL),(6,6,'N/A','2025-08-01 06:31:34','',NULL);
/*!40000 ALTER TABLE `test_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TestCases`
--

DROP TABLE IF EXISTS `TestCases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TestCases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `main_category` varchar(255) NOT NULL,
  `sub_category` varchar(255) NOT NULL,
  `detail_category` varchar(255) NOT NULL,
  `pre_condition` text,
  `description` text,
  `result_status` varchar(10) DEFAULT NULL,
  `remark` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `testcases_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TestCases`
--

LOCK TABLES `TestCases` WRITE;
/*!40000 ALTER TABLE `TestCases` DISABLE KEYS */;
INSERT INTO `TestCases` VALUES (1,1,'로그인','페이지 진입','','','로그인 페이지 진입이 가능한지 확인','Pass','','2025-08-01 06:25:15','2025-08-01 06:31:48'),(2,1,'로그인','페이지 진입','text 입력','','이메일 입력이 가능한지 확인','Pass','','2025-08-01 06:25:33','2025-08-01 06:31:46'),(3,1,'로그인','페이지 진입','text 입력','','password 입력이 가능한지 확인','Pass','','2025-08-01 06:25:54','2025-08-01 06:31:45'),(4,1,'로그인','페이지 진입','btn 동작','','[로그인] 버튼 클릭이 가능한지 확인','Fail','','2025-08-01 06:26:27','2025-08-01 06:31:42'),(5,1,'로그인','페이지 진입','btn 동작','정상 값 입력','로그인이 진행되는 지 확인','N/A','','2025-08-01 06:26:57','2025-08-01 06:31:39'),(6,1,'로그인','페이지 진입','btn동작','비정상 값 입력','로그인이 실패하는 지 확인','N/A','','2025-08-01 06:27:56','2025-08-01 06:31:31');
/*!40000 ALTER TABLE `TestCases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TestExecutions`
--

DROP TABLE IF EXISTS `TestExecutions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TestExecutions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_case_id` int DEFAULT NULL,
  `performance_test_id` int DEFAULT NULL,
  `test_type` varchar(50) DEFAULT NULL,
  `execution_start` datetime DEFAULT NULL,
  `execution_end` datetime DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `result_data` text,
  `report_path` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_case_id` (`test_case_id`),
  KEY `performance_test_id` (`performance_test_id`),
  CONSTRAINT `testexecutions_ibfk_1` FOREIGN KEY (`test_case_id`) REFERENCES `TestCases` (`id`),
  CONSTRAINT `testexecutions_ibfk_2` FOREIGN KEY (`performance_test_id`) REFERENCES `PerformanceTests` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TestExecutions`
--

LOCK TABLES `TestExecutions` WRITE;
/*!40000 ALTER TABLE `TestExecutions` DISABLE KEYS */;
/*!40000 ALTER TABLE `TestExecutions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-01 18:10:43
