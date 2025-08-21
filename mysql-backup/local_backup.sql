-- MySQL dump 10.13  Distrib 9.3.0, for macos15.2 (arm64)
--
-- Host: localhost    Database: test_management
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
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('354e4022d50d');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AutomationTestResults`
--

DROP TABLE IF EXISTS `AutomationTestResults`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AutomationTestResults` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_id` int DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `execution_time` float DEFAULT NULL,
  `result_data` text,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_id` (`test_id`),
  CONSTRAINT `automationtestresults_ibfk_1` FOREIGN KEY (`test_id`) REFERENCES `AutomationTests` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AutomationTestResults`
--

LOCK TABLES `AutomationTestResults` WRITE;
/*!40000 ALTER TABLE `AutomationTestResults` DISABLE KEYS */;
/*!40000 ALTER TABLE `AutomationTestResults` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AutomationTests`
--

DROP TABLE IF EXISTS `AutomationTests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AutomationTests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` text,
  `test_type` varchar(50) DEFAULT NULL,
  `script_path` varchar(500) DEFAULT NULL,
  `environment` varchar(100) DEFAULT NULL,
  `parameters` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `creator_id` int DEFAULT NULL,
  `project_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_automation_tests_creator` (`creator_id`),
  KEY `fk_automationtests_project` (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AutomationTests`
--

LOCK TABLES `AutomationTests` WRITE;
/*!40000 ALTER TABLE `AutomationTests` DISABLE KEYS */;
INSERT INTO `AutomationTests` VALUES (1,'로그인','','playwright','test-scripts/performance/login/login_to_dashboard.js','dev','','2025-08-13 05:31:04',NULL,NULL,1),(2,'자동화 테스트 1','첫 번째 자동화 테스트입니다.','functional','/scripts/auto1.js','dev','browser:chrome,timeout:30','2025-08-14 09:25:11','2025-08-14 09:25:11',NULL,1),(3,'자동화 테스트 2','두 번째 자동화 테스트입니다.','ui','/scripts/auto2.js','staging','browser:firefox,timeout:60','2025-08-14 09:25:11','2025-08-14 09:25:11',NULL,1);
/*!40000 ALTER TABLE `AutomationTests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DashboardSummaries`
--

DROP TABLE IF EXISTS `DashboardSummaries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DashboardSummaries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `environment` varchar(100) DEFAULT NULL,
  `total_tests` int DEFAULT NULL,
  `passed_tests` int DEFAULT NULL,
  `failed_tests` int DEFAULT NULL,
  `skipped_tests` int DEFAULT NULL,
  `pass_rate` float DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DashboardSummaries`
--

LOCK TABLES `DashboardSummaries` WRITE;
/*!40000 ALTER TABLE `DashboardSummaries` DISABLE KEYS */;
INSERT INTO `DashboardSummaries` VALUES (1,'production',3,1,1,1,33.33,'2025-08-14 08:56:18'),(2,'alpha',6,1,1,3,16.67,'2025-08-14 08:56:18'),(3,'dev',54,0,0,54,0,'2025-08-14 08:56:18');
/*!40000 ALTER TABLE `DashboardSummaries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Folders`
--

DROP TABLE IF EXISTS `Folders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Folders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `folder_name` varchar(100) NOT NULL,
  `folder_type` varchar(50) DEFAULT NULL,
  `environment` varchar(50) DEFAULT NULL,
  `deployment_date` date DEFAULT NULL,
  `parent_folder_id` int DEFAULT NULL,
  `project_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_folder_id` (`parent_folder_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `folders_ibfk_1` FOREIGN KEY (`parent_folder_id`) REFERENCES `Folders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Folders`
--

LOCK TABLES `Folders` WRITE;
/*!40000 ALTER TABLE `Folders` DISABLE KEYS */;
INSERT INTO `Folders` VALUES (1,'DEV 환경','environment','dev',NULL,NULL,NULL,'2025-08-14 02:45:42'),(2,'ALPHA 환경','environment','alpha',NULL,NULL,NULL,'2025-08-14 02:45:42'),(3,'PRODUCTION 환경','environment','production',NULL,NULL,NULL,'2025-08-14 02:45:42'),(4,'2024-08-01','deployment_date','dev','2025-08-13',1,NULL,'2025-08-14 02:45:42'),(5,'2024-08-15','deployment_date','alpha','2025-08-13',2,NULL,'2025-08-14 02:45:42'),(6,'2024-09-01','deployment_date','production','2025-08-13',3,NULL,'2025-08-14 02:45:42'),(7,'CLM','feature','dev',NULL,4,NULL,'2025-08-14 02:45:42'),(8,'Litigation','feature','alpha',NULL,5,NULL,'2025-08-14 02:45:42'),(9,'Dashboard','feature','production',NULL,6,NULL,'2025-08-14 02:45:42');
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
  `test_id` int DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `execution_time` float DEFAULT NULL,
  `result_data` text,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_id` (`test_id`),
  CONSTRAINT `performancetestresults_ibfk_1` FOREIGN KEY (`test_id`) REFERENCES `PerformanceTests` (`id`)
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
  `name` varchar(200) NOT NULL,
  `description` text,
  `script_path` varchar(500) DEFAULT NULL,
  `environment` varchar(100) DEFAULT NULL,
  `parameters` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `creator_id` int DEFAULT NULL,
  `test_type` varchar(50) DEFAULT 'load',
  `project_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_performance_tests_creator` (`creator_id`),
  KEY `fk_performancetests_project` (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PerformanceTests`
--

LOCK TABLES `PerformanceTests` WRITE;
/*!40000 ALTER TABLE `PerformanceTests` DISABLE KEYS */;
INSERT INTO `PerformanceTests` VALUES (1,'CLM 계약서 생성 테스트','LFBZ CLM 시스템 계약서 생성 성능 테스트','clm_draft.js','prod','\"{\\\"DRAFT_TYPE\\\": \\\"new\\\", \\\"SECURITY_TYPE\\\": \\\"all\\\", \\\"REVIEW_TYPE\\\": \\\"use\\\"}\"','2025-08-03 11:23:03','2025-08-19 05:57:50',NULL,'load',1),(2,'CLM 계약서 생성 테스트','Description: LFBZ CLM 시스템 계약서 생성 성능 테스트','clm_draft.js','prod','{}','2025-08-03 14:28:33','2025-08-03 14:28:33',NULL,'load',1),(3,'로그인 테스트','LFBZ 로그인 테스트',NULL,'dev','{}','2025-08-13 06:01:14','2025-08-13 06:01:14',NULL,'load',1);
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
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
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
  `test_result_id` int DEFAULT NULL,
  `file_path` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_result_id` (`test_result_id`)
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
-- Table structure for table `TestCases`
--

DROP TABLE IF EXISTS `TestCases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TestCases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` text,
  `test_type` varchar(50) DEFAULT NULL,
  `script_path` varchar(500) DEFAULT NULL,
  `folder_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `main_category` varchar(100) DEFAULT NULL,
  `sub_category` varchar(100) DEFAULT NULL,
  `detail_category` varchar(100) DEFAULT NULL,
  `pre_condition` text,
  `expected_result` text,
  `remark` text,
  `automation_code_path` varchar(500) DEFAULT NULL,
  `environment` varchar(50) DEFAULT NULL,
  `creator_id` int DEFAULT NULL,
  `priority` varchar(20) DEFAULT 'medium',
  `status` varchar(20) DEFAULT 'draft',
  `project_id` int DEFAULT NULL,
  `result_status` varchar(20) DEFAULT 'pending',
  `automation_code_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `folder_id` (`folder_id`),
  KEY `fk_test_cases_creator` (`creator_id`),
  KEY `fk_testcases_project` (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TestCases`
--

LOCK TABLES `TestCases` WRITE;
/*!40000 ALTER TABLE `TestCases` DISABLE KEYS */;
INSERT INTO `TestCases` VALUES (1,'CLM/Draft/기안 작성','로그인 완료','CLM 기안 작성 기능 테스트','test-scripts/clm/draft.js',7,'2025-08-03 11:23:01','2025-08-14 08:57:34','CLM','Draft','기안 작성','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/draft.js','dev',NULL,'medium','draft',1,'Pass',NULL),(2,'CLM/Review/검토','기안 작성 완료','CLM 검토 기능 테스트','test-scripts/clm/review.js',8,'2025-08-03 11:23:01','2025-08-14 08:49:41','CLM','Review','검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/review.js','alpha',NULL,'medium','draft',1,'Pass',NULL),(3,'CLM/Sign/전자서명','검토 완료','CLM 전자서명 기능 테스트','test-scripts/clm/sign.js',9,'2025-08-03 11:23:01','2025-08-14 08:50:10','CLM','Sign','전자서명','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/sign.js','production',NULL,'medium','draft',1,'Pass',NULL),(4,'CLM/Financial/재무 검토','ALPHA 환경 접속','CLM 재무 검토 기능 테스트','test-scripts/performance/login/simple_test.js',7,'2025-08-03 11:23:01','2025-08-19 05:40:43','CLM','Financial','재무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/performance/login/simple_test.js','dev',NULL,'medium','draft',1,'Pass',NULL),(5,'CLM/Legal/법무 검토','ALPHA 환경 접속','CLM 법무 검토 기능 테스트','test-scripts/clm/legal.js',7,'2025-08-03 11:23:01','2025-08-12 02:46:30','CLM','Legal','법무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/legal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(6,'CLM/Final/최종 승인','PRODUCTION 환경 접속','CLM 최종 승인 기능 테스트','test-scripts/clm/final.js',7,'2025-08-03 11:23:01','2025-08-12 02:46:30','CLM','Final','최종 승인','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/final.js','dev',NULL,'medium','draft',1,'N/T',NULL),(7,'CLM/Seal/도장 찍기','PRODUCTION 환경 접속','CLM 도장 찍기 기능 테스트','test-scripts/clm/seal.js',7,'2025-08-03 11:23:01','2025-08-12 02:46:30','CLM','Seal','도장 찍기','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/seal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(8,'CLM/Draft/기안 작성','로그인 완료','CLM 기안 작성 기능 테스트','test-scripts/performance/clm/nomerl/clm_draft.js',7,'2025-08-03 13:22:05','2025-08-12 02:46:30','CLM','Draft','기안 작성','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/performance/clm/nomerl/clm_draft.js','dev',NULL,'medium','draft',1,'N/T',NULL),(9,'CLM/Review/검토','기안 작성 완료','CLM 검토 기능 테스트','test-scripts/clm/review.js',8,'2025-08-03 13:22:05','2025-08-14 08:49:46','CLM','Review','검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/review.js','alpha',NULL,'medium','draft',1,'Fail',NULL),(11,'CLM/Financial/재무 검토','ALPHA 환경 접속','CLM 재무 검토 기능 테스트','test-scripts/clm/financial.js',7,'2025-08-03 13:22:05','2025-08-12 02:46:30','CLM','Financial','재무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/financial.js','dev',NULL,'medium','draft',1,'N/T',NULL),(12,'CLM/Legal/법무 검토','ALPHA 환경 접속','CLM 법무 검토 기능 테스트','test-scripts/clm/legal.js',7,'2025-08-03 13:22:05','2025-08-12 02:46:30','CLM','Legal','법무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/legal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(13,'CLM/Final/최종 승인','PRODUCTION 환경 접속','CLM 최종 승인 기능 테스트','test-scripts/clm/final.js',7,'2025-08-03 13:22:05','2025-08-12 02:46:30','CLM','Final','최종 승인','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/final.js','dev',NULL,'medium','draft',1,'N/T',NULL),(14,'CLM/Seal/도장 찍기','PRODUCTION 환경 접속','CLM 도장 찍기 기능 테스트','test-scripts/clm/seal.js',7,'2025-08-03 13:22:05','2025-08-12 02:46:30','CLM','Seal','도장 찍기','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/seal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(17,'2/2/2','2','2','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 04:43:40','2025-08-05 04:43:40','2','2','2','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(18,'CLM 시스템/기안 작성/기본 기안 작성','사용자가 로그인되어 있음','기안이 성공적으로 작성됨','test-scripts/playwright/clm_draft.js',7,'2025-08-05 05:38:09','2025-08-12 02:46:30','CLM 시스템','기안 작성','기본 기안 작성','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/clm_draft.js','dev',NULL,'medium','draft',1,'N/T',NULL),(19,'CLM 시스템/검토/법무 검토','기안이 작성되어 있음','법무 검토가 완료됨','test-scripts/playwright/clm_lagel.js',7,'2025-08-05 05:38:09','2025-08-12 02:46:30','CLM 시스템','검토','법무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/clm_lagel.js','dev',NULL,'medium','draft',1,'N/T',NULL),(20,'CLM 시스템/재무 검토/재무 검토','기안이 작성되어 있음','재무 검토가 완료됨','test-scripts/playwright/clm_financial.js',7,'2025-08-05 05:38:09','2025-08-12 02:46:30','CLM 시스템','재무 검토','재무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/clm_financial.js','dev',NULL,'medium','draft',1,'N/T',NULL),(21,'CLM 시스템/기안 작성/기본 기안 작성','사용자가 로그인되어 있음','기안이 성공적으로 작성됨','test-scripts/playwright/clm_draft.js',7,'2025-08-05 05:43:37','2025-08-12 02:46:30','CLM 시스템','기안 작성','기본 기안 작성','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/clm_draft.js','dev',NULL,'medium','draft',1,'N/T',NULL),(22,'CLM 시스템/검토/법무 검토','기안이 작성되어 있음','법무 검토가 완료됨','test-scripts/playwright/clm_lagel.js',7,'2025-08-05 05:43:37','2025-08-12 02:46:30','CLM 시스템','검토','법무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/clm_lagel.js','dev',NULL,'medium','draft',1,'N/T',NULL),(23,'CLM 시스템/재무 검토/재무 검토','기안이 작성되어 있음','재무 검토가 완료됨','test-scripts/playwright/clm_financial.js',7,'2025-08-05 05:43:37','2025-08-12 02:46:30','CLM 시스템','재무 검토','재무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/clm_financial.js','dev',NULL,'medium','draft',1,'N/T',NULL),(24,'CLM/Review/검토','기안 작성 완료','CLM 검토 기능 테스트','test-scripts/clm/review.js',8,'2025-08-05 05:46:35','2025-08-14 08:49:57','CLM','Review','검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/review.js','alpha',NULL,'medium','draft',1,'N/A',NULL),(25,'CLM/Draft/기안 작성','로그인 완료','CLM 기안 작성 기능 테스트','test-scripts/performance/clm/nomerl/clm_draft.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Draft','기안 작성','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/performance/clm/nomerl/clm_draft.js','dev',NULL,'medium','draft',1,'N/T',NULL),(26,'CLM/Financial/재무 검토','ALPHA 환경 접속','CLM 재무 검토 기능 테스트','test-scripts/performance/login/simple_test.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Financial','재무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/performance/login/simple_test.js','dev',NULL,'medium','draft',1,'N/T',NULL),(27,'CLM/Draft/기안 작성','로그인 완료','CLM 기안 작성 기능 테스트','test-scripts/clm/draft.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Draft','기안 작성','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/draft.js','dev',NULL,'medium','draft',1,'N/T',NULL),(28,'CLM/Sign/전자서명','검토 완료','CLM 전자서명 기능 테스트','test-scripts/clm/sign.js',9,'2025-08-05 05:46:35','2025-08-14 08:50:15','CLM','Sign','전자서명','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/sign.js','production',NULL,'medium','draft',1,'Fail',NULL),(29,'CLM/Review/검토','기안 작성 완료','CLM 검토 기능 테스트','test-scripts/clm/review.js',8,'2025-08-05 05:46:35','2025-08-14 08:50:02','CLM','Review','검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/review.js','alpha',NULL,'medium','draft',1,'Block',NULL),(30,'CLM/Legal/법무 검토','ALPHA 환경 접속','CLM 법무 검토 기능 테스트','test-scripts/clm/legal.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Legal','법무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/legal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(31,'CLM/Final/최종 승인','PRODUCTION 환경 접속','CLM 최종 승인 기능 테스트','test-scripts/clm/final.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Final','최종 승인','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/final.js','dev',NULL,'medium','draft',1,'N/T',NULL),(32,'CLM/Seal/도장 찍기','PRODUCTION 환경 접속','CLM 도장 찍기 기능 테스트','test-scripts/clm/seal.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Seal','도장 찍기','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/seal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(33,'CLM/Financial/재무 검토','ALPHA 환경 접속','CLM 재무 검토 기능 테스트','test-scripts/clm/financial.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Financial','재무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/financial.js','dev',NULL,'medium','draft',1,'N/T',NULL),(34,'CLM/Legal/법무 검토','ALPHA 환경 접속','CLM 법무 검토 기능 테스트','test-scripts/clm/legal.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Legal','법무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/legal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(35,'CLM/Seal/도장 찍기','PRODUCTION 환경 접속','CLM 도장 찍기 기능 테스트','test-scripts/clm/seal.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Seal','도장 찍기','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/seal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(36,'CLM/Final/최종 승인','PRODUCTION 환경 접속','CLM 최종 승인 기능 테스트','test-scripts/clm/final.js',7,'2025-08-05 05:46:35','2025-08-12 02:46:30','CLM','Final','최종 승인','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/final.js','dev',NULL,'medium','draft',1,'N/T',NULL),(37,'2/2/2','2','2','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:46:35','2025-08-14 08:40:57','2','2','2','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(38,'로그인/페이지 진입/-','-','로그인 페이지 진입이 가능한지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:46:35','2025-08-14 08:40:57','로그인','페이지 진입','-','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(39,'로그인/페이지 진입/text 입력','-','이메일 입력이 가능한지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:46:35','2025-08-14 08:40:57','로그인','페이지 진입','text 입력','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(40,'로그인/페이지 진입/text 입력','-','Password 입력이 가능한지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:46:35','2025-08-14 08:40:57','로그인','페이지 진입','text 입력','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(41,'로그인/페이지 진입/btn 동작','-','[로그인] 버튼 클릭이 가능한지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:46:35','2025-08-14 08:40:57','로그인','페이지 진입','btn 동작','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(42,'로그인/페이지 진입/정상 값 입력','-','로그인이 진행되는 지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:46:35','2025-08-14 08:40:57','로그인','페이지 진입','정상 값 입력','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(43,'로그인/페이지 진입/비정상 값 입력','-','로그인이 실패하는 지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:46:35','2025-08-14 08:40:57','로그인','페이지 진입','비정상 값 입력','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(44,'CLM/Review/검토','기안 작성 완료','CLM 검토 기능 테스트','test-scripts/clm/review.js',8,'2025-08-05 05:47:06','2025-08-14 08:38:55','CLM','Review','검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/review.js','alpha',NULL,'medium','draft',1,'N/T',NULL),(45,'CLM/Draft/기안 작성','로그인 완료','CLM 기안 작성 기능 테스트','test-scripts/performance/clm/nomerl/clm_draft.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Draft','기안 작성','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/performance/clm/nomerl/clm_draft.js','dev',NULL,'medium','draft',1,'N/T',NULL),(46,'CLM/Financial/재무 검토','ALPHA 환경 접속','CLM 재무 검토 기능 테스트','test-scripts/performance/login/simple_test.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Financial','재무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/performance/login/simple_test.js','dev',NULL,'medium','draft',1,'N/T',NULL),(47,'CLM/Draft/기안 작성','로그인 완료','CLM 기안 작성 기능 테스트','test-scripts/clm/draft.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Draft','기안 작성','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/draft.js','dev',NULL,'medium','draft',1,'N/T',NULL),(48,'CLM/Sign/전자서명','검토 완료','CLM 전자서명 기능 테스트','test-scripts/clm/sign.js',9,'2025-08-05 05:47:06','2025-08-14 08:38:56','CLM','Sign','전자서명','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/sign.js','production',NULL,'medium','draft',1,'N/T',NULL),(49,'CLM/Review/검토','기안 작성 완료','CLM 검토 기능 테스트','test-scripts/clm/review.js',8,'2025-08-05 05:47:06','2025-08-14 08:38:55','CLM','Review','검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/review.js','alpha',NULL,'medium','draft',1,'N/T',NULL),(50,'CLM/Legal/법무 검토','ALPHA 환경 접속','CLM 법무 검토 기능 테스트','test-scripts/clm/legal.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Legal','법무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/legal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(51,'CLM/Final/최종 승인','PRODUCTION 환경 접속','CLM 최종 승인 기능 테스트','test-scripts/clm/final.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Final','최종 승인','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/final.js','dev',NULL,'medium','draft',1,'N/T',NULL),(52,'CLM/Seal/도장 찍기','PRODUCTION 환경 접속','CLM 도장 찍기 기능 테스트','test-scripts/clm/seal.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Seal','도장 찍기','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/seal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(53,'CLM/Financial/재무 검토','ALPHA 환경 접속','CLM 재무 검토 기능 테스트','test-scripts/clm/financial.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Financial','재무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/financial.js','dev',NULL,'medium','draft',1,'N/T',NULL),(54,'CLM/Legal/법무 검토','ALPHA 환경 접속','CLM 법무 검토 기능 테스트','test-scripts/clm/legal.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Legal','법무 검토','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/legal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(55,'CLM/Seal/도장 찍기','PRODUCTION 환경 접속','CLM 도장 찍기 기능 테스트','test-scripts/clm/seal.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Seal','도장 찍기','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/seal.js','dev',NULL,'medium','draft',1,'N/T',NULL),(56,'CLM/Final/최종 승인','PRODUCTION 환경 접속','CLM 최종 승인 기능 테스트','test-scripts/clm/final.js',7,'2025-08-05 05:47:06','2025-08-12 02:46:30','CLM','Final','최종 승인','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/clm/final.js','dev',NULL,'medium','draft',1,'N/T',NULL),(57,'2/2/2','2','2','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:47:06','2025-08-14 08:40:57','2','2','2','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(58,'로그인/페이지 진입/-','-','로그인 페이지 진입이 가능한지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:47:06','2025-08-14 08:40:57','로그인','페이지 진입','-','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(59,'로그인/페이지 진입/text 입력','-','이메일 입력이 가능한지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:47:06','2025-08-14 08:40:57','로그인','페이지 진입','text 입력','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(60,'로그인/페이지 진입/text 입력','-','Password 입력이 가능한지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:47:06','2025-08-14 08:40:57','로그인','페이지 진입','text 입력','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(61,'로그인/페이지 진입/btn 동작','-','[로그인] 버튼 클릭이 가능한지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:47:06','2025-08-14 08:40:57','로그인','페이지 진입','btn 동작','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(62,'로그인/페이지 진입/정상 값 입력','-','로그인이 진행되는 지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:47:06','2025-08-14 08:40:57','로그인','페이지 진입','정상 값 입력','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(63,'로그인/페이지 진입/비정상 값 입력','-','로그인이 실패하는 지 확인','test-scripts/playwright/sample-login.spec.js',4,'2025-08-05 05:47:06','2025-08-14 08:40:57','로그인','페이지 진입','비정상 값 입력','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','test-scripts/playwright/sample-login.spec.js','dev',NULL,'medium','draft',1,'N/T',NULL),(64,'기능 테스트/UI 테스트/버튼 클릭','로그인 상태','버튼 클릭 후 페이지 이동','',4,'2025-08-05 05:55:02','2025-08-05 05:55:02','기능 테스트','UI 테스트','버튼 클릭','테스트 실행을 위한 사전 조건','테스트가 성공적으로 완료되어야 함','자동화 테스트 가능','','dev',NULL,'medium','draft',1,'N/T',NULL),(65,'테스트 케이스 1','첫 번째 테스트 케이스입니다.','functional',NULL,4,'2025-08-14 09:24:46','2025-08-14 08:40:57',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'dev',NULL,'high','active',1,'N/T',NULL),(66,'테스트 케이스 2','두 번째 테스트 케이스입니다.','performance',NULL,4,'2025-08-14 09:24:46','2025-08-14 08:40:57',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'dev',NULL,'medium','draft',1,'N/T',NULL);
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
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `execution_time` float DEFAULT NULL,
  `result_data` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `test_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `automation_test_id` int DEFAULT NULL,
  `performance_test_id` int DEFAULT NULL,
  `environment` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `executed_by` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `started_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `completed_at` datetime DEFAULT NULL,
  `result_summary` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `test_case_id` (`test_case_id`),
  KEY `fk_execution_automation_test` (`automation_test_id`),
  KEY `fk_execution_performance_test` (`performance_test_id`),
  CONSTRAINT `fk_execution_automation_test` FOREIGN KEY (`automation_test_id`) REFERENCES `AutomationTests` (`id`),
  CONSTRAINT `fk_execution_performance_test` FOREIGN KEY (`performance_test_id`) REFERENCES `PerformanceTests` (`id`),
  CONSTRAINT `testexecutions_ibfk_1` FOREIGN KEY (`test_case_id`) REFERENCES `TestCases` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TestExecutions`
--

LOCK TABLES `TestExecutions` WRITE;
/*!40000 ALTER TABLE `TestExecutions` DISABLE KEYS */;
INSERT INTO `TestExecutions` VALUES (1,NULL,'Error',NULL,NULL,'2025-08-13 15:04:23','performance',NULL,1,NULL,NULL,'2025-08-13 06:04:24',NULL,'{\"status\": \"Error\", \"error\": \"\\uc2a4\\ud06c\\ub9bd\\ud2b8 \\ud30c\\uc77c\\uc744 \\ucc3e\\uc744 \\uc218 \\uc5c6\\uc2b5\\ub2c8\\ub2e4: /Users/ggpark/Desktop/Team_Git/integrated-test-platform/backend/engines/../../clm_draft.js\"}'),(2,NULL,'Error',NULL,NULL,'2025-08-13 15:04:41','performance',NULL,3,NULL,NULL,'2025-08-13 06:04:42',NULL,'{\"status\": \"Error\", \"error\": \"expected str, bytes or os.PathLike object, not NoneType\"}'),(3,NULL,'Error',NULL,NULL,'2025-08-13 15:04:42','performance',NULL,3,NULL,NULL,'2025-08-13 06:04:43',NULL,'{\"status\": \"Error\", \"error\": \"expected str, bytes or os.PathLike object, not NoneType\"}'),(4,NULL,'Error',NULL,NULL,'2025-08-13 15:05:01','performance',NULL,3,NULL,NULL,'2025-08-13 06:05:02',NULL,'{\"status\": \"Error\", \"error\": \"expected str, bytes or os.PathLike object, not NoneType\"}'),(5,NULL,'Error',NULL,NULL,'2025-08-19 14:49:34','performance',NULL,1,NULL,NULL,'2025-08-19 05:49:35',NULL,'{\"status\": \"Error\", \"error\": \"\\uc2a4\\ud06c\\ub9bd\\ud2b8 \\ud30c\\uc77c\\uc744 \\ucc3e\\uc744 \\uc218 \\uc5c6\\uc2b5\\ub2c8\\ub2e4: /Users/ggpark/Desktop/Team_Git/integrated-test-platform/backend/engines/../../clm_draft.js\"}'),(6,NULL,'Error',NULL,NULL,'2025-08-19 14:53:36','performance',NULL,1,NULL,NULL,'2025-08-19 05:53:36',NULL,'{\"status\": \"Error\", \"error\": \"\\uc2a4\\ud06c\\ub9bd\\ud2b8 \\ud30c\\uc77c\\uc744 \\ucc3e\\uc744 \\uc218 \\uc5c6\\uc2b5\\ub2c8\\ub2e4: /Users/ggpark/Desktop/Team_Git/integrated-test-platform/backend/engines/../../clm_draft.js\"}'),(7,NULL,'Error',NULL,NULL,'2025-08-19 14:56:51','performance',NULL,1,NULL,NULL,'2025-08-19 05:56:51',NULL,'{\"status\": \"Error\", \"error\": \"\\uc2a4\\ud06c\\ub9bd\\ud2b8 \\ud30c\\uc77c\\uc744 \\ucc3e\\uc744 \\uc218 \\uc5c6\\uc2b5\\ub2c8\\ub2e4: /Users/ggpark/Desktop/Team_Git/integrated-test-platform/backend/engines/../../clm_draft.js\"}'),(8,NULL,'Error',NULL,NULL,'2025-08-19 15:04:00','performance',NULL,1,NULL,NULL,'2025-08-19 06:04:00',NULL,'{\"status\": \"Error\", \"error\": \"\\uc2a4\\ud06c\\ub9bd\\ud2b8 \\ud30c\\uc77c\\uc744 \\ucc3e\\uc744 \\uc218 \\uc5c6\\uc2b5\\ub2c8\\ub2e4: /Users/ggpark/Desktop/Team_Git/integrated-test-platform/backend/engines/../../clm_draft.js\"}');
/*!40000 ALTER TABLE `TestExecutions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TestResults`
--

DROP TABLE IF EXISTS `TestResults`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TestResults` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_case_id` int DEFAULT NULL,
  `result` varchar(20) DEFAULT NULL,
  `execution_time` float DEFAULT NULL,
  `environment` varchar(50) DEFAULT NULL,
  `executed_by` varchar(100) DEFAULT NULL,
  `executed_at` datetime DEFAULT NULL,
  `notes` text,
  `automation_test_id` int DEFAULT NULL,
  `performance_test_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_case_id` (`test_case_id`),
  KEY `fk_automation_test` (`automation_test_id`),
  KEY `fk_performance_test` (`performance_test_id`),
  CONSTRAINT `fk_automation_test` FOREIGN KEY (`automation_test_id`) REFERENCES `AutomationTests` (`id`),
  CONSTRAINT `fk_performance_test` FOREIGN KEY (`performance_test_id`) REFERENCES `PerformanceTests` (`id`),
  CONSTRAINT `testresults_ibfk_1` FOREIGN KEY (`test_case_id`) REFERENCES `TestCases` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TestResults`
--

LOCK TABLES `TestResults` WRITE;
/*!40000 ALTER TABLE `TestResults` DISABLE KEYS */;
INSERT INTO `TestResults` VALUES (1,NULL,'Pass',2.00188,'dev','system','2025-08-13 05:51:50','테스트 \'로그인\' 실행 완료',1,NULL),(2,NULL,'Pass',2.00095,'dev','system','2025-08-13 05:52:34','테스트 \'로그인\' 실행 완료',1,NULL);
/*!40000 ALTER TABLE `TestResults` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'admin','admin@example.com','scrypt:32768:8:1$pIBrF9FxYTQ4dgFU$f7d8451d2365fc33302c2482aceeb13141f9e543398311ec8dc7b99ead7b9910248a21eb56962f270ea00132b5fa4bfac9e890509d63bc1dc188aaba5a7e262e','Admin','User','admin',1,NULL,'2025-08-14 02:45:41','2025-08-14 05:57:37'),(2,'testuser','test@example.com','scrypt:32768:8:1$ng66OPMcYZ3eolJ6$93380805687414a0e0fb4ddba65b10642f9cc472943b004df8cf1c018039348064bca9eeccb60f0cfc4a39ea2cb2957d588face494c82fd585cc5f52e09b4297','Test','User','user',1,NULL,'2025-08-14 02:45:42','2025-08-14 02:45:42');
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UserSessions`
--

DROP TABLE IF EXISTS `UserSessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserSessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `session_token` varchar(255) NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `expires_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_token` (`session_token`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UserSessions`
--

LOCK TABLES `UserSessions` WRITE;
/*!40000 ALTER TABLE `UserSessions` DISABLE KEYS */;
/*!40000 ALTER TABLE `UserSessions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-21 11:58:13
