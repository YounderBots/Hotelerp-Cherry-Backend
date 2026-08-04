CREATE DATABASE  IF NOT EXISTS `hotelerp_bar` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `hotelerp_bar`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: hotelerp_bar
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
  `sub_total` float DEFAULT NULL,
  `cgst_percentage` float DEFAULT NULL,
  `cgst_amount` float DEFAULT NULL,
  `sgst_percentage` float DEFAULT NULL,
  `sgst_amount` float DEFAULT NULL,
  `service_charge_percentage` float DEFAULT NULL,
  `service_charge_amount` float DEFAULT NULL,
  `discount_type` enum('Percentage','Flat') DEFAULT NULL,
  `discount_value` float DEFAULT NULL,
  `discount_amount` float DEFAULT NULL,
  `round_off` float DEFAULT NULL,
  `grand_total` float NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_bill`
--

LOCK TABLES `bar_bill` WRITE;
/*!40000 ALTER TABLE `bar_bill` DISABLE KEYS */;
INSERT INTO `bar_bill` VALUES (1,'BBILL-EDB850F7','2026-07-31','19:10:00',7,'BORD-2026-0007',5,'BT3',1,'Aditya Verma','9845019201',820,6,49.2,6,49.2,5,41,NULL,0,0,-0.4,959,'Paid','Paid',NULL,'12f86856-2dd4-4865-b03f-82580d40ff30','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'BBILL-E1ABE69A','2026-07-31','19:10:00',8,'BORD-2026-0008',6,'BT4',2,'Ritu Chawla','9845019202',1080,6,64.8,6,64.8,5,54,'Percentage',5,54,0.4,1210,'Paid','Paid',NULL,'e18feae2-04ea-4f57-9e79-2e512abcb85d','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,'BBILL-2321DB29','2026-07-31','19:10:00',9,'BORD-2026-0009',7,'BB1',3,'Suresh Pillai','9845019203',960,6,57.6,6,57.6,5,48,NULL,0,0,-0.2,1123,'Paid','Paid',NULL,'165f8e2c-c4d6-48c3-a533-c1c412b75119','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,'BBILL-6D0F9775','2026-07-31','19:10:00',10,'BORD-2026-0010',10,'RV1',4,'Meera Desai','9845019204',1530,6,91.8,6,91.8,5,76.5,NULL,0,0,-0.1,1790,'Paid','Paid',NULL,'4dae0663-fe42-4537-9e74-7536d9c48da8','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,'BBILL-963EDE98','2026-08-01','14:04:19',12,'BORD-8CBDD100',6,'BT4',NULL,NULL,NULL,780,6,46.8,6,46.8,0,0,NULL,0,0,0.4,874,'Paid','Paid',NULL,'9832ee1c-8059-4821-ae23-83abbc271fda','ACTIVE','1','2026-08-01 14:04:19','2026-08-01 14:04:39',NULL,'1','MAIN');
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
  `rate` float NOT NULL,
  `amount` float NOT NULL,
  `tax_amount` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_bill_item`
--

LOCK TABLES `bar_bill_item` WRITE;
/*!40000 ALTER TABLE `bar_bill_item` DISABLE KEYS */;
INSERT INTO `bar_bill_item` VALUES (1,1,12,10,'Old Fashioned',2,350,700,84,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,1,13,16,'Peanut Masala',1,120,120,14.4,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,2,14,11,'Mojito',2,280,560,67.2,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,2,15,13,'Margarita',1,300,300,36,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,2,16,17,'Nachos with Salsa',1,220,220,26.4,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,3,17,1,'Kingfisher Draft',4,180,720,86.4,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(7,3,18,16,'Peanut Masala',2,120,240,28.8,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(8,4,19,6,'Sparkling Wine',1,450,450,54,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(9,4,20,12,'Whisky Sour',2,320,640,76.8,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(10,4,21,17,'Nachos with Salsa',2,220,440,52.8,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(11,5,22,11,'Mojito',2,280,560,67.2,'ACTIVE','1','2026-08-01 14:04:19',NULL,NULL,'1','MAIN'),(12,5,23,17,'Nachos with Salsa',1,220,220,26.4,'ACTIVE','1','2026-08-01 14:04:19',NULL,NULL,'1','MAIN');
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
  `paid_amount` float NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_bill_payment`
--

LOCK TABLES `bar_bill_payment` WRITE;
/*!40000 ALTER TABLE `bar_bill_payment` DISABLE KEYS */;
INSERT INTO `bar_bill_payment` VALUES (1,1,2,959,NULL,'2026-07-31','19:12:00','Success',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,2,3,1210,NULL,'2026-07-31','19:12:00','Success',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,3,1,1123,NULL,'2026-07-31','19:12:00','Success',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,4,2,1790,NULL,'2026-07-31','19:12:00','Success',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,5,1,874,NULL,'2026-08-01','14:04:39','Success','Full settlement','ACTIVE','1','2026-08-01 14:04:39',NULL,NULL,'1','MAIN');
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
  `split_amount` float NOT NULL,
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
  `total_sales` float DEFAULT NULL,
  `total_tax` float DEFAULT NULL,
  `total_discount` float DEFAULT NULL,
  `total_service_charge` float DEFAULT NULL,
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
INSERT INTO `bar_floor` VALUES (1,'LOUNGE-FL','Bar Lounge',1,NULL,7,28,NULL,NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'ROOFTOP','Rooftop Bar',2,NULL,3,12,NULL,NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `loyalty_points` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_guest`
--

LOCK TABLES `bar_guest` WRITE;
/*!40000 ALTER TABLE `bar_guest` DISABLE KEYS */;
INSERT INTO `bar_guest` VALUES (1,'GST-BCD90EE9','Aditya','Verma','9845019201','aditya.verma@example.com','Regular',NULL,9,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(2,'GST-C90C5C77','Ritu','Chawla','9845019202','ritu.chawla@example.com','VIP',NULL,12,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(3,'GST-9AC16573','Suresh','Pillai','9845019203','suresh.pillai@example.com','Walk-In',NULL,11,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(4,'GST-2F5DA76C','Meera','Desai','9845019204','meera.desai@example.com','Regular',NULL,17,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(5,'GST-4B1EF9A9','Ibrahim','Ansari','9845019205','ibrahim.ansari@example.com','Walk-In',NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,'GST-AC25BBD0','Lakshmi','Krishnan','9845019206','lakshmi.krishnan@example.com','Hotel Guest',NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(7,'GST-A6549293','Yusuf','Sheikh','9845019207','yusuf.sheikh@example.com','Regular',NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(8,'GST-E253E77D','Pooja','Bhatt','9845019208','pooja.bhatt@example.com','VIP',NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_guest_feedback`
--

LOCK TABLES `bar_guest_feedback` WRITE;
/*!40000 ALTER TABLE `bar_guest_feedback` DISABLE KEYS */;
INSERT INTO `bar_guest_feedback` VALUES (1,1,7,5,'Great cocktails and friendly staff!','ACTIVE','1','2026-07-31 12:35:48','1','MAIN'),(2,3,9,4,'Nice ambience, will come again.','ACTIVE','1','2026-07-31 12:35:48','1','MAIN');
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
  `total_amount` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_guest_visit_history`
--

LOCK TABLES `bar_guest_visit_history` WRITE;
/*!40000 ALTER TABLE `bar_guest_visit_history` DISABLE KEYS */;
INSERT INTO `bar_guest_visit_history` VALUES (1,1,'2026-07-31',7,1,'At Table',959,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','1','MAIN'),(2,2,'2026-07-31',8,2,'At Table',1210,5,NULL,'ACTIVE','1','2026-07-31 12:35:48','1','MAIN'),(3,3,'2026-07-31',9,3,'At Table',1123,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','1','MAIN'),(4,4,'2026-07-31',10,4,'At Table',1790,5,NULL,'ACTIVE','1','2026-07-31 12:35:48','1','MAIN');
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
  `min_stock_level` float DEFAULT NULL,
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
INSERT INTO `bar_inventory_item` VALUES (1,'INV-C374D32F','Whisky','Bar Staples','Bottle',3,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'INV-6D55EAA8','Vodka','Bar Staples','Bottle',3,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,'INV-CB08F008','Rum','Bar Staples','Bottle',3,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,'INV-20146739','Red Wine','Bar Staples','Bottle',3,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,'INV-B32A82BB','White Wine','Bar Staples','Bottle',3,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,'INV-33A79837','Beer Keg','Bar Staples','Litre',3,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(7,'INV-54CA39EE','Soda Water','Bar Staples','Litre',3,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(8,'INV-477DE69C','Lime','Bar Staples','Nos',3,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(9,'INV-EB6B07CE','Mint Leaves','Bar Staples','Nos',3,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(10,'INV-18158F1B','Peanuts','Bar Staples','Nos',3,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `quantity` float NOT NULL,
  `unit_price` float NOT NULL,
  `total_amount` float NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_inventory_purchase`
--

LOCK TABLES `bar_inventory_purchase` WRITE;
/*!40000 ALTER TABLE `bar_inventory_purchase` DISABLE KEYS */;
INSERT INTO `bar_inventory_purchase` VALUES (1,1,12,800,9600,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,2,10,800,8000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,3,10,800,8000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,4,15,800,12000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,5,15,800,12000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,6,60,800,48000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(7,7,40,800,32000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(8,8,100,800,80000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(9,9,80,800,64000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(10,10,50,800,40000,'2026-07-28','Metro Beverages Distributors','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `available_quantity` float NOT NULL,
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
INSERT INTO `bar_inventory_stock` VALUES (1,1,NULL,12,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,2,NULL,10,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,3,NULL,10,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,4,NULL,15,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,5,NULL,15,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,6,NULL,60,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(7,7,NULL,40,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(8,8,NULL,100,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(9,9,NULL,80,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(10,10,NULL,50,'2026-07-31','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `quantity` float NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_inventory_stock_transaction`
--

LOCK TABLES `bar_inventory_stock_transaction` WRITE;
/*!40000 ALTER TABLE `bar_inventory_stock_transaction` DISABLE KEYS */;
INSERT INTO `bar_inventory_stock_transaction` VALUES (1,1,NULL,'IN',12,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(2,2,NULL,'IN',10,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(3,3,NULL,'IN',10,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(4,4,NULL,'IN',15,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(5,5,NULL,'IN',15,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(6,6,NULL,'IN',60,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(7,7,NULL,'IN',40,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(8,8,NULL,'IN',100,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(9,9,NULL,'IN',80,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN'),(10,10,NULL,'IN',50,'Purchase',NULL,'Opening stock','1','2026-07-31 12:35:48','1','MAIN');
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
  `total_amount` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_category`
--

LOCK TABLES `bar_menu_category` WRITE;
/*!40000 ALTER TABLE `bar_menu_category` DISABLE KEYS */;
INSERT INTO `bar_menu_category` VALUES (1,'CAT-BEER','Beer',NULL,1,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'CAT-WINE','Wine',NULL,1,2,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,'CAT-SPIRITS','Spirits',NULL,1,3,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,'CAT-COCKTAILS','Cocktails',NULL,2,4,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,'CAT-MOCKTAILS','Mocktails',NULL,2,5,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,'CAT-SNACKS','Bar Snacks',NULL,1,6,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `price` float NOT NULL,
  `cost_price` float DEFAULT NULL,
  `tax_percentage` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_item`
--

LOCK TABLES `bar_menu_item` WRITE;
/*!40000 ALTER TABLE `bar_menu_item` DISABLE KEYS */;
INSERT INTO `bar_menu_item` VALUES (1,'ITEM-32652343','Kingfisher Draft',NULL,1,NULL,180,63,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'ITEM-1B367BCC','Corona',NULL,1,NULL,250,87.5,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,'ITEM-02BFC052','Bira White',NULL,1,NULL,220,77,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,'ITEM-1D90E118','House Red Wine',NULL,2,NULL,350,122.5,12,1,8,1,'Available',NULL,1,NULL,0,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(5,'ITEM-A40D4C8D','House White Wine',NULL,2,NULL,350,122.5,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,'ITEM-D791D817','Sparkling Wine',NULL,2,NULL,450,157.5,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(7,'ITEM-A89B650B','Whisky (Single)',NULL,3,NULL,300,105,12,1,8,1,'Available',NULL,1,NULL,0,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(8,'ITEM-6F64C956','Vodka Shot',NULL,3,NULL,250,87.5,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(9,'ITEM-6BCC74FB','Rum Shot',NULL,3,NULL,220,77,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(10,'ITEM-999ECEFD','Old Fashioned',NULL,4,NULL,350,122.5,12,1,8,2,'Available',NULL,0,NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(11,'ITEM-3D811D8D','Mojito',NULL,4,NULL,280,98,12,1,8,2,'Available',NULL,0,NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(12,'ITEM-12D71A51','Whisky Sour',NULL,4,NULL,320,112,12,1,8,2,'Available',NULL,0,NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(13,'ITEM-A29E5333','Margarita',NULL,4,NULL,300,105,12,1,8,2,'Available',NULL,0,NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(14,'ITEM-C0A7FE73','Virgin Mojito',NULL,5,NULL,180,63,12,1,8,2,'Available',NULL,0,NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(15,'ITEM-5F6AC54F','Fruit Punch',NULL,5,NULL,150,52.5,12,1,8,2,'Available',NULL,0,NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(16,'ITEM-BD50762E','Peanut Masala',NULL,6,NULL,120,42,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(17,'ITEM-2E53CDDB','Nachos with Salsa',NULL,6,NULL,220,77,12,1,8,1,'Available',NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `price` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_modifier`
--

LOCK TABLES `bar_menu_modifier` WRITE;
/*!40000 ALTER TABLE `bar_menu_modifier` DISABLE KEYS */;
INSERT INTO `bar_menu_modifier` VALUES (1,10,'On the Rocks',NULL,'Add-on','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,11,'Extra Mint',20,'Add-on','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `price` float NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_menu_variant`
--

LOCK TABLES `bar_menu_variant` WRITE;
/*!40000 ALTER TABLE `bar_menu_variant` DISABLE KEYS */;
INSERT INTO `bar_menu_variant` VALUES (1,7,'30ml',300,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,7,'60ml',550,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,4,'Glass',350,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,4,'Bottle',1800,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `sub_total` float DEFAULT NULL,
  `tax_amount` float DEFAULT NULL,
  `service_charge` float DEFAULT NULL,
  `discount_type` enum('Percentage','Flat') DEFAULT NULL,
  `discount_value` float DEFAULT NULL,
  `discount_amount` float DEFAULT NULL,
  `grand_total` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order`
--

LOCK TABLES `bar_order` WRITE;
/*!40000 ALTER TABLE `bar_order` DISABLE KEYS */;
INSERT INTO `bar_order` VALUES (1,'BORD-2026-0001','2026-07-31','19:55:00','At Table',1,'BC1',1,'LOUNGE-FL',NULL,NULL,NULL,2,'301','Vishal Nair','New','Pending',480,0,0,NULL,0,0,480,NULL,'448a431a-81fd-4f1e-a020-0381b57a6c44','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(2,'BORD-2026-0002','2026-07-31','19:57:00','At Table',3,'BT1',1,'LOUNGE-FL',NULL,NULL,NULL,2,'301','Vishal Nair','New','Pending',780,0,0,NULL,0,0,780,NULL,'08279e2e-3a6b-447d-8151-bc90915e45bb','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(3,'BORD-2026-0003','2026-07-31','19:58:00','At Table',8,'RT1',2,'ROOFTOP',NULL,NULL,NULL,2,'301','Vishal Nair','New','Pending',700,0,0,NULL,0,0,700,NULL,'b55a1430-7510-4b40-a036-3a2da33059d7','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(4,'BORD-2026-0004','2026-07-31','19:35:00','At Table',2,'BC2',1,'LOUNGE-FL',NULL,NULL,NULL,2,'301','Vishal Nair','In Progress','Pending',700,0,0,NULL,0,0,700,NULL,'41c478e1-013b-4fa4-8672-ae5fd7944dc9','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(5,'BORD-2026-0005','2026-07-31','19:35:00','At Table',4,'BT2',1,'LOUNGE-FL',NULL,NULL,NULL,2,'301','Vishal Nair','In Progress','Pending',840,0,0,NULL,0,0,840,NULL,'c16d52fb-25f1-4f94-ad89-acf8744acfcd','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(6,'BORD-2026-0006','2026-07-31','19:35:00','At Table',9,'RT2',2,'ROOFTOP',NULL,NULL,NULL,2,'301','Vishal Nair','In Progress','Pending',740,0,0,NULL,0,0,740,NULL,'f5775781-c162-43ec-965e-8e1d790f962c','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(7,'BORD-2026-0007','2026-07-31','18:45:00','At Table',5,'BT3',1,'LOUNGE-FL',1,'Aditya Verma','9845019201',2,'301','Vishal Nair','Completed','Paid',820,0,0,NULL,0,0,820,NULL,'97b37822-356e-429e-a963-f484c1bdf5ba','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(8,'BORD-2026-0008','2026-07-31','18:45:00','At Table',6,'BT4',1,'LOUNGE-FL',2,'Ritu Chawla','9845019202',2,'301','Vishal Nair','Completed','Paid',1080,0,0,NULL,0,0,1080,NULL,'93e14e34-36a6-465d-8c98-207502f23e89','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(9,'BORD-2026-0009','2026-07-31','18:45:00','At Table',7,'BB1',1,'LOUNGE-FL',3,'Suresh Pillai','9845019203',2,'301','Vishal Nair','Completed','Paid',960,0,0,NULL,0,0,960,NULL,'d50a81f0-80b1-42cc-a13f-d51b0ba24314','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(10,'BORD-2026-0010','2026-07-31','18:45:00','At Table',10,'RV1',2,'ROOFTOP',4,'Meera Desai','9845019204',2,'301','Vishal Nair','Completed','Paid',1530,0,0,NULL,0,0,1530,NULL,'257fff6e-9fe7-49a6-971b-c0092f60bb55','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(11,'BORD-AEA1CC87','2026-08-01','09:54:32','At Table',10,'RV1',2,'ROOFTOP',NULL,NULL,NULL,NULL,NULL,NULL,'New','Pending',0,0,0,NULL,0,0,0,NULL,'3b19d884-8508-411e-94e9-75795851683b','ACTIVE','1','2026-08-01 09:54:32',NULL,NULL,'1','MAIN'),(12,'BORD-8CBDD100','2026-08-01','14:03:52','At Table',6,'BT4',1,'LOUNGE-FL',NULL,NULL,NULL,2,NULL,NULL,'Completed','Paid',780,0,0,NULL,0,0,780,NULL,'28fb2a2f-6136-4454-9500-ed4917a8baa9','ACTIVE','1','2026-08-01 14:03:51','2026-08-01 14:04:39','1','1','MAIN');
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
  `price` float NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order_item`
--

LOCK TABLES `bar_order_item` WRITE;
/*!40000 ALTER TABLE `bar_order_item` DISABLE KEYS */;
INSERT INTO `bar_order_item` VALUES (1,1,1,1,2,180,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,1,16,1,1,120,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,2,11,2,2,280,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,2,17,1,1,220,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,3,4,1,2,350,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,4,10,2,2,350,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(7,5,12,2,1,320,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(8,5,13,2,1,300,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(9,5,17,1,1,220,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(10,6,2,1,2,250,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(11,6,16,1,2,120,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(12,7,10,2,2,350,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(13,7,16,1,1,120,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(14,8,11,2,2,280,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(15,8,13,2,1,300,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(16,8,17,1,1,220,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(17,9,1,1,4,180,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(18,9,16,1,2,120,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(19,10,6,1,1,450,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(20,10,12,2,2,320,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(21,10,17,1,2,220,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(22,12,11,2,2,280,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-08-01 14:04:00','2026-08-01 14:04:09',NULL,'1','MAIN'),(23,12,17,1,1,220,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-08-01 14:04:00','2026-08-01 14:04:09',NULL,'1','MAIN');
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
  `price` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order_ticket`
--

LOCK TABLES `bar_order_ticket` WRITE;
/*!40000 ALTER TABLE `bar_order_ticket` DISABLE KEYS */;
INSERT INTO `bar_order_ticket` VALUES (1,'BOT-1E13DF24',4,NULL,'Original',2,'In Progress','Normal',0,NULL,'Vishal Nair','2026-07-31 19:40:00',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'BOT-CF49EB99',5,NULL,'Original',2,'In Progress','Normal',0,NULL,'Vishal Nair','2026-07-31 19:40:00',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,'BOT-85094CCE',6,NULL,'Original',1,'In Progress','Normal',0,NULL,'Vishal Nair','2026-07-31 19:40:00',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,'BOT-3FE4EE4B',7,NULL,'Original',2,'Completed','Normal',0,NULL,'Vishal Nair','2026-07-31 18:50:00','Vishal Nair','2026-07-31 19:05:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,'BOT-AB6BADBE',8,NULL,'Original',2,'Completed','Normal',0,NULL,'Vishal Nair','2026-07-31 18:50:00','Vishal Nair','2026-07-31 19:05:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,'BOT-E5695C7F',9,NULL,'Original',1,'Completed','Normal',0,NULL,'Vishal Nair','2026-07-31 18:50:00','Vishal Nair','2026-07-31 19:05:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(7,'BOT-B862AF0C',10,NULL,'Original',1,'Completed','Normal',0,NULL,'Vishal Nair','2026-07-31 18:50:00','Vishal Nair','2026-07-31 19:05:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(8,'BOT-29785A02',12,NULL,'Original',2,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-08-01 14:04:09',NULL,NULL,'1','MAIN'),(9,'BOT-BBC3AB6F',12,NULL,'Original',1,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-08-01 14:04:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_order_ticket_item`
--

LOCK TABLES `bar_order_ticket_item` WRITE;
/*!40000 ALTER TABLE `bar_order_ticket_item` DISABLE KEYS */;
INSERT INTO `bar_order_ticket_item` VALUES (1,1,6,'Preparing','2026-07-31 19:42:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,2,7,'Preparing','2026-07-31 19:42:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,2,8,'Preparing','2026-07-31 19:42:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,2,9,'Preparing','2026-07-31 19:42:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,3,10,'Preparing','2026-07-31 19:42:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,3,11,'Preparing','2026-07-31 19:42:00',NULL,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(7,4,12,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(8,4,13,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(9,5,14,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(10,5,15,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(11,5,16,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(12,6,17,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(13,6,18,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(14,7,19,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(15,7,20,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(16,7,21,'Ready','2026-07-31 18:52:00','2026-07-31 19:04:00','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(17,8,22,'Pending',NULL,NULL,'ACTIVE','1','2026-08-01 14:04:09',NULL,NULL,'1','MAIN'),(18,9,23,'Pending',NULL,NULL,'ACTIVE','1','2026-08-01 14:04:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_payment_method`
--

LOCK TABLES `bar_payment_method` WRITE;
/*!40000 ALTER TABLE `bar_payment_method` DISABLE KEYS */;
INSERT INTO `bar_payment_method` VALUES (1,'Cash','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'Card','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,'UPI','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `total_amount` float DEFAULT NULL,
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
  `quantity_required` float NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_recipe`
--

LOCK TABLES `bar_recipe` WRITE;
/*!40000 ALTER TABLE `bar_recipe` DISABLE KEYS */;
INSERT INTO `bar_recipe` VALUES (1,10,1,0.06,'Bottle','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,11,3,0.06,'Bottle','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,11,9,6,'Nos','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,11,7,0.1,'Litre','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,12,1,0.06,'Bottle','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,1,6,0.5,'Litre','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_settings`
--

LOCK TABLES `bar_settings` WRITE;
/*!40000 ALTER TABLE `bar_settings` DISABLE KEYS */;
INSERT INTO `bar_settings` VALUES (1,'opening_time','17:00','OperatingHours','Bar daily opening time','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'closing_time','01:00','OperatingHours','Bar daily closing time','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,'cgst_percentage','6','Tax','Default CGST applied on bills','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(4,'sgst_percentage','6','Tax','Default SGST applied on bills','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(5,'service_charge_percentage','5','ServiceCharge','Default service charge applied on bills','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(6,'bill_number_prefix','BBILL','Numbering','Prefix used for generated bill numbers','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `sales_target` float DEFAULT NULL,
  `actual_sales` float DEFAULT NULL,
  `clock_in_at` datetime DEFAULT NULL,
  `clock_out_at` datetime DEFAULT NULL,
  `opening_cash_float` float DEFAULT NULL,
  `closing_cash_amount` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bar_staff_assignment`
--

LOCK TABLES `bar_staff_assignment` WRITE;
/*!40000 ALTER TABLE `bar_staff_assignment` DISABLE KEYS */;
INSERT INTO `bar_staff_assignment` VALUES (1,301,'Vishal Nair','Bartender','2026-07-31','17:00:00','01:00:00',1,12000,0,'2026-07-31 16:45:00',NULL,NULL,NULL,'On Shift','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,302,'Rohit Sen','Bartender','2026-07-31','17:00:00','01:00:00',1,12000,0,'2026-07-31 16:45:00',NULL,NULL,NULL,'On Shift','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(3,303,'Kavya Menon','Cashier','2026-07-31','17:00:00','01:00:00',1,12000,0,'2026-07-31 16:45:00',NULL,1500,NULL,'On Shift','ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
  `total_sales` float DEFAULT NULL,
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
INSERT INTO `bar_station` VALUES (1,'STN-MAIN','Main Bar',NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN'),(2,'STN-LOUNGE','Lounge Bar',NULL,1,'ACTIVE','1','2026-07-31 12:35:48',NULL,NULL,'1','MAIN');
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
INSERT INTO `bar_table` VALUES (1,'BC1','Counter BC1',1,1,'LOUNGE-FL','Counter',2,1,NULL,NULL,'Occupied','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(2,'BC2','Counter BC2',2,1,'LOUNGE-FL','Counter',2,4,NULL,NULL,'Occupied','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(3,'BT1','Table BT1',3,1,'LOUNGE-FL','Table',4,2,NULL,NULL,'Occupied','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(4,'BT2','Table BT2',4,1,'LOUNGE-FL','Table',4,5,NULL,NULL,'Occupied','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(5,'BT3','Table BT3',5,1,'LOUNGE-FL','Table',4,NULL,NULL,NULL,'Cleaning','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(6,'BT4','Table BT4',6,1,'LOUNGE-FL','Table',4,NULL,NULL,NULL,'Cleaning','ACTIVE','1','2026-07-31 12:35:48','2026-08-01 14:04:39','1','1','MAIN'),(7,'BB1','Booth BB1',7,1,'LOUNGE-FL','Booth',6,NULL,NULL,NULL,'Cleaning','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(8,'RT1','Table RT1',8,2,'ROOFTOP','Table',4,3,NULL,NULL,'Occupied','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(9,'RT2','Table RT2',9,2,'ROOFTOP','Table',4,6,NULL,NULL,'Occupied','ACTIVE','1','2026-07-31 12:35:48','2026-07-31 12:35:48',NULL,'1','MAIN'),(10,'RV1','VIP Lounge RV1',10,2,'ROOFTOP','VIP Lounge',8,11,NULL,NULL,'Occupied','ACTIVE','1','2026-07-31 12:35:48','2026-08-01 09:54:32','1','1','MAIN');
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

-- Dump completed on 2026-08-04 14:36:05
