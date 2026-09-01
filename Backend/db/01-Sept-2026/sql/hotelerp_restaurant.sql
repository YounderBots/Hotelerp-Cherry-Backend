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
INSERT INTO `alembic_version` VALUES ('3e3d820c4703');
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
  `total_sales` float DEFAULT NULL,
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
  `combo_price` float NOT NULL,
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_combo_code` (`company_id`,`branch_id`,`combo_code`),
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
  `loyalty_points` float DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_guest_mobile` (`company_id`,`branch_id`,`mobile`),
  UNIQUE KEY `ix_guest_guest_code` (`guest_code`),
  KEY `ix_guest_email` (`email`),
  KEY `ix_guest_first_name` (`first_name`),
  KEY `ix_guest_guest_type` (`guest_type`),
  KEY `ix_guest_company_id` (`company_id`),
  KEY `ix_guest_last_name` (`last_name`),
  KEY `ix_guest_branch_id` (`branch_id`),
  KEY `ix_guest_status` (`status`),
  KEY `ix_guest_mobile` (`mobile`),
  KEY `ix_guest_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest`
--

LOCK TABLES `guest` WRITE;
/*!40000 ALTER TABLE `guest` DISABLE KEYS */;
INSERT INTO `guest` VALUES (1,'RG-0001','Deepak','Anand','9840120007','deepak.anand@gmail.com','Regular',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'RG-0002','Sridevi','Raman','9840120014','sridevi.raman@gmail.com','VIP',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'RG-0003','Michael','Fernandes','9840120021','michael.fernandes@gmail.com','Walk-In',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(4,'RG-0004','Aisha','Rahman','9840120028','aisha.rahman@gmail.com','Regular',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(5,'RG-0005','Ganesh','Iyer','9840120035','ganesh.iyer@gmail.com','VIP',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(6,'RG-0006','Sarah','Thomas','9840120042','sarah.thomas@gmail.com','Walk-In',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(7,'RG-0007','Rohan','Mehta','9840120049','rohan.mehta@gmail.com','Hotel Guest',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(8,'RG-0008','Priya','Nair','9840120056','priya.nair@gmail.com','Hotel Guest',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  `total_amount` float DEFAULT NULL,
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
  UNIQUE KEY `uq_inventory_item_code` (`company_id`,`branch_id`,`item_code`),
  KEY `ix_inventory_item_unit` (`unit`),
  KEY `ix_inventory_item_id` (`id`),
  KEY `ix_inventory_item_status` (`status`),
  KEY `ix_inventory_item_branch_id` (`branch_id`),
  KEY `ix_inventory_item_item_code` (`item_code`),
  KEY `ix_inventory_item_item_name` (`item_name`),
  KEY `ix_inventory_item_category` (`category`),
  KEY `ix_inventory_item_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_item`
--

LOCK TABLES `inventory_item` WRITE;
/*!40000 ALTER TABLE `inventory_item` DISABLE KEYS */;
INSERT INTO `inventory_item` VALUES (1,'RIN-001','Basmati Rice','Kitchen Store','Kg',11,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'RIN-002','Paneer','Kitchen Store','Kg',12,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'RIN-003','Chicken','Kitchen Store','Kg',13,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(4,'RIN-004','Prawns','Kitchen Store','Kg',14,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(5,'RIN-005','Refined Oil','Kitchen Store','Litre',15,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(6,'RIN-006','Wheat Flour','Kitchen Store','Kg',16,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(7,'RIN-007','Onion','Kitchen Store','Kg',17,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(8,'RIN-008','Tomato','Kitchen Store','Kg',18,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(9,'RIN-009','Fresh Cream','Kitchen Store','Litre',19,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(10,'RIN-010','Mixed Spices','Kitchen Store','Kg',20,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  UNIQUE KEY `uq_inventory_stock_location` (`inventory_item_id`,`kitchen_id`,`company_id`,`branch_id`),
  KEY `ix_inventory_stock_id` (`id`),
  KEY `ix_inventory_stock_inventory_item_id` (`inventory_item_id`),
  KEY `ix_inventory_stock_status` (`status`),
  KEY `ix_inventory_stock_branch_id` (`branch_id`),
  KEY `ix_inventory_stock_kitchen_id` (`kitchen_id`),
  KEY `ix_inventory_stock_company_id` (`company_id`),
  CONSTRAINT `inventory_stock_ibfk_1` FOREIGN KEY (`inventory_item_id`) REFERENCES `inventory_item` (`id`),
  CONSTRAINT `inventory_stock_ibfk_2` FOREIGN KEY (`kitchen_id`) REFERENCES `kitchen` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_stock`
--

LOCK TABLES `inventory_stock` WRITE;
/*!40000 ALTER TABLE `inventory_stock` DISABLE KEYS */;
INSERT INTO `inventory_stock` VALUES (1,1,1,46,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,2,1,52,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,3,1,58,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(4,4,1,64,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(5,5,1,70,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(6,6,1,76,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(7,7,1,82,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(8,8,1,88,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(9,9,1,94,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(10,10,1,100,'2026-08-31','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  `quantity` float NOT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  `total_amount` float DEFAULT NULL,
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
INSERT INTO `kitchen` VALUES (1,'KIT-MAIN','Main Kitchen','Main','KIT-MAIN-PRN',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'KIT-GRILL','Grill Kitchen','Grill','KIT-GRILL-PRN',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'KIT-DESS','Dessert Kitchen','Dessert','KIT-DESS-PRN',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_order_item`
--

LOCK TABLES `kitchen_order_item` WRITE;
/*!40000 ALTER TABLE `kitchen_order_item` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_order_ticket`
--

LOCK TABLES `kitchen_order_ticket` WRITE;
/*!40000 ALTER TABLE `kitchen_order_ticket` DISABLE KEYS */;
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
  `avg_preparation_time` float DEFAULT NULL,
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
INSERT INTO `menu_category` VALUES (1,'CAT-STR','Starters','Starters menu section',1,1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'CAT-SOUP','Soups & Salads','Soups & Salads menu section',1,2,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'CAT-MAIN','Main Course','Main Course menu section',1,3,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(4,'CAT-GRILL','Tandoor & Grill','Tandoor & Grill menu section',2,4,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(5,'CAT-BRD','Breads & Rice','Breads & Rice menu section',1,5,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(6,'CAT-DES','Desserts','Desserts menu section',3,6,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  `quantity_required` float NOT NULL,
  `unit` enum('Kg','Gram','Litre','ml','Nos') NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_menu_recipe_line` (`menu_id`,`inventory_item_id`),
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
  `price` float NOT NULL,
  `status` enum('ACTIVE','INACTIVE') NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `branch_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_menu_variant_name` (`menu_id`,`variant_name`),
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
INSERT INTO `payment_method` VALUES (1,'Cash','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'Credit Card','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'Debit Card','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(4,'UPI','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(5,'Room Charge','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  `total_amount` float DEFAULT NULL,
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
  `sub_total` float DEFAULT NULL,
  `cgst_percentage` float DEFAULT NULL,
  `cgst_amount` float DEFAULT NULL,
  `sgst_percentage` float DEFAULT NULL,
  `sgst_amount` float DEFAULT NULL,
  `igst_percentage` float DEFAULT NULL,
  `igst_amount` float DEFAULT NULL,
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
  UNIQUE KEY `uq_bill_number` (`company_id`,`branch_id`,`bill_number`),
  UNIQUE KEY `ix_restaurant_bill_token` (`token`),
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill`
--

LOCK TABLES `restaurant_bill` WRITE;
/*!40000 ALTER TABLE `restaurant_bill` DISABLE KEYS */;
INSERT INTO `restaurant_bill` VALUES (1,'RB-20260831-001','2026-08-31','13:55:00',1,'RO-20260831-001',4,'FL-GRD-T04',NULL,NULL,NULL,NULL,2740,2.5,75.35,2.5,75.35,0,0,10,274,NULL,0,0,0,3164.7,'Paid','Paid',NULL,'b6a4358e-40fd-40f2-a124-f6f8c3ba6451','ACTIVE','1','2026-08-31 13:55:00',NULL,NULL,'1','1'),(2,'RB-20260830-002','2026-08-30','14:55:00',2,'RO-20260830-002',7,'FL-GRD-T07',NULL,NULL,NULL,NULL,2410,2.5,66.28,2.5,66.27,0,0,10,241,NULL,0,0,0,2783.55,'Paid','Paid',NULL,'496a235f-8be0-4538-b361-1f98f5b4a78c','ACTIVE','1','2026-08-30 14:55:00',NULL,NULL,'1','1'),(3,'RB-20260901-003','2026-09-01','15:55:00',3,'RO-20260901-003',10,'FL-FST-T02',NULL,NULL,NULL,NULL,1780,2.5,48.95,2.5,48.95,0,0,10,178,NULL,0,0,0,2055.9,'Paid','Paid',NULL,'d6c4363d-f5b3-42d7-9687-8d323bc97bb6','ACTIVE','1','2026-09-01 15:55:00',NULL,NULL,'1','1'),(4,'RB-20260831-004','2026-08-31','16:55:00',4,'RO-20260831-004',13,'FL-FST-T05',NULL,NULL,NULL,NULL,3360,2.5,92.4,2.5,92.4,0,0,10,336,NULL,0,0,0,3880.8,'Paid','Paid',NULL,'623edeec-7dec-4c33-adce-8e61edd098dd','ACTIVE','1','2026-08-31 16:55:00',NULL,NULL,'1','1'),(5,'RB-20260830-005','2026-08-30','17:55:00',5,'RO-20260830-005',16,'FL-TER-T02',NULL,NULL,NULL,NULL,4030,2.5,110.83,2.5,110.82,0,0,10,403,NULL,0,0,0,4654.65,'Paid','Paid',NULL,'b18b1068-fe34-402c-b5f8-9d8142000a8a','ACTIVE','1','2026-08-30 17:55:00',NULL,NULL,'1','1'),(6,'RB-20260901-006','2026-09-01','18:55:00',6,'RO-20260901-006',1,'FL-GRD-T01',NULL,NULL,NULL,NULL,1430,2.5,39.33,2.5,39.32,0,0,10,143,NULL,0,0,0,1651.65,'Paid','Paid',NULL,'7c9e8e32-e8bc-4774-beda-1c671ac43316','ACTIVE','1','2026-09-01 18:55:00',NULL,NULL,'1','1'),(7,'RB-20260831-007','2026-08-31','19:55:00',7,'RO-20260831-007',4,'FL-GRD-T04',NULL,NULL,NULL,NULL,2330,2.5,64.08,2.5,64.07,0,0,10,233,NULL,0,0,0,2691.15,'Paid','Paid',NULL,'aed51b1f-fb8d-4b3f-87d6-6b36d3a61083','ACTIVE','1','2026-08-31 19:55:00',NULL,NULL,'1','1'),(8,'RB-20260830-008','2026-08-30','12:55:00',8,'RO-20260830-008',7,'FL-GRD-T07',NULL,NULL,NULL,NULL,3220,2.5,88.55,2.5,88.55,0,0,10,322,NULL,0,0,0,3719.1,'Paid','Paid',NULL,'5101c7d2-2c76-4fba-9da1-9e71bd738f35','ACTIVE','1','2026-08-30 12:55:00',NULL,NULL,'1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill_item`
--

LOCK TABLES `restaurant_bill_item` WRITE;
/*!40000 ALTER TABLE `restaurant_bill_item` DISABLE KEYS */;
INSERT INTO `restaurant_bill_item` VALUES (1,1,1,15,'Tandoori Chicken (Half)',2,420,840,NULL,'ACTIVE','1','2026-08-31 13:55:00',NULL,NULL,'1','1'),(2,1,2,1,'Paneer Tikka',3,320,960,NULL,'ACTIVE','1','2026-08-31 13:55:00',NULL,NULL,'1','1'),(3,1,3,17,'Tandoori Pomfret',1,620,620,NULL,'ACTIVE','1','2026-08-31 13:55:00',NULL,NULL,'1','1'),(4,1,4,24,'Rasmalai',2,160,320,NULL,'ACTIVE','1','2026-08-31 13:55:00',NULL,NULL,'1','1'),(5,2,5,22,'Steamed Basmati Rice',1,150,150,NULL,'ACTIVE','1','2026-08-30 14:55:00',NULL,NULL,'1','1'),(6,2,6,18,'Grilled Vegetable Platter',3,340,1020,NULL,'ACTIVE','1','2026-08-30 14:55:00',NULL,NULL,'1','1'),(7,2,7,10,'Chettinad Chicken Curry',1,460,460,NULL,'ACTIVE','1','2026-08-30 14:55:00',NULL,NULL,'1','1'),(8,2,8,20,'Garlic Naan',2,90,180,NULL,'ACTIVE','1','2026-08-30 14:55:00',NULL,NULL,'1','1'),(9,2,9,11,'Dal Makhani',2,300,600,NULL,'ACTIVE','1','2026-08-30 14:55:00',NULL,NULL,'1','1'),(10,3,10,6,'Mulligatawny Soup',1,200,200,NULL,'ACTIVE','1','2026-09-01 15:55:00',NULL,NULL,'1','1'),(11,3,11,13,'Vegetable Biryani',2,340,680,NULL,'ACTIVE','1','2026-09-01 15:55:00',NULL,NULL,'1','1'),(12,3,12,11,'Dal Makhani',3,300,900,NULL,'ACTIVE','1','2026-09-01 15:55:00',NULL,NULL,'1','1'),(13,4,13,9,'Paneer Butter Masala',2,380,760,NULL,'ACTIVE','1','2026-08-31 16:55:00',NULL,NULL,'1','1'),(14,4,14,4,'Prawn Koliwada',3,420,1260,NULL,'ACTIVE','1','2026-08-31 16:55:00',NULL,NULL,'1','1'),(15,4,15,12,'Kerala Fish Curry',2,520,1040,NULL,'ACTIVE','1','2026-08-31 16:55:00',NULL,NULL,'1','1'),(16,4,16,11,'Dal Makhani',1,300,300,NULL,'ACTIVE','1','2026-08-31 16:55:00',NULL,NULL,'1','1'),(17,5,17,9,'Paneer Butter Masala',3,380,1140,NULL,'ACTIVE','1','2026-08-30 17:55:00',NULL,NULL,'1','1'),(18,5,18,19,'Butter Naan',1,70,70,NULL,'ACTIVE','1','2026-08-30 17:55:00',NULL,NULL,'1','1'),(19,5,19,14,'Hyderabadi Chicken Biryani',2,460,920,NULL,'ACTIVE','1','2026-08-30 17:55:00',NULL,NULL,'1','1'),(20,5,20,12,'Kerala Fish Curry',3,520,1560,NULL,'ACTIVE','1','2026-08-30 17:55:00',NULL,NULL,'1','1'),(21,5,21,13,'Vegetable Biryani',1,340,340,NULL,'ACTIVE','1','2026-08-30 17:55:00',NULL,NULL,'1','1'),(22,6,22,20,'Garlic Naan',3,90,270,NULL,'ACTIVE','1','2026-09-01 18:55:00',NULL,NULL,'1','1'),(23,6,23,7,'Garden Green Salad',2,160,320,NULL,'ACTIVE','1','2026-09-01 18:55:00',NULL,NULL,'1','1'),(24,6,24,4,'Prawn Koliwada',2,420,840,NULL,'ACTIVE','1','2026-09-01 18:55:00',NULL,NULL,'1','1'),(25,7,25,20,'Garlic Naan',1,90,90,NULL,'ACTIVE','1','2026-08-31 19:55:00',NULL,NULL,'1','1'),(26,7,26,23,'Gulab Jamun',1,140,140,NULL,'ACTIVE','1','2026-08-31 19:55:00',NULL,NULL,'1','1'),(27,7,27,16,'Seekh Kebab',3,380,1140,NULL,'ACTIVE','1','2026-08-31 19:55:00',NULL,NULL,'1','1'),(28,7,28,1,'Paneer Tikka',3,320,960,NULL,'ACTIVE','1','2026-08-31 19:55:00',NULL,NULL,'1','1'),(29,8,29,25,'Chocolate Brownie',1,220,220,NULL,'ACTIVE','1','2026-08-30 12:55:00',NULL,NULL,'1','1'),(30,8,30,23,'Gulab Jamun',2,140,280,NULL,'ACTIVE','1','2026-08-30 12:55:00',NULL,NULL,'1','1'),(31,8,31,3,'Gobi Manchurian',3,260,780,NULL,'ACTIVE','1','2026-08-30 12:55:00',NULL,NULL,'1','1'),(32,8,32,18,'Grilled Vegetable Platter',3,340,1020,NULL,'ACTIVE','1','2026-08-30 12:55:00',NULL,NULL,'1','1'),(33,8,33,14,'Hyderabadi Chicken Biryani',2,460,920,NULL,'ACTIVE','1','2026-08-30 12:55:00',NULL,NULL,'1','1');
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
  KEY `ix_restaurant_bill_payment_payment_method_id` (`payment_method_id`),
  KEY `ix_restaurant_bill_payment_company_id` (`company_id`),
  KEY `ix_restaurant_bill_payment_status` (`status`),
  KEY `ix_restaurant_bill_payment_id` (`id`),
  KEY `ix_restaurant_bill_payment_bill_id` (`bill_id`),
  KEY `ix_restaurant_bill_payment_payment_date` (`payment_date`),
  KEY `ix_restaurant_bill_payment_branch_id` (`branch_id`),
  KEY `ix_restaurant_bill_payment_payment_status` (`payment_status`),
  CONSTRAINT `restaurant_bill_payment_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `restaurant_bill` (`id`),
  CONSTRAINT `restaurant_bill_payment_ibfk_2` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill_payment`
--

LOCK TABLES `restaurant_bill_payment` WRITE;
/*!40000 ALTER TABLE `restaurant_bill_payment` DISABLE KEYS */;
INSERT INTO `restaurant_bill_payment` VALUES (1,1,2,3164.7,NULL,'2026-08-31','13:58:00','Success',NULL,'ACTIVE','1','2026-08-31 13:58:00',NULL,NULL,'1','1'),(2,2,3,2783.55,NULL,'2026-08-30','14:58:00','Success',NULL,'ACTIVE','1','2026-08-30 14:58:00',NULL,NULL,'1','1'),(3,3,4,2055.9,NULL,'2026-09-01','15:58:00','Success',NULL,'ACTIVE','1','2026-09-01 15:58:00',NULL,NULL,'1','1'),(4,4,5,3880.8,NULL,'2026-08-31','16:58:00','Success',NULL,'ACTIVE','1','2026-08-31 16:58:00',NULL,NULL,'1','1'),(5,5,1,4654.65,NULL,'2026-08-30','17:58:00','Success',NULL,'ACTIVE','1','2026-08-30 17:58:00',NULL,NULL,'1','1'),(6,6,2,1651.65,NULL,'2026-09-01','18:58:00','Success',NULL,'ACTIVE','1','2026-09-01 18:58:00',NULL,NULL,'1','1'),(7,7,3,2691.15,NULL,'2026-08-31','19:58:00','Success',NULL,'ACTIVE','1','2026-08-31 19:58:00',NULL,NULL,'1','1'),(8,8,4,3719.1,NULL,'2026-08-30','12:58:00','Success',NULL,'ACTIVE','1','2026-08-30 12:58:00',NULL,NULL,'1','1');
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
  `split_amount` float NOT NULL,
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_floor_code` (`company_id`,`branch_id`,`floor_code`),
  KEY `ix_restaurant_floor_branch_id` (`branch_id`),
  KEY `ix_restaurant_floor_status` (`status`),
  KEY `ix_restaurant_floor_company_id` (`company_id`),
  KEY `ix_restaurant_floor_floor_code` (`floor_code`),
  KEY `ix_restaurant_floor_floor_name` (`floor_name`),
  KEY `ix_restaurant_floor_id` (`id`),
  KEY `ix_restaurant_floor_floor_number` (`floor_number`),
  KEY `ix_restaurant_floor_floor_type` (`floor_type`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_floor`
--

LOCK TABLES `restaurant_floor` WRITE;
/*!40000 ALTER TABLE `restaurant_floor` DISABLE KEYS */;
INSERT INTO `restaurant_floor` VALUES (1,'FL-GRD','Ground Floor',1,'Restaurant','Ground Floor seating',8,32,NULL,'#850126',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'FL-FST','First Floor',2,'Restaurant','First Floor seating',6,28,NULL,'#850126',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'FL-TER','Rooftop Terrace',3,'Outdoor','Rooftop Terrace seating',4,16,NULL,'#850126',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  `price` float NOT NULL,
  `cost_price` float DEFAULT NULL,
  `tax_percentage` float DEFAULT NULL,
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_item_code` (`company_id`,`branch_id`,`item_code`),
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_menu`
--

LOCK TABLES `restaurant_menu` WRITE;
/*!40000 ALTER TABLE `restaurant_menu` DISABLE KEYS */;
INSERT INTO `restaurant_menu` VALUES (1,'RES-001','Paneer Tikka','Starters — prepared to order.',1,NULL,320,121.6,5,1,18,1,'Available',1,NULL,0,'/templates/static/upload_image/08d10ad838de41d3a3ee392d04f12451.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'RES-002','Chicken 65','Starters — prepared to order.',1,NULL,340,129.2,5,1,16,1,'Available',0,NULL,0,'/templates/static/upload_image/d9411723dd8f4b70b41ffb4afe9705ee.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'RES-003','Gobi Manchurian','Starters — prepared to order.',1,NULL,260,98.8,5,1,14,1,'Available',1,NULL,0,'/templates/static/upload_image/c1e6203a3f54462f8ee064b908b1208f.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(4,'RES-004','Prawn Koliwada','Starters — prepared to order.',1,NULL,420,159.6,5,1,18,1,'Available',0,NULL,0,'/templates/static/upload_image/baf30ed614b34e6e9e85ee4a41638035.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(5,'RES-005','Sweet Corn Soup','Soups & Salads — prepared to order.',2,NULL,180,68.4,5,1,10,1,'Available',1,NULL,0,'/templates/static/upload_image/cb5ee6201b3b40e8a60231052c3e94ab.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(6,'RES-006','Mulligatawny Soup','Soups & Salads — prepared to order.',2,NULL,200,76,5,1,12,1,'Available',0,NULL,0,'/templates/static/upload_image/148648c8da2e4ec0b4e3b8486f3a1e11.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(7,'RES-007','Garden Green Salad','Soups & Salads — prepared to order.',2,NULL,160,60.8,5,1,6,1,'Available',1,NULL,0,'/templates/static/upload_image/c44d46dc6d1d419e94e83cb0e8a51073.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(8,'RES-008','Butter Chicken','Main Course — prepared to order.',3,NULL,480,182.4,5,1,25,1,'Available',0,NULL,0,'/templates/static/upload_image/45d8c6d9507148aa960c0c50d88e99ce.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(9,'RES-009','Paneer Butter Masala','Main Course — prepared to order.',3,NULL,380,144.4,5,1,22,1,'Available',1,NULL,0,'/templates/static/upload_image/1d12fa57c9364e9eb535939517b21dfd.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(10,'RES-010','Chettinad Chicken Curry','Main Course — prepared to order.',3,NULL,460,174.8,5,1,26,1,'Available',0,NULL,0,'/templates/static/upload_image/c2b2c00ca405426493e5aef01f908d58.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(11,'RES-011','Dal Makhani','Main Course — prepared to order.',3,NULL,300,114,5,1,20,1,'Available',1,NULL,0,'/templates/static/upload_image/63ac4ca9ebe1418c846461bf5ce012cf.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(12,'RES-012','Kerala Fish Curry','Main Course — prepared to order.',3,NULL,520,197.6,5,1,24,1,'Available',0,NULL,0,'/templates/static/upload_image/cb7e696d9532486c9d55293683095b00.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(13,'RES-013','Vegetable Biryani','Main Course — prepared to order.',3,NULL,340,129.2,5,1,28,1,'Available',1,NULL,0,'/templates/static/upload_image/210a5f76bb1e4369b7e91201733e2304.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(14,'RES-014','Hyderabadi Chicken Biryani','Main Course — prepared to order.',3,NULL,460,174.8,5,1,32,1,'Available',0,NULL,0,'/templates/static/upload_image/af5f5348413d49abb263869217e7144b.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(15,'RES-015','Tandoori Chicken (Half)','Tandoor & Grill — prepared to order.',4,NULL,420,159.6,5,1,30,2,'Available',0,NULL,0,'/templates/static/upload_image/eef6c06cb58849beb88654449f36bda2.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(16,'RES-016','Seekh Kebab','Tandoor & Grill — prepared to order.',4,NULL,380,144.4,5,1,22,2,'Available',0,NULL,0,'/templates/static/upload_image/be98417b08ad42ddbf022d969d5d93b5.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(17,'RES-017','Tandoori Pomfret','Tandoor & Grill — prepared to order.',4,NULL,620,235.6,5,1,28,2,'Available',0,NULL,0,'/templates/static/upload_image/550389768f6747e18a8314140a25e098.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(18,'RES-018','Grilled Vegetable Platter','Tandoor & Grill — prepared to order.',4,NULL,340,129.2,5,1,20,2,'Available',1,NULL,0,'/templates/static/upload_image/118f6161246f43158710cad209a32cd0.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(19,'RES-019','Butter Naan','Breads & Rice — prepared to order.',5,NULL,70,26.6,5,1,8,1,'Available',1,NULL,0,'/templates/static/upload_image/4b20db3c462d4f65a660e753767fda9a.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(20,'RES-020','Garlic Naan','Breads & Rice — prepared to order.',5,NULL,90,34.2,5,1,8,1,'Available',1,NULL,0,'/templates/static/upload_image/217860d7b1cf43b4851c9fe95df360d2.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(21,'RES-021','Laccha Paratha','Breads & Rice — prepared to order.',5,NULL,80,30.4,5,1,9,1,'Available',1,NULL,0,'/templates/static/upload_image/23bafd143a4b48a29c61c22be805ddf7.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(22,'RES-022','Steamed Basmati Rice','Breads & Rice — prepared to order.',5,NULL,150,57,5,1,12,1,'Available',1,NULL,0,'/templates/static/upload_image/abeb12c8b94240dfac0da88fb82d8711.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(23,'RES-023','Gulab Jamun','Desserts — prepared to order.',6,NULL,140,53.2,5,1,5,3,'Available',1,NULL,0,'/templates/static/upload_image/8d914cc4e32f4fbd80eb3df12d58b4f6.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(24,'RES-024','Rasmalai','Desserts — prepared to order.',6,NULL,160,60.8,5,1,5,3,'Available',1,NULL,0,'/templates/static/upload_image/c9d5b74414fb4dc3ab5d3b27a7890070.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(25,'RES-025','Chocolate Brownie','Desserts — prepared to order.',6,NULL,220,83.6,5,1,8,3,'Available',1,NULL,0,'/templates/static/upload_image/7fd80c19e6af40de878f87fefd25a915.jpg',0,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  `sub_total` float DEFAULT NULL,
  `tax_amount` float DEFAULT NULL,
  `service_charge` float DEFAULT NULL,
  `discount_type` enum('Percentage','Flat') DEFAULT NULL,
  `discount_value` float DEFAULT NULL,
  `discount_amount` float DEFAULT NULL,
  `grand_total` float DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_order`
--

LOCK TABLES `restaurant_order` WRITE;
/*!40000 ALTER TABLE `restaurant_order` DISABLE KEYS */;
INSERT INTO `restaurant_order` VALUES (1,'RO-20260831-001','2026-08-31','13:15:00','Dine-In',4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',2740,150.7,274,NULL,NULL,0,3164.7,NULL,NULL,'26280e0d-10b7-458e-949b-b2e26ed95179','ACTIVE','1','2026-08-31 13:15:00',NULL,NULL,'1','1'),(2,'RO-20260830-002','2026-08-30','14:15:00','Dine-In',7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',2410,132.55,241,NULL,NULL,0,2783.55,NULL,NULL,'d929f132-8ad0-4909-8529-0a649d32c7fa','ACTIVE','1','2026-08-30 14:15:00',NULL,NULL,'1','1'),(3,'RO-20260901-003','2026-09-01','15:15:00','Dine-In',10,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',1780,97.9,178,NULL,NULL,0,2055.9,NULL,NULL,'6600e61c-d653-4022-9646-2209e8575c95','ACTIVE','1','2026-09-01 15:15:00',NULL,NULL,'1','1'),(4,'RO-20260831-004','2026-08-31','16:15:00','Dine-In',13,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',3360,184.8,336,NULL,NULL,0,3880.8,NULL,NULL,'af5a94cf-1448-4b80-ad22-32703aa58c58','ACTIVE','1','2026-08-31 16:15:00',NULL,NULL,'1','1'),(5,'RO-20260830-005','2026-08-30','17:15:00','Dine-In',16,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',4030,221.65,403,NULL,NULL,0,4654.65,NULL,NULL,'c3a71571-a9fe-4d61-8506-914087f43ca0','ACTIVE','1','2026-08-30 17:15:00',NULL,NULL,'1','1'),(6,'RO-20260901-006','2026-09-01','18:15:00','Dine-In',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',1430,78.65,143,NULL,NULL,0,1651.65,NULL,NULL,'03c4d995-7a43-40db-a30f-d33bd666b59a','ACTIVE','1','2026-09-01 18:15:00',NULL,NULL,'1','1'),(7,'RO-20260831-007','2026-08-31','19:15:00','Dine-In',4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',2330,128.15,233,NULL,NULL,0,2691.15,NULL,NULL,'0aaed273-c594-4cdf-a95b-93084ed06aa2','ACTIVE','1','2026-08-31 19:15:00',NULL,NULL,'1','1'),(8,'RO-20260830-008','2026-08-30','12:15:00','Dine-In',7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Completed','Paid',3220,177.1,322,NULL,NULL,0,3719.1,NULL,NULL,'181927c5-fb2e-49f0-89d1-219089f9f3fe','ACTIVE','1','2026-08-30 12:15:00',NULL,NULL,'1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_order_item`
--

LOCK TABLES `restaurant_order_item` WRITE;
/*!40000 ALTER TABLE `restaurant_order_item` DISABLE KEYS */;
INSERT INTO `restaurant_order_item` VALUES (1,1,15,2,2,420,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 13:20:00',NULL,NULL,'1','1'),(2,1,1,1,3,320,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 13:20:00',NULL,NULL,'1','1'),(3,1,17,2,1,620,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 13:20:00',NULL,NULL,'1','1'),(4,1,24,3,2,160,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 13:20:00',NULL,NULL,'1','1'),(5,2,22,1,1,150,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 14:20:00',NULL,NULL,'1','1'),(6,2,18,2,3,340,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 14:20:00',NULL,NULL,'1','1'),(7,2,10,1,1,460,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 14:20:00',NULL,NULL,'1','1'),(8,2,20,1,2,90,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 14:20:00',NULL,NULL,'1','1'),(9,2,11,1,2,300,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 14:20:00',NULL,NULL,'1','1'),(10,3,6,1,1,200,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 15:20:00',NULL,NULL,'1','1'),(11,3,13,1,2,340,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 15:20:00',NULL,NULL,'1','1'),(12,3,11,1,3,300,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 15:20:00',NULL,NULL,'1','1'),(13,4,9,1,2,380,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 16:20:00',NULL,NULL,'1','1'),(14,4,4,1,3,420,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 16:20:00',NULL,NULL,'1','1'),(15,4,12,1,2,520,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 16:20:00',NULL,NULL,'1','1'),(16,4,11,1,1,300,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 16:20:00',NULL,NULL,'1','1'),(17,5,9,1,3,380,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 17:20:00',NULL,NULL,'1','1'),(18,5,19,1,1,70,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 17:20:00',NULL,NULL,'1','1'),(19,5,14,1,2,460,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 17:20:00',NULL,NULL,'1','1'),(20,5,12,1,3,520,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 17:20:00',NULL,NULL,'1','1'),(21,5,13,1,1,340,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 17:20:00',NULL,NULL,'1','1'),(22,6,20,1,3,90,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 18:20:00',NULL,NULL,'1','1'),(23,6,7,1,2,160,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 18:20:00',NULL,NULL,'1','1'),(24,6,4,1,2,420,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-09-01 18:20:00',NULL,NULL,'1','1'),(25,7,20,1,1,90,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 19:20:00',NULL,NULL,'1','1'),(26,7,23,3,1,140,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 19:20:00',NULL,NULL,'1','1'),(27,7,16,2,3,380,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 19:20:00',NULL,NULL,'1','1'),(28,7,1,1,3,320,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-31 19:20:00',NULL,NULL,'1','1'),(29,8,25,3,1,220,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 12:20:00',NULL,NULL,'1','1'),(30,8,23,3,2,140,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 12:20:00',NULL,NULL,'1','1'),(31,8,3,1,3,260,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 12:20:00',NULL,NULL,'1','1'),(32,8,18,2,3,340,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 12:20:00',NULL,NULL,'1','1'),(33,8,14,1,2,460,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-08-30 12:20:00',NULL,NULL,'1','1');
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
  `price` float DEFAULT NULL,
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
INSERT INTO `restaurant_settings` VALUES (1,'service_charge_percent','10','ServiceCharge','Service charge added to dine-in bills','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'default_tax_percent','5','Tax','GST applied to restaurant bills','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'opening_time','07:00','OperatingHours','Kitchen opens','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(4,'closing_time','23:30','OperatingHours','Last order','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(5,'bill_prefix','RB','Numbering','Prefix for restaurant bill numbers','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(6,'order_prefix','RO','Numbering','Prefix for restaurant order numbers','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  `position_x` float DEFAULT NULL,
  `position_y` float DEFAULT NULL,
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_table_code` (`company_id`,`branch_id`,`table_code`),
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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_table`
--

LOCK TABLES `restaurant_table` WRITE;
/*!40000 ALTER TABLE `restaurant_table` DISABLE KEYS */;
INSERT INTO `restaurant_table` VALUES (1,'FL-GRD-T01','Table 1',1,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,60,0,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(2,'FL-GRD-T02','Table 2',2,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,120,0,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(3,'FL-GRD-T03','Table 3',3,1,'FL-GRD','Standard',2,'Restaurant',NULL,NULL,NULL,180,0,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(4,'FL-GRD-T04','Table 4',4,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,0,60,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(5,'FL-GRD-T05','Table 5',5,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,60,60,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(6,'FL-GRD-T06','Table 6',6,1,'FL-GRD','Standard',2,'Restaurant',NULL,NULL,NULL,120,60,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(7,'FL-GRD-T07','Table 7',7,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,180,60,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(8,'FL-GRD-T08','Table 8',8,1,'FL-GRD','Standard',4,'Restaurant',NULL,NULL,NULL,0,120,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(9,'FL-FST-T01','Table 9',9,2,'FL-FST','Standard',4,'Restaurant',NULL,NULL,NULL,60,0,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(10,'FL-FST-T02','Table 10',10,2,'FL-FST','Standard',4,'Restaurant',NULL,NULL,NULL,120,0,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(11,'FL-FST-T03','Table 11',11,2,'FL-FST','Standard',2,'Restaurant',NULL,NULL,NULL,180,0,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(12,'FL-FST-T04','Table 12',12,2,'FL-FST','Standard',4,'Restaurant',NULL,NULL,NULL,0,60,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(13,'FL-FST-T05','Table 13',13,2,'FL-FST','Standard',4,'Restaurant',NULL,NULL,NULL,60,60,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(14,'FL-FST-T06','Table 14',14,2,'FL-FST','Standard',2,'Restaurant',NULL,NULL,NULL,120,60,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(15,'FL-TER-T01','Table 15',15,3,'FL-TER','VIP',4,'Outdoor',NULL,NULL,NULL,60,0,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(16,'FL-TER-T02','Table 16',16,3,'FL-TER','Standard',4,'Outdoor',NULL,NULL,NULL,120,0,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(17,'FL-TER-T03','Table 17',17,3,'FL-TER','Standard',2,'Outdoor',NULL,NULL,NULL,180,0,'round','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1'),(18,'FL-TER-T04','Table 18',18,3,'FL-TER','Standard',4,'Outdoor',NULL,NULL,NULL,0,60,'square','#E5E7EB','Available',1,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1','1');
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
  `total_sales` float DEFAULT NULL,
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

-- Dump completed on 2026-09-01 20:55:00
