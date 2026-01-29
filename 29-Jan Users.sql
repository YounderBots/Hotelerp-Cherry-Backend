CREATE DATABASE  IF NOT EXISTS `hotelerp_users` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `hotelerp_users`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: hotelerp_users
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'Luxury Swimming Pool','INACTIVE','1','2026-01-29 14:04:31','2026-01-29 14:05:09','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `designation`
--

LOCK TABLES `designation` WRITE;
/*!40000 ALTER TABLE `designation` DISABLE KEYS */;
INSERT INTO `designation` VALUES (1,'Luxury Swimming Pool','INACTIVE','1','2026-01-29 14:05:44','2026-01-29 14:06:31','1','1');
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
INSERT INTO `menus` VALUES (1,'Dashboard','/dashboard','dashboard',1,'ACTIVE','1','2026-01-22 12:27:52',NULL,NULL,'1'),(2,'Reservation','/reservation','reservation',2,'ACTIVE','1','2026-01-22 12:42:04',NULL,NULL,'1'),(3,'Night Audit','','night-auditing',3,'ACTIVE','1','2026-01-22 12:42:38',NULL,NULL,'1'),(4,'Guest Enquiry','/guest_enquiry','guest-enquiry',4,'ACTIVE','1','2026-01-22 12:47:40',NULL,NULL,'1'),(5,'House Keeper','','house-keeper',5,'ACTIVE','1','2026-01-22 14:03:08',NULL,NULL,'1'),(6,'HRM','','hrm',6,'ACTIVE','1','2026-01-22 14:03:55',NULL,NULL,'1'),(7,'Restaurant','','restaurant',7,'ACTIVE','1','2026-01-22 14:05:07',NULL,NULL,'1'),(8,'Master Data','','master-data',8,'ACTIVE','1','2026-01-22 14:05:44',NULL,NULL,'1'),(9,'MasterData','/masters','settings',5,'INACTIVE','1','2026-01-29 15:50:39','2026-01-29 15:58:00','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
INSERT INTO `role_permissions` VALUES (1,'1','1',NULL,1,1,1,1,'ACTIVE','1','2026-01-23 15:11:04','2026-01-29 15:46:45','1','1'),(2,'1','2',NULL,1,1,1,1,'ACTIVE','1','2026-01-23 15:13:56',NULL,NULL,'1'),(3,'1','2','1',1,1,1,1,'ACTIVE','1','2026-01-23 15:14:13',NULL,NULL,'1'),(4,'1','2','2',1,1,1,1,'ACTIVE','1','2026-01-23 15:15:09',NULL,NULL,'1'),(5,'1','2','3',1,1,1,1,'ACTIVE','1','2026-01-23 15:15:17',NULL,NULL,'1'),(6,'1','2','4',1,1,1,1,'ACTIVE','1','2026-01-23 15:15:25',NULL,NULL,'1'),(7,'1','3',NULL,1,1,1,1,'ACTIVE','1','2026-01-23 15:16:13',NULL,NULL,'1'),(8,'1','3','5',1,1,1,1,'ACTIVE','1','2026-01-23 15:16:30',NULL,NULL,'1'),(9,'1','3','6',1,1,1,1,'ACTIVE','1','2026-01-23 15:16:42',NULL,NULL,'1'),(10,'1','3','7',1,1,1,1,'ACTIVE','1','2026-01-23 15:16:49',NULL,NULL,'1'),(11,'1','4',NULL,1,1,1,1,'ACTIVE','1','2026-01-23 15:21:16',NULL,NULL,'1'),(12,'1','5',NULL,1,1,1,1,'ACTIVE','1','2026-01-23 15:22:10',NULL,NULL,'1'),(13,'1','5','8',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:34',NULL,NULL,'1'),(14,'1','5','9',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(15,'1','6',NULL,1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(16,'1','6','32',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(17,'1','6','33',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(18,'1','7','10',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(19,'1','7','11',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(20,'1','7','12',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(21,'1','7','13',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(22,'1','7','14',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(23,'1','7','15',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(24,'1','7','16',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(25,'1','7','17',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(26,'1','7','18',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(27,'1','8','19',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(28,'1','8','20',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(29,'1','8','21',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(30,'1','8','22',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(31,'1','8','23',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(32,'1','8','24',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(33,'1','8','25',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(34,'1','8','26',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(35,'1','8','27',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(36,'1','8','28',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(37,'1','8','29',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(38,'1','8','30',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(39,'1','8','31',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(40,'1','8','34',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(41,'1','8','35',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(42,'1','7','36',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(43,'1','7','37',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(44,'1','7','38',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(45,'1','7','39',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(46,'1','7','40',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(47,'1','6','43',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(48,'1','6','34',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(49,'1','6','35',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1'),(50,'1','6','44',1,1,1,1,'ACTIVE','1','2026-01-23 15:22:43',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Admin','Full system access','ACTIVE','1','2026-01-22 12:22:54',NULL,NULL,'1'),(2,'Front Office','Handles reservations and check-in','ACTIVE','1','2026-01-22 12:23:02',NULL,NULL,'1'),(3,'House Keeping','Room cleaning and maintenance tasks','ACTIVE','1','2026-01-22 12:23:10',NULL,NULL,'1'),(4,'Front Office Manager','Manages front office operations','INACTIVE','1','2026-01-29 14:27:00','2026-01-29 15:30:57','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shift`
--

LOCK TABLES `shift` WRITE;
/*!40000 ALTER TABLE `shift` DISABLE KEYS */;
INSERT INTO `shift` VALUES (1,'Evening Shift','16:00','00:00','INACTIVE','1','2026-01-29 16:27:05','2026-01-29 16:49:09','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `submenus`
--

LOCK TABLES `submenus` WRITE;
/*!40000 ALTER TABLE `submenus` DISABLE KEYS */;
INSERT INTO `submenus` VALUES (1,'2','Add New Reservation','/add_new_reservation',1,'ACTIVE','1','2026-01-22 14:09:06',NULL,NULL,'1'),(2,'2','Booking','/booking',2,'ACTIVE','1','2026-01-22 14:09:19',NULL,NULL,'1'),(3,'2','Room View','/room_view',3,'ACTIVE','1','2026-01-22 14:10:45',NULL,NULL,'1'),(4,'2','Reservation View','/reservation_view',4,'ACTIVE','1','2026-01-22 14:10:57',NULL,NULL,'1'),(5,'3','User Reserved Details','/user_reserved_details',1,'ACTIVE','1','2026-01-22 14:11:08',NULL,NULL,'1'),(6,'3','Room Booked Details','/room_booked_details',2,'ACTIVE','1','2026-01-22 14:11:14',NULL,NULL,'1'),(7,'3','Settlement Summary','/settlement_summary',3,'ACTIVE','1','2026-01-22 14:11:19',NULL,NULL,'1'),(8,'5','Task Assign','/task_assign',1,'ACTIVE','1','2026-01-22 14:11:25',NULL,NULL,'1'),(9,'5','Room Incident Log','/room_incident_log',2,'ACTIVE','1','2026-01-22 14:11:30',NULL,NULL,'1'),(10,'7','Floor Layout','/floor_layout',1,'ACTIVE','1','2026-01-22 14:11:34',NULL,NULL,'1'),(11,'7','Table Master','/table_master',2,'ACTIVE','1','2026-01-22 14:11:39',NULL,NULL,'1'),(12,'7','Order Management','/orders',3,'ACTIVE','1','2026-01-22 14:11:45',NULL,NULL,'1'),(13,'7','Table Reservation','/table_reservation',4,'ACTIVE','1','2026-01-22 14:11:52',NULL,NULL,'1'),(14,'7','Menu Management','/menus',5,'ACTIVE','1','2026-01-22 14:11:58',NULL,NULL,'1'),(15,'7','Main Kitchen','/kot/main_kitchen',6,'ACTIVE','1','2026-01-22 14:12:11',NULL,NULL,'1'),(16,'7','Grill Kitchen','/kot/grill',7,'ACTIVE','1','2026-01-22 14:12:18',NULL,NULL,'1'),(17,'7','Dessert Kitchen','/kot/dessert',8,'ACTIVE','1','2026-01-22 14:12:48',NULL,NULL,'1'),(18,'7','Bar Kitchen','/kot/bar',9,'ACTIVE','1','2026-01-22 14:13:02',NULL,NULL,'1'),(19,'8','Facilities','/facilities',1,'ACTIVE','1','2026-01-22 14:13:16',NULL,NULL,'1'),(20,'8','Room Type','/room_type',2,'ACTIVE','1','2026-01-22 14:13:21',NULL,NULL,'1'),(21,'8','Bed Type','/bed_type',3,'ACTIVE','1','2026-01-22 14:13:58',NULL,NULL,'1'),(22,'8','Hall / Floor','/hall_floor',4,'ACTIVE','1','2026-01-22 14:14:04',NULL,NULL,'1'),(23,'8','Rooms','/rooms',5,'ACTIVE','1','2026-01-22 14:14:11',NULL,NULL,'1'),(24,'8','Discount Type','/discount_type',6,'ACTIVE','1','2026-01-22 14:14:19',NULL,NULL,'1'),(25,'8','Tax Types','/tax_types',7,'ACTIVE','1','2026-01-22 14:14:29',NULL,NULL,'1'),(26,'8','Payment Methods','/payment_methods',8,'ACTIVE','1','2026-01-22 14:14:37',NULL,NULL,'1'),(27,'8','Identification Proof','/identification_proof',9,'ACTIVE','1','2026-01-22 14:14:44',NULL,NULL,'1'),(28,'8','Currency & Country','/currency_country',10,'ACTIVE','1','2026-01-22 14:14:51',NULL,NULL,'1'),(29,'8','HSK Task Type','/hsk_task_type',11,'ACTIVE','1','2026-01-22 14:15:00',NULL,NULL,'1'),(30,'8','Complementary','/complementary',12,'ACTIVE','1','2026-01-22 14:15:11',NULL,NULL,'1'),(31,'8','Reservation Status','/reservation_status',13,'ACTIVE','1','2026-01-22 14:15:17',NULL,NULL,'1'),(32,'6','Employee','/employee',1,'ACTIVE','1','2026-01-23 15:43:38',NULL,NULL,'1'),(33,'6','User','/user',2,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(34,'6','Department','/department',4,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(35,'6','Designation','/designation',5,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(36,'7','Billing & Payments','/billing_payments',10,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(37,'7','Inventory Control','/stock',11,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(38,'7','Recipe Management','/recipe_management',12,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(39,'7','Staff Master','/staff_master',13,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(40,'7','Staff Planning','/staff_planning',14,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(41,'7','Guest Management','/guest_management',15,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(42,'7','Report & Analytics','/reports_analytics',16,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(43,'6','Roles','/roles',3,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(44,'6','Shift','/shift',6,'ACTIVE','1','2026-01-23 15:44:53',NULL,NULL,'1'),(52,'2','Roles','/master/roles',10,'INACTIVE','1','2026-01-29 16:14:51','2026-01-29 16:24:31','1','1');
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
  `Designation_ID` varchar(45) NOT NULL,
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
  UNIQUE KEY `ix_users_Company_Email` (`Company_Email`),
  UNIQUE KEY `ix_users_User_Code` (`User_Code`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `ix_users_Role_ID` (`Role_ID`),
  KEY `ix_users_First_Name` (`First_Name`),
  KEY `ix_users_Emergency_Relationship` (`Emergency_Relationship`),
  KEY `ix_users_Last_Name` (`Last_Name`),
  KEY `ix_users_status` (`status`),
  KEY `ix_users_Emergency_Contact` (`Emergency_Contact`),
  KEY `ix_users_Personal_Email` (`Personal_Email`),
  KEY `ix_users_Experience` (`Experience`),
  KEY `ix_users_created_by` (`created_by`),
  KEY `ix_users_Mobile` (`Mobile`),
  KEY `ix_users_Salary_Details` (`Salary_Details`),
  KEY `ix_users_D_O_B` (`D_O_B`),
  KEY `ix_users_Postal_Code` (`Postal_Code`),
  KEY `ix_users_updated_by` (`updated_by`),
  KEY `ix_users_id` (`id`),
  KEY `ix_users_Gender` (`Gender`),
  KEY `ix_users_Register_Code` (`Register_Code`),
  KEY `ix_users_Marital_Status` (`Marital_Status`),
  KEY `ix_users_company_id` (`company_id`),
  KEY `ix_users_State` (`State`),
  KEY `ix_users_Emergency_Name` (`Emergency_Name`),
  KEY `ix_users_City` (`City`),
  KEY `ix_users_Shift_ID` (`Shift_ID`),
  KEY `ix_users_Country` (`Country`),
  KEY `ix_users_Department_ID` (`Department_ID`),
  KEY `ix_users_Date_Of_Joining` (`Date_Of_Joining`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'EMP-335E08D0',NULL,'admin','System','Admin','admin.personal@gmail.com','admin@hotel.com','$2b$12$1aE0FG/A2xN6hKdKyhPSae1LqC5AFMHFYmE3TOAK1FutvBU1Gs5XW','9000000001',NULL,'1990-01-01','Male','Married','Head Office','Chennai','Tamil Nadu','600001','India','1','1','1','1','2020-01-01','10 Years','100000','REG001','Admin Spouse','9000000002','Wife',0,'ACTIVE','SYSTEM','2026-01-22 12:15:33',NULL,NULL,'1'),(2,'EMP-A513FF1C',NULL,'frontdesk','Front','Office','front.personal@gmail.com','frontoffice@hotel.com','$2b$12$DpiBnd2TSDDuIBAF/JwsLuSeSdLJpE9vza5JKPahfDJ.vR06RJFvy','9000000011',NULL,'1996-05-15','Female','Single','Reception Area','Coimbatore','Tamil Nadu','641001','India','2','2','2','2','2023-06-01','2 Years','30000','REG002','Father','9000000012','Father',0,'ACTIVE','ADMIN','2026-01-22 12:15:40',NULL,NULL,'1'),(3,'EMP-69ADB91A','templates/static/users\\user_a04aad1fd784433c870c78cce7543dd2.jpeg','john.doe','John','Doe','john.personal@gmail.com','john.updated@hotel.com','$2b$12$fbT38UQAItbgqxqx3LlNF.Ql3RL8PuOwLW5vehVi0r48okJmHAO62','9998887776','9123456780','1995-06-15','Male','Single','123, MG Road','Bangalore','Karnataka','560001','India','2','3','4','2','2024-01-10','4 Years','40000','REG-1001','Jane Doe','9988776655','Wife',1,'INACTIVE','1','2026-01-29 17:09:33','2026-01-29 17:42:22','1','1');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'hotelerp_users'
--

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

-- Dump completed on 2026-01-29 18:02:55
