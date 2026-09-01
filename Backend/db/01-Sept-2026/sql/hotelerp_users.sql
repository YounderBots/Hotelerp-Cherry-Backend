-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: hotelerp_users
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Current Database: `hotelerp_users`
--

/*!40000 DROP DATABASE IF EXISTS `hotelerp_users`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hotelerp_users` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hotelerp_users`;

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
INSERT INTO `alembic_version` VALUES ('198e9660fd95');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Department_Name` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_department_company_id` (`company_id`),
  KEY `ix_department_id` (`id`),
  KEY `ix_department_updated_by` (`updated_by`),
  KEY `ix_department_status` (`status`),
  KEY `ix_department_Department_Name` (`Department_Name`),
  KEY `ix_department_created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'Front Office','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Housekeeping','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Food & Beverage','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Kitchen','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Maintenance','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Accounts','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Human Resources','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Security','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `designation`
--

DROP TABLE IF EXISTS `designation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `designation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Designation_Name` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_designation_updated_by` (`updated_by`),
  KEY `ix_designation_status` (`status`),
  KEY `ix_designation_created_by` (`created_by`),
  KEY `ix_designation_Designation_Name` (`Designation_Name`),
  KEY `ix_designation_company_id` (`company_id`),
  KEY `ix_designation_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `designation`
--

LOCK TABLES `designation` WRITE;
/*!40000 ALTER TABLE `designation` DISABLE KEYS */;
INSERT INTO `designation` VALUES (1,'General Manager','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Front Office Manager','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Front Desk Executive','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Reservation Executive','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Housekeeping Supervisor','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Room Attendant','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Restaurant Manager','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Chef','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(9,'Bartender','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(10,'Accountant','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `designation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menus`
--

DROP TABLE IF EXISTS `menus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `menu_name` varchar(100) NOT NULL,
  `menu_link` varchar(255) NOT NULL,
  `menu_icon` varchar(100) DEFAULT NULL,
  `order` int NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_menus_menu_name` (`menu_name`),
  KEY `ix_menus_company_id` (`company_id`),
  KEY `ix_menus_id` (`id`),
  KEY `ix_menus_updated_by` (`updated_by`),
  KEY `ix_menus_status` (`status`),
  KEY `ix_menus_created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menus`
--

LOCK TABLES `menus` WRITE;
/*!40000 ALTER TABLE `menus` DISABLE KEYS */;
INSERT INTO `menus` VALUES (1,'Dashboard','/dashboard','dashboard',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Reservation','/reservation','reservation',2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Night Audit','','night-auditing',3,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Guest Enquiry','/guest_enquiry','guest-enquiry',4,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'House Keeper','','house-keeper',5,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'HRM','','hrm',6,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Restaurant','','restaurant',7,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Bar','','bar',8,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(9,'Master Data','','master-data',9,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `menus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_id` varchar(100) NOT NULL,
  `menu_id` varchar(100) NOT NULL,
  `submenu_id` varchar(100) DEFAULT NULL,
  `view_permission` tinyint(1) DEFAULT NULL,
  `create_permission` tinyint(1) DEFAULT NULL,
  `edit_permission` tinyint(1) DEFAULT NULL,
  `delete_permission` tinyint(1) DEFAULT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_role_permissions_id` (`id`),
  KEY `ix_role_permissions_company_id` (`company_id`),
  KEY `ix_role_permissions_status` (`status`),
  KEY `ix_role_permissions_menu_id` (`menu_id`),
  KEY `ix_role_permissions_updated_by` (`updated_by`),
  KEY `ix_role_permissions_submenu_id` (`submenu_id`),
  KEY `ix_role_permissions_role_id` (`role_id`),
  KEY `ix_role_permissions_created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=139 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
INSERT INTO `role_permissions` VALUES (1,'1','1',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'1','2',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'1','2','101',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'1','2','102',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'1','2','103',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'1','2','104',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'1','3',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'1','3','111',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(9,'1','3','112',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(10,'1','3','113',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(11,'1','3','114',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(12,'1','4',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(13,'1','5',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(14,'1','5','121',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(15,'1','5','122',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(16,'1','6',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(17,'1','6','131',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(18,'1','6','132',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(19,'1','6','133',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(20,'1','6','134',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(21,'1','6','135',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(22,'1','6','136',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(23,'1','6','137',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(24,'1','6','138',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(25,'1','6','139',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(26,'1','6','140',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(27,'1','7',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(28,'1','7','151',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(29,'1','7','152',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(30,'1','7','153',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(31,'1','7','154',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(32,'1','7','155',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(33,'1','7','156',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(34,'1','7','157',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(35,'1','7','158',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(36,'1','7','159',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(37,'1','7','160',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(38,'1','7','161',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(39,'1','7','162',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(40,'1','7','163',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(41,'1','7','164',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(42,'1','8',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(43,'1','8','171',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(44,'1','8','172',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(45,'1','8','173',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(46,'1','8','174',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(47,'1','8','175',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(48,'1','8','176',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(49,'1','8','177',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(50,'1','8','178',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(51,'1','8','179',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(52,'1','8','180',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(53,'1','9',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(54,'1','9','191',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(55,'1','9','192',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(56,'1','9','193',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(57,'1','9','194',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(58,'1','9','195',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(59,'1','9','196',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(60,'1','9','197',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(61,'1','9','198',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(62,'1','9','199',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(63,'1','9','200',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(64,'1','9','201',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(65,'1','9','202',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(66,'1','9','203',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(67,'2','1',NULL,1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(68,'2','2',NULL,1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(69,'2','2','101',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(70,'2','2','102',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(71,'2','2','103',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(72,'2','2','104',1,1,1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(73,'2','3',NULL,1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(74,'2','3','111',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(75,'2','3','112',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(76,'2','3','113',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(77,'2','3','114',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(78,'2','4',NULL,1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(79,'2','5',NULL,1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(80,'2','5','121',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(81,'2','5','122',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(82,'2','9',NULL,1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(83,'2','9','191',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(84,'2','9','192',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(85,'2','9','193',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(86,'2','9','194',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(87,'2','9','195',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(88,'2','9','196',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(89,'2','9','197',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(90,'2','9','198',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(91,'2','9','199',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(92,'2','9','200',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(93,'2','9','201',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(94,'2','9','202',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(95,'2','9','203',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(96,'3','1',NULL,1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(97,'3','2',NULL,1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(98,'3','2','101',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(99,'3','2','102',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(100,'3','2','103',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(101,'3','2','104',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(102,'3','4',NULL,1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(103,'4','1',NULL,1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(104,'4','2',NULL,1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(105,'4','2','101',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(106,'4','2','102',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(107,'4','2','103',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(108,'4','2','104',1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(109,'4','5',NULL,1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(110,'4','5','121',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(111,'4','5','122',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(112,'5','1',NULL,1,0,0,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(113,'5','7',NULL,1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(114,'5','7','151',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(115,'5','7','152',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(116,'5','7','153',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(117,'5','7','154',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(118,'5','7','155',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(119,'5','7','156',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(120,'5','7','157',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(121,'5','7','158',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(122,'5','7','159',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(123,'5','7','160',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(124,'5','7','161',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(125,'5','7','162',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(126,'5','7','163',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(127,'5','7','164',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(128,'5','8',NULL,1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(129,'5','8','171',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(130,'5','8','172',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(131,'5','8','173',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(132,'5','8','174',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(133,'5','8','175',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(134,'5','8','176',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(135,'5','8','177',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(136,'5','8','178',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(137,'5','8','179',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(138,'5','8','180',1,1,1,0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(45) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_roles_role_name` (`role_name`),
  KEY `ix_roles_id` (`id`),
  KEY `ix_roles_company_id` (`company_id`),
  KEY `ix_roles_status` (`status`),
  KEY `ix_roles_created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Admin','Full access to every module, including Master Data and HRM.','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Front Office Manager','Reservations, night audit, guest enquiry and reporting.','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Front Desk','Day-to-day reservations: book, check in, take payment, check out.','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Housekeeping','Room status, task assignment and incident logging.','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Food & Beverage','Restaurant and bar: menu, orders, kitchen and billing.','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shift`
--

DROP TABLE IF EXISTS `shift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shift` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Shift_Name` varchar(100) NOT NULL,
  `Start_Time` varchar(20) NOT NULL,
  `End_Time` varchar(20) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_shift_company_id` (`company_id`),
  KEY `ix_shift_id` (`id`),
  KEY `ix_shift_updated_by` (`updated_by`),
  KEY `ix_shift_status` (`status`),
  KEY `ix_shift_created_by` (`created_by`),
  KEY `ix_shift_Shift_Name` (`Shift_Name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shift`
--

LOCK TABLES `shift` WRITE;
/*!40000 ALTER TABLE `shift` DISABLE KEYS */;
INSERT INTO `shift` VALUES (1,'Morning','06:00','14:00','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Evening','14:00','22:00','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Night','22:00','06:00','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'General','09:00','18:00','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `shift` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `submenus`
--

DROP TABLE IF EXISTS `submenus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `submenus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `menu_id` varchar(100) NOT NULL,
  `submenu_name` varchar(100) NOT NULL,
  `submenu_link` varchar(255) NOT NULL,
  `order` int NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_submenus_status` (`status`),
  KEY `ix_submenus_menu_id` (`menu_id`),
  KEY `ix_submenus_updated_by` (`updated_by`),
  KEY `ix_submenus_id` (`id`),
  KEY `ix_submenus_created_by` (`created_by`),
  KEY `ix_submenus_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=204 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `submenus`
--

LOCK TABLES `submenus` WRITE;
/*!40000 ALTER TABLE `submenus` DISABLE KEYS */;
INSERT INTO `submenus` VALUES (101,'2','Add New Reservation','/add_new_reservation',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(102,'2','Booking','/booking',2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(103,'2','Room View','/room_view',3,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(104,'2','Reservation View','/reservation_view',4,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(111,'3','Night Audit','/night_audit',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(112,'3','User Reserved Details','/user_reserved_details',2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(113,'3','Room Booked Details','/room_booked_details',3,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(114,'3','Settlement Summary','/settlement_summary',4,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(121,'5','Task Assign','/task_assign',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(122,'5','Room Incident Log','/room_incident_log',2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(131,'6','Employee','/employee',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(132,'6','User','/user',2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(133,'6','Roles','/roles',3,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(134,'6','Department','/department',4,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(135,'6','Designation','/designation',5,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(136,'6','Shift','/shift',6,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(137,'6','Restaurant Roster','/restaurant_roster',7,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(138,'6','Restaurant Shift Planning','/restaurant_shift_planning',8,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(139,'6','Bar Roster','/bar_roster',9,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(140,'6','Bar Shift Planning','/bar_shift_planning',10,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(151,'7','Menu Management','/menus',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(152,'7','Combo / Package Deals','/combo_deals',2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(153,'7','Floor Layout','/floor_layout',3,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(154,'7','Table Master','/table_master',4,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(155,'7','Order Management','/orders',5,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(156,'7','Table Reservation','/table_reservation',6,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(157,'7','Main Kitchen','/kot/main_kitchen',7,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(158,'7','Grill Kitchen','/kot/grill',8,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(159,'7','Dessert Kitchen','/kot/dessert',9,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(160,'7','Billing & Payments','/billing_payments',10,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(161,'7','Inventory Control','/stock',11,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(162,'7','Recipe Management','/recipe_management',12,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(163,'7','Guest Management','/guest_management',13,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(164,'7','Report & Analytics','/reports_analytics',14,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(171,'8','Menu Management','/bar_menus',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(172,'8','Floor Layout','/bar_floor_layout',2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(173,'8','Table Master','/bar_table_master',3,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(174,'8','Order Management','/bar_orders',4,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(175,'8','Station Display','/bar_station',5,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(176,'8','Billing & Payments','/bar_billing_payments',6,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(177,'8','Stock','/bar_stock',7,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(178,'8','Recipe Management','/bar_recipe_management',8,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(179,'8','Guest Management','/bar_guest_management',9,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(180,'8','Report & Analytics','/bar_reports_analytics',10,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(191,'9','Facilities','/facilities',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(192,'9','Room Type','/room_type',2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(193,'9','Bed Type','/bed_type',3,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(194,'9','Hall / Floor','/hall_floor',4,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(195,'9','Rooms','/rooms',5,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(196,'9','Discount Type','/discount_type',6,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(197,'9','Tax Types','/tax_types',7,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(198,'9','Payment Methods','/payment_methods',8,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(199,'9','Identification Proof','/identification_proof',9,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(200,'9','Currency & Country','/currency_country',10,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(201,'9','HSK Task Type','/hsk_task_type',11,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(202,'9','Complementary','/complementary',12,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(203,'9','Reservation Status','/reservation_status',13,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `submenus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `User_Code` varchar(100) NOT NULL,
  `Photo` varchar(255) DEFAULT NULL,
  `username` varchar(100) NOT NULL,
  `First_Name` varchar(100) NOT NULL,
  `Last_Name` varchar(100) NOT NULL,
  `Personal_Email` varchar(100) NOT NULL,
  `Company_Email` varchar(100) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `Mobile` varchar(20) NOT NULL,
  `Alternative_Mobile` varchar(20) DEFAULT NULL,
  `D_O_B` varchar(20) NOT NULL,
  `Gender` varchar(20) NOT NULL,
  `Marital_Status` varchar(50) NOT NULL,
  `Address` varchar(255) NOT NULL,
  `City` varchar(100) NOT NULL,
  `State` varchar(100) NOT NULL,
  `Postal_Code` varchar(20) NOT NULL,
  `Country` varchar(100) NOT NULL,
  `Department_ID` varchar(100) NOT NULL,
  `Designation_ID` varchar(100) NOT NULL,
  `Role_ID` varchar(100) NOT NULL,
  `Shift_ID` varchar(100) NOT NULL,
  `Date_Of_Joining` varchar(20) NOT NULL,
  `Experience` varchar(50) NOT NULL,
  `Salary_Details` varchar(100) NOT NULL,
  `Register_Code` varchar(100) NOT NULL,
  `Emergency_Name` varchar(100) NOT NULL,
  `Emergency_Contact` varchar(20) NOT NULL,
  `Emergency_Relationship` varchar(50) NOT NULL,
  `Acknowledgment_of_Hotel_Policies` tinyint(1) DEFAULT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_Company_Email` (`Company_Email`),
  UNIQUE KEY `ix_users_User_Code` (`User_Code`),
  KEY `ix_users_Mobile` (`Mobile`),
  KEY `ix_users_Designation_ID` (`Designation_ID`),
  KEY `ix_users_updated_by` (`updated_by`),
  KEY `ix_users_Register_Code` (`Register_Code`),
  KEY `ix_users_First_Name` (`First_Name`),
  KEY `ix_users_company_id` (`company_id`),
  KEY `ix_users_Personal_Email` (`Personal_Email`),
  KEY `ix_users_Emergency_Name` (`Emergency_Name`),
  KEY `ix_users_Last_Name` (`Last_Name`),
  KEY `ix_users_D_O_B` (`D_O_B`),
  KEY `ix_users_Emergency_Contact` (`Emergency_Contact`),
  KEY `ix_users_Role_ID` (`Role_ID`),
  KEY `ix_users_Country` (`Country`),
  KEY `ix_users_Gender` (`Gender`),
  KEY `ix_users_Postal_Code` (`Postal_Code`),
  KEY `ix_users_Shift_ID` (`Shift_ID`),
  KEY `ix_users_Emergency_Relationship` (`Emergency_Relationship`),
  KEY `ix_users_Date_Of_Joining` (`Date_Of_Joining`),
  KEY `ix_users_Marital_Status` (`Marital_Status`),
  KEY `ix_users_State` (`State`),
  KEY `ix_users_status` (`status`),
  KEY `ix_users_City` (`City`),
  KEY `ix_users_id` (`id`),
  KEY `ix_users_Experience` (`Experience`),
  KEY `ix_users_Department_ID` (`Department_ID`),
  KEY `ix_users_created_by` (`created_by`),
  KEY `ix_users_Salary_Details` (`Salary_Details`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'EMP001','/templates/static/users/user_3046ca43684242709d820c63be6ecead.png','admin','Aarav','Sharma','admin@gmail.com','admin@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100001','','1981-02-11','Male','Single','11 Anna Salai','Chennai','Tamil Nadu','600002','India','1','1','1','4','2025-08-17','2 years','28500','REG1001','Sharma Family','9840110001','Parent',1,'ACTIVE','1','2025-08-17 09:00:00',NULL,NULL,'1'),(2,'EMP002','/templates/static/users/user_1e872fc3786e441aa8a98780a4d7d630.png','priya.menon','Priya','Menon','priya.menon@gmail.com','priya.menon@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100002','','1982-03-12','Female','Single','12 Anna Salai','Chennai','Tamil Nadu','600002','India','1','2','2','4','2025-09-06','3 years','32000','REG1002','Menon Family','9840110002','Parent',1,'ACTIVE','1','2025-09-06 09:00:00',NULL,NULL,'1'),(3,'EMP003','/templates/static/users/user_235a1327a9ac4b70bfac77b427a4748d.png','rahul.nair','Rahul','Nair','rahul.nair@gmail.com','rahul.nair@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100003','','1983-04-13','Male','Married','13 Anna Salai','Chennai','Tamil Nadu','600002','India','1','3','3','1','2025-09-26','4 years','35500','REG1003','Nair Family','9840110003','Spouse',1,'ACTIVE','1','2025-09-26 09:00:00',NULL,NULL,'1'),(4,'EMP004','/templates/static/users/user_427626ebffe9471fb18ad8921f6a7db8.png','divya.rao','Divya','Rao','divya.rao@gmail.com','divya.rao@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100004','','1984-05-14','Female','Single','14 Anna Salai','Chennai','Tamil Nadu','600002','India','1','4','3','2','2025-10-16','5 years','39000','REG1004','Rao Family','9840110004','Parent',1,'ACTIVE','1','2025-10-16 09:00:00',NULL,NULL,'1'),(5,'EMP005','/templates/static/users/user_838cd7dab5314cad8bf853f8dd4cd929.png','imran.khan','Imran','Khan','imran.khan@gmail.com','imran.khan@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100005','','1985-06-15','Male','Single','15 Anna Salai','Chennai','Tamil Nadu','600002','India','2','5','4','1','2025-11-05','6 years','42500','REG1005','Khan Family','9840110005','Parent',1,'ACTIVE','1','2025-11-05 09:00:00',NULL,NULL,'1'),(6,'EMP006','/templates/static/users/user_842b6d6e59f5468b825c5c2b2f645ec3.png','lakshmi.iyer','Lakshmi','Iyer','lakshmi.iyer@gmail.com','lakshmi.iyer@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100006','','1986-07-16','Female','Married','16 Anna Salai','Chennai','Tamil Nadu','600002','India','2','6','4','2','2025-11-25','7 years','46000','REG1006','Iyer Family','9840110006','Spouse',1,'ACTIVE','1','2025-11-25 09:00:00',NULL,NULL,'1'),(7,'EMP007','/templates/static/users/user_ec96133e55f94e46943e2cd9fdad405d.png','vikram.singh','Vikram','Singh','vikram.singh@gmail.com','vikram.singh@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100007','','1987-08-17','Male','Single','17 Anna Salai','Chennai','Tamil Nadu','600002','India','3','7','5','2','2025-12-15','8 years','49500','REG1007','Singh Family','9840110007','Parent',1,'ACTIVE','1','2025-12-15 09:00:00',NULL,NULL,'1'),(8,'EMP008','/templates/static/users/user_891b6ccfc2814d97b7cd67eaa6b8982c.png','sunita.patel','Sunita','Patel','sunita.patel@gmail.com','sunita.patel@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100008','','1988-09-18','Female','Single','18 Anna Salai','Chennai','Tamil Nadu','600002','India','4','8','5','1','2026-01-04','9 years','53000','REG1008','Patel Family','9840110008','Parent',1,'ACTIVE','1','2026-01-04 09:00:00',NULL,NULL,'1'),(9,'EMP009','/templates/static/users/user_e4a1b633d60648218a4b76bd380b6136.png','joseph.dsouza','Joseph','D\'Souza','joseph.dsouza@gmail.com','joseph.dsouza@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100009','','1989-01-10','Male','Married','19 Anna Salai','Chennai','Tamil Nadu','600002','India','3','9','5','2','2026-01-24','1 years','56500','REG1009','D\'Souza Family','9840110009','Spouse',1,'ACTIVE','1','2026-01-24 09:00:00',NULL,NULL,'1'),(10,'EMP010','/templates/static/users/user_5ea4a7716769473196272c6e3ee424af.png','meera.krishnan','Meera','Krishnan','meera.krishnan@gmail.com','meera.krishnan@cherryhotel.com','$2b$12$O8OEdcfx5v3eonjmEuolfOOgIDdib/gtt.Jqh5LTVWo6Al1K/S1KC','9840100010','','1990-02-11','Female','Single','20 Anna Salai','Chennai','Tamil Nadu','600002','India','6','10','2','4','2026-02-13','2 years','60000','REG1010','Krishnan Family','9840110010','Parent',1,'ACTIVE','1','2026-02-13 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'hotelerp_users'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-01 20:55:00
