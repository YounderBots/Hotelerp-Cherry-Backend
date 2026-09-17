-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: hotelerp_bar
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
-- Current Database: `hotelerp_bar`
--

/*!40000 DROP DATABASE IF EXISTS `hotelerp_bar`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hotelerp_bar` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hotelerp_bar`;

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
INSERT INTO `alembic_version` VALUES ('7f2a8c6d1e45');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_bill`
--

DROP TABLE IF EXISTS `bar_bill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_bill` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_number` varchar(100) NOT NULL,
  `bill_date` date NOT NULL,
  `bill_time` time NOT NULL,
  `order_id` int NOT NULL,
  `order_number` varchar(100) NOT NULL,
  `table_id` int DEFAULT NULL,
  `table_code` varchar(100) DEFAULT NULL,
  `guest_id` int DEFAULT NULL,
  `guest_name` varchar(100) DEFAULT NULL,
  `guest_mobile` varchar(20) DEFAULT NULL,
  `sub_total` decimal(12,2) DEFAULT NULL,
  `cgst_percentage` decimal(6,3) DEFAULT NULL,
  `cgst_amount` decimal(12,2) DEFAULT NULL,
  `sgst_percentage` decimal(6,3) DEFAULT NULL,
  `sgst_amount` decimal(12,2) DEFAULT NULL,
  `service_charge_percentage` decimal(6,3) DEFAULT NULL,
  `service_charge_amount` decimal(12,2) DEFAULT NULL,
  `discount_type` enum('Percentage','Flat') DEFAULT NULL,
  `discount_value` decimal(12,2) DEFAULT NULL,
  `discount_amount` decimal(12,2) DEFAULT NULL,
  `round_off` decimal(12,2) DEFAULT NULL,
  `grand_total` decimal(12,2) NOT NULL,
  `bill_status` enum('Open','Paid','Cancelled') NOT NULL,
  `payment_status` enum('Pending','Partial','Paid') NOT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_bill_number` (`company_id`,`branch_id`,`bill_number`),
  UNIQUE KEY `ix_bar_bill_token` (`token`),
  KEY `ix_bar_bill_id` (`id`),
  KEY `ix_bar_bill_branch_id` (`branch_id`),
  KEY `ix_bar_bill_status` (`status`),
  KEY `ix_bar_bill_bill_number` (`bill_number`),
  KEY `ix_bar_bill_guest_id` (`guest_id`),
  KEY `ix_bar_bill_order_id` (`order_id`),
  KEY `ix_bar_bill_table_id` (`table_id`),
  KEY `ix_bar_bill_payment_status` (`payment_status`),
  KEY `ix_bar_bill_table_code` (`table_code`),
  KEY `ix_bar_bill_guest_mobile` (`guest_mobile`),
  KEY `ix_bar_bill_company_id` (`company_id`),
  KEY `ix_bar_bill_order_number` (`order_number`),
  KEY `ix_bar_bill_bill_date` (`bill_date`),
  KEY `ix_bar_bill_bill_status` (`bill_status`),
  CONSTRAINT `bar_bill_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `bar_order` (`id`),
  CONSTRAINT `bar_bill_ibfk_2` FOREIGN KEY (`table_id`) REFERENCES `bar_table` (`id`),
  CONSTRAINT `bar_bill_ibfk_3` FOREIGN KEY (`guest_id`) REFERENCES `bar_guest` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_bill`
--

LOCK TABLES `bar_bill` WRITE;
/*!40000 ALTER TABLE `bar_bill` DISABLE KEYS */;
INSERT INTO `bar_bill` VALUES (1,'BB-20260916-001','2026-09-16','13:55:00',1,'BO-20260916-001',4,'BF-MAIN-T04',NULL,NULL,NULL,4970.00,2.500,136.68,2.500,136.67,10.000,497.00,NULL,0.00,0.00,0.00,5740.35,'Paid','Paid',NULL,'c29f127a-fbd1-4929-b68f-9aa6052e185f','ACTIVE','1','2026-09-16 13:55:00',NULL,NULL,'1','1'),(2,'BB-20260915-002','2026-09-15','14:55:00',2,'BO-20260915-002',7,'BF-LNG-T01',NULL,NULL,NULL,4110.00,2.500,113.03,2.500,113.02,10.000,411.00,NULL,0.00,0.00,0.00,4747.05,'Paid','Paid',NULL,'e96c877a-d36e-477a-a755-d9c595aac670','ACTIVE','1','2026-09-15 14:55:00',NULL,NULL,'1','1'),(3,'BB-20260917-003','2026-09-17','15:55:00',3,'BO-20260917-003',10,'BF-LNG-T04',NULL,NULL,NULL,2070.00,2.500,56.93,2.500,56.92,10.000,207.00,NULL,0.00,0.00,0.00,2390.85,'Paid','Paid',NULL,'56adf5b5-d630-4b16-8c20-611883c9334c','ACTIVE','1','2026-09-17 15:55:00',NULL,NULL,'1','1'),(4,'BB-20260916-004','2026-09-16','16:55:00',4,'BO-20260916-004',3,'BF-MAIN-T03',NULL,NULL,NULL,3870.00,2.500,106.43,2.500,106.42,10.000,387.00,NULL,0.00,0.00,0.00,4469.85,'Paid','Paid',NULL,'79bbfbc3-386b-4b10-aadc-234b97a6d50f','ACTIVE','1','2026-09-16 16:55:00',NULL,NULL,'1','1'),(5,'BB-20260915-005','2026-09-15','17:55:00',5,'BO-20260915-005',6,'BF-MAIN-T06',NULL,NULL,NULL,3100.00,2.500,85.25,2.500,85.25,10.000,310.00,NULL,0.00,0.00,0.00,3580.50,'Paid','Paid',NULL,'7b847489-dfce-4c29-ab39-c0ca1318fc32','ACTIVE','1','2026-09-15 17:55:00',NULL,NULL,'1','1'),(6,'BB-20260917-006','2026-09-17','18:55:00',6,'BO-20260917-006',9,'BF-LNG-T03',NULL,NULL,NULL,3080.00,2.500,84.70,2.500,84.70,10.000,308.00,NULL,0.00,0.00,0.00,3557.40,'Paid','Paid',NULL,'35041567-dac4-42ff-9217-3a024ce450fc','ACTIVE','1','2026-09-17 18:55:00',NULL,NULL,'1','1'),(7,'BB-20260916-007','2026-09-16','19:55:00',7,'BO-20260916-007',2,'BF-MAIN-T02',NULL,NULL,NULL,2820.00,2.500,77.55,2.500,77.55,10.000,282.00,NULL,0.00,0.00,0.00,3257.10,'Paid','Paid',NULL,'675245d7-4d71-493d-a18f-a4f93a22140e','ACTIVE','1','2026-09-16 19:55:00',NULL,NULL,'1','1'),(8,'BB-20260915-008','2026-09-15','12:55:00',8,'BO-20260915-008',5,'BF-MAIN-T05',NULL,NULL,NULL,4550.00,2.500,125.13,2.500,125.12,10.000,455.00,NULL,0.00,0.00,0.00,5255.25,'Paid','Paid',NULL,'dad4d91a-d590-419a-a0ed-6a8aa58eb106','ACTIVE','1','2026-09-15 12:55:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_bill` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_bill_item`
--

DROP TABLE IF EXISTS `bar_bill_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_bill_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_id` int NOT NULL,
  `order_item_id` int NOT NULL,
  `menu_id` int NOT NULL,
  `item_name` varchar(150) NOT NULL,
  `quantity` int NOT NULL,
  `rate` decimal(12,2) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `tax_amount` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_bill_item_branch_id` (`branch_id`),
  KEY `ix_bar_bill_item_id` (`id`),
  KEY `ix_bar_bill_item_bill_id` (`bill_id`),
  KEY `ix_bar_bill_item_company_id` (`company_id`),
  KEY `ix_bar_bill_item_order_item_id` (`order_item_id`),
  KEY `ix_bar_bill_item_menu_id` (`menu_id`),
  KEY `ix_bar_bill_item_status` (`status`),
  CONSTRAINT `bar_bill_item_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `bar_bill` (`id`),
  CONSTRAINT `bar_bill_item_ibfk_2` FOREIGN KEY (`order_item_id`) REFERENCES `bar_order_item` (`id`),
  CONSTRAINT `bar_bill_item_ibfk_3` FOREIGN KEY (`menu_id`) REFERENCES `bar_menu_item` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_bill_item`
--

LOCK TABLES `bar_bill_item` WRITE;
/*!40000 ALTER TABLE `bar_bill_item` DISABLE KEYS */;
INSERT INTO `bar_bill_item` VALUES (1,1,1,13,'Negroni',3,640.00,1920.00,NULL,'ACTIVE','1','2026-09-16 13:55:00',NULL,NULL,'1','1'),(2,1,2,1,'Single Malt 12 Yr (30ml)',3,650.00,1950.00,NULL,'ACTIVE','1','2026-09-16 13:55:00',NULL,NULL,'1','1'),(3,1,3,3,'Premium Vodka (30ml)',2,340.00,680.00,NULL,'ACTIVE','1','2026-09-16 13:55:00',NULL,NULL,'1','1'),(4,1,4,8,'Craft IPA Pint',1,420.00,420.00,NULL,'ACTIVE','1','2026-09-16 13:55:00',NULL,NULL,'1','1'),(5,2,5,1,'Single Malt 12 Yr (30ml)',1,650.00,650.00,NULL,'ACTIVE','1','2026-09-15 14:55:00',NULL,NULL,'1','1'),(6,2,6,3,'Premium Vodka (30ml)',3,340.00,1020.00,NULL,'ACTIVE','1','2026-09-15 14:55:00',NULL,NULL,'1','1'),(7,2,7,13,'Negroni',1,640.00,640.00,NULL,'ACTIVE','1','2026-09-15 14:55:00',NULL,NULL,'1','1'),(8,2,8,8,'Craft IPA Pint',2,420.00,840.00,NULL,'ACTIVE','1','2026-09-15 14:55:00',NULL,NULL,'1','1'),(9,2,9,6,'Lager Pint',3,320.00,960.00,NULL,'ACTIVE','1','2026-09-15 14:55:00',NULL,NULL,'1','1'),(10,3,10,9,'House Red (Glass)',1,450.00,450.00,NULL,'ACTIVE','1','2026-09-17 15:55:00',NULL,NULL,'1','1'),(11,3,11,18,'Fresh Lime Soda',1,180.00,180.00,NULL,'ACTIVE','1','2026-09-17 15:55:00',NULL,NULL,'1','1'),(12,3,12,14,'Mojito',3,480.00,1440.00,NULL,'ACTIVE','1','2026-09-17 15:55:00',NULL,NULL,'1','1'),(13,4,13,7,'Wheat Beer Pint',3,380.00,1140.00,NULL,'ACTIVE','1','2026-09-16 16:55:00',NULL,NULL,'1','1'),(14,4,14,10,'House White (Glass)',3,450.00,1350.00,NULL,'ACTIVE','1','2026-09-16 16:55:00',NULL,NULL,'1','1'),(15,4,15,4,'London Dry Gin (30ml)',3,360.00,1080.00,NULL,'ACTIVE','1','2026-09-16 16:55:00',NULL,NULL,'1','1'),(16,4,16,5,'Dark Rum (30ml)',1,300.00,300.00,NULL,'ACTIVE','1','2026-09-16 16:55:00',NULL,NULL,'1','1'),(17,5,17,5,'Dark Rum (30ml)',2,300.00,600.00,NULL,'ACTIVE','1','2026-09-15 17:55:00',NULL,NULL,'1','1'),(18,5,18,4,'London Dry Gin (30ml)',1,360.00,360.00,NULL,'ACTIVE','1','2026-09-15 17:55:00',NULL,NULL,'1','1'),(19,5,19,13,'Negroni',1,640.00,640.00,NULL,'ACTIVE','1','2026-09-15 17:55:00',NULL,NULL,'1','1'),(20,5,20,8,'Craft IPA Pint',2,420.00,840.00,NULL,'ACTIVE','1','2026-09-15 17:55:00',NULL,NULL,'1','1'),(21,5,21,16,'Espresso Martini',1,660.00,660.00,NULL,'ACTIVE','1','2026-09-15 17:55:00',NULL,NULL,'1','1'),(22,6,22,3,'Premium Vodka (30ml)',1,340.00,340.00,NULL,'ACTIVE','1','2026-09-17 18:55:00',NULL,NULL,'1','1'),(23,6,23,1,'Single Malt 12 Yr (30ml)',2,650.00,1300.00,NULL,'ACTIVE','1','2026-09-17 18:55:00',NULL,NULL,'1','1'),(24,6,24,14,'Mojito',3,480.00,1440.00,NULL,'ACTIVE','1','2026-09-17 18:55:00',NULL,NULL,'1','1'),(25,7,25,5,'Dark Rum (30ml)',1,300.00,300.00,NULL,'ACTIVE','1','2026-09-16 19:55:00',NULL,NULL,'1','1'),(26,7,26,9,'House Red (Glass)',2,450.00,900.00,NULL,'ACTIVE','1','2026-09-16 19:55:00',NULL,NULL,'1','1'),(27,7,27,14,'Mojito',1,480.00,480.00,NULL,'ACTIVE','1','2026-09-16 19:55:00',NULL,NULL,'1','1'),(28,7,28,7,'Wheat Beer Pint',3,380.00,1140.00,NULL,'ACTIVE','1','2026-09-16 19:55:00',NULL,NULL,'1','1'),(29,8,29,9,'House Red (Glass)',3,450.00,1350.00,NULL,'ACTIVE','1','2026-09-15 12:55:00',NULL,NULL,'1','1'),(30,8,30,18,'Fresh Lime Soda',3,180.00,540.00,NULL,'ACTIVE','1','2026-09-15 12:55:00',NULL,NULL,'1','1'),(31,8,31,5,'Dark Rum (30ml)',2,300.00,600.00,NULL,'ACTIVE','1','2026-09-15 12:55:00',NULL,NULL,'1','1'),(32,8,32,15,'Margarita',3,560.00,1680.00,NULL,'ACTIVE','1','2026-09-15 12:55:00',NULL,NULL,'1','1'),(33,8,33,7,'Wheat Beer Pint',1,380.00,380.00,NULL,'ACTIVE','1','2026-09-15 12:55:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_bill_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_bill_payment`
--

DROP TABLE IF EXISTS `bar_bill_payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_bill_payment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_id` int NOT NULL,
  `payment_method_id` int NOT NULL,
  `paid_amount` decimal(12,2) NOT NULL,
  `payment_reference` varchar(100) DEFAULT NULL,
  `payment_date` date NOT NULL,
  `payment_time` time NOT NULL,
  `payment_status` enum('Success','Failed','Refunded') NOT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_bill_payment_company_id` (`company_id`),
  KEY `ix_bar_bill_payment_status` (`status`),
  KEY `ix_bar_bill_payment_id` (`id`),
  KEY `ix_bar_bill_payment_payment_date` (`payment_date`),
  KEY `ix_bar_bill_payment_bill_id` (`bill_id`),
  KEY `ix_bar_bill_payment_branch_id` (`branch_id`),
  KEY `ix_bar_bill_payment_payment_status` (`payment_status`),
  KEY `ix_bar_bill_payment_payment_method_id` (`payment_method_id`),
  CONSTRAINT `bar_bill_payment_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `bar_bill` (`id`),
  CONSTRAINT `bar_bill_payment_ibfk_2` FOREIGN KEY (`payment_method_id`) REFERENCES `bar_payment_method` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_bill_payment`
--

LOCK TABLES `bar_bill_payment` WRITE;
/*!40000 ALTER TABLE `bar_bill_payment` DISABLE KEYS */;
INSERT INTO `bar_bill_payment` VALUES (1,1,2,5740.35,NULL,'2026-09-16','13:58:00','Success',NULL,'ACTIVE','1','2026-09-16 13:58:00',NULL,NULL,'1','1'),(2,2,3,4747.05,NULL,'2026-09-15','14:58:00','Success',NULL,'ACTIVE','1','2026-09-15 14:58:00',NULL,NULL,'1','1'),(3,3,4,2390.85,NULL,'2026-09-17','15:58:00','Success',NULL,'ACTIVE','1','2026-09-17 15:58:00',NULL,NULL,'1','1'),(4,4,5,4469.85,NULL,'2026-09-16','16:58:00','Success',NULL,'ACTIVE','1','2026-09-16 16:58:00',NULL,NULL,'1','1'),(5,5,1,3580.50,NULL,'2026-09-15','17:58:00','Success',NULL,'ACTIVE','1','2026-09-15 17:58:00',NULL,NULL,'1','1'),(6,6,2,3557.40,NULL,'2026-09-17','18:58:00','Success',NULL,'ACTIVE','1','2026-09-17 18:58:00',NULL,NULL,'1','1'),(7,7,3,3257.10,NULL,'2026-09-16','19:58:00','Success',NULL,'ACTIVE','1','2026-09-16 19:58:00',NULL,NULL,'1','1'),(8,8,4,5255.25,NULL,'2026-09-15','12:58:00','Success',NULL,'ACTIVE','1','2026-09-15 12:58:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_bill_payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_bill_split`
--

DROP TABLE IF EXISTS `bar_bill_split`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_bill_split` (
  `id` int NOT NULL AUTO_INCREMENT,
  `original_bill_id` int NOT NULL,
  `split_type` enum('By Person','By Item','By Amount') NOT NULL,
  `split_count` int NOT NULL,
  `split_datetime` datetime DEFAULT (now()),
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_bill_split_id` (`id`),
  KEY `ix_bar_bill_split_original_bill_id` (`original_bill_id`),
  KEY `ix_bar_bill_split_company_id` (`company_id`),
  KEY `ix_bar_bill_split_status` (`status`),
  KEY `ix_bar_bill_split_branch_id` (`branch_id`),
  CONSTRAINT `bar_bill_split_ibfk_1` FOREIGN KEY (`original_bill_id`) REFERENCES `bar_bill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_bill_split`
--

LOCK TABLES `bar_bill_split` WRITE;
/*!40000 ALTER TABLE `bar_bill_split` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_bill_split` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_bill_split_detail`
--

DROP TABLE IF EXISTS `bar_bill_split_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_bill_split_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `split_id` int NOT NULL,
  `child_bill_id` int NOT NULL,
  `split_number` int NOT NULL,
  `split_amount` decimal(12,2) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_bill_split_detail_split_id` (`split_id`),
  KEY `ix_bar_bill_split_detail_id` (`id`),
  KEY `ix_bar_bill_split_detail_branch_id` (`branch_id`),
  KEY `ix_bar_bill_split_detail_company_id` (`company_id`),
  KEY `ix_bar_bill_split_detail_child_bill_id` (`child_bill_id`),
  KEY `ix_bar_bill_split_detail_status` (`status`),
  CONSTRAINT `bar_bill_split_detail_ibfk_1` FOREIGN KEY (`split_id`) REFERENCES `bar_bill_split` (`id`),
  CONSTRAINT `bar_bill_split_detail_ibfk_2` FOREIGN KEY (`child_bill_id`) REFERENCES `bar_bill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_bill_split_detail`
--

LOCK TABLES `bar_bill_split_detail` WRITE;
/*!40000 ALTER TABLE `bar_bill_split_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_bill_split_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_daily_sales_report`
--

DROP TABLE IF EXISTS `bar_daily_sales_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_daily_sales_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `total_orders` int DEFAULT NULL,
  `total_bills` int DEFAULT NULL,
  `total_sales` decimal(12,2) DEFAULT NULL,
  `total_tax` decimal(12,2) DEFAULT NULL,
  `total_discount` decimal(12,2) DEFAULT NULL,
  `total_service_charge` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_daily_sales_report_date` (`company_id`,`branch_id`,`report_date`),
  KEY `ix_bar_daily_sales_report_id` (`id`),
  KEY `ix_bar_daily_sales_report_company_id` (`company_id`),
  KEY `ix_bar_daily_sales_report_report_date` (`report_date`),
  KEY `ix_bar_daily_sales_report_branch_id` (`branch_id`),
  KEY `ix_bar_daily_sales_report_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_daily_sales_report`
--

LOCK TABLES `bar_daily_sales_report` WRITE;
/*!40000 ALTER TABLE `bar_daily_sales_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_daily_sales_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_floor`
--

DROP TABLE IF EXISTS `bar_floor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_floor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `floor_code` varchar(100) NOT NULL,
  `floor_name` varchar(100) NOT NULL,
  `floor_number` int NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `total_tables` int DEFAULT NULL,
  `total_capacity` int DEFAULT NULL,
  `layout_json` json DEFAULT NULL,
  `color_code` varchar(20) DEFAULT NULL,
  `is_open` tinyint(1) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_floor_code` (`company_id`,`branch_id`,`floor_code`),
  KEY `ix_bar_floor_floor_code` (`floor_code`),
  KEY `ix_bar_floor_status` (`status`),
  KEY `ix_bar_floor_floor_number` (`floor_number`),
  KEY `ix_bar_floor_id` (`id`),
  KEY `ix_bar_floor_floor_name` (`floor_name`),
  KEY `ix_bar_floor_branch_id` (`branch_id`),
  KEY `ix_bar_floor_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_floor`
--

LOCK TABLES `bar_floor` WRITE;
/*!40000 ALTER TABLE `bar_floor` DISABLE KEYS */;
INSERT INTO `bar_floor` VALUES (1,'BF-MAIN','Bar Level',1,'Bar Level seating',6,24,NULL,'#850126',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,'BF-LNG','Lounge',2,'Lounge seating',4,20,NULL,'#850126',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_floor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_guest`
--

DROP TABLE IF EXISTS `bar_guest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_guest` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guest_code` varchar(100) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `mobile` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `guest_type` enum('Walk-In','Regular','VIP','Hotel Guest') NOT NULL,
  `special_notes` varchar(255) DEFAULT NULL,
  `loyalty_points` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_guest_mobile` (`company_id`,`branch_id`,`mobile`),
  UNIQUE KEY `ix_bar_guest_guest_code` (`guest_code`),
  KEY `ix_bar_guest_last_name` (`last_name`),
  KEY `ix_bar_guest_branch_id` (`branch_id`),
  KEY `ix_bar_guest_mobile` (`mobile`),
  KEY `ix_bar_guest_id` (`id`),
  KEY `ix_bar_guest_company_id` (`company_id`),
  KEY `ix_bar_guest_email` (`email`),
  KEY `ix_bar_guest_first_name` (`first_name`),
  KEY `ix_bar_guest_guest_type` (`guest_type`),
  KEY `ix_bar_guest_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_guest`
--

LOCK TABLES `bar_guest` WRITE;
/*!40000 ALTER TABLE `bar_guest` DISABLE KEYS */;
INSERT INTO `bar_guest` VALUES (1,'BG-0001','Deepak','Anand','9840230011','deepak.anand@gmail.com','Regular',NULL,NULL,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,'BG-0002','Sridevi','Raman','9840230022','sridevi.raman@gmail.com','VIP',NULL,NULL,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(3,'BG-0003','Michael','Fernandes','9840230033','michael.fernandes@gmail.com','Walk-In',NULL,NULL,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(4,'BG-0004','Aisha','Rahman','9840230044','aisha.rahman@gmail.com','Regular',NULL,NULL,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(5,'BG-0005','Ganesh','Iyer','9840230055','ganesh.iyer@gmail.com','VIP',NULL,NULL,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(6,'BG-0006','Sarah','Thomas','9840230066','sarah.thomas@gmail.com','Walk-In',NULL,NULL,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_guest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_guest_address`
--

DROP TABLE IF EXISTS `bar_guest_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_guest_address` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guest_id` int NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `postal_code` varchar(20) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_guest_address_branch_id` (`branch_id`),
  KEY `ix_bar_guest_address_city` (`city`),
  KEY `ix_bar_guest_address_state` (`state`),
  KEY `ix_bar_guest_address_company_id` (`company_id`),
  KEY `ix_bar_guest_address_id` (`id`),
  KEY `ix_bar_guest_address_guest_id` (`guest_id`),
  KEY `ix_bar_guest_address_country` (`country`),
  KEY `ix_bar_guest_address_status` (`status`),
  CONSTRAINT `bar_guest_address_ibfk_1` FOREIGN KEY (`guest_id`) REFERENCES `bar_guest` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_guest_address`
--

LOCK TABLES `bar_guest_address` WRITE;
/*!40000 ALTER TABLE `bar_guest_address` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_guest_address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_guest_feedback`
--

DROP TABLE IF EXISTS `bar_guest_feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_guest_feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guest_id` int NOT NULL,
  `order_id` int DEFAULT NULL,
  `rating` int NOT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_guest_feedback_order_id` (`order_id`),
  KEY `ix_bar_guest_feedback_guest_id` (`guest_id`),
  KEY `ix_bar_guest_feedback_branch_id` (`branch_id`),
  KEY `ix_bar_guest_feedback_id` (`id`),
  KEY `ix_bar_guest_feedback_status` (`status`),
  KEY `ix_bar_guest_feedback_company_id` (`company_id`),
  CONSTRAINT `bar_guest_feedback_ibfk_1` FOREIGN KEY (`guest_id`) REFERENCES `bar_guest` (`id`),
  CONSTRAINT `bar_guest_feedback_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `bar_order` (`id`),
  CONSTRAINT `ck_bar_guest_feedback_rating` CHECK (((`rating` >= 1) and (`rating` <= 5)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_guest_feedback`
--

LOCK TABLES `bar_guest_feedback` WRITE;
/*!40000 ALTER TABLE `bar_guest_feedback` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_guest_feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_guest_visit_history`
--

DROP TABLE IF EXISTS `bar_guest_visit_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_guest_visit_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guest_id` int NOT NULL,
  `visit_date` date NOT NULL,
  `order_id` int DEFAULT NULL,
  `bill_id` int DEFAULT NULL,
  `visit_type` enum('At Table','At Counter','Takeaway') NOT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `rating` int DEFAULT NULL,
  `feedback` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_guest_visit_history_visit_type` (`visit_type`),
  KEY `ix_bar_guest_visit_history_id` (`id`),
  KEY `ix_bar_guest_visit_history_guest_id` (`guest_id`),
  KEY `ix_bar_guest_visit_history_company_id` (`company_id`),
  KEY `ix_bar_guest_visit_history_bill_id` (`bill_id`),
  KEY `ix_bar_guest_visit_history_visit_date` (`visit_date`),
  KEY `ix_bar_guest_visit_history_branch_id` (`branch_id`),
  KEY `ix_bar_guest_visit_history_status` (`status`),
  KEY `ix_bar_guest_visit_history_order_id` (`order_id`),
  CONSTRAINT `bar_guest_visit_history_ibfk_1` FOREIGN KEY (`guest_id`) REFERENCES `bar_guest` (`id`),
  CONSTRAINT `bar_guest_visit_history_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `bar_order` (`id`),
  CONSTRAINT `bar_guest_visit_history_ibfk_3` FOREIGN KEY (`bill_id`) REFERENCES `bar_bill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_guest_visit_history`
--

LOCK TABLES `bar_guest_visit_history` WRITE;
/*!40000 ALTER TABLE `bar_guest_visit_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_guest_visit_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_inventory_item`
--

DROP TABLE IF EXISTS `bar_inventory_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_inventory_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_code` varchar(100) NOT NULL,
  `item_name` varchar(150) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `unit` enum('Bottle','Litre','ml','Can','Nos') NOT NULL,
  `min_stock_level` decimal(12,3) DEFAULT NULL,
  `is_perishable` tinyint(1) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_inventory_item_code` (`company_id`,`branch_id`,`item_code`),
  KEY `ix_bar_inventory_item_item_code` (`item_code`),
  KEY `ix_bar_inventory_item_branch_id` (`branch_id`),
  KEY `ix_bar_inventory_item_category` (`category`),
  KEY `ix_bar_inventory_item_company_id` (`company_id`),
  KEY `ix_bar_inventory_item_item_name` (`item_name`),
  KEY `ix_bar_inventory_item_unit` (`unit`),
  KEY `ix_bar_inventory_item_status` (`status`),
  KEY `ix_bar_inventory_item_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_inventory_item`
--

LOCK TABLES `bar_inventory_item` WRITE;
/*!40000 ALTER TABLE `bar_inventory_item` DISABLE KEYS */;
INSERT INTO `bar_inventory_item` VALUES (1,'BIN-001','Single Malt 12 Yr','Bar Store','Bottle',7.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,'BIN-002','Blended Whisky','Bar Store','Bottle',8.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(3,'BIN-003','Premium Vodka','Bar Store','Bottle',9.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(4,'BIN-004','London Dry Gin','Bar Store','Bottle',10.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(5,'BIN-005','Dark Rum','Bar Store','Bottle',11.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(6,'BIN-006','Lager Keg','Bar Store','Litre',12.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(7,'BIN-007','Red Wine','Bar Store','Bottle',13.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(8,'BIN-008','White Wine','Bar Store','Bottle',14.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(9,'BIN-009','Tonic Water','Bar Store','Can',15.000,0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(10,'BIN-010','Fresh Lime','Bar Store','Nos',16.000,1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_inventory_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_inventory_purchase`
--

DROP TABLE IF EXISTS `bar_inventory_purchase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_inventory_purchase` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_item_id` int NOT NULL,
  `quantity` decimal(12,3) NOT NULL,
  `unit_price` decimal(12,2) NOT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `purchase_date` date NOT NULL,
  `supplier_name` varchar(150) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_inventory_purchase_id` (`id`),
  KEY `ix_bar_inventory_purchase_company_id` (`company_id`),
  KEY `ix_bar_inventory_purchase_inventory_item_id` (`inventory_item_id`),
  KEY `ix_bar_inventory_purchase_status` (`status`),
  KEY `ix_bar_inventory_purchase_branch_id` (`branch_id`),
  KEY `ix_bar_inventory_purchase_purchase_date` (`purchase_date`),
  CONSTRAINT `bar_inventory_purchase_ibfk_1` FOREIGN KEY (`inventory_item_id`) REFERENCES `bar_inventory_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_inventory_purchase`
--

LOCK TABLES `bar_inventory_purchase` WRITE;
/*!40000 ALTER TABLE `bar_inventory_purchase` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_inventory_purchase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_inventory_stock`
--

DROP TABLE IF EXISTS `bar_inventory_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_inventory_stock` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_item_id` int NOT NULL,
  `station_id` int DEFAULT NULL,
  `available_quantity` decimal(12,3) NOT NULL,
  `last_updated_date` date DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_inventory_stock_location` (`inventory_item_id`,`station_id`,`company_id`,`branch_id`),
  KEY `ix_bar_inventory_stock_branch_id` (`branch_id`),
  KEY `ix_bar_inventory_stock_company_id` (`company_id`),
  KEY `ix_bar_inventory_stock_inventory_item_id` (`inventory_item_id`),
  KEY `ix_bar_inventory_stock_status` (`status`),
  KEY `ix_bar_inventory_stock_station_id` (`station_id`),
  KEY `ix_bar_inventory_stock_id` (`id`),
  CONSTRAINT `bar_inventory_stock_ibfk_1` FOREIGN KEY (`inventory_item_id`) REFERENCES `bar_inventory_item` (`id`),
  CONSTRAINT `bar_inventory_stock_ibfk_2` FOREIGN KEY (`station_id`) REFERENCES `bar_station` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_inventory_stock`
--

LOCK TABLES `bar_inventory_stock` WRITE;
/*!40000 ALTER TABLE `bar_inventory_stock` DISABLE KEYS */;
INSERT INTO `bar_inventory_stock` VALUES (1,1,1,21.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,2,1,24.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(3,3,1,27.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(4,4,1,30.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(5,5,1,33.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(6,6,1,36.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(7,7,1,39.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(8,8,1,42.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(9,9,1,45.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(10,10,1,48.000,'2026-09-16','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_inventory_stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_inventory_stock_transaction`
--

DROP TABLE IF EXISTS `bar_inventory_stock_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_inventory_stock_transaction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_item_id` int NOT NULL,
  `station_id` int DEFAULT NULL,
  `transaction_type` enum('IN','OUT','ADJUSTMENT','WASTE') NOT NULL,
  `quantity` decimal(12,3) NOT NULL,
  `reference_type` enum('Purchase','BOT','Manual','Transfer') DEFAULT NULL,
  `reference_id` varchar(100) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_inventory_stock_transaction_station_id` (`station_id`),
  KEY `ix_bar_inventory_stock_transaction_inventory_item_id` (`inventory_item_id`),
  KEY `ix_bar_inventory_stock_transaction_company_id` (`company_id`),
  KEY `ix_bar_inventory_stock_transaction_transaction_type` (`transaction_type`),
  KEY `ix_bar_inventory_stock_transaction_id` (`id`),
  KEY `ix_bar_inventory_stock_transaction_branch_id` (`branch_id`),
  CONSTRAINT `bar_inventory_stock_transaction_ibfk_1` FOREIGN KEY (`inventory_item_id`) REFERENCES `bar_inventory_item` (`id`),
  CONSTRAINT `bar_inventory_stock_transaction_ibfk_2` FOREIGN KEY (`station_id`) REFERENCES `bar_station` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_inventory_stock_transaction`
--

LOCK TABLES `bar_inventory_stock_transaction` WRITE;
/*!40000 ALTER TABLE `bar_inventory_stock_transaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_inventory_stock_transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_item_sales_report`
--

DROP TABLE IF EXISTS `bar_item_sales_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_item_sales_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `menu_id` int NOT NULL,
  `item_name` varchar(150) NOT NULL,
  `category_id` int DEFAULT NULL,
  `quantity_sold` int DEFAULT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_item_sales_report_line` (`company_id`,`branch_id`,`report_date`,`menu_id`),
  KEY `ix_bar_item_sales_report_status` (`status`),
  KEY `ix_bar_item_sales_report_category_id` (`category_id`),
  KEY `ix_bar_item_sales_report_company_id` (`company_id`),
  KEY `ix_bar_item_sales_report_id` (`id`),
  KEY `ix_bar_item_sales_report_report_date` (`report_date`),
  KEY `ix_bar_item_sales_report_menu_id` (`menu_id`),
  KEY `ix_bar_item_sales_report_branch_id` (`branch_id`),
  CONSTRAINT `bar_item_sales_report_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `bar_menu_item` (`id`),
  CONSTRAINT `bar_item_sales_report_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `bar_menu_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_item_sales_report`
--

LOCK TABLES `bar_item_sales_report` WRITE;
/*!40000 ALTER TABLE `bar_item_sales_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_item_sales_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_menu_category`
--

DROP TABLE IF EXISTS `bar_menu_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_menu_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_code` varchar(100) NOT NULL,
  `category_name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `station_id` int NOT NULL,
  `display_order` int DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_category_code` (`company_id`,`branch_id`,`category_code`),
  KEY `ix_bar_menu_category_category_code` (`category_code`),
  KEY `ix_bar_menu_category_branch_id` (`branch_id`),
  KEY `ix_bar_menu_category_station_id` (`station_id`),
  KEY `ix_bar_menu_category_status` (`status`),
  KEY `ix_bar_menu_category_company_id` (`company_id`),
  KEY `ix_bar_menu_category_id` (`id`),
  KEY `ix_bar_menu_category_category_name` (`category_name`),
  CONSTRAINT `bar_menu_category_ibfk_1` FOREIGN KEY (`station_id`) REFERENCES `bar_station` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_category`
--

LOCK TABLES `bar_menu_category` WRITE;
/*!40000 ALTER TABLE `bar_menu_category` DISABLE KEYS */;
INSERT INTO `bar_menu_category` VALUES (1,'BC-SPI','Spirits','Spirits selection',1,1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,'BC-BEER','Beer','Beer selection',1,2,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(3,'BC-WINE','Wine','Wine selection',2,3,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(4,'BC-COCK','Cocktails','Cocktails selection',1,4,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(5,'BC-NON','Non-Alcoholic','Non-Alcoholic selection',2,5,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_menu_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_menu_item`
--

DROP TABLE IF EXISTS `bar_menu_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_menu_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_code` varchar(100) NOT NULL,
  `item_name` varchar(150) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `category_id` int NOT NULL,
  `sub_category_id` int DEFAULT NULL,
  `price` decimal(12,2) NOT NULL,
  `cost_price` decimal(12,2) DEFAULT NULL,
  `tax_percentage` decimal(6,3) DEFAULT NULL,
  `service_charge_applicable` tinyint(1) NOT NULL,
  `preparation_time` int DEFAULT NULL,
  `station_id` int NOT NULL,
  `availability_status` enum('Available','Out of Stock') NOT NULL,
  `dietary_tags` json DEFAULT NULL,
  `has_variants` tinyint(1) NOT NULL,
  `item_image` varchar(255) DEFAULT NULL,
  `happy_hour_eligible` tinyint(1) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_item_code` (`company_id`,`branch_id`,`item_code`),
  KEY `ix_bar_menu_item_branch_id` (`branch_id`),
  KEY `ix_bar_menu_item_category_id` (`category_id`),
  KEY `ix_bar_menu_item_availability_status` (`availability_status`),
  KEY `ix_bar_menu_item_status` (`status`),
  KEY `ix_bar_menu_item_item_code` (`item_code`),
  KEY `ix_bar_menu_item_id` (`id`),
  KEY `ix_bar_menu_item_station_id` (`station_id`),
  KEY `ix_bar_menu_item_company_id` (`company_id`),
  KEY `ix_bar_menu_item_item_name` (`item_name`),
  KEY `ix_bar_menu_item_sub_category_id` (`sub_category_id`),
  CONSTRAINT `bar_menu_item_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `bar_menu_category` (`id`),
  CONSTRAINT `bar_menu_item_ibfk_2` FOREIGN KEY (`sub_category_id`) REFERENCES `bar_menu_sub_category` (`id`),
  CONSTRAINT `bar_menu_item_ibfk_3` FOREIGN KEY (`station_id`) REFERENCES `bar_station` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_item`
--

LOCK TABLES `bar_menu_item` WRITE;
/*!40000 ALTER TABLE `bar_menu_item` DISABLE KEYS */;
INSERT INTO `bar_menu_item` VALUES (1,'BAR-001','Single Malt 12 Yr (30ml)','Spirits — prepared to order.',1,NULL,650.00,247.00,5.000,1,3,1,'Available',NULL,0,'/templates/static/upload_image/38c2386e3a354c45a5a38e0e95825e3c.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,'BAR-002','Blended Whisky (30ml)','Spirits — prepared to order.',1,NULL,380.00,144.40,5.000,1,3,1,'Available',NULL,0,'/templates/static/upload_image/1e1b4c0a9f184de3a7e9bc37b1abc5be.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(3,'BAR-003','Premium Vodka (30ml)','Spirits — prepared to order.',1,NULL,340.00,129.20,5.000,1,3,1,'Available',NULL,0,'/templates/static/upload_image/b48b42bebf5e4f96b7e6c752ec517a6b.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(4,'BAR-004','London Dry Gin (30ml)','Spirits — prepared to order.',1,NULL,360.00,136.80,5.000,1,3,1,'Available',NULL,0,'/templates/static/upload_image/bf5066402a8e438e99ba1cf6e03859e0.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(5,'BAR-005','Dark Rum (30ml)','Spirits — prepared to order.',1,NULL,300.00,114.00,5.000,1,3,1,'Available',NULL,0,'/templates/static/upload_image/1a34036e1d4b4e6781c6f41416e625d0.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(6,'BAR-006','Lager Pint','Beer — prepared to order.',2,NULL,320.00,121.60,5.000,1,2,1,'Available',NULL,0,'/templates/static/upload_image/2df810e45c8e4c289501770d24925955.jpg',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(7,'BAR-007','Wheat Beer Pint','Beer — prepared to order.',2,NULL,380.00,144.40,5.000,1,2,1,'Available',NULL,0,'/templates/static/upload_image/bec24c2fbd2c406eb4cf55f3dd4360c3.jpg',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(8,'BAR-008','Craft IPA Pint','Beer — prepared to order.',2,NULL,420.00,159.60,5.000,1,2,1,'Available',NULL,0,'/templates/static/upload_image/2c1f62c0a68440f2ae2ca57c85b775c9.jpg',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(9,'BAR-009','House Red (Glass)','Wine — prepared to order.',3,NULL,450.00,171.00,5.000,1,3,2,'Available',NULL,0,'/templates/static/upload_image/b0e05a362ad248e5a79736fd2ceb33a9.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(10,'BAR-010','House White (Glass)','Wine — prepared to order.',3,NULL,450.00,171.00,5.000,1,3,2,'Available',NULL,0,'/templates/static/upload_image/44746d0d13f541698099b355c6885b0a.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(11,'BAR-011','Sparkling Wine (Glass)','Wine — prepared to order.',3,NULL,620.00,235.60,5.000,1,3,2,'Available',NULL,0,'/templates/static/upload_image/39e2bb3b0f05444a918d0f10a329a39e.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(12,'BAR-012','Old Fashioned','Cocktails — prepared to order.',4,NULL,620.00,235.60,5.000,1,6,1,'Available',NULL,0,'/templates/static/upload_image/ec6be47fceb641d4b07eaeb995b07f06.jpg',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(13,'BAR-013','Negroni','Cocktails — prepared to order.',4,NULL,640.00,243.20,5.000,1,5,1,'Available',NULL,0,'/templates/static/upload_image/6c56917c12de4a70976b422105937e3a.jpg',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(14,'BAR-014','Mojito','Cocktails — prepared to order.',4,NULL,480.00,182.40,5.000,1,5,1,'Available',NULL,0,'/templates/static/upload_image/4095d327b8234819b1d5661e79a1a13d.jpg',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(15,'BAR-015','Margarita','Cocktails — prepared to order.',4,NULL,560.00,212.80,5.000,1,5,1,'Available',NULL,0,'/templates/static/upload_image/25aafcaa18174dfb9612a19e27f7d4e7.jpg',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(16,'BAR-016','Espresso Martini','Cocktails — prepared to order.',4,NULL,660.00,250.80,5.000,1,6,1,'Available',NULL,0,'/templates/static/upload_image/bc2fe7f0f14a432199adc833c72d2309.jpg',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(17,'BAR-017','Virgin Mojito','Non-Alcoholic — prepared to order.',5,NULL,260.00,98.80,5.000,1,4,2,'Available',NULL,0,'/templates/static/upload_image/f6ce15933f684d8fb6e95ad6a5ec55a0.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(18,'BAR-018','Fresh Lime Soda','Non-Alcoholic — prepared to order.',5,NULL,180.00,68.40,5.000,1,3,2,'Available',NULL,0,'/templates/static/upload_image/499e37ff136c49f886d2d31292fd3f67.jpg',0,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_menu_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_menu_modifier`
--

DROP TABLE IF EXISTS `bar_menu_modifier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_menu_modifier` (
  `id` int NOT NULL AUTO_INCREMENT,
  `menu_id` int NOT NULL,
  `modifier_name` varchar(100) NOT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  `modifier_type` enum('Add-on','Remove') DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_menu_modifier_status` (`status`),
  KEY `ix_bar_menu_modifier_id` (`id`),
  KEY `ix_bar_menu_modifier_company_id` (`company_id`),
  KEY `ix_bar_menu_modifier_menu_id` (`menu_id`),
  KEY `ix_bar_menu_modifier_modifier_name` (`modifier_name`),
  KEY `ix_bar_menu_modifier_branch_id` (`branch_id`),
  CONSTRAINT `bar_menu_modifier_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `bar_menu_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_modifier`
--

LOCK TABLES `bar_menu_modifier` WRITE;
/*!40000 ALTER TABLE `bar_menu_modifier` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_menu_modifier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_menu_sub_category`
--

DROP TABLE IF EXISTS `bar_menu_sub_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_menu_sub_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_id` int NOT NULL,
  `category_code` varchar(100) NOT NULL,
  `sub_category_code` varchar(100) NOT NULL,
  `sub_category_name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `display_order` int DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_sub_category_code` (`company_id`,`branch_id`,`sub_category_code`),
  KEY `ix_bar_menu_sub_category_category_code` (`category_code`),
  KEY `ix_bar_menu_sub_category_company_id` (`company_id`),
  KEY `ix_bar_menu_sub_category_sub_category_name` (`sub_category_name`),
  KEY `ix_bar_menu_sub_category_category_id` (`category_id`),
  KEY `ix_bar_menu_sub_category_id` (`id`),
  KEY `ix_bar_menu_sub_category_sub_category_code` (`sub_category_code`),
  KEY `ix_bar_menu_sub_category_branch_id` (`branch_id`),
  KEY `ix_bar_menu_sub_category_status` (`status`),
  CONSTRAINT `bar_menu_sub_category_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `bar_menu_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_sub_category`
--

LOCK TABLES `bar_menu_sub_category` WRITE;
/*!40000 ALTER TABLE `bar_menu_sub_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_menu_sub_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_menu_variant`
--

DROP TABLE IF EXISTS `bar_menu_variant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_menu_variant` (
  `id` int NOT NULL AUTO_INCREMENT,
  `menu_id` int NOT NULL,
  `variant_name` varchar(50) NOT NULL,
  `price` decimal(12,2) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_menu_variant_name` (`menu_id`,`variant_name`),
  KEY `ix_bar_menu_variant_company_id` (`company_id`),
  KEY `ix_bar_menu_variant_menu_id` (`menu_id`),
  KEY `ix_bar_menu_variant_id` (`id`),
  KEY `ix_bar_menu_variant_branch_id` (`branch_id`),
  KEY `ix_bar_menu_variant_variant_name` (`variant_name`),
  KEY `ix_bar_menu_variant_status` (`status`),
  CONSTRAINT `bar_menu_variant_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `bar_menu_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_variant`
--

LOCK TABLES `bar_menu_variant` WRITE;
/*!40000 ALTER TABLE `bar_menu_variant` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_menu_variant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_order`
--

DROP TABLE IF EXISTS `bar_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_number` varchar(100) NOT NULL,
  `order_date` date NOT NULL,
  `order_time` time NOT NULL,
  `order_type` enum('At Table','At Counter','Takeaway') NOT NULL,
  `table_id` int DEFAULT NULL,
  `table_code` varchar(100) DEFAULT NULL,
  `floor_id` int DEFAULT NULL,
  `floor_code` varchar(100) DEFAULT NULL,
  `guest_id` int DEFAULT NULL,
  `guest_name` varchar(100) DEFAULT NULL,
  `guest_mobile` varchar(20) DEFAULT NULL,
  `no_of_guests` int DEFAULT NULL,
  `server_id` varchar(100) DEFAULT NULL,
  `server_name` varchar(100) DEFAULT NULL,
  `order_status` enum('New','In Progress','Ready','Served','Completed','Cancelled') NOT NULL,
  `payment_status` enum('Pending','Partial','Paid') NOT NULL,
  `sub_total` decimal(12,2) DEFAULT NULL,
  `tax_amount` decimal(12,2) DEFAULT NULL,
  `service_charge` decimal(12,2) DEFAULT NULL,
  `discount_type` enum('Percentage','Flat') DEFAULT NULL,
  `discount_value` decimal(12,2) DEFAULT NULL,
  `discount_amount` decimal(12,2) DEFAULT NULL,
  `grand_total` decimal(12,2) DEFAULT NULL,
  `special_notes` varchar(255) DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_order_number` (`company_id`,`branch_id`,`order_number`),
  UNIQUE KEY `ix_bar_order_token` (`token`),
  KEY `ix_bar_order_order_type` (`order_type`),
  KEY `ix_bar_order_branch_id` (`branch_id`),
  KEY `ix_bar_order_status` (`status`),
  KEY `ix_bar_order_guest_id` (`guest_id`),
  KEY `ix_bar_order_payment_status` (`payment_status`),
  KEY `ix_bar_order_order_status` (`order_status`),
  KEY `ix_bar_order_floor_id` (`floor_id`),
  KEY `ix_bar_order_floor_code` (`floor_code`),
  KEY `ix_bar_order_order_date` (`order_date`),
  KEY `ix_bar_order_guest_mobile` (`guest_mobile`),
  KEY `ix_bar_order_company_id` (`company_id`),
  KEY `ix_bar_order_table_id` (`table_id`),
  KEY `ix_bar_order_id` (`id`),
  KEY `ix_bar_order_table_code` (`table_code`),
  KEY `ix_bar_order_order_number` (`order_number`),
  KEY `ix_bar_order_server_id` (`server_id`),
  CONSTRAINT `bar_order_ibfk_1` FOREIGN KEY (`table_id`) REFERENCES `bar_table` (`id`),
  CONSTRAINT `bar_order_ibfk_2` FOREIGN KEY (`floor_id`) REFERENCES `bar_floor` (`id`),
  CONSTRAINT `bar_order_ibfk_3` FOREIGN KEY (`guest_id`) REFERENCES `bar_guest` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order`
--

LOCK TABLES `bar_order` WRITE;
/*!40000 ALTER TABLE `bar_order` DISABLE KEYS */;
INSERT INTO `bar_order` VALUES (1,'BO-20260916-001','2026-09-16','13:15:00','At Table',4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',4970.00,273.35,497.00,NULL,NULL,0.00,5740.35,NULL,'683ce47c-046a-4552-bfa9-79a6221643f1','ACTIVE','1','2026-09-16 13:15:00',NULL,NULL,'1','1'),(2,'BO-20260915-002','2026-09-15','14:15:00','At Table',7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',4110.00,226.05,411.00,NULL,NULL,0.00,4747.05,NULL,'2bd24487-b428-4630-81db-2aa0ab0e7c71','ACTIVE','1','2026-09-15 14:15:00',NULL,NULL,'1','1'),(3,'BO-20260917-003','2026-09-17','15:15:00','At Table',10,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',2070.00,113.85,207.00,NULL,NULL,0.00,2390.85,NULL,'7f1bc55a-5107-49aa-bc28-2b663170eda9','ACTIVE','1','2026-09-17 15:15:00',NULL,NULL,'1','1'),(4,'BO-20260916-004','2026-09-16','16:15:00','At Table',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',3870.00,212.85,387.00,NULL,NULL,0.00,4469.85,NULL,'22aed6b3-a6be-49fb-93c5-502c3a1cad64','ACTIVE','1','2026-09-16 16:15:00',NULL,NULL,'1','1'),(5,'BO-20260915-005','2026-09-15','17:15:00','At Table',6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',3100.00,170.50,310.00,NULL,NULL,0.00,3580.50,NULL,'cea2bc1a-5579-4a9d-ad52-46fd2608e4ce','ACTIVE','1','2026-09-15 17:15:00',NULL,NULL,'1','1'),(6,'BO-20260917-006','2026-09-17','18:15:00','At Table',9,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',3080.00,169.40,308.00,NULL,NULL,0.00,3557.40,NULL,'57a0635c-d43b-4740-a845-63537a8ce5da','ACTIVE','1','2026-09-17 18:15:00',NULL,NULL,'1','1'),(7,'BO-20260916-007','2026-09-16','19:15:00','At Table',2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',2820.00,155.10,282.00,NULL,NULL,0.00,3257.10,NULL,'16096761-e2a8-4ed3-827b-9b1a969d5944','ACTIVE','1','2026-09-16 19:15:00',NULL,NULL,'1','1'),(8,'BO-20260915-008','2026-09-15','12:15:00','At Table',5,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',4550.00,250.25,455.00,NULL,NULL,0.00,5255.25,NULL,'fa8032d0-1cff-413d-ae15-169c5ad99554','ACTIVE','1','2026-09-15 12:15:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_order_item`
--

DROP TABLE IF EXISTS `bar_order_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_order_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `menu_id` int NOT NULL,
  `station_id` int NOT NULL,
  `quantity` int NOT NULL,
  `price` decimal(12,2) NOT NULL,
  `item_status` enum('Pending','Preparing','Ready','Served','Cancelled') NOT NULL,
  `special_instructions` varchar(255) DEFAULT NULL,
  `variant_id` int DEFAULT NULL,
  `variant_name` varchar(50) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `variant_id` (`variant_id`),
  KEY `ix_bar_order_item_company_id` (`company_id`),
  KEY `ix_bar_order_item_id` (`id`),
  KEY `ix_bar_order_item_order_id` (`order_id`),
  KEY `ix_bar_order_item_status` (`status`),
  KEY `ix_bar_order_item_branch_id` (`branch_id`),
  KEY `ix_bar_order_item_item_status` (`item_status`),
  KEY `ix_bar_order_item_menu_id` (`menu_id`),
  KEY `ix_bar_order_item_station_id` (`station_id`),
  CONSTRAINT `bar_order_item_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `bar_order` (`id`),
  CONSTRAINT `bar_order_item_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `bar_menu_item` (`id`),
  CONSTRAINT `bar_order_item_ibfk_3` FOREIGN KEY (`station_id`) REFERENCES `bar_station` (`id`),
  CONSTRAINT `bar_order_item_ibfk_4` FOREIGN KEY (`variant_id`) REFERENCES `bar_menu_variant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order_item`
--

LOCK TABLES `bar_order_item` WRITE;
/*!40000 ALTER TABLE `bar_order_item` DISABLE KEYS */;
INSERT INTO `bar_order_item` VALUES (1,1,13,1,3,640.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 13:20:00',NULL,NULL,'1','1'),(2,1,1,1,3,650.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 13:20:00',NULL,NULL,'1','1'),(3,1,3,1,2,340.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 13:20:00',NULL,NULL,'1','1'),(4,1,8,1,1,420.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 13:20:00',NULL,NULL,'1','1'),(5,2,1,1,1,650.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 14:20:00',NULL,NULL,'1','1'),(6,2,3,1,3,340.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 14:20:00',NULL,NULL,'1','1'),(7,2,13,1,1,640.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 14:20:00',NULL,NULL,'1','1'),(8,2,8,1,2,420.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 14:20:00',NULL,NULL,'1','1'),(9,2,6,1,3,320.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 14:20:00',NULL,NULL,'1','1'),(10,3,9,2,1,450.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-17 15:20:00',NULL,NULL,'1','1'),(11,3,18,2,1,180.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-17 15:20:00',NULL,NULL,'1','1'),(12,3,14,1,3,480.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-17 15:20:00',NULL,NULL,'1','1'),(13,4,7,1,3,380.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 16:20:00',NULL,NULL,'1','1'),(14,4,10,2,3,450.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 16:20:00',NULL,NULL,'1','1'),(15,4,4,1,3,360.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 16:20:00',NULL,NULL,'1','1'),(16,4,5,1,1,300.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 16:20:00',NULL,NULL,'1','1'),(17,5,5,1,2,300.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 17:20:00',NULL,NULL,'1','1'),(18,5,4,1,1,360.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 17:20:00',NULL,NULL,'1','1'),(19,5,13,1,1,640.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 17:20:00',NULL,NULL,'1','1'),(20,5,8,1,2,420.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 17:20:00',NULL,NULL,'1','1'),(21,5,16,1,1,660.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 17:20:00',NULL,NULL,'1','1'),(22,6,3,1,1,340.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-17 18:20:00',NULL,NULL,'1','1'),(23,6,1,1,2,650.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-17 18:20:00',NULL,NULL,'1','1'),(24,6,14,1,3,480.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-17 18:20:00',NULL,NULL,'1','1'),(25,7,5,1,1,300.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 19:20:00',NULL,NULL,'1','1'),(26,7,9,2,2,450.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 19:20:00',NULL,NULL,'1','1'),(27,7,14,1,1,480.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 19:20:00',NULL,NULL,'1','1'),(28,7,7,1,3,380.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-16 19:20:00',NULL,NULL,'1','1'),(29,8,9,2,3,450.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 12:20:00',NULL,NULL,'1','1'),(30,8,18,2,3,180.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 12:20:00',NULL,NULL,'1','1'),(31,8,5,1,2,300.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 12:20:00',NULL,NULL,'1','1'),(32,8,15,1,3,560.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 12:20:00',NULL,NULL,'1','1'),(33,8,7,1,1,380.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-15 12:20:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_order_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_order_item_modifier`
--

DROP TABLE IF EXISTS `bar_order_item_modifier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_order_item_modifier` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_item_id` int NOT NULL,
  `modifier_id` int NOT NULL,
  `modifier_name` varchar(100) NOT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_order_item_modifier_company_id` (`company_id`),
  KEY `ix_bar_order_item_modifier_modifier_id` (`modifier_id`),
  KEY `ix_bar_order_item_modifier_branch_id` (`branch_id`),
  KEY `ix_bar_order_item_modifier_id` (`id`),
  KEY `ix_bar_order_item_modifier_order_item_id` (`order_item_id`),
  CONSTRAINT `bar_order_item_modifier_ibfk_1` FOREIGN KEY (`order_item_id`) REFERENCES `bar_order_item` (`id`),
  CONSTRAINT `bar_order_item_modifier_ibfk_2` FOREIGN KEY (`modifier_id`) REFERENCES `bar_menu_modifier` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order_item_modifier`
--

LOCK TABLES `bar_order_item_modifier` WRITE;
/*!40000 ALTER TABLE `bar_order_item_modifier` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_order_item_modifier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_order_ticket`
--

DROP TABLE IF EXISTS `bar_order_ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_order_ticket` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bot_number` varchar(100) NOT NULL,
  `order_id` int NOT NULL,
  `parent_bot_id` int DEFAULT NULL,
  `bot_type` enum('Original','Supplementary','Modification','Cancellation') NOT NULL,
  `station_id` int NOT NULL,
  `bot_status` enum('New','Acknowledged','In Progress','Completed','Cancelled') NOT NULL,
  `priority` enum('Normal','High','ASAP') DEFAULT NULL,
  `print_count` int DEFAULT NULL,
  `printed_by` varchar(100) DEFAULT NULL,
  `acknowledged_by` varchar(100) DEFAULT NULL,
  `acknowledged_at` datetime DEFAULT NULL,
  `completed_by` varchar(100) DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bot_number` (`company_id`,`branch_id`,`bot_number`),
  KEY `ix_bar_order_ticket_bot_number` (`bot_number`),
  KEY `ix_bar_order_ticket_bot_type` (`bot_type`),
  KEY `ix_bar_order_ticket_parent_bot_id` (`parent_bot_id`),
  KEY `ix_bar_order_ticket_company_id` (`company_id`),
  KEY `ix_bar_order_ticket_station_id` (`station_id`),
  KEY `ix_bar_order_ticket_bot_status` (`bot_status`),
  KEY `ix_bar_order_ticket_order_id` (`order_id`),
  KEY `ix_bar_order_ticket_status` (`status`),
  KEY `ix_bar_order_ticket_id` (`id`),
  KEY `ix_bar_order_ticket_branch_id` (`branch_id`),
  CONSTRAINT `bar_order_ticket_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `bar_order` (`id`),
  CONSTRAINT `bar_order_ticket_ibfk_2` FOREIGN KEY (`parent_bot_id`) REFERENCES `bar_order_ticket` (`id`),
  CONSTRAINT `bar_order_ticket_ibfk_3` FOREIGN KEY (`station_id`) REFERENCES `bar_station` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order_ticket`
--

LOCK TABLES `bar_order_ticket` WRITE;
/*!40000 ALTER TABLE `bar_order_ticket` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_order_ticket` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_order_ticket_item`
--

DROP TABLE IF EXISTS `bar_order_ticket_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_order_ticket_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bot_id` int NOT NULL,
  `order_item_id` int NOT NULL,
  `preparation_status` enum('Pending','Preparing','Ready','Cancelled') NOT NULL,
  `prep_start_time` datetime DEFAULT NULL,
  `prep_end_time` datetime DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_order_ticket_item_bot_id` (`bot_id`),
  KEY `ix_bar_order_ticket_item_company_id` (`company_id`),
  KEY `ix_bar_order_ticket_item_order_item_id` (`order_item_id`),
  KEY `ix_bar_order_ticket_item_status` (`status`),
  KEY `ix_bar_order_ticket_item_branch_id` (`branch_id`),
  KEY `ix_bar_order_ticket_item_preparation_status` (`preparation_status`),
  KEY `ix_bar_order_ticket_item_id` (`id`),
  CONSTRAINT `bar_order_ticket_item_ibfk_1` FOREIGN KEY (`bot_id`) REFERENCES `bar_order_ticket` (`id`),
  CONSTRAINT `bar_order_ticket_item_ibfk_2` FOREIGN KEY (`order_item_id`) REFERENCES `bar_order_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order_ticket_item`
--

LOCK TABLES `bar_order_ticket_item` WRITE;
/*!40000 ALTER TABLE `bar_order_ticket_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_order_ticket_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_payment_method`
--

DROP TABLE IF EXISTS `bar_payment_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_payment_method` (
  `id` int NOT NULL AUTO_INCREMENT,
  `method_name` varchar(50) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_payment_method_name` (`company_id`,`branch_id`,`method_name`),
  KEY `ix_bar_payment_method_method_name` (`method_name`),
  KEY `ix_bar_payment_method_company_id` (`company_id`),
  KEY `ix_bar_payment_method_id` (`id`),
  KEY `ix_bar_payment_method_branch_id` (`branch_id`),
  KEY `ix_bar_payment_method_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_payment_method`
--

LOCK TABLES `bar_payment_method` WRITE;
/*!40000 ALTER TABLE `bar_payment_method` DISABLE KEYS */;
INSERT INTO `bar_payment_method` VALUES (1,'Cash','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,'Credit Card','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(3,'Debit Card','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(4,'UPI','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(5,'Room Charge','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_payment_method` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_payment_mode_report`
--

DROP TABLE IF EXISTS `bar_payment_mode_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_payment_mode_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `payment_method_id` int NOT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_payment_mode_report_line` (`company_id`,`branch_id`,`report_date`,`payment_method_id`),
  KEY `ix_bar_payment_mode_report_report_date` (`report_date`),
  KEY `ix_bar_payment_mode_report_id` (`id`),
  KEY `ix_bar_payment_mode_report_branch_id` (`branch_id`),
  KEY `ix_bar_payment_mode_report_payment_method_id` (`payment_method_id`),
  KEY `ix_bar_payment_mode_report_company_id` (`company_id`),
  KEY `ix_bar_payment_mode_report_status` (`status`),
  CONSTRAINT `bar_payment_mode_report_ibfk_1` FOREIGN KEY (`payment_method_id`) REFERENCES `bar_payment_method` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_payment_mode_report`
--

LOCK TABLES `bar_payment_mode_report` WRITE;
/*!40000 ALTER TABLE `bar_payment_mode_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_payment_mode_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_recipe`
--

DROP TABLE IF EXISTS `bar_recipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_recipe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `menu_id` int NOT NULL,
  `inventory_item_id` int NOT NULL,
  `quantity_required` decimal(12,3) NOT NULL,
  `unit` enum('Bottle','Litre','ml','Can','Nos') NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_recipe_line` (`menu_id`,`inventory_item_id`),
  KEY `ix_bar_recipe_status` (`status`),
  KEY `ix_bar_recipe_id` (`id`),
  KEY `ix_bar_recipe_branch_id` (`branch_id`),
  KEY `ix_bar_recipe_menu_id` (`menu_id`),
  KEY `ix_bar_recipe_inventory_item_id` (`inventory_item_id`),
  KEY `ix_bar_recipe_company_id` (`company_id`),
  CONSTRAINT `bar_recipe_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `bar_menu_item` (`id`),
  CONSTRAINT `bar_recipe_ibfk_2` FOREIGN KEY (`inventory_item_id`) REFERENCES `bar_inventory_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_recipe`
--

LOCK TABLES `bar_recipe` WRITE;
/*!40000 ALTER TABLE `bar_recipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_recipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_settings`
--

DROP TABLE IF EXISTS `bar_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(100) NOT NULL,
  `setting_value` varchar(255) DEFAULT NULL,
  `setting_group` enum('OperatingHours','Tax','ServiceCharge','Printer','Numbering','Discount','Language') DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_setting_key` (`company_id`,`branch_id`,`setting_key`),
  KEY `ix_bar_settings_id` (`id`),
  KEY `ix_bar_settings_setting_group` (`setting_group`),
  KEY `ix_bar_settings_company_id` (`company_id`),
  KEY `ix_bar_settings_setting_key` (`setting_key`),
  KEY `ix_bar_settings_branch_id` (`branch_id`),
  KEY `ix_bar_settings_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_settings`
--

LOCK TABLES `bar_settings` WRITE;
/*!40000 ALTER TABLE `bar_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_staff_assignment`
--

DROP TABLE IF EXISTS `bar_staff_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_staff_assignment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `employee_name` varchar(150) DEFAULT NULL,
  `role` enum('Bartender','Cashier','Manager') NOT NULL,
  `shift_date` date NOT NULL,
  `shift_start` time NOT NULL,
  `shift_end` time DEFAULT NULL,
  `floor_id` int DEFAULT NULL,
  `sales_target` decimal(12,2) DEFAULT NULL,
  `actual_sales` decimal(12,2) DEFAULT NULL,
  `clock_in_at` datetime DEFAULT NULL,
  `clock_out_at` datetime DEFAULT NULL,
  `opening_cash_float` decimal(12,2) DEFAULT NULL,
  `closing_cash_amount` decimal(12,2) DEFAULT NULL,
  `shift_status` enum('Scheduled','On Shift','On Break','Closed') NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bar_staff_assignment_status` (`status`),
  KEY `ix_bar_staff_assignment_branch_id` (`branch_id`),
  KEY `ix_bar_staff_assignment_shift_date` (`shift_date`),
  KEY `ix_bar_staff_assignment_id` (`id`),
  KEY `ix_bar_staff_assignment_employee_id` (`employee_id`),
  KEY `ix_bar_staff_assignment_floor_id` (`floor_id`),
  KEY `ix_bar_staff_assignment_shift_status` (`shift_status`),
  KEY `ix_bar_staff_assignment_company_id` (`company_id`),
  KEY `ix_bar_staff_assignment_role` (`role`),
  CONSTRAINT `bar_staff_assignment_ibfk_1` FOREIGN KEY (`floor_id`) REFERENCES `bar_floor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_staff_assignment`
--

LOCK TABLES `bar_staff_assignment` WRITE;
/*!40000 ALTER TABLE `bar_staff_assignment` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_staff_assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_staff_performance_report`
--

DROP TABLE IF EXISTS `bar_staff_performance_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_staff_performance_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `employee_id` int NOT NULL,
  `role` enum('Bartender','Cashier','Manager') NOT NULL,
  `total_orders` int DEFAULT NULL,
  `total_sales` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_staff_performance_report_line` (`company_id`,`branch_id`,`report_date`,`employee_id`),
  KEY `ix_bar_staff_performance_report_report_date` (`report_date`),
  KEY `ix_bar_staff_performance_report_branch_id` (`branch_id`),
  KEY `ix_bar_staff_performance_report_status` (`status`),
  KEY `ix_bar_staff_performance_report_employee_id` (`employee_id`),
  KEY `ix_bar_staff_performance_report_role` (`role`),
  KEY `ix_bar_staff_performance_report_company_id` (`company_id`),
  KEY `ix_bar_staff_performance_report_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_staff_performance_report`
--

LOCK TABLES `bar_staff_performance_report` WRITE;
/*!40000 ALTER TABLE `bar_staff_performance_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `bar_staff_performance_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_station`
--

DROP TABLE IF EXISTS `bar_station`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_station` (
  `id` int NOT NULL AUTO_INCREMENT,
  `station_code` varchar(100) NOT NULL,
  `station_name` varchar(100) NOT NULL,
  `printer_name` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_station_code` (`company_id`,`branch_id`,`station_code`),
  KEY `ix_bar_station_station_name` (`station_name`),
  KEY `ix_bar_station_company_id` (`company_id`),
  KEY `ix_bar_station_branch_id` (`branch_id`),
  KEY `ix_bar_station_station_code` (`station_code`),
  KEY `ix_bar_station_id` (`id`),
  KEY `ix_bar_station_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_station`
--

LOCK TABLES `bar_station` WRITE;
/*!40000 ALTER TABLE `bar_station` DISABLE KEYS */;
INSERT INTO `bar_station` VALUES (1,'STN-BAR','Main Bar','STN-BAR-PRN',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,'STN-LNG','Lounge Bar','STN-LNG-PRN',1,'ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_station` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bar_table`
--

DROP TABLE IF EXISTS `bar_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bar_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `table_code` varchar(100) NOT NULL,
  `table_name` varchar(100) NOT NULL,
  `table_number` int NOT NULL,
  `floor_id` int NOT NULL,
  `floor_code` varchar(100) NOT NULL,
  `table_type` enum('Counter','Table','Booth','VIP Lounge') NOT NULL,
  `seating_capacity` int NOT NULL,
  `current_order_id` int DEFAULT NULL,
  `server_id` varchar(100) DEFAULT NULL,
  `server_name` varchar(100) DEFAULT NULL,
  `table_status` enum('Available','Occupied','Reserved','Cleaning','Blocked') NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bar_table_code` (`company_id`,`branch_id`,`table_code`),
  KEY `ix_bar_table_server_id` (`server_id`),
  KEY `ix_bar_table_table_number` (`table_number`),
  KEY `ix_bar_table_company_id` (`company_id`),
  KEY `ix_bar_table_status` (`status`),
  KEY `ix_bar_table_branch_id` (`branch_id`),
  KEY `ix_bar_table_current_order_id` (`current_order_id`),
  KEY `ix_bar_table_table_code` (`table_code`),
  KEY `ix_bar_table_table_type` (`table_type`),
  KEY `ix_bar_table_id` (`id`),
  KEY `ix_bar_table_floor_code` (`floor_code`),
  KEY `ix_bar_table_table_status` (`table_status`),
  KEY `ix_bar_table_floor_id` (`floor_id`),
  KEY `ix_bar_table_table_name` (`table_name`),
  CONSTRAINT `bar_table_ibfk_1` FOREIGN KEY (`floor_id`) REFERENCES `bar_floor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_table`
--

LOCK TABLES `bar_table` WRITE;
/*!40000 ALTER TABLE `bar_table` DISABLE KEYS */;
INSERT INTO `bar_table` VALUES (1,'BF-MAIN-T01','Counter 1',1,1,'BF-MAIN','Counter',2,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(2,'BF-MAIN-T02','Table 2',2,1,'BF-MAIN','Table',4,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(3,'BF-MAIN-T03','Table 3',3,1,'BF-MAIN','Table',2,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(4,'BF-MAIN-T04','Table 4',4,1,'BF-MAIN','Table',4,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(5,'BF-MAIN-T05','Table 5',5,1,'BF-MAIN','Table',2,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(6,'BF-MAIN-T06','Table 6',6,1,'BF-MAIN','Table',4,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(7,'BF-LNG-T01','Counter 7',7,2,'BF-LNG','Counter',2,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(8,'BF-LNG-T02','Table 8',8,2,'BF-LNG','VIP Lounge',4,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(9,'BF-LNG-T03','Table 9',9,2,'BF-LNG','Table',2,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1'),(10,'BF-LNG-T04','Table 10',10,2,'BF-LNG','Table',4,NULL,NULL,NULL,'Available','ACTIVE','1','2026-09-17 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `bar_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'hotelerp_bar'
--

--
-- Dumping routines for database 'hotelerp_bar'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-17 17:08:24
