-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: hotelerp_restaurant
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
-- Current Database: `hotelerp_restaurant`
--

/*!40000 DROP DATABASE IF EXISTS `hotelerp_restaurant`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hotelerp_restaurant` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hotelerp_restaurant`;

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
INSERT INTO `alembic_version` VALUES ('87d058e6824d');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category_sales_report`
--

DROP TABLE IF EXISTS `category_sales_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category_sales_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `category_id` int NOT NULL,
  `category_name` varchar(100) NOT NULL,
  `total_quantity` int DEFAULT NULL,
  `total_sales` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_category_sales_report_line` (`company_id`,`branch_id`,`report_date`,`category_id`),
  KEY `ix_category_sales_report_company_id` (`company_id`),
  KEY `ix_category_sales_report_category_id` (`category_id`),
  KEY `ix_category_sales_report_branch_id` (`branch_id`),
  KEY `ix_category_sales_report_report_date` (`report_date`),
  KEY `ix_category_sales_report_status` (`status`),
  KEY `ix_category_sales_report_id` (`id`),
  CONSTRAINT `category_sales_report_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `menu_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category_sales_report`
--

LOCK TABLES `category_sales_report` WRITE;
/*!40000 ALTER TABLE `category_sales_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `category_sales_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `combo_deal`
--

DROP TABLE IF EXISTS `combo_deal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `combo_deal` (
  `id` int NOT NULL AUTO_INCREMENT,
  `combo_code` varchar(100) NOT NULL,
  `combo_name` varchar(150) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `combo_price` decimal(12,2) NOT NULL,
  `valid_from` datetime DEFAULT NULL,
  `valid_to` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  `active_combo_name` varchar(150) GENERATED ALWAYS AS ((case when ((`status` = _utf8mb4'ACTIVE') and (`is_active` = 1)) then `combo_name` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_combo_code` (`company_id`,`branch_id`,`combo_code`),
  UNIQUE KEY `uq_restaurant_combo_active_name` (`company_id`,`branch_id`,`active_combo_name`),
  KEY `ix_combo_deal_company_id` (`company_id`),
  KEY `ix_combo_deal_status` (`status`),
  KEY `ix_combo_deal_id` (`id`),
  KEY `ix_combo_deal_branch_id` (`branch_id`),
  KEY `ix_combo_deal_combo_code` (`combo_code`),
  KEY `ix_combo_deal_combo_name` (`combo_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combo_deal`
--

LOCK TABLES `combo_deal` WRITE;
/*!40000 ALTER TABLE `combo_deal` DISABLE KEYS */;
/*!40000 ALTER TABLE `combo_deal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `combo_item`
--

DROP TABLE IF EXISTS `combo_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `combo_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `combo_id` int NOT NULL,
  `menu_id` int NOT NULL,
  `quantity` int NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_combo_item` (`combo_id`,`menu_id`),
  KEY `ix_combo_item_id` (`id`),
  KEY `ix_combo_item_company_id` (`company_id`),
  KEY `ix_combo_item_menu_id` (`menu_id`),
  KEY `ix_combo_item_branch_id` (`branch_id`),
  KEY `ix_combo_item_combo_id` (`combo_id`),
  KEY `ix_combo_item_status` (`status`),
  CONSTRAINT `combo_item_ibfk_1` FOREIGN KEY (`combo_id`) REFERENCES `combo_deal` (`id`),
  CONSTRAINT `combo_item_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `restaurant_menu` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combo_item`
--

LOCK TABLES `combo_item` WRITE;
/*!40000 ALTER TABLE `combo_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `combo_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `daily_sales_report`
--

DROP TABLE IF EXISTS `daily_sales_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_sales_report` (
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
  UNIQUE KEY `uq_daily_sales_report_date` (`company_id`,`branch_id`,`report_date`),
  KEY `ix_daily_sales_report_id` (`id`),
  KEY `ix_daily_sales_report_report_date` (`report_date`),
  KEY `ix_daily_sales_report_company_id` (`company_id`),
  KEY `ix_daily_sales_report_branch_id` (`branch_id`),
  KEY `ix_daily_sales_report_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_sales_report`
--

LOCK TABLES `daily_sales_report` WRITE;
/*!40000 ALTER TABLE `daily_sales_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `daily_sales_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guest`
--

DROP TABLE IF EXISTS `guest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guest_code` varchar(100) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `mobile` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `guest_type` enum('Walk-In','Regular','VIP','Hotel Guest') NOT NULL,
  `food_preferences` json DEFAULT NULL,
  `special_notes` varchar(255) DEFAULT NULL,
  `loyalty_points` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  `active_mobile` varchar(20) GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `mobile` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_guest_guest_code` (`guest_code`),
  UNIQUE KEY `uq_restaurant_guest_active_mobile` (`company_id`,`active_mobile`),
  KEY `ix_guest_email` (`email`),
  KEY `ix_guest_first_name` (`first_name`),
  KEY `ix_guest_guest_type` (`guest_type`),
  KEY `ix_guest_company_id` (`company_id`),
  KEY `ix_guest_last_name` (`last_name`),
  KEY `ix_guest_branch_id` (`branch_id`),
  KEY `ix_guest_status` (`status`),
  KEY `ix_guest_mobile` (`mobile`),
  KEY `ix_guest_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest`
--

LOCK TABLES `guest` WRITE;
/*!40000 ALTER TABLE `guest` DISABLE KEYS */;
INSERT INTO `guest` (`id`, `guest_code`, `first_name`, `last_name`, `mobile`, `email`, `guest_type`, `food_preferences`, `special_notes`, `loyalty_points`, `status`, `created_by`, `created_at`, `updated_at`, `updated_by`, `company_id`, `branch_id`) VALUES (1,'RG-0001','Deepak','Anand','+14155550001','deepak.anand@gmail.com','Regular',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,'RG-0002','Sridevi','Raman','+442079460002','sridevi.raman@gmail.com','VIP',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,'RG-0003','Michael','Fernandes','+971501000003','michael.fernandes@gmail.com','Walk-In',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(5,'RG-0005','Ganesh','Iyer','+14155550005','ganesh.iyer@gmail.com','VIP',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(6,'RG-0006','Sarah','Thomas','+442079460006','sarah.thomas@gmail.com','Walk-In',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(7,'RG-0007','Rohan','Mehta','+971501000007','rohan.mehta@gmail.com','Hotel Guest',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(8,'RG-0008','Priya','Nair','+919876500008','priya.nair@gmail.com','Hotel Guest',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(13,'GST-06B8FC58','ZZ3210',NULL,'+919876543210',NULL,'Walk-In','null',NULL,0.00,'ACTIVE','1','2026-10-11 21:52:29',NULL,NULL,'1','MAIN'),(14,'GST-3CC95459','ZZ5432',NULL,'+919198765432',NULL,'Walk-In','null',NULL,0.00,'ACTIVE','1','2026-10-11 21:53:03',NULL,NULL,'1','MAIN');
/*!40000 ALTER TABLE `guest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guest_address`
--

DROP TABLE IF EXISTS `guest_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest_address` (
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
  KEY `ix_guest_address_state` (`state`),
  KEY `ix_guest_address_company_id` (`company_id`),
  KEY `ix_guest_address_id` (`id`),
  KEY `ix_guest_address_guest_id` (`guest_id`),
  KEY `ix_guest_address_country` (`country`),
  KEY `ix_guest_address_status` (`status`),
  KEY `ix_guest_address_branch_id` (`branch_id`),
  KEY `ix_guest_address_city` (`city`),
  CONSTRAINT `guest_address_ibfk_1` FOREIGN KEY (`guest_id`) REFERENCES `guest` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest_address`
--

LOCK TABLES `guest_address` WRITE;
/*!40000 ALTER TABLE `guest_address` DISABLE KEYS */;
/*!40000 ALTER TABLE `guest_address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guest_feedback`
--

DROP TABLE IF EXISTS `guest_feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest_feedback` (
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
  KEY `ix_guest_feedback_company_id` (`company_id`),
  KEY `ix_guest_feedback_order_id` (`order_id`),
  KEY `ix_guest_feedback_guest_id` (`guest_id`),
  KEY `ix_guest_feedback_id` (`id`),
  KEY `ix_guest_feedback_branch_id` (`branch_id`),
  KEY `ix_guest_feedback_status` (`status`),
  CONSTRAINT `guest_feedback_ibfk_1` FOREIGN KEY (`guest_id`) REFERENCES `guest` (`id`),
  CONSTRAINT `guest_feedback_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `restaurant_order` (`id`),
  CONSTRAINT `ck_guest_feedback_rating` CHECK (((`rating` >= 1) and (`rating` <= 5)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest_feedback`
--

LOCK TABLES `guest_feedback` WRITE;
/*!40000 ALTER TABLE `guest_feedback` DISABLE KEYS */;
/*!40000 ALTER TABLE `guest_feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guest_visit_history`
--

DROP TABLE IF EXISTS `guest_visit_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest_visit_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guest_id` int NOT NULL,
  `visit_date` date NOT NULL,
  `order_id` int DEFAULT NULL,
  `bill_id` int DEFAULT NULL,
  `visit_type` enum('Dine-In','Takeaway','Delivery','Room Service') NOT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `rating` int DEFAULT NULL,
  `feedback` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_guest_visit_history_visit_type` (`visit_type`),
  KEY `ix_guest_visit_history_visit_date` (`visit_date`),
  KEY `ix_guest_visit_history_branch_id` (`branch_id`),
  KEY `ix_guest_visit_history_company_id` (`company_id`),
  KEY `ix_guest_visit_history_order_id` (`order_id`),
  KEY `ix_guest_visit_history_bill_id` (`bill_id`),
  KEY `ix_guest_visit_history_id` (`id`),
  KEY `ix_guest_visit_history_guest_id` (`guest_id`),
  KEY `ix_guest_visit_history_status` (`status`),
  CONSTRAINT `guest_visit_history_ibfk_1` FOREIGN KEY (`guest_id`) REFERENCES `guest` (`id`),
  CONSTRAINT `guest_visit_history_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `restaurant_order` (`id`),
  CONSTRAINT `guest_visit_history_ibfk_3` FOREIGN KEY (`bill_id`) REFERENCES `restaurant_bill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest_visit_history`
--

LOCK TABLES `guest_visit_history` WRITE;
/*!40000 ALTER TABLE `guest_visit_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `guest_visit_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_item`
--

DROP TABLE IF EXISTS `inventory_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_code` varchar(100) NOT NULL,
  `item_name` varchar(150) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `unit` enum('Kg','Gram','Litre','ml','Nos') NOT NULL,
  `min_stock_level` decimal(12,3) DEFAULT NULL,
  `is_perishable` tinyint(1) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  `active_item_name` varchar(150) GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `item_name` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_inventory_item_code` (`company_id`,`branch_id`,`item_code`),
  UNIQUE KEY `uq_restaurant_inventory_active_name` (`company_id`,`active_item_name`),
  KEY `ix_inventory_item_unit` (`unit`),
  KEY `ix_inventory_item_id` (`id`),
  KEY `ix_inventory_item_status` (`status`),
  KEY `ix_inventory_item_branch_id` (`branch_id`),
  KEY `ix_inventory_item_item_code` (`item_code`),
  KEY `ix_inventory_item_item_name` (`item_name`),
  KEY `ix_inventory_item_category` (`category`),
  KEY `ix_inventory_item_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_item`
--

LOCK TABLES `inventory_item` WRITE;
/*!40000 ALTER TABLE `inventory_item` DISABLE KEYS */;
INSERT INTO `inventory_item` (`id`, `item_code`, `item_name`, `category`, `unit`, `min_stock_level`, `is_perishable`, `status`, `created_by`, `created_at`, `updated_at`, `updated_by`, `company_id`, `branch_id`) VALUES (1,'RIN-001','Basmati Rice','Kitchen Store','Kg',11.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,'RIN-002','Paneer','Kitchen Store','Kg',12.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,'RIN-003','Chicken','Kitchen Store','Kg',13.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(4,'RIN-004','Prawns','Kitchen Store','Kg',14.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(5,'RIN-005','Refined Oil','Kitchen Store','Litre',15.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(6,'RIN-006','Wheat Flour','Kitchen Store','Kg',16.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(7,'RIN-007','Onion','Kitchen Store','Kg',17.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(8,'RIN-008','Tomato','Kitchen Store','Kg',18.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(9,'RIN-009','Fresh Cream','Kitchen Store','Litre',19.000,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(11,'INV-4CA2E9E1','ZZSTOCK-1791728363',NULL,'Kg',5.000,0,'ACTIVE','1','2026-10-11 19:49:23',NULL,NULL,'1','MAIN');
/*!40000 ALTER TABLE `inventory_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_purchase`
--

DROP TABLE IF EXISTS `inventory_purchase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory_purchase` (
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
  KEY `ix_inventory_purchase_purchase_date` (`purchase_date`),
  KEY `ix_inventory_purchase_company_id` (`company_id`),
  KEY `ix_inventory_purchase_status` (`status`),
  KEY `ix_inventory_purchase_id` (`id`),
  KEY `ix_inventory_purchase_inventory_item_id` (`inventory_item_id`),
  KEY `ix_inventory_purchase_branch_id` (`branch_id`),
  CONSTRAINT `inventory_purchase_ibfk_1` FOREIGN KEY (`inventory_item_id`) REFERENCES `inventory_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_purchase`
--

LOCK TABLES `inventory_purchase` WRITE;
/*!40000 ALTER TABLE `inventory_purchase` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_purchase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_stock`
--

DROP TABLE IF EXISTS `inventory_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory_stock` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_item_id` int NOT NULL,
  `kitchen_id` int DEFAULT NULL,
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
  UNIQUE KEY `uq_inventory_stock_location` (`inventory_item_id`,`kitchen_id`,`company_id`,`branch_id`),
  KEY `ix_inventory_stock_id` (`id`),
  KEY `ix_inventory_stock_inventory_item_id` (`inventory_item_id`),
  KEY `ix_inventory_stock_status` (`status`),
  KEY `ix_inventory_stock_branch_id` (`branch_id`),
  KEY `ix_inventory_stock_kitchen_id` (`kitchen_id`),
  KEY `ix_inventory_stock_company_id` (`company_id`),
  CONSTRAINT `inventory_stock_ibfk_1` FOREIGN KEY (`inventory_item_id`) REFERENCES `inventory_item` (`id`),
  CONSTRAINT `inventory_stock_ibfk_2` FOREIGN KEY (`kitchen_id`) REFERENCES `kitchen` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_stock`
--

LOCK TABLES `inventory_stock` WRITE;
/*!40000 ALTER TABLE `inventory_stock` DISABLE KEYS */;
INSERT INTO `inventory_stock` VALUES (1,1,1,46.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,2,1,52.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,3,1,58.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(4,4,1,64.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(5,5,1,70.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(6,6,1,76.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(7,7,1,82.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(8,8,1,88.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(9,9,1,94.000,'2026-10-09','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `inventory_stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_stock_transaction`
--

DROP TABLE IF EXISTS `inventory_stock_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory_stock_transaction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_item_id` int NOT NULL,
  `kitchen_id` int DEFAULT NULL,
  `transaction_type` enum('IN','OUT','ADJUSTMENT','WASTE') NOT NULL,
  `quantity` decimal(12,3) NOT NULL,
  `reference_type` enum('Purchase','KOT','Manual','Transfer') DEFAULT NULL,
  `reference_id` varchar(100) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_inventory_stock_transaction_branch_id` (`branch_id`),
  KEY `ix_inventory_stock_transaction_id` (`id`),
  KEY `ix_inventory_stock_transaction_kitchen_id` (`kitchen_id`),
  KEY `ix_inventory_stock_transaction_company_id` (`company_id`),
  KEY `ix_inventory_stock_transaction_inventory_item_id` (`inventory_item_id`),
  KEY `ix_inventory_stock_transaction_transaction_type` (`transaction_type`),
  CONSTRAINT `inventory_stock_transaction_ibfk_1` FOREIGN KEY (`inventory_item_id`) REFERENCES `inventory_item` (`id`),
  CONSTRAINT `inventory_stock_transaction_ibfk_2` FOREIGN KEY (`kitchen_id`) REFERENCES `kitchen` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_stock_transaction`
--

LOCK TABLES `inventory_stock_transaction` WRITE;
/*!40000 ALTER TABLE `inventory_stock_transaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_stock_transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_sales_report`
--

DROP TABLE IF EXISTS `item_sales_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_sales_report` (
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
  UNIQUE KEY `uq_item_sales_report_line` (`company_id`,`branch_id`,`report_date`,`menu_id`),
  KEY `ix_item_sales_report_category_id` (`category_id`),
  KEY `ix_item_sales_report_branch_id` (`branch_id`),
  KEY `ix_item_sales_report_company_id` (`company_id`),
  KEY `ix_item_sales_report_report_date` (`report_date`),
  KEY `ix_item_sales_report_menu_id` (`menu_id`),
  KEY `ix_item_sales_report_id` (`id`),
  KEY `ix_item_sales_report_status` (`status`),
  CONSTRAINT `item_sales_report_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `restaurant_menu` (`id`),
  CONSTRAINT `item_sales_report_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `menu_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_sales_report`
--

LOCK TABLES `item_sales_report` WRITE;
/*!40000 ALTER TABLE `item_sales_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `item_sales_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kitchen`
--

DROP TABLE IF EXISTS `kitchen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kitchen` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kitchen_code` varchar(100) NOT NULL,
  `kitchen_name` varchar(100) NOT NULL,
  `kitchen_type` enum('Main','Grill','Dessert') NOT NULL,
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
  UNIQUE KEY `uq_kitchen_code` (`company_id`,`branch_id`,`kitchen_code`),
  KEY `ix_kitchen_kitchen_name` (`kitchen_name`),
  KEY `ix_kitchen_branch_id` (`branch_id`),
  KEY `ix_kitchen_id` (`id`),
  KEY `ix_kitchen_kitchen_code` (`kitchen_code`),
  KEY `ix_kitchen_status` (`status`),
  KEY `ix_kitchen_kitchen_type` (`kitchen_type`),
  KEY `ix_kitchen_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen`
--

LOCK TABLES `kitchen` WRITE;
/*!40000 ALTER TABLE `kitchen` DISABLE KEYS */;
INSERT INTO `kitchen` VALUES (1,'KIT-MAIN','Main Kitchen','Main','KIT-MAIN-PRN',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,'KIT-GRILL','Grill Kitchen','Grill','KIT-GRILL-PRN',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,'KIT-DESS','Dessert Kitchen','Dessert','KIT-DESS-PRN',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `kitchen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kitchen_order_item`
--

DROP TABLE IF EXISTS `kitchen_order_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kitchen_order_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kot_id` int NOT NULL,
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
  KEY `ix_kitchen_order_item_status` (`status`),
  KEY `ix_kitchen_order_item_order_item_id` (`order_item_id`),
  KEY `ix_kitchen_order_item_branch_id` (`branch_id`),
  KEY `ix_kitchen_order_item_preparation_status` (`preparation_status`),
  KEY `ix_kitchen_order_item_id` (`id`),
  KEY `ix_kitchen_order_item_company_id` (`company_id`),
  KEY `ix_kitchen_order_item_kot_id` (`kot_id`),
  CONSTRAINT `kitchen_order_item_ibfk_1` FOREIGN KEY (`kot_id`) REFERENCES `kitchen_order_ticket` (`id`),
  CONSTRAINT `kitchen_order_item_ibfk_2` FOREIGN KEY (`order_item_id`) REFERENCES `restaurant_order_item` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_order_item`
--

LOCK TABLES `kitchen_order_item` WRITE;
/*!40000 ALTER TABLE `kitchen_order_item` DISABLE KEYS */;
INSERT INTO `kitchen_order_item` VALUES (1,1,34,'Pending',NULL,NULL,'ACTIVE','1','2026-10-11 20:00:06',NULL,NULL,'1','MAIN'),(2,2,35,'Pending',NULL,NULL,'ACTIVE','1','2026-10-11 20:04:20',NULL,NULL,'1','MAIN'),(3,3,36,'Pending',NULL,NULL,'ACTIVE','1','2026-10-12 14:16:28',NULL,NULL,'1','MAIN'),(4,4,37,'Pending',NULL,NULL,'ACTIVE','1','2026-10-12 14:20:47',NULL,NULL,'1','MAIN');
/*!40000 ALTER TABLE `kitchen_order_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kitchen_order_modification`
--

DROP TABLE IF EXISTS `kitchen_order_modification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kitchen_order_modification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kot_id` int NOT NULL,
  `original_kot_item_id` int DEFAULT NULL,
  `modification_type` enum('Add','Remove','Change') NOT NULL,
  `modification_details` varchar(255) DEFAULT NULL,
  `modified_by` varchar(100) NOT NULL,
  `modification_datetime` datetime DEFAULT (now()),
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_kitchen_order_modification_id` (`id`),
  KEY `ix_kitchen_order_modification_modification_type` (`modification_type`),
  KEY `ix_kitchen_order_modification_company_id` (`company_id`),
  KEY `ix_kitchen_order_modification_branch_id` (`branch_id`),
  KEY `ix_kitchen_order_modification_original_kot_item_id` (`original_kot_item_id`),
  KEY `ix_kitchen_order_modification_status` (`status`),
  KEY `ix_kitchen_order_modification_kot_id` (`kot_id`),
  CONSTRAINT `kitchen_order_modification_ibfk_1` FOREIGN KEY (`kot_id`) REFERENCES `kitchen_order_ticket` (`id`),
  CONSTRAINT `kitchen_order_modification_ibfk_2` FOREIGN KEY (`original_kot_item_id`) REFERENCES `kitchen_order_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_order_modification`
--

LOCK TABLES `kitchen_order_modification` WRITE;
/*!40000 ALTER TABLE `kitchen_order_modification` DISABLE KEYS */;
/*!40000 ALTER TABLE `kitchen_order_modification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kitchen_order_ticket`
--

DROP TABLE IF EXISTS `kitchen_order_ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kitchen_order_ticket` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kot_number` varchar(100) NOT NULL,
  `order_id` int NOT NULL,
  `parent_kot_id` int DEFAULT NULL,
  `kot_type` enum('Original','Supplementary','Modification','Cancellation') NOT NULL,
  `kitchen_id` int NOT NULL,
  `kot_status` enum('New','Acknowledged','In Progress','Completed','Cancelled') NOT NULL,
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
  UNIQUE KEY `uq_kot_number` (`company_id`,`branch_id`,`kot_number`),
  KEY `ix_kitchen_order_ticket_kot_type` (`kot_type`),
  KEY `ix_kitchen_order_ticket_status` (`status`),
  KEY `ix_kitchen_order_ticket_branch_id` (`branch_id`),
  KEY `ix_kitchen_order_ticket_id` (`id`),
  KEY `ix_kitchen_order_ticket_kitchen_id` (`kitchen_id`),
  KEY `ix_kitchen_order_ticket_parent_kot_id` (`parent_kot_id`),
  KEY `ix_kitchen_order_ticket_kot_number` (`kot_number`),
  KEY `ix_kitchen_order_ticket_company_id` (`company_id`),
  KEY `ix_kitchen_order_ticket_order_id` (`order_id`),
  KEY `ix_kitchen_order_ticket_kot_status` (`kot_status`),
  CONSTRAINT `kitchen_order_ticket_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `restaurant_order` (`id`),
  CONSTRAINT `kitchen_order_ticket_ibfk_2` FOREIGN KEY (`parent_kot_id`) REFERENCES `kitchen_order_ticket` (`id`),
  CONSTRAINT `kitchen_order_ticket_ibfk_3` FOREIGN KEY (`kitchen_id`) REFERENCES `kitchen` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_order_ticket`
--

LOCK TABLES `kitchen_order_ticket` WRITE;
/*!40000 ALTER TABLE `kitchen_order_ticket` DISABLE KEYS */;
INSERT INTO `kitchen_order_ticket` VALUES (1,'KOT-8AEDC853',9,NULL,'Original',1,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-10-11 20:00:06',NULL,NULL,'1','MAIN'),(2,'KOT-5FD1C87F',10,NULL,'Original',1,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-10-11 20:04:20',NULL,NULL,'1','MAIN'),(3,'KOT-58E9026E',24,NULL,'Original',1,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-10-12 14:16:28',NULL,NULL,'1','MAIN'),(4,'KOT-803A87BA',25,NULL,'Original',1,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-10-12 14:20:47',NULL,NULL,'1','MAIN');
/*!40000 ALTER TABLE `kitchen_order_ticket` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kitchen_performance_report`
--

DROP TABLE IF EXISTS `kitchen_performance_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kitchen_performance_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `kitchen_id` int NOT NULL,
  `total_kots` int DEFAULT NULL,
  `avg_preparation_time` decimal(8,2) DEFAULT NULL,
  `completed_kots` int DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_kitchen_performance_report_line` (`company_id`,`branch_id`,`report_date`,`kitchen_id`),
  KEY `ix_kitchen_performance_report_kitchen_id` (`kitchen_id`),
  KEY `ix_kitchen_performance_report_id` (`id`),
  KEY `ix_kitchen_performance_report_report_date` (`report_date`),
  KEY `ix_kitchen_performance_report_company_id` (`company_id`),
  KEY `ix_kitchen_performance_report_branch_id` (`branch_id`),
  KEY `ix_kitchen_performance_report_status` (`status`),
  CONSTRAINT `kitchen_performance_report_ibfk_1` FOREIGN KEY (`kitchen_id`) REFERENCES `kitchen` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_performance_report`
--

LOCK TABLES `kitchen_performance_report` WRITE;
/*!40000 ALTER TABLE `kitchen_performance_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `kitchen_performance_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_category`
--

DROP TABLE IF EXISTS `menu_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_code` varchar(100) NOT NULL,
  `category_name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `kitchen_id` int NOT NULL,
  `display_order` int DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_category_code` (`company_id`,`branch_id`,`category_code`),
  KEY `ix_menu_category_kitchen_id` (`kitchen_id`),
  KEY `ix_menu_category_branch_id` (`branch_id`),
  KEY `ix_menu_category_category_code` (`category_code`),
  KEY `ix_menu_category_status` (`status`),
  KEY `ix_menu_category_id` (`id`),
  KEY `ix_menu_category_category_name` (`category_name`),
  KEY `ix_menu_category_company_id` (`company_id`),
  CONSTRAINT `menu_category_ibfk_1` FOREIGN KEY (`kitchen_id`) REFERENCES `kitchen` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_category`
--

LOCK TABLES `menu_category` WRITE;
/*!40000 ALTER TABLE `menu_category` DISABLE KEYS */;
INSERT INTO `menu_category` VALUES (1,'CAT-STR','Starters','Starters menu section',1,1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,'CAT-SOUP','Soups & Salads','Soups & Salads menu section',1,2,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,'CAT-MAIN','Main Course','Main Course menu section',1,3,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(4,'CAT-GRILL','Tandoor & Grill','Tandoor & Grill menu section',2,4,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(5,'CAT-BRD','Breads & Rice','Breads & Rice menu section',1,5,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(6,'CAT-DES','Desserts','Desserts menu section',3,6,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `menu_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_modifier`
--

DROP TABLE IF EXISTS `menu_modifier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_modifier` (
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
  `active_modifier_name` varchar(100) GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `modifier_name` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_menu_modifier_active_name` (`menu_id`,`active_modifier_name`),
  KEY `ix_menu_modifier_status` (`status`),
  KEY `ix_menu_modifier_branch_id` (`branch_id`),
  KEY `ix_menu_modifier_menu_id` (`menu_id`),
  KEY `ix_menu_modifier_id` (`id`),
  KEY `ix_menu_modifier_modifier_name` (`modifier_name`),
  KEY `ix_menu_modifier_company_id` (`company_id`),
  CONSTRAINT `menu_modifier_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `restaurant_menu` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_modifier`
--

LOCK TABLES `menu_modifier` WRITE;
/*!40000 ALTER TABLE `menu_modifier` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_modifier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_recipe`
--

DROP TABLE IF EXISTS `menu_recipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_recipe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `menu_id` int NOT NULL,
  `inventory_item_id` int NOT NULL,
  `quantity_required` decimal(12,3) NOT NULL,
  `unit` enum('Kg','Gram','Litre','ml','Nos') NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  `active_inventory_item_id` int GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `inventory_item_id` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_menu_recipe_active_line` (`menu_id`,`active_inventory_item_id`),
  KEY `ix_menu_recipe_inventory_item_id` (`inventory_item_id`),
  KEY `ix_menu_recipe_company_id` (`company_id`),
  KEY `ix_menu_recipe_id` (`id`),
  KEY `ix_menu_recipe_status` (`status`),
  KEY `ix_menu_recipe_menu_id` (`menu_id`),
  KEY `ix_menu_recipe_branch_id` (`branch_id`),
  CONSTRAINT `menu_recipe_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `restaurant_menu` (`id`),
  CONSTRAINT `menu_recipe_ibfk_2` FOREIGN KEY (`inventory_item_id`) REFERENCES `inventory_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_recipe`
--

LOCK TABLES `menu_recipe` WRITE;
/*!40000 ALTER TABLE `menu_recipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_recipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_sub_category`
--

DROP TABLE IF EXISTS `menu_sub_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_sub_category` (
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
  UNIQUE KEY `uq_sub_category_code` (`company_id`,`branch_id`,`sub_category_code`),
  KEY `ix_menu_sub_category_category_id` (`category_id`),
  KEY `ix_menu_sub_category_sub_category_name` (`sub_category_name`),
  KEY `ix_menu_sub_category_company_id` (`company_id`),
  KEY `ix_menu_sub_category_category_code` (`category_code`),
  KEY `ix_menu_sub_category_status` (`status`),
  KEY `ix_menu_sub_category_sub_category_code` (`sub_category_code`),
  KEY `ix_menu_sub_category_branch_id` (`branch_id`),
  KEY `ix_menu_sub_category_id` (`id`),
  CONSTRAINT `menu_sub_category_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `menu_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_sub_category`
--

LOCK TABLES `menu_sub_category` WRITE;
/*!40000 ALTER TABLE `menu_sub_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_sub_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_variant`
--

DROP TABLE IF EXISTS `menu_variant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_variant` (
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
  `active_variant_name` varchar(50) GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `variant_name` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_menu_variant_active_name` (`menu_id`,`active_variant_name`),
  KEY `ix_menu_variant_status` (`status`),
  KEY `ix_menu_variant_branch_id` (`branch_id`),
  KEY `ix_menu_variant_id` (`id`),
  KEY `ix_menu_variant_menu_id` (`menu_id`),
  KEY `ix_menu_variant_variant_name` (`variant_name`),
  KEY `ix_menu_variant_company_id` (`company_id`),
  CONSTRAINT `menu_variant_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `restaurant_menu` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_variant`
--

LOCK TABLES `menu_variant` WRITE;
/*!40000 ALTER TABLE `menu_variant` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_variant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_method`
--

DROP TABLE IF EXISTS `payment_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_method` (
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
  UNIQUE KEY `uq_payment_method_name` (`company_id`,`branch_id`,`method_name`),
  KEY `ix_payment_method_id` (`id`),
  KEY `ix_payment_method_branch_id` (`branch_id`),
  KEY `ix_payment_method_status` (`status`),
  KEY `ix_payment_method_company_id` (`company_id`),
  KEY `ix_payment_method_method_name` (`method_name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_method`
--

LOCK TABLES `payment_method` WRITE;
/*!40000 ALTER TABLE `payment_method` DISABLE KEYS */;
INSERT INTO `payment_method` VALUES (1,'Cash','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,'Credit Card','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,'Debit Card','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(4,'UPI','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(5,'Room Charge','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `payment_method` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_mode_report`
--

DROP TABLE IF EXISTS `payment_mode_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_mode_report` (
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
  UNIQUE KEY `uq_payment_mode_report_line` (`company_id`,`branch_id`,`report_date`,`payment_method_id`),
  KEY `ix_payment_mode_report_branch_id` (`branch_id`),
  KEY `ix_payment_mode_report_report_date` (`report_date`),
  KEY `ix_payment_mode_report_status` (`status`),
  KEY `ix_payment_mode_report_id` (`id`),
  KEY `ix_payment_mode_report_company_id` (`company_id`),
  KEY `ix_payment_mode_report_payment_method_id` (`payment_method_id`),
  CONSTRAINT `payment_mode_report_ibfk_1` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_mode_report`
--

LOCK TABLES `payment_mode_report` WRITE;
/*!40000 ALTER TABLE `payment_mode_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_mode_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_bill`
--

DROP TABLE IF EXISTS `restaurant_bill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_bill` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_number` varchar(100) NOT NULL,
  `bill_date` date NOT NULL,
  `bill_time` time NOT NULL,
  `order_id` int NOT NULL,
  `order_number` varchar(100) NOT NULL,
  `table_id` int DEFAULT NULL,
  `table_code` varchar(100) DEFAULT NULL,
  `room_no` varchar(50) DEFAULT NULL,
  `guest_id` int DEFAULT NULL,
  `guest_name` varchar(100) DEFAULT NULL,
  `guest_mobile` varchar(20) DEFAULT NULL,
  `sub_total` decimal(12,2) DEFAULT NULL,
  `cgst_percentage` decimal(6,3) DEFAULT NULL,
  `cgst_amount` decimal(12,2) DEFAULT NULL,
  `sgst_percentage` decimal(6,3) DEFAULT NULL,
  `sgst_amount` decimal(12,2) DEFAULT NULL,
  `igst_percentage` decimal(6,3) DEFAULT NULL,
  `igst_amount` decimal(12,2) DEFAULT NULL,
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
  `active_order_id` int GENERATED ALWAYS AS ((case when ((`status` = _utf8mb4'ACTIVE') and (`bill_status` <> _utf8mb4'Cancelled')) then `order_id` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bill_number` (`company_id`,`branch_id`,`bill_number`),
  UNIQUE KEY `ix_restaurant_bill_token` (`token`),
  UNIQUE KEY `uq_restaurant_bill_active_order` (`company_id`,`branch_id`,`active_order_id`),
  KEY `ix_restaurant_bill_table_id` (`table_id`),
  KEY `ix_restaurant_bill_guest_id` (`guest_id`),
  KEY `ix_restaurant_bill_bill_status` (`bill_status`),
  KEY `ix_restaurant_bill_table_code` (`table_code`),
  KEY `ix_restaurant_bill_branch_id` (`branch_id`),
  KEY `ix_restaurant_bill_status` (`status`),
  KEY `ix_restaurant_bill_company_id` (`company_id`),
  KEY `ix_restaurant_bill_order_number` (`order_number`),
  KEY `ix_restaurant_bill_bill_date` (`bill_date`),
  KEY `ix_restaurant_bill_guest_mobile` (`guest_mobile`),
  KEY `ix_restaurant_bill_payment_status` (`payment_status`),
  KEY `ix_restaurant_bill_id` (`id`),
  KEY `ix_restaurant_bill_bill_number` (`bill_number`),
  KEY `ix_restaurant_bill_room_no` (`room_no`),
  KEY `ix_restaurant_bill_order_id` (`order_id`),
  CONSTRAINT `restaurant_bill_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `restaurant_order` (`id`),
  CONSTRAINT `restaurant_bill_ibfk_2` FOREIGN KEY (`table_id`) REFERENCES `restaurant_table` (`id`),
  CONSTRAINT `restaurant_bill_ibfk_3` FOREIGN KEY (`guest_id`) REFERENCES `guest` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill`
--

LOCK TABLES `restaurant_bill` WRITE;
/*!40000 ALTER TABLE `restaurant_bill` DISABLE KEYS */;
INSERT INTO `restaurant_bill` (`id`, `bill_number`, `bill_date`, `bill_time`, `order_id`, `order_number`, `table_id`, `table_code`, `room_no`, `guest_id`, `guest_name`, `guest_mobile`, `sub_total`, `cgst_percentage`, `cgst_amount`, `sgst_percentage`, `sgst_amount`, `igst_percentage`, `igst_amount`, `service_charge_percentage`, `service_charge_amount`, `discount_type`, `discount_value`, `discount_amount`, `round_off`, `grand_total`, `bill_status`, `payment_status`, `remarks`, `token`, `status`, `created_by`, `created_at`, `updated_at`, `updated_by`, `company_id`, `branch_id`) VALUES (1,'RB-20261009-001','2026-10-09','13:55:00',1,'RO-20261009-001',4,'FL-GRD-T04',NULL,NULL,NULL,NULL,2740.00,2.500,75.35,2.500,75.35,0.000,0.00,10.000,274.00,NULL,0.00,0.00,0.00,3164.70,'Paid','Paid',NULL,'b6d95557-ef25-4deb-bdb5-bf6bc9fb4090','ACTIVE','1','2026-10-09 13:55:00',NULL,NULL,'1','1'),(2,'RB-20261008-002','2026-10-08','14:55:00',2,'RO-20261008-002',7,'FL-GRD-T07',NULL,NULL,NULL,NULL,2410.00,2.500,66.28,2.500,66.27,0.000,0.00,10.000,241.00,NULL,0.00,0.00,0.00,2783.55,'Paid','Paid',NULL,'244e6df7-72b2-4f67-9559-c095786caf3e','ACTIVE','1','2026-10-08 14:55:00',NULL,NULL,'1','1'),(3,'RB-20261010-003','2026-10-10','15:55:00',3,'RO-20261010-003',10,'FL-FST-T02',NULL,NULL,NULL,NULL,1780.00,2.500,48.95,2.500,48.95,0.000,0.00,10.000,178.00,NULL,0.00,0.00,0.00,2055.90,'Paid','Paid',NULL,'64e0cefe-8872-48bf-8ef0-529a70bb0a0e','ACTIVE','1','2026-10-10 15:55:00',NULL,NULL,'1','1'),(4,'RB-20261009-004','2026-10-09','16:55:00',4,'RO-20261009-004',13,'FL-FST-T05',NULL,NULL,NULL,NULL,3360.00,2.500,92.40,2.500,92.40,0.000,0.00,10.000,336.00,NULL,0.00,0.00,0.00,3880.80,'Paid','Paid',NULL,'4ca8ec5d-45a8-40f5-9752-67f0c3ded20b','ACTIVE','1','2026-10-09 16:55:00',NULL,NULL,'1','1'),(5,'RB-20261008-005','2026-10-08','17:55:00',5,'RO-20261008-005',16,'FL-TER-T02',NULL,NULL,NULL,NULL,4030.00,2.500,110.83,2.500,110.82,0.000,0.00,10.000,403.00,NULL,0.00,0.00,0.00,4654.65,'Paid','Paid',NULL,'60c0d2a6-20cc-4538-a6b4-11c5e58f2524','ACTIVE','1','2026-10-08 17:55:00',NULL,NULL,'1','1'),(6,'RB-20261010-006','2026-10-10','18:55:00',6,'RO-20261010-006',1,'FL-GRD-T01',NULL,NULL,NULL,NULL,1430.00,2.500,39.33,2.500,39.32,0.000,0.00,10.000,143.00,NULL,0.00,0.00,0.00,1651.65,'Paid','Paid',NULL,'02223d1d-ca79-4b46-b1f9-136896bfd3f0','ACTIVE','1','2026-10-10 18:55:00',NULL,NULL,'1','1'),(7,'RB-20261009-007','2026-10-09','19:55:00',7,'RO-20261009-007',4,'FL-GRD-T04',NULL,NULL,NULL,NULL,2330.00,2.500,64.08,2.500,64.07,0.000,0.00,10.000,233.00,NULL,0.00,0.00,0.00,2691.15,'Paid','Paid',NULL,'d8fb12bc-39ad-4612-8e0e-0373bfbabe0e','ACTIVE','1','2026-10-09 19:55:00',NULL,NULL,'1','1'),(8,'RB-20261008-008','2026-10-08','12:55:00',8,'RO-20261008-008',7,'FL-GRD-T07',NULL,NULL,NULL,NULL,3220.00,2.500,88.55,2.500,88.55,0.000,0.00,10.000,322.00,NULL,0.00,0.00,0.00,3719.10,'Paid','Paid',NULL,'f0ba2907-4fd0-4adf-a604-d44e3325557c','ACTIVE','1','2026-10-08 12:55:00',NULL,NULL,'1','1'),(9,'BILL-468DF530','2026-10-11','20:00:06',9,'ORD-C5DB7FFB',1,'FL-GRD-T01',NULL,NULL,'Flow Tester','+919876500999',960.00,2.500,24.00,2.500,24.00,NULL,0.00,0.000,0.00,NULL,0.00,0.00,0.00,1008.00,'Paid','Paid',NULL,'d8ef06ae-63b9-423c-adb8-0b0b6a2e64ab','ACTIVE','1','2026-10-11 20:00:06','2026-10-11 20:00:06',NULL,'1','MAIN'),(10,'BILL-AB3183F6','2026-10-11','20:04:21',10,'ORD-E8491E8D',2,'FL-GRD-T02',NULL,NULL,'Flow Tester','+919876500999',960.00,2.500,24.00,2.500,24.00,NULL,0.00,0.000,0.00,NULL,0.00,0.00,0.00,1008.00,'Paid','Paid',NULL,'1a2f8ab2-9fc0-4c7c-9590-c328a3da6cd2','ACTIVE','1','2026-10-11 20:04:20','2026-10-11 20:04:21',NULL,'1','MAIN'),(11,'BILL-FC9594AB','2026-10-12','14:16:29',24,'ORD-8EF35DF1',4,'FL-GRD-T04',NULL,NULL,'Flow Tester','+919876500999',960.00,2.500,24.00,2.500,24.00,NULL,0.00,0.000,0.00,NULL,0.00,0.00,0.00,1008.00,'Paid','Paid',NULL,'ee75b454-f6d3-494e-9280-009d354213c0','ACTIVE','1','2026-10-12 14:16:28','2026-10-12 14:16:29',NULL,'1','MAIN'),(12,'BILL-B5FE2B56','2026-10-12','14:20:47',25,'ORD-1F53861D',5,'FL-GRD-T05',NULL,NULL,'Flow Tester','+919876500999',960.00,2.500,24.00,2.500,24.00,NULL,0.00,0.000,0.00,NULL,0.00,0.00,0.00,1008.00,'Paid','Paid',NULL,'210c8dbc-b949-42b3-a7fc-1ad854274445','ACTIVE','1','2026-10-12 14:20:47','2026-10-12 14:20:47',NULL,'1','MAIN');
/*!40000 ALTER TABLE `restaurant_bill` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_bill_item`
--

DROP TABLE IF EXISTS `restaurant_bill_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_bill_item` (
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
  KEY `ix_restaurant_bill_item_menu_id` (`menu_id`),
  KEY `ix_restaurant_bill_item_status` (`status`),
  KEY `ix_restaurant_bill_item_branch_id` (`branch_id`),
  KEY `ix_restaurant_bill_item_id` (`id`),
  KEY `ix_restaurant_bill_item_bill_id` (`bill_id`),
  KEY `ix_restaurant_bill_item_order_item_id` (`order_item_id`),
  KEY `ix_restaurant_bill_item_company_id` (`company_id`),
  CONSTRAINT `restaurant_bill_item_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `restaurant_bill` (`id`),
  CONSTRAINT `restaurant_bill_item_ibfk_2` FOREIGN KEY (`order_item_id`) REFERENCES `restaurant_order_item` (`id`),
  CONSTRAINT `restaurant_bill_item_ibfk_3` FOREIGN KEY (`menu_id`) REFERENCES `restaurant_menu` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill_item`
--

LOCK TABLES `restaurant_bill_item` WRITE;
/*!40000 ALTER TABLE `restaurant_bill_item` DISABLE KEYS */;
INSERT INTO `restaurant_bill_item` VALUES (1,1,1,15,'Tandoori Chicken (Half)',2,420.00,840.00,NULL,'ACTIVE','1','2026-10-09 13:55:00',NULL,NULL,'1','1'),(2,1,2,1,'Paneer Tikka',3,320.00,960.00,NULL,'ACTIVE','1','2026-10-09 13:55:00',NULL,NULL,'1','1'),(3,1,3,17,'Tandoori Pomfret',1,620.00,620.00,NULL,'ACTIVE','1','2026-10-09 13:55:00',NULL,NULL,'1','1'),(4,1,4,24,'Rasmalai',2,160.00,320.00,NULL,'ACTIVE','1','2026-10-09 13:55:00',NULL,NULL,'1','1'),(5,2,5,22,'Steamed Basmati Rice',1,150.00,150.00,NULL,'ACTIVE','1','2026-10-08 14:55:00',NULL,NULL,'1','1'),(6,2,6,18,'Grilled Vegetable Platter',3,340.00,1020.00,NULL,'ACTIVE','1','2026-10-08 14:55:00',NULL,NULL,'1','1'),(7,2,7,10,'Chettinad Chicken Curry',1,460.00,460.00,NULL,'ACTIVE','1','2026-10-08 14:55:00',NULL,NULL,'1','1'),(8,2,8,20,'Garlic Naan',2,90.00,180.00,NULL,'ACTIVE','1','2026-10-08 14:55:00',NULL,NULL,'1','1'),(9,2,9,11,'Dal Makhani',2,300.00,600.00,NULL,'ACTIVE','1','2026-10-08 14:55:00',NULL,NULL,'1','1'),(10,3,10,6,'Mulligatawny Soup',1,200.00,200.00,NULL,'ACTIVE','1','2026-10-10 15:55:00',NULL,NULL,'1','1'),(11,3,11,13,'Vegetable Biryani',2,340.00,680.00,NULL,'ACTIVE','1','2026-10-10 15:55:00',NULL,NULL,'1','1'),(12,3,12,11,'Dal Makhani',3,300.00,900.00,NULL,'ACTIVE','1','2026-10-10 15:55:00',NULL,NULL,'1','1'),(13,4,13,9,'Paneer Butter Masala',2,380.00,760.00,NULL,'ACTIVE','1','2026-10-09 16:55:00',NULL,NULL,'1','1'),(14,4,14,4,'Prawn Koliwada',3,420.00,1260.00,NULL,'ACTIVE','1','2026-10-09 16:55:00',NULL,NULL,'1','1'),(15,4,15,12,'Kerala Fish Curry',2,520.00,1040.00,NULL,'ACTIVE','1','2026-10-09 16:55:00',NULL,NULL,'1','1'),(16,4,16,11,'Dal Makhani',1,300.00,300.00,NULL,'ACTIVE','1','2026-10-09 16:55:00',NULL,NULL,'1','1'),(17,5,17,9,'Paneer Butter Masala',3,380.00,1140.00,NULL,'ACTIVE','1','2026-10-08 17:55:00',NULL,NULL,'1','1'),(18,5,18,19,'Butter Naan',1,70.00,70.00,NULL,'ACTIVE','1','2026-10-08 17:55:00',NULL,NULL,'1','1'),(19,5,19,14,'Hyderabadi Chicken Biryani',2,460.00,920.00,NULL,'ACTIVE','1','2026-10-08 17:55:00',NULL,NULL,'1','1'),(20,5,20,12,'Kerala Fish Curry',3,520.00,1560.00,NULL,'ACTIVE','1','2026-10-08 17:55:00',NULL,NULL,'1','1'),(21,5,21,13,'Vegetable Biryani',1,340.00,340.00,NULL,'ACTIVE','1','2026-10-08 17:55:00',NULL,NULL,'1','1'),(22,6,22,20,'Garlic Naan',3,90.00,270.00,NULL,'ACTIVE','1','2026-10-10 18:55:00',NULL,NULL,'1','1'),(23,6,23,7,'Garden Green Salad',2,160.00,320.00,NULL,'ACTIVE','1','2026-10-10 18:55:00',NULL,NULL,'1','1'),(24,6,24,4,'Prawn Koliwada',2,420.00,840.00,NULL,'ACTIVE','1','2026-10-10 18:55:00',NULL,NULL,'1','1'),(25,7,25,20,'Garlic Naan',1,90.00,90.00,NULL,'ACTIVE','1','2026-10-09 19:55:00',NULL,NULL,'1','1'),(26,7,26,23,'Gulab Jamun',1,140.00,140.00,NULL,'ACTIVE','1','2026-10-09 19:55:00',NULL,NULL,'1','1'),(27,7,27,16,'Seekh Kebab',3,380.00,1140.00,NULL,'ACTIVE','1','2026-10-09 19:55:00',NULL,NULL,'1','1'),(28,7,28,1,'Paneer Tikka',3,320.00,960.00,NULL,'ACTIVE','1','2026-10-09 19:55:00',NULL,NULL,'1','1'),(29,8,29,25,'Chocolate Brownie',1,220.00,220.00,NULL,'ACTIVE','1','2026-10-08 12:55:00',NULL,NULL,'1','1'),(30,8,30,23,'Gulab Jamun',2,140.00,280.00,NULL,'ACTIVE','1','2026-10-08 12:55:00',NULL,NULL,'1','1'),(31,8,31,3,'Gobi Manchurian',3,260.00,780.00,NULL,'ACTIVE','1','2026-10-08 12:55:00',NULL,NULL,'1','1'),(32,8,32,18,'Grilled Vegetable Platter',3,340.00,1020.00,NULL,'ACTIVE','1','2026-10-08 12:55:00',NULL,NULL,'1','1'),(33,8,33,14,'Hyderabadi Chicken Biryani',2,460.00,920.00,NULL,'ACTIVE','1','2026-10-08 12:55:00',NULL,NULL,'1','1'),(34,9,34,8,'Butter Chicken',2,480.00,960.00,48.00,'ACTIVE','1','2026-10-11 20:00:06',NULL,NULL,'1','MAIN'),(35,10,35,8,'Butter Chicken',2,480.00,960.00,48.00,'ACTIVE','1','2026-10-11 20:04:20',NULL,NULL,'1','MAIN'),(36,11,36,8,'Butter Chicken',2,480.00,960.00,48.00,'ACTIVE','1','2026-10-12 14:16:28',NULL,NULL,'1','MAIN'),(37,12,37,8,'Butter Chicken',2,480.00,960.00,48.00,'ACTIVE','1','2026-10-12 14:20:47',NULL,NULL,'1','MAIN');
/*!40000 ALTER TABLE `restaurant_bill_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_bill_payment`
--

DROP TABLE IF EXISTS `restaurant_bill_payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_bill_payment` (
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
  KEY `ix_restaurant_bill_payment_payment_method_id` (`payment_method_id`),
  KEY `ix_restaurant_bill_payment_company_id` (`company_id`),
  KEY `ix_restaurant_bill_payment_id` (`id`),
  KEY `ix_restaurant_bill_payment_bill_id` (`bill_id`),
  KEY `ix_restaurant_bill_payment_payment_date` (`payment_date`),
  KEY `ix_restaurant_bill_payment_branch_id` (`branch_id`),
  KEY `ix_restaurant_bill_payment_payment_status` (`payment_status`),
  KEY `ix_restaurant_bill_payment_lifecycle_status` (`status`),
  CONSTRAINT `restaurant_bill_payment_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `restaurant_bill` (`id`),
  CONSTRAINT `restaurant_bill_payment_ibfk_2` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill_payment`
--

LOCK TABLES `restaurant_bill_payment` WRITE;
/*!40000 ALTER TABLE `restaurant_bill_payment` DISABLE KEYS */;
INSERT INTO `restaurant_bill_payment` VALUES (1,1,2,3164.70,NULL,'2026-10-09','13:58:00','Success',NULL,'ACTIVE','1','2026-10-09 13:58:00',NULL,NULL,'1','1'),(2,2,3,2783.55,NULL,'2026-10-08','14:58:00','Success',NULL,'ACTIVE','1','2026-10-08 14:58:00',NULL,NULL,'1','1'),(3,3,4,2055.90,NULL,'2026-10-10','15:58:00','Success',NULL,'ACTIVE','1','2026-10-10 15:58:00',NULL,NULL,'1','1'),(4,4,5,3880.80,NULL,'2026-10-09','16:58:00','Success',NULL,'ACTIVE','1','2026-10-09 16:58:00',NULL,NULL,'1','1'),(5,5,1,4654.65,NULL,'2026-10-08','17:58:00','Success',NULL,'ACTIVE','1','2026-10-08 17:58:00',NULL,NULL,'1','1'),(6,6,2,1651.65,NULL,'2026-10-10','18:58:00','Success',NULL,'ACTIVE','1','2026-10-10 18:58:00',NULL,NULL,'1','1'),(7,7,3,2691.15,NULL,'2026-10-09','19:58:00','Success',NULL,'ACTIVE','1','2026-10-09 19:58:00',NULL,NULL,'1','1'),(8,8,4,3719.10,NULL,'2026-10-08','12:58:00','Success',NULL,'ACTIVE','1','2026-10-08 12:58:00',NULL,NULL,'1','1'),(9,9,1,1008.00,'FLOWTEST','2026-10-11','20:00:06','Success','flow test','ACTIVE','1','2026-10-11 20:00:06',NULL,NULL,'1','MAIN'),(10,10,1,1008.00,'FLOWTEST','2026-10-11','20:04:21','Success','flow test','ACTIVE','1','2026-10-11 20:04:21',NULL,NULL,'1','MAIN'),(11,11,1,1008.00,'FLOWTEST','2026-10-12','14:16:29','Success','flow test','ACTIVE','1','2026-10-12 14:16:29',NULL,NULL,'1','MAIN'),(12,12,1,1008.00,'FLOWTEST','2026-10-12','14:20:48','Success','flow test','ACTIVE','1','2026-10-12 14:20:47',NULL,NULL,'1','MAIN');
/*!40000 ALTER TABLE `restaurant_bill_payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_bill_split`
--

DROP TABLE IF EXISTS `restaurant_bill_split`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_bill_split` (
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
  KEY `ix_restaurant_bill_split_branch_id` (`branch_id`),
  KEY `ix_restaurant_bill_split_company_id` (`company_id`),
  KEY `ix_restaurant_bill_split_id` (`id`),
  KEY `ix_restaurant_bill_split_status` (`status`),
  KEY `ix_restaurant_bill_split_original_bill_id` (`original_bill_id`),
  CONSTRAINT `restaurant_bill_split_ibfk_1` FOREIGN KEY (`original_bill_id`) REFERENCES `restaurant_bill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill_split`
--

LOCK TABLES `restaurant_bill_split` WRITE;
/*!40000 ALTER TABLE `restaurant_bill_split` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_bill_split` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_bill_split_detail`
--

DROP TABLE IF EXISTS `restaurant_bill_split_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_bill_split_detail` (
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
  KEY `ix_restaurant_bill_split_detail_branch_id` (`branch_id`),
  KEY `ix_restaurant_bill_split_detail_status` (`status`),
  KEY `ix_restaurant_bill_split_detail_child_bill_id` (`child_bill_id`),
  KEY `ix_restaurant_bill_split_detail_company_id` (`company_id`),
  KEY `ix_restaurant_bill_split_detail_split_id` (`split_id`),
  KEY `ix_restaurant_bill_split_detail_id` (`id`),
  CONSTRAINT `restaurant_bill_split_detail_ibfk_1` FOREIGN KEY (`split_id`) REFERENCES `restaurant_bill_split` (`id`),
  CONSTRAINT `restaurant_bill_split_detail_ibfk_2` FOREIGN KEY (`child_bill_id`) REFERENCES `restaurant_bill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill_split_detail`
--

LOCK TABLES `restaurant_bill_split_detail` WRITE;
/*!40000 ALTER TABLE `restaurant_bill_split_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_bill_split_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_floor`
--

DROP TABLE IF EXISTS `restaurant_floor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_floor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `floor_code` varchar(100) NOT NULL,
  `floor_name` varchar(100) NOT NULL,
  `floor_number` int NOT NULL,
  `floor_type` enum('Restaurant','Banquet','Outdoor') NOT NULL,
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
  `active_floor_number` int GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `floor_number` else NULL end)) STORED,
  `active_floor_name` varchar(100) GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `floor_name` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_floor_code` (`company_id`,`branch_id`,`floor_code`),
  UNIQUE KEY `uq_restaurant_floor_active_number` (`company_id`,`branch_id`,`active_floor_number`),
  UNIQUE KEY `uq_restaurant_floor_active_name` (`company_id`,`branch_id`,`active_floor_name`),
  KEY `ix_restaurant_floor_branch_id` (`branch_id`),
  KEY `ix_restaurant_floor_status` (`status`),
  KEY `ix_restaurant_floor_company_id` (`company_id`),
  KEY `ix_restaurant_floor_floor_code` (`floor_code`),
  KEY `ix_restaurant_floor_floor_name` (`floor_name`),
  KEY `ix_restaurant_floor_id` (`id`),
  KEY `ix_restaurant_floor_floor_number` (`floor_number`),
  KEY `ix_restaurant_floor_floor_type` (`floor_type`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_floor`
--

LOCK TABLES `restaurant_floor` WRITE;
/*!40000 ALTER TABLE `restaurant_floor` DISABLE KEYS */;
INSERT INTO `restaurant_floor` (`id`, `floor_code`, `floor_name`, `floor_number`, `floor_type`, `description`, `total_tables`, `total_capacity`, `layout_json`, `color_code`, `is_open`, `status`, `created_by`, `created_at`, `updated_at`, `updated_by`, `company_id`, `branch_id`) VALUES (1,'FL-GRD','Ground Floor',1,'Restaurant','Ground Floor seating',8,32,NULL,'#850126',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,'FL-FST','First Floor',2,'Restaurant','First Floor seating',6,28,NULL,'#850126',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,'FL-TER','Rooftop Terrace',3,'Outdoor','Rooftop Terrace seating',4,16,NULL,'#850126',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `restaurant_floor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_menu`
--

DROP TABLE IF EXISTS `restaurant_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_menu` (
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
  `kitchen_id` int NOT NULL,
  `availability_status` enum('Available','Out of Stock') NOT NULL,
  `is_veg` tinyint(1) NOT NULL,
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
  `active_menu_name` varchar(150) GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `item_name` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_item_code` (`company_id`,`branch_id`,`item_code`),
  UNIQUE KEY `uq_restaurant_menu_active_name` (`company_id`,`branch_id`,`category_id`,`active_menu_name`),
  KEY `ix_restaurant_menu_branch_id` (`branch_id`),
  KEY `ix_restaurant_menu_status` (`status`),
  KEY `ix_restaurant_menu_sub_category_id` (`sub_category_id`),
  KEY `ix_restaurant_menu_item_name` (`item_name`),
  KEY `ix_restaurant_menu_company_id` (`company_id`),
  KEY `ix_restaurant_menu_kitchen_id` (`kitchen_id`),
  KEY `ix_restaurant_menu_id` (`id`),
  KEY `ix_restaurant_menu_item_code` (`item_code`),
  KEY `ix_restaurant_menu_availability_status` (`availability_status`),
  KEY `ix_restaurant_menu_category_id` (`category_id`),
  CONSTRAINT `restaurant_menu_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `menu_category` (`id`),
  CONSTRAINT `restaurant_menu_ibfk_2` FOREIGN KEY (`sub_category_id`) REFERENCES `menu_sub_category` (`id`),
  CONSTRAINT `restaurant_menu_ibfk_3` FOREIGN KEY (`kitchen_id`) REFERENCES `kitchen` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_menu`
--

LOCK TABLES `restaurant_menu` WRITE;
/*!40000 ALTER TABLE `restaurant_menu` DISABLE KEYS */;
INSERT INTO `restaurant_menu` (`id`, `item_code`, `item_name`, `description`, `category_id`, `sub_category_id`, `price`, `cost_price`, `tax_percentage`, `service_charge_applicable`, `preparation_time`, `kitchen_id`, `availability_status`, `is_veg`, `dietary_tags`, `has_variants`, `item_image`, `happy_hour_eligible`, `status`, `created_by`, `created_at`, `updated_at`, `updated_by`, `company_id`, `branch_id`) VALUES (1,'RES-001','Paneer Tikka','Starters — prepared to order.',1,NULL,320.00,121.60,5.000,1,18,1,'Available',1,NULL,0,'/templates/static/upload_image/4f85cba4c522490081a75a3f4491f17f.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,'RES-002','Chicken 65','Starters — prepared to order.',1,NULL,340.00,129.20,5.000,1,16,1,'Available',0,NULL,0,'/templates/static/upload_image/afd2326468ae46c5acc00f1b5ca5e0e1.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,'RES-003','Gobi Manchurian','Starters — prepared to order.',1,NULL,260.00,98.80,5.000,1,14,1,'Available',1,NULL,0,'/templates/static/upload_image/b7607386c96f4e62a1f47b2c68f743de.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(4,'RES-004','Prawn Koliwada','Starters — prepared to order.',1,NULL,420.00,159.60,5.000,1,18,1,'Available',0,NULL,0,'/templates/static/upload_image/a86f51b40bb44ff4bfdbc19474a57780.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(5,'RES-005','Sweet Corn Soup','Soups & Salads — prepared to order.',2,NULL,180.00,68.40,5.000,1,10,1,'Available',1,NULL,0,'/templates/static/upload_image/8ab75ecb592c451d955332ec89bf8163.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(6,'RES-006','Mulligatawny Soup','Soups & Salads — prepared to order.',2,NULL,200.00,76.00,5.000,1,12,1,'Available',0,NULL,0,'/templates/static/upload_image/e8d2e2cfccf9447eb87579e9e13ad40a.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(7,'RES-007','Garden Green Salad','Soups & Salads — prepared to order.',2,NULL,160.00,60.80,5.000,1,6,1,'Available',1,NULL,0,'/templates/static/upload_image/f0ffc178e79243508af8b562dda1d086.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(8,'RES-008','Butter Chicken','Main Course — prepared to order.',3,NULL,480.00,182.40,5.000,1,25,1,'Available',0,NULL,0,'/templates/static/upload_image/615562d87e6b4c36950683e692b4ec3b.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(9,'RES-009','Paneer Butter Masala','Main Course — prepared to order.',3,NULL,380.00,144.40,5.000,1,22,1,'Available',1,NULL,0,'/templates/static/upload_image/a701b323621244e695566ee80ee653be.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(10,'RES-010','Chettinad Chicken Curry','Main Course — prepared to order.',3,NULL,460.00,174.80,5.000,1,26,1,'Available',0,NULL,0,'/templates/static/upload_image/fa2a969d2a4f4822b404bbba30bc9723.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(11,'RES-011','Dal Makhani','Main Course — prepared to order.',3,NULL,300.00,114.00,5.000,1,20,1,'Available',1,NULL,0,'/templates/static/upload_image/2aae479ce3e3403c89b4e5f033addd86.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(12,'RES-012','Kerala Fish Curry','Main Course — prepared to order.',3,NULL,520.00,197.60,5.000,1,24,1,'Available',0,NULL,0,'/templates/static/upload_image/ccd4f25d136647ddb3ee8c239ea4ef46.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(13,'RES-013','Vegetable Biryani','Main Course — prepared to order.',3,NULL,340.00,129.20,5.000,1,28,1,'Available',1,NULL,0,'/templates/static/upload_image/c150cefee0d54ef1b444f295d13e1e07.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(14,'RES-014','Hyderabadi Chicken Biryani','Main Course — prepared to order.',3,NULL,460.00,174.80,5.000,1,32,1,'Available',0,NULL,0,'/templates/static/upload_image/917674a4a2fb44cda8a439589c6554fe.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(15,'RES-015','Tandoori Chicken (Half)','Tandoor & Grill — prepared to order.',4,NULL,420.00,159.60,5.000,1,30,2,'Available',0,NULL,0,'/templates/static/upload_image/3fe93ea9169f43c0a2bf21e56d6ed322.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(16,'RES-016','Seekh Kebab','Tandoor & Grill — prepared to order.',4,NULL,380.00,144.40,5.000,1,22,2,'Available',0,NULL,0,'/templates/static/upload_image/181bd281072d453d95cf09a2f11be2bd.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(17,'RES-017','Tandoori Pomfret','Tandoor & Grill — prepared to order.',4,NULL,620.00,235.60,5.000,1,28,2,'Available',0,NULL,0,'/templates/static/upload_image/aae9c2248cd94b95a54b8e6d4a921305.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(18,'RES-018','Grilled Vegetable Platter','Tandoor & Grill — prepared to order.',4,NULL,340.00,129.20,5.000,1,20,2,'Available',1,NULL,0,'/templates/static/upload_image/61c3416f694449f7923f20abc5bd795f.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(19,'RES-019','Butter Naan','Breads & Rice — prepared to order.',5,NULL,70.00,26.60,5.000,1,8,1,'Available',1,NULL,0,'/templates/static/upload_image/f7cec27408964fd08169c903e3d4b0b3.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(20,'RES-020','Garlic Naan','Breads & Rice — prepared to order.',5,NULL,90.00,34.20,5.000,1,8,1,'Available',1,NULL,0,'/templates/static/upload_image/5340b0735a5848de8d0e343c16bdcf4a.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(21,'RES-021','Laccha Paratha','Breads & Rice — prepared to order.',5,NULL,80.00,30.40,5.000,1,9,1,'Available',1,NULL,0,'/templates/static/upload_image/b69ffbb167724d43a964b2ea6ad7b9de.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(22,'RES-022','Steamed Basmati Rice','Breads & Rice — prepared to order.',5,NULL,150.00,57.00,5.000,1,12,1,'Available',1,NULL,0,'/templates/static/upload_image/0dc391ce28a44e1bbdeacf05611c0c6c.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(23,'RES-023','Gulab Jamun','Desserts — prepared to order.',6,NULL,140.00,53.20,5.000,1,5,3,'Available',1,NULL,0,'/templates/static/upload_image/4e74356d16784bc190b023adbc68f1f3.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(24,'RES-024','Rasmalai','Desserts — prepared to order.',6,NULL,160.00,60.80,5.000,1,5,3,'Available',1,NULL,0,'/templates/static/upload_image/6b421966b0d842dabbbc1f18394abf20.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(25,'RES-025','Chocolate Brownie','Desserts — prepared to order.',6,NULL,220.00,83.60,5.000,1,8,3,'Available',1,NULL,0,'/templates/static/upload_image/a594ff3e13b348ee863108634d0f8c15.jpg',0,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(26,'ITM-18A65FEE','QB ZZQA40BTKJA changed','QB ZZQA40BTKJB changed',1,NULL,11.00,12.00,13.000,0,11,3,'Available',1,'[\"QB ZZQA40BTKJA changed\"]',0,NULL,0,'ACTIVE','1','2026-10-11 21:29:11','2026-10-11 21:29:16','1','1','MAIN'),(27,'ITM-1856B182','QB ZZQA40EO5PA changed','QB ZZQA40EO5PB changed',1,NULL,11.00,12.00,13.000,0,11,3,'Available',1,'[\"QB ZZQA40EO5PA changed\"]',0,NULL,0,'INACTIVE','1','2026-10-11 21:31:51','2026-10-11 21:32:03','1','1','MAIN'),(28,'ITM-FFE10191','QB ZZQA41IXPSA changed','QB ZZQA41IXPSB changed',1,NULL,11.00,12.00,13.000,0,11,3,'Available',1,'[\"QB ZZQA41IXPSA changed\"]',0,NULL,0,'INACTIVE','1','2026-10-11 22:04:43','2026-10-11 22:04:55','1','1','MAIN'),(29,'ITM-86D61B4C','QB ZZQA42H55CA changed','QB ZZQA42H55CB changed',1,NULL,11.00,12.00,13.000,0,11,3,'Available',1,'[\"QB ZZQA42H55CA changed\"]',0,NULL,0,'INACTIVE','1','2026-10-11 22:31:16','2026-10-11 22:31:28','1','1','MAIN'),(30,'ITM-67AE8501','QB ZZQA434N8GA changed','QB ZZQA434N8GB changed',1,NULL,11.00,12.00,13.000,0,11,3,'Available',1,'[\"QB ZZQA434N8GA changed\"]',0,NULL,0,'INACTIVE','1','2026-10-11 22:49:40','2026-10-11 22:49:52','1','1','MAIN'),(31,'ITM-E6E1DDD1','QB ZZQA4YDEH5A changed','QB ZZQA4YDEH5B changed',1,NULL,11.00,12.00,13.000,0,11,3,'Available',1,'[\"QB ZZQA4YDEH5A changed\"]',0,NULL,0,'INACTIVE','1','2026-10-12 13:24:24','2026-10-12 13:24:37','1','1','MAIN'),(32,'ITM-975B9AF2','QB ZZQA51PGWVA changed','QB ZZQA51PGWVB changed',1,NULL,11.00,12.00,13.000,0,11,3,'Available',1,'[\"QB ZZQA51PGWVA changed\"]',0,NULL,0,'INACTIVE','1','2026-10-12 14:57:34','2026-10-12 14:57:46','1','1','MAIN');
/*!40000 ALTER TABLE `restaurant_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_order`
--

DROP TABLE IF EXISTS `restaurant_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_number` varchar(100) NOT NULL,
  `order_date` date NOT NULL,
  `order_time` time NOT NULL,
  `order_type` enum('Dine-In','Takeaway','Delivery','Room Service') NOT NULL,
  `table_id` int DEFAULT NULL,
  `table_code` varchar(100) DEFAULT NULL,
  `room_no` varchar(50) DEFAULT NULL,
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
  `estimated_prep_time` int DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_order_number` (`company_id`,`branch_id`,`order_number`),
  UNIQUE KEY `ix_restaurant_order_token` (`token`),
  KEY `ix_restaurant_order_payment_status` (`payment_status`),
  KEY `ix_restaurant_order_guest_mobile` (`guest_mobile`),
  KEY `ix_restaurant_order_floor_code` (`floor_code`),
  KEY `ix_restaurant_order_table_code` (`table_code`),
  KEY `ix_restaurant_order_order_number` (`order_number`),
  KEY `ix_restaurant_order_floor_id` (`floor_id`),
  KEY `ix_restaurant_order_table_id` (`table_id`),
  KEY `ix_restaurant_order_id` (`id`),
  KEY `ix_restaurant_order_order_status` (`order_status`),
  KEY `ix_restaurant_order_status` (`status`),
  KEY `ix_restaurant_order_company_id` (`company_id`),
  KEY `ix_restaurant_order_branch_id` (`branch_id`),
  KEY `ix_restaurant_order_guest_id` (`guest_id`),
  KEY `ix_restaurant_order_room_no` (`room_no`),
  KEY `ix_restaurant_order_order_date` (`order_date`),
  KEY `ix_restaurant_order_order_type` (`order_type`),
  KEY `ix_restaurant_order_server_id` (`server_id`),
  CONSTRAINT `restaurant_order_ibfk_1` FOREIGN KEY (`table_id`) REFERENCES `restaurant_table` (`id`),
  CONSTRAINT `restaurant_order_ibfk_2` FOREIGN KEY (`floor_id`) REFERENCES `restaurant_floor` (`id`),
  CONSTRAINT `restaurant_order_ibfk_3` FOREIGN KEY (`guest_id`) REFERENCES `guest` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_order`
--

LOCK TABLES `restaurant_order` WRITE;
/*!40000 ALTER TABLE `restaurant_order` DISABLE KEYS */;
INSERT INTO `restaurant_order` VALUES (1,'RO-20261009-001','2026-10-09','13:15:00','Dine-In',4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',2740.00,150.70,274.00,NULL,NULL,0.00,3164.70,NULL,NULL,'c33e7535-c8d6-4737-a036-3d43b0e9edc4','ACTIVE','1','2026-10-09 13:15:00',NULL,NULL,'1','1'),(2,'RO-20261008-002','2026-10-08','14:15:00','Dine-In',7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',2410.00,132.55,241.00,NULL,NULL,0.00,2783.55,NULL,NULL,'4f7f4702-9be5-4bc9-9e48-9e1303a36ea9','ACTIVE','1','2026-10-08 14:15:00',NULL,NULL,'1','1'),(3,'RO-20261010-003','2026-10-10','15:15:00','Dine-In',10,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',1780.00,97.90,178.00,NULL,NULL,0.00,2055.90,NULL,NULL,'1cc49305-1d88-4ec0-98c9-49da8e5ed94b','ACTIVE','1','2026-10-10 15:15:00',NULL,NULL,'1','1'),(4,'RO-20261009-004','2026-10-09','16:15:00','Dine-In',13,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',3360.00,184.80,336.00,NULL,NULL,0.00,3880.80,NULL,NULL,'6ae143b3-7c86-4ea5-82fc-de710df3f7cd','ACTIVE','1','2026-10-09 16:15:00',NULL,NULL,'1','1'),(5,'RO-20261008-005','2026-10-08','17:15:00','Dine-In',16,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',4030.00,221.65,403.00,NULL,NULL,0.00,4654.65,NULL,NULL,'340aa6a7-7054-426f-bb28-3f731c9c517e','ACTIVE','1','2026-10-08 17:15:00',NULL,NULL,'1','1'),(6,'RO-20261010-006','2026-10-10','18:15:00','Dine-In',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',1430.00,78.65,143.00,NULL,NULL,0.00,1651.65,NULL,NULL,'4065254e-bb04-4b51-a9f1-ab93fe444d91','ACTIVE','1','2026-10-10 18:15:00',NULL,NULL,'1','1'),(7,'RO-20261009-007','2026-10-09','19:15:00','Dine-In',4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',2330.00,128.15,233.00,NULL,NULL,0.00,2691.15,NULL,NULL,'72fac234-5cf8-497b-b182-9a4020f55c4f','ACTIVE','1','2026-10-09 19:15:00',NULL,NULL,'1','1'),(8,'RO-20261008-008','2026-10-08','12:15:00','Dine-In',7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',3220.00,177.10,322.00,NULL,NULL,0.00,3719.10,NULL,NULL,'fa6c3f3c-cac3-431c-950b-f3b88bacea79','ACTIVE','1','2026-10-08 12:15:00',NULL,NULL,'1','1'),(9,'ORD-C5DB7FFB','2026-10-11','20:00:06','Dine-In',1,'FL-GRD-T01',NULL,1,'FL-GRD',NULL,'Flow Tester','+919876500999',2,NULL,NULL,'Completed','Paid',960.00,0.00,0.00,NULL,0.00,0.00,960.00,NULL,NULL,'be159864-207b-464f-916e-e3164d370aa9','ACTIVE','1','2026-10-11 20:00:06','2026-10-11 20:00:06','1','1','MAIN'),(10,'ORD-E8491E8D','2026-10-11','20:04:20','Dine-In',2,'FL-GRD-T02',NULL,1,'FL-GRD',NULL,'Flow Tester','+919876500999',2,NULL,NULL,'Completed','Paid',960.00,0.00,0.00,NULL,0.00,0.00,960.00,NULL,NULL,'52c42b32-fa79-4dfd-85bd-ca292f8b7c3c','ACTIVE','1','2026-10-11 20:04:20','2026-10-11 20:04:21','1','1','MAIN'),(24,'ORD-8EF35DF1','2026-10-12','14:16:28','Dine-In',4,'FL-GRD-T04',NULL,1,'FL-GRD',NULL,'Flow Tester','+919876500999',2,NULL,NULL,'Completed','Paid',960.00,0.00,0.00,NULL,0.00,0.00,960.00,NULL,NULL,'79a8f9c6-d037-4782-9177-4836b978309a','ACTIVE','1','2026-10-12 14:16:28','2026-10-12 14:16:29','1','1','MAIN'),(25,'ORD-1F53861D','2026-10-12','14:20:47','Dine-In',5,'FL-GRD-T05',NULL,1,'FL-GRD',NULL,'Flow Tester','+919876500999',2,NULL,NULL,'Completed','Paid',960.00,0.00,0.00,NULL,0.00,0.00,960.00,NULL,NULL,'9e008f6b-68ff-4ba7-b65c-8a13252b915c','ACTIVE','1','2026-10-12 14:20:47','2026-10-12 14:20:47','1','1','MAIN');
/*!40000 ALTER TABLE `restaurant_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_order_item`
--

DROP TABLE IF EXISTS `restaurant_order_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_order_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `menu_id` int NOT NULL,
  `kitchen_id` int NOT NULL,
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
  KEY `ix_restaurant_order_item_item_status` (`item_status`),
  KEY `ix_restaurant_order_item_kitchen_id` (`kitchen_id`),
  KEY `ix_restaurant_order_item_id` (`id`),
  KEY `ix_restaurant_order_item_order_id` (`order_id`),
  KEY `ix_restaurant_order_item_company_id` (`company_id`),
  KEY `ix_restaurant_order_item_menu_id` (`menu_id`),
  KEY `ix_restaurant_order_item_status` (`status`),
  KEY `ix_restaurant_order_item_branch_id` (`branch_id`),
  CONSTRAINT `restaurant_order_item_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `restaurant_order` (`id`),
  CONSTRAINT `restaurant_order_item_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `restaurant_menu` (`id`),
  CONSTRAINT `restaurant_order_item_ibfk_3` FOREIGN KEY (`kitchen_id`) REFERENCES `kitchen` (`id`),
  CONSTRAINT `restaurant_order_item_ibfk_4` FOREIGN KEY (`variant_id`) REFERENCES `menu_variant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_order_item`
--

LOCK TABLES `restaurant_order_item` WRITE;
/*!40000 ALTER TABLE `restaurant_order_item` DISABLE KEYS */;
INSERT INTO `restaurant_order_item` VALUES (1,1,15,2,2,420.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 13:20:00',NULL,NULL,'1','1'),(2,1,1,1,3,320.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 13:20:00',NULL,NULL,'1','1'),(3,1,17,2,1,620.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 13:20:00',NULL,NULL,'1','1'),(4,1,24,3,2,160.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 13:20:00',NULL,NULL,'1','1'),(5,2,22,1,1,150.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 14:20:00',NULL,NULL,'1','1'),(6,2,18,2,3,340.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 14:20:00',NULL,NULL,'1','1'),(7,2,10,1,1,460.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 14:20:00',NULL,NULL,'1','1'),(8,2,20,1,2,90.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 14:20:00',NULL,NULL,'1','1'),(9,2,11,1,2,300.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 14:20:00',NULL,NULL,'1','1'),(10,3,6,1,1,200.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 15:20:00',NULL,NULL,'1','1'),(11,3,13,1,2,340.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 15:20:00',NULL,NULL,'1','1'),(12,3,11,1,3,300.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 15:20:00',NULL,NULL,'1','1'),(13,4,9,1,2,380.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 16:20:00',NULL,NULL,'1','1'),(14,4,4,1,3,420.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 16:20:00',NULL,NULL,'1','1'),(15,4,12,1,2,520.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 16:20:00',NULL,NULL,'1','1'),(16,4,11,1,1,300.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 16:20:00',NULL,NULL,'1','1'),(17,5,9,1,3,380.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 17:20:00',NULL,NULL,'1','1'),(18,5,19,1,1,70.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 17:20:00',NULL,NULL,'1','1'),(19,5,14,1,2,460.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 17:20:00',NULL,NULL,'1','1'),(20,5,12,1,3,520.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 17:20:00',NULL,NULL,'1','1'),(21,5,13,1,1,340.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 17:20:00',NULL,NULL,'1','1'),(22,6,20,1,3,90.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 18:20:00',NULL,NULL,'1','1'),(23,6,7,1,2,160.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 18:20:00',NULL,NULL,'1','1'),(24,6,4,1,2,420.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-10 18:20:00',NULL,NULL,'1','1'),(25,7,20,1,1,90.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 19:20:00',NULL,NULL,'1','1'),(26,7,23,3,1,140.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 19:20:00',NULL,NULL,'1','1'),(27,7,16,2,3,380.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 19:20:00',NULL,NULL,'1','1'),(28,7,1,1,3,320.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-09 19:20:00',NULL,NULL,'1','1'),(29,8,25,3,1,220.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 12:20:00',NULL,NULL,'1','1'),(30,8,23,3,2,140.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 12:20:00',NULL,NULL,'1','1'),(31,8,3,1,3,260.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 12:20:00',NULL,NULL,'1','1'),(32,8,18,2,3,340.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 12:20:00',NULL,NULL,'1','1'),(33,8,14,1,2,460.00,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-10-08 12:20:00',NULL,NULL,'1','1'),(34,9,8,1,2,480.00,'Preparing','no ice',NULL,NULL,'ACTIVE','1','2026-10-11 20:00:06','2026-10-11 20:00:06',NULL,'1','MAIN'),(35,10,8,1,2,480.00,'Preparing','no ice',NULL,NULL,'ACTIVE','1','2026-10-11 20:04:20','2026-10-11 20:04:20',NULL,'1','MAIN'),(36,24,8,1,2,480.00,'Preparing','no ice',NULL,NULL,'ACTIVE','1','2026-10-12 14:16:28','2026-10-12 14:16:28',NULL,'1','MAIN'),(37,25,8,1,2,480.00,'Preparing','no ice',NULL,NULL,'ACTIVE','1','2026-10-12 14:20:47','2026-10-12 14:20:47',NULL,'1','MAIN');
/*!40000 ALTER TABLE `restaurant_order_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_order_item_modifier`
--

DROP TABLE IF EXISTS `restaurant_order_item_modifier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_order_item_modifier` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_item_id` int NOT NULL,
  `modifier_id` int NOT NULL,
  `modifier_name` varchar(100) NOT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_restaurant_order_item_modifier_order_item_id` (`order_item_id`),
  KEY `ix_restaurant_order_item_modifier_id` (`id`),
  KEY `ix_restaurant_order_item_modifier_branch_id` (`branch_id`),
  KEY `ix_restaurant_order_item_modifier_company_id` (`company_id`),
  KEY `ix_restaurant_order_item_modifier_modifier_id` (`modifier_id`),
  CONSTRAINT `restaurant_order_item_modifier_ibfk_1` FOREIGN KEY (`order_item_id`) REFERENCES `restaurant_order_item` (`id`),
  CONSTRAINT `restaurant_order_item_modifier_ibfk_2` FOREIGN KEY (`modifier_id`) REFERENCES `menu_modifier` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_order_item_modifier`
--

LOCK TABLES `restaurant_order_item_modifier` WRITE;
/*!40000 ALTER TABLE `restaurant_order_item_modifier` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_order_item_modifier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_settings`
--

DROP TABLE IF EXISTS `restaurant_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_settings` (
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
  UNIQUE KEY `uq_setting_key` (`company_id`,`branch_id`,`setting_key`),
  KEY `ix_restaurant_settings_branch_id` (`branch_id`),
  KEY `ix_restaurant_settings_id` (`id`),
  KEY `ix_restaurant_settings_setting_key` (`setting_key`),
  KEY `ix_restaurant_settings_company_id` (`company_id`),
  KEY `ix_restaurant_settings_status` (`status`),
  KEY `ix_restaurant_settings_setting_group` (`setting_group`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_settings`
--

LOCK TABLES `restaurant_settings` WRITE;
/*!40000 ALTER TABLE `restaurant_settings` DISABLE KEYS */;
INSERT INTO `restaurant_settings` VALUES (1,'service_charge_percent','10','ServiceCharge','Service charge added to dine-in bills','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(2,'default_tax_percent','5','Tax','GST applied to restaurant bills','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(3,'opening_time','07:00','OperatingHours','Kitchen opens','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(4,'closing_time','23:30','OperatingHours','Last order','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(5,'bill_prefix','RB','Numbering','Prefix for restaurant bill numbers','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(6,'order_prefix','RO','Numbering','Prefix for restaurant order numbers','ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `restaurant_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_staff_assignment`
--

DROP TABLE IF EXISTS `restaurant_staff_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_staff_assignment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `employee_name` varchar(150) DEFAULT NULL,
  `role` enum('Waiter','Chef','Cashier','Manager') NOT NULL,
  `shift_date` date NOT NULL,
  `shift_start` time NOT NULL,
  `shift_end` time DEFAULT NULL,
  `section` varchar(100) DEFAULT NULL,
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
  `active_employee_date` varchar(40) GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then concat(cast(`employee_id` as char charset utf8mb4),_utf8mb4':',date_format(`shift_date`,_utf8mb4'%Y-%m-%d')) else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_restaurant_staff_active_employee_date` (`company_id`,`active_employee_date`),
  KEY `ix_restaurant_staff_assignment_branch_id` (`branch_id`),
  KEY `ix_restaurant_staff_assignment_floor_id` (`floor_id`),
  KEY `ix_restaurant_staff_assignment_role` (`role`),
  KEY `ix_restaurant_staff_assignment_shift_date` (`shift_date`),
  KEY `ix_restaurant_staff_assignment_shift_status` (`shift_status`),
  KEY `ix_restaurant_staff_assignment_status` (`status`),
  KEY `ix_restaurant_staff_assignment_company_id` (`company_id`),
  KEY `ix_restaurant_staff_assignment_id` (`id`),
  KEY `ix_restaurant_staff_assignment_employee_id` (`employee_id`),
  KEY `ix_restaurant_staff_assignment_section` (`section`),
  CONSTRAINT `restaurant_staff_assignment_ibfk_1` FOREIGN KEY (`floor_id`) REFERENCES `restaurant_floor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_staff_assignment`
--

LOCK TABLES `restaurant_staff_assignment` WRITE;
/*!40000 ALTER TABLE `restaurant_staff_assignment` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_staff_assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_table`
--

DROP TABLE IF EXISTS `restaurant_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `table_code` varchar(100) NOT NULL,
  `table_name` varchar(100) NOT NULL,
  `table_number` int NOT NULL,
  `floor_id` int NOT NULL,
  `floor_code` varchar(100) NOT NULL,
  `table_type` enum('Standard','VIP','Private') NOT NULL,
  `seating_capacity` int NOT NULL,
  `section` enum('Restaurant','Outdoor','Banquet') DEFAULT NULL,
  `current_order_id` int DEFAULT NULL,
  `server_id` varchar(100) DEFAULT NULL,
  `server_name` varchar(100) DEFAULT NULL,
  `position_x` decimal(10,2) DEFAULT NULL,
  `position_y` decimal(10,2) DEFAULT NULL,
  `shape` varchar(50) DEFAULT NULL,
  `color_code` varchar(20) DEFAULT NULL,
  `table_status` enum('Available','Occupied','Reserved','Cleaning','Blocked') NOT NULL,
  `is_mergeable` tinyint(1) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  `active_table_number` int GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `table_number` else NULL end)) STORED,
  `active_table_name` varchar(100) GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ACTIVE') then `table_name` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_table_code` (`company_id`,`branch_id`,`table_code`),
  UNIQUE KEY `uq_restaurant_table_active_number` (`company_id`,`branch_id`,`floor_id`,`active_table_number`),
  UNIQUE KEY `uq_restaurant_table_active_name` (`company_id`,`branch_id`,`floor_id`,`active_table_name`),
  KEY `ix_restaurant_table_current_order_id` (`current_order_id`),
  KEY `ix_restaurant_table_table_number` (`table_number`),
  KEY `ix_restaurant_table_id` (`id`),
  KEY `ix_restaurant_table_server_id` (`server_id`),
  KEY `ix_restaurant_table_table_code` (`table_code`),
  KEY `ix_restaurant_table_floor_code` (`floor_code`),
  KEY `ix_restaurant_table_table_type` (`table_type`),
  KEY `ix_restaurant_table_branch_id` (`branch_id`),
  KEY `ix_restaurant_table_floor_id` (`floor_id`),
  KEY `ix_restaurant_table_section` (`section`),
  KEY `ix_restaurant_table_table_status` (`table_status`),
  KEY `ix_restaurant_table_table_name` (`table_name`),
  KEY `ix_restaurant_table_company_id` (`company_id`),
  KEY `ix_restaurant_table_status` (`status`),
  CONSTRAINT `restaurant_table_ibfk_1` FOREIGN KEY (`floor_id`) REFERENCES `restaurant_floor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_table`
--

LOCK TABLES `restaurant_table` WRITE;
/*!40000 ALTER TABLE `restaurant_table` DISABLE KEYS */;
INSERT INTO `restaurant_table` (`id`, `table_code`, `table_name`, `table_number`, `floor_id`, `floor_code`, `table_type`, `seating_capacity`, `section`, `current_order_id`, `server_id`, `server_name`, `position_x`, `position_y`, `shape`, `color_code`, `table_status`, `is_mergeable`, `status`, `created_by`, `created_at`, `updated_at`, `updated_by`, `company_id`, `branch_id`) VALUES (1,'FL-GRD-T01','Table 1',1,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,60.00,0.00,'round','#E5E7EB','Cleaning',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-11 20:00:06','1','1','1'),(2,'FL-GRD-T02','Table 2',2,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,120.00,0.00,'square','#E5E7EB','Cleaning',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-11 20:04:21','1','1','1'),(3,'FL-GRD-T03','Table 3',3,1,'FL-GRD','Standard',2,'Restaurant',NULL,NULL,NULL,180.00,0.00,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-12 13:24:15','1','1','1'),(4,'FL-GRD-T04','Table 4',4,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,0.00,60.00,'square','#E5E7EB','Cleaning',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-12 14:16:29','1','1','1'),(5,'FL-GRD-T05','Table 5',5,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,60.00,60.00,'round','#E5E7EB','Cleaning',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-12 14:20:47','1','1','1'),(6,'FL-GRD-T06','Table 6',6,1,'FL-GRD','Standard',2,'Restaurant',NULL,NULL,NULL,120.00,60.00,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-12 14:57:25','1','1','1'),(7,'FL-GRD-T07','Table 7',7,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,180.00,60.00,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-11 22:31:08','1','1','1'),(8,'FL-GRD-T08','Table 8',8,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,0.00,120.00,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-11 22:37:40','1','1','1'),(9,'FL-FST-T01','Table 9',9,2,'FL-FST','Standard',4,'Restaurant',NULL,NULL,NULL,60.00,0.00,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-11 22:41:14','1','1','1'),(10,'FL-FST-T02','Table 10',10,2,'FL-FST','Standard',4,'Restaurant',NULL,NULL,NULL,120.00,0.00,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-11 22:49:31','1','1','1'),(11,'FL-FST-T03','Table 11',11,2,'FL-FST','Standard',2,'Restaurant',NULL,NULL,NULL,180.00,0.00,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-11 22:58:54','1','1','1'),(12,'FL-FST-T04','Table 12',12,2,'FL-FST','Standard',4,'Restaurant',NULL,NULL,NULL,0.00,60.00,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00','2026-10-11 23:00:13','1','1','1'),(13,'FL-FST-T05','Table 13',13,2,'FL-FST','Standard',4,'Restaurant',NULL,NULL,NULL,60.00,60.00,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(14,'FL-FST-T06','Table 14',14,2,'FL-FST','Standard',2,'Restaurant',NULL,NULL,NULL,120.00,60.00,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(15,'FL-TER-T01','Table 15',15,3,'FL-TER','VIP',4,'Outdoor',NULL,NULL,NULL,60.00,0.00,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(16,'FL-TER-T02','Table 16',16,3,'FL-TER','Standard',4,'Outdoor',NULL,NULL,NULL,120.00,0.00,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(17,'FL-TER-T03','Table 17',17,3,'FL-TER','Standard',2,'Outdoor',NULL,NULL,NULL,180.00,0.00,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1'),(18,'FL-TER-T04','Table 18',18,3,'FL-TER','Standard',4,'Outdoor',NULL,NULL,NULL,0.00,60.00,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-10-10 09:00:00',NULL,NULL,'1','1');
/*!40000 ALTER TABLE `restaurant_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_table_merge`
--

DROP TABLE IF EXISTS `restaurant_table_merge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_table_merge` (
  `id` int NOT NULL AUTO_INCREMENT,
  `merge_code` varchar(100) NOT NULL,
  `merged_table_name` varchar(150) NOT NULL,
  `merged_by` varchar(100) NOT NULL,
  `merge_datetime` datetime DEFAULT (now()),
  `unmerged_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_merge_code` (`company_id`,`branch_id`,`merge_code`),
  KEY `ix_restaurant_table_merge_branch_id` (`branch_id`),
  KEY `ix_restaurant_table_merge_id` (`id`),
  KEY `ix_restaurant_table_merge_merge_code` (`merge_code`),
  KEY `ix_restaurant_table_merge_company_id` (`company_id`),
  KEY `ix_restaurant_table_merge_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_table_merge`
--

LOCK TABLES `restaurant_table_merge` WRITE;
/*!40000 ALTER TABLE `restaurant_table_merge` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_table_merge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_table_merge_detail`
--

DROP TABLE IF EXISTS `restaurant_table_merge_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_table_merge_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `merge_id` int NOT NULL,
  `table_id` int NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_restaurant_table_merge_detail_company_id` (`company_id`),
  KEY `ix_restaurant_table_merge_detail_merge_id` (`merge_id`),
  KEY `ix_restaurant_table_merge_detail_id` (`id`),
  KEY `ix_restaurant_table_merge_detail_table_id` (`table_id`),
  KEY `ix_restaurant_table_merge_detail_status` (`status`),
  KEY `ix_restaurant_table_merge_detail_branch_id` (`branch_id`),
  CONSTRAINT `restaurant_table_merge_detail_ibfk_1` FOREIGN KEY (`merge_id`) REFERENCES `restaurant_table_merge` (`id`),
  CONSTRAINT `restaurant_table_merge_detail_ibfk_2` FOREIGN KEY (`table_id`) REFERENCES `restaurant_table` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_table_merge_detail`
--

LOCK TABLES `restaurant_table_merge_detail` WRITE;
/*!40000 ALTER TABLE `restaurant_table_merge_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_table_merge_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_table_reservation`
--

DROP TABLE IF EXISTS `restaurant_table_reservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_table_reservation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reservation_code` varchar(100) NOT NULL,
  `reservation_date` date NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time DEFAULT NULL,
  `table_id` int NOT NULL,
  `table_code` varchar(100) NOT NULL,
  `floor_id` int NOT NULL,
  `floor_code` varchar(100) NOT NULL,
  `guest_name` varchar(100) NOT NULL,
  `guest_mobile` varchar(20) NOT NULL,
  `guest_email` varchar(100) DEFAULT NULL,
  `no_of_guests` int NOT NULL,
  `reservation_type` enum('Walk-In','Phone','Online','Hotel Guest') NOT NULL,
  `occasion` varchar(100) DEFAULT NULL,
  `special_requests` varchar(255) DEFAULT NULL,
  `reservation_status` enum('Reserved','Checked-In','Cancelled','No-Show','Completed') NOT NULL,
  `check_in_time` time DEFAULT NULL,
  `check_out_time` time DEFAULT NULL,
  `order_id` int DEFAULT NULL,
  `order_number` varchar(100) DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_reservation_code` (`company_id`,`branch_id`,`reservation_code`),
  UNIQUE KEY `ix_restaurant_table_reservation_token` (`token`),
  KEY `ix_restaurant_table_reservation_guest_name` (`guest_name`),
  KEY `ix_restaurant_table_reservation_reservation_date` (`reservation_date`),
  KEY `ix_restaurant_table_reservation_reservation_type` (`reservation_type`),
  KEY `ix_restaurant_table_reservation_table_id` (`table_id`),
  KEY `ix_restaurant_table_reservation_table_code` (`table_code`),
  KEY `ix_restaurant_table_reservation_reservation_code` (`reservation_code`),
  KEY `ix_restaurant_table_reservation_floor_code` (`floor_code`),
  KEY `ix_restaurant_table_reservation_order_id` (`order_id`),
  KEY `ix_restaurant_table_reservation_order_number` (`order_number`),
  KEY `ix_restaurant_table_reservation_branch_id` (`branch_id`),
  KEY `ix_restaurant_table_reservation_id` (`id`),
  KEY `ix_restaurant_table_reservation_status` (`status`),
  KEY `ix_restaurant_table_reservation_guest_mobile` (`guest_mobile`),
  KEY `ix_restaurant_table_reservation_reservation_status` (`reservation_status`),
  KEY `ix_restaurant_table_reservation_company_id` (`company_id`),
  KEY `ix_restaurant_table_reservation_floor_id` (`floor_id`),
  KEY `ix_restaurant_reservation_table_date_status` (`company_id`,`table_id`,`reservation_date`,`status`,`start_time`),
  CONSTRAINT `restaurant_table_reservation_ibfk_1` FOREIGN KEY (`table_id`) REFERENCES `restaurant_table` (`id`),
  CONSTRAINT `restaurant_table_reservation_ibfk_2` FOREIGN KEY (`floor_id`) REFERENCES `restaurant_floor` (`id`),
  CONSTRAINT `restaurant_table_reservation_ibfk_3` FOREIGN KEY (`order_id`) REFERENCES `restaurant_order` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_table_reservation`
--

LOCK TABLES `restaurant_table_reservation` WRITE;
/*!40000 ALTER TABLE `restaurant_table_reservation` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_table_reservation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_waitlist`
--

DROP TABLE IF EXISTS `restaurant_waitlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_waitlist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `waitlist_code` varchar(100) NOT NULL,
  `guest_name` varchar(100) NOT NULL,
  `guest_mobile` varchar(20) NOT NULL,
  `party_size` int NOT NULL,
  `floor_id` int DEFAULT NULL,
  `section` varchar(100) DEFAULT NULL,
  `wait_start_time` datetime DEFAULT (now()),
  `estimated_wait_minutes` int DEFAULT NULL,
  `waitlist_status` enum('Waiting','Notified','Seated','Cancelled') NOT NULL,
  `notified_at` datetime DEFAULT NULL,
  `seated_at` datetime DEFAULT NULL,
  `table_id` int DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_waitlist_code` (`company_id`,`branch_id`,`waitlist_code`),
  KEY `ix_restaurant_waitlist_guest_name` (`guest_name`),
  KEY `ix_restaurant_waitlist_waitlist_status` (`waitlist_status`),
  KEY `ix_restaurant_waitlist_status` (`status`),
  KEY `ix_restaurant_waitlist_floor_id` (`floor_id`),
  KEY `ix_restaurant_waitlist_id` (`id`),
  KEY `ix_restaurant_waitlist_branch_id` (`branch_id`),
  KEY `ix_restaurant_waitlist_waitlist_code` (`waitlist_code`),
  KEY `ix_restaurant_waitlist_section` (`section`),
  KEY `ix_restaurant_waitlist_table_id` (`table_id`),
  KEY `ix_restaurant_waitlist_guest_mobile` (`guest_mobile`),
  KEY `ix_restaurant_waitlist_company_id` (`company_id`),
  CONSTRAINT `restaurant_waitlist_ibfk_1` FOREIGN KEY (`floor_id`) REFERENCES `restaurant_floor` (`id`),
  CONSTRAINT `restaurant_waitlist_ibfk_2` FOREIGN KEY (`table_id`) REFERENCES `restaurant_table` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_waitlist`
--

LOCK TABLES `restaurant_waitlist` WRITE;
/*!40000 ALTER TABLE `restaurant_waitlist` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_waitlist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff_performance_report`
--

DROP TABLE IF EXISTS `staff_performance_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_performance_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `employee_id` int NOT NULL,
  `role` enum('Waiter','Chef','Cashier','Manager') NOT NULL,
  `total_orders` int DEFAULT NULL,
  `total_sales` decimal(12,2) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_staff_performance_report_line` (`company_id`,`branch_id`,`report_date`,`employee_id`),
  KEY `ix_staff_performance_report_company_id` (`company_id`),
  KEY `ix_staff_performance_report_report_date` (`report_date`),
  KEY `ix_staff_performance_report_branch_id` (`branch_id`),
  KEY `ix_staff_performance_report_status` (`status`),
  KEY `ix_staff_performance_report_id` (`id`),
  KEY `ix_staff_performance_report_role` (`role`),
  KEY `ix_staff_performance_report_employee_id` (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_performance_report`
--

LOCK TABLES `staff_performance_report` WRITE;
/*!40000 ALTER TABLE `staff_performance_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `staff_performance_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'hotelerp_restaurant'
--

--
-- Dumping routines for database 'hotelerp_restaurant'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-12 15:32:59
