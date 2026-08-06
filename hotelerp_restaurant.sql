-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: hotelerp_restaurant
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

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hotelerp_restaurant` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hotelerp_restaurant`;

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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combo_deal`
--

LOCK TABLES `combo_deal` WRITE;
/*!40000 ALTER TABLE `combo_deal` DISABLE KEYS */;
INSERT INTO `combo_deal` VALUES (1,'COMBO-9F2907E1','Family Feast','Butter Chicken, Veg Biryani, 2 Butter Naan, Gulab Jamun',1200,NULL,NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'COMBO-AE9A4B00','Lunch Combo','Dal Makhani, Jeera Rice, Butter Naan',350,NULL,NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'CMB-AC243EA8','Briyani Combo',NULL,400,'2026-08-06 00:00:00','2026-08-15 00:00:00',1,'INACTIVE','1','2026-08-06 14:27:37','2026-08-06 14:27:48','1','1','MAIN'),(4,'CMB-A58F021B','Briyani Combo',NULL,400,'2026-08-06 00:00:00','2026-08-15 00:00:00',1,'ACTIVE','1','2026-08-06 14:30:04',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combo_item`
--

LOCK TABLES `combo_item` WRITE;
/*!40000 ALTER TABLE `combo_item` DISABLE KEYS */;
INSERT INTO `combo_item` VALUES (1,1,5,1,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(2,1,16,1,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(3,1,14,2,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(4,1,20,1,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(5,2,6,1,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(6,2,15,1,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(7,2,14,1,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(8,3,25,1,'ACTIVE','1','2026-08-06 14:27:37','1','MAIN'),(9,3,2,1,'ACTIVE','1','2026-08-06 14:27:37','1','MAIN'),(10,3,20,1,'ACTIVE','1','2026-08-06 14:27:37','1','MAIN'),(11,3,22,1,'ACTIVE','1','2026-08-06 14:27:37','1','MAIN'),(12,4,25,1,'ACTIVE','1','2026-08-06 14:30:04','1','MAIN'),(13,4,2,1,'ACTIVE','1','2026-08-06 14:30:04','1','MAIN'),(14,4,20,1,'ACTIVE','1','2026-08-06 14:30:04','1','MAIN'),(15,4,22,1,'ACTIVE','1','2026-08-06 14:30:04','1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest`
--

LOCK TABLES `guest` WRITE;
/*!40000 ALTER TABLE `guest` DISABLE KEYS */;
INSERT INTO `guest` VALUES (1,'GST-0A03CCD9','Rohan','Mehta','9845012301','rohan.mehta@example.com','Regular',NULL,NULL,9,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(2,'GST-742428C6','Priya','Nair','9845012302','priya.nair@example.com','Regular',NULL,NULL,5,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(3,'GST-D03E9314','Arjun','Kapoor','9845012303','arjun.kapoor@example.com','VIP',NULL,NULL,12,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(4,'GST-A3F18441','Sana','Sheikh','9845012304','sana.sheikh@example.com','Regular',NULL,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,'GST-C0F57862','Vikram','Rao','9845012305','vikram.rao@example.com','Walk-In',NULL,NULL,4,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(6,'GST-8281C9D0','Neha','Gupta','9845012306','neha.gupta@example.com','VIP',NULL,NULL,11,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(7,'GST-F5B14E27','Karan','Malhotra','9845012307','karan.malhotra@example.com','Walk-In',NULL,NULL,5,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(8,'GST-0BCD368D','Ananya','Iyer','9845012308','ananya.iyer@example.com','Hotel Guest',NULL,NULL,8,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(9,'GST-269CF708','Farhan','Khan','9845019101','farhan.khan@example.com','Walk-In',NULL,NULL,6,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(10,'GST-6A1DD45A','Divya','Menon','9845019102','divya.menon@example.com','Regular',NULL,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(11,'GST-4785638F','Ramesh',NULL,'8576553342',NULL,'Walk-In','null',NULL,0,'ACTIVE','1','2026-08-06 15:35:23',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest_feedback`
--

LOCK TABLES `guest_feedback` WRITE;
/*!40000 ALTER TABLE `guest_feedback` DISABLE KEYS */;
INSERT INTO `guest_feedback` VALUES (1,1,7,5,'Excellent food and quick service!','ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(2,3,9,4,'Great experience, will visit again.','ACTIVE','1','2026-07-31 12:34:09','1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest_visit_history`
--

LOCK TABLES `guest_visit_history` WRITE;
/*!40000 ALTER TABLE `guest_visit_history` DISABLE KEYS */;
INSERT INTO `guest_visit_history` VALUES (1,1,'2026-07-31',7,1,'Dine-In',901,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(2,2,'2026-07-31',8,2,'Dine-In',562,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(3,3,'2026-07-31',9,3,'Dine-In',1266,5,NULL,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(4,6,'2026-07-31',10,4,'Dine-In',1147,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(5,5,'2026-07-31',11,5,'Dine-In',456,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(6,7,'2026-07-31',12,6,'Dine-In',585,5,NULL,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(7,9,'2026-07-31',13,7,'Takeaway',655,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN'),(8,8,'2026-07-31',14,8,'Room Service',889,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_item`
--

LOCK TABLES `inventory_item` WRITE;
/*!40000 ALTER TABLE `inventory_item` DISABLE KEYS */;
INSERT INTO `inventory_item` VALUES (1,'INV-91081CFF','Chicken','Kitchen Staples','Kg',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'INV-D49D2361','Paneer','Kitchen Staples','Kg',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'INV-98F95DD6','Basmati Rice','Kitchen Staples','Kg',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,'INV-54C104C8','Wheat Flour','Kitchen Staples','Kg',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,'INV-1597826D','Tomato','Kitchen Staples','Kg',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,'INV-5B4F6890','Onion','Kitchen Staples','Kg',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,'INV-B33CB78C','Fresh Cream','Kitchen Staples','Litre',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,'INV-5CE3FB38','Sugar','Kitchen Staples','Kg',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,'INV-4FFE0B4D','Milk','Kitchen Staples','Litre',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(10,'INV-6D82D77E','Butter','Kitchen Staples','Kg',5,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(11,'INV-02ED7682','Onion',NULL,'Kg',1,0,'ACTIVE','1','2026-08-06 15:31:12',NULL,NULL,'1','MAIN'),(12,'INV-4AD90DCA','cashew',NULL,'Kg',5,0,'ACTIVE','1','2026-08-06 15:32:14',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_purchase`
--

LOCK TABLES `inventory_purchase` WRITE;
/*!40000 ALTER TABLE `inventory_purchase` DISABLE KEYS */;
INSERT INTO `inventory_purchase` VALUES (1,1,25,120,3000,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,2,15,120,1800,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,3,40,120,4800,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,4,30,120,3600,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,5,20,120,2400,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,6,25,120,3000,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,7,10,120,1200,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,8,15,120,1800,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,9,20,120,2400,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(10,10,8,120,960,'2026-07-29','Fresh Foods Wholesale','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_stock`
--

LOCK TABLES `inventory_stock` WRITE;
/*!40000 ALTER TABLE `inventory_stock` DISABLE KEYS */;
INSERT INTO `inventory_stock` VALUES (1,1,NULL,25,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,2,NULL,15,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,3,NULL,40,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,4,NULL,30,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,5,NULL,20,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,6,NULL,25,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,7,NULL,10,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,8,NULL,15,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,9,NULL,20,'2026-07-31','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(10,10,NULL,12,'2026-08-06','ACTIVE','1','2026-07-31 12:34:09','2026-08-06 15:29:26',NULL,'1','MAIN'),(11,1,1,4.4,'2026-08-06','ACTIVE',NULL,'2026-08-06 15:14:55','2026-08-06 15:29:52',NULL,'1','MAIN'),(12,7,1,-0.2,'2026-08-06','ACTIVE',NULL,'2026-08-06 15:14:55','2026-08-06 15:14:55',NULL,'1','MAIN'),(13,4,1,-0.48,'2026-08-06','ACTIVE',NULL,'2026-08-06 15:14:55','2026-08-06 15:14:55',NULL,'1','MAIN'),(14,10,1,-0.08,'2026-08-06','ACTIVE',NULL,'2026-08-06 15:14:55','2026-08-06 15:14:55',NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_stock_transaction`
--

LOCK TABLES `inventory_stock_transaction` WRITE;
/*!40000 ALTER TABLE `inventory_stock_transaction` DISABLE KEYS */;
INSERT INTO `inventory_stock_transaction` VALUES (1,1,NULL,'IN',25,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(2,2,NULL,'IN',15,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(3,3,NULL,'IN',40,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(4,4,NULL,'IN',30,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(5,5,NULL,'IN',20,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(6,6,NULL,'IN',25,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(7,7,NULL,'IN',10,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(8,8,NULL,'IN',15,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(9,9,NULL,'IN',20,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(10,10,NULL,'IN',8,'Purchase',NULL,'Opening stock','1','2026-07-31 12:34:09','1','MAIN'),(11,1,1,'OUT',0.6,'KOT','KOT-332C2D3C',NULL,'1','2026-08-06 15:14:55','1','MAIN'),(12,7,1,'OUT',0.2,'KOT','KOT-332C2D3C',NULL,'1','2026-08-06 15:14:55','1','MAIN'),(13,4,1,'OUT',0.48,'KOT','KOT-332C2D3C',NULL,'1','2026-08-06 15:14:55','1','MAIN'),(14,10,1,'OUT',0.08,'KOT','KOT-332C2D3C',NULL,'1','2026-08-06 15:14:55','1','MAIN'),(15,10,NULL,'ADJUSTMENT',1,'Manual',NULL,NULL,'1','2026-08-06 15:28:05','1','MAIN'),(16,10,NULL,'ADJUSTMENT',-1,'Manual',NULL,NULL,'1','2026-08-06 15:29:15','1','MAIN'),(17,10,NULL,'ADJUSTMENT',4,'Manual',NULL,NULL,'1','2026-08-06 15:29:26','1','MAIN'),(18,1,1,'ADJUSTMENT',5,'Manual',NULL,NULL,'1','2026-08-06 15:29:52','1','MAIN');
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
INSERT INTO `kitchen` VALUES (1,'KIT-MAIN','Main Kitchen','Main',NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'KIT-GRILL','Grill Station','Grill',NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'KIT-DESSERT','Dessert Station','Dessert',NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_order_item`
--

LOCK TABLES `kitchen_order_item` WRITE;
/*!40000 ALTER TABLE `kitchen_order_item` DISABLE KEYS */;
INSERT INTO `kitchen_order_item` VALUES (1,1,8,'Preparing','2026-07-31 13:15:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,1,9,'Preparing','2026-07-31 13:15:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,1,10,'Preparing','2026-07-31 13:15:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,2,11,'Preparing','2026-07-31 13:15:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,2,12,'Preparing','2026-07-31 13:15:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,3,13,'Preparing','2026-07-31 13:15:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,3,14,'Preparing','2026-07-31 13:15:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,3,15,'Preparing','2026-07-31 13:15:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,4,16,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(10,4,17,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(11,4,18,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(12,4,19,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(13,5,20,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(14,5,21,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(15,6,22,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(16,6,23,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(17,6,24,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(18,6,25,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(19,7,26,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(20,7,27,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(21,7,28,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(22,8,29,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(23,8,30,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(24,9,31,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(25,9,32,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(26,9,33,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(27,10,34,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(28,10,35,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(29,10,36,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(30,11,37,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(31,11,38,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(32,11,39,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(33,11,40,'Ready','2026-07-31 12:08:00','2026-07-31 12:24:00','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(34,12,41,'Ready',NULL,'2026-08-06 15:14:56','ACTIVE','1','2026-08-01 14:02:02','2026-08-06 15:14:55',NULL,'1','MAIN'),(35,12,42,'Ready',NULL,'2026-08-06 15:14:56','ACTIVE','1','2026-08-01 14:02:02','2026-08-06 15:14:55',NULL,'1','MAIN'),(36,13,43,'Ready',NULL,'2026-08-06 15:14:18','ACTIVE','1','2026-08-06 14:38:07','2026-08-06 15:14:17',NULL,'1','MAIN'),(37,13,44,'Ready',NULL,'2026-08-06 15:14:18','ACTIVE','1','2026-08-06 14:38:07','2026-08-06 15:14:17',NULL,'1','MAIN'),(38,13,45,'Ready',NULL,'2026-08-06 15:14:18','ACTIVE','1','2026-08-06 14:38:07','2026-08-06 15:14:17',NULL,'1','MAIN'),(39,14,46,'Pending',NULL,NULL,'ACTIVE','1','2026-08-06 15:09:05',NULL,NULL,'1','MAIN'),(40,15,47,'Pending',NULL,NULL,'ACTIVE','1','2026-08-06 15:16:13',NULL,NULL,'1','MAIN'),(41,15,49,'Pending',NULL,NULL,'ACTIVE','1','2026-08-06 15:16:13',NULL,NULL,'1','MAIN'),(42,16,48,'Pending',NULL,NULL,'ACTIVE','1','2026-08-06 15:16:13',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_order_ticket`
--

LOCK TABLES `kitchen_order_ticket` WRITE;
/*!40000 ALTER TABLE `kitchen_order_ticket` DISABLE KEYS */;
INSERT INTO `kitchen_order_ticket` VALUES (1,'KOT-589E60EE',4,NULL,'Original',1,'In Progress','Normal',0,NULL,'Chef Antoine','2026-07-31 13:12:00',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'KOT-3B1B5DEE',5,NULL,'Original',1,'In Progress','Normal',0,NULL,'Chef Antoine','2026-07-31 13:12:00',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'KOT-61D6C708',6,NULL,'Original',2,'In Progress','Normal',0,NULL,'Chef Antoine','2026-07-31 13:12:00',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,'KOT-02AE6BC1',7,NULL,'Original',1,'Completed','Normal',0,NULL,'Chef Antoine','2026-07-31 12:05:00','Chef Antoine','2026-07-31 12:25:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,'KOT-41D85783',8,NULL,'Original',1,'Completed','Normal',0,NULL,'Chef Antoine','2026-07-31 12:05:00','Chef Antoine','2026-07-31 12:25:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,'KOT-87E4917C',9,NULL,'Original',2,'Completed','Normal',0,NULL,'Chef Antoine','2026-07-31 12:05:00','Chef Antoine','2026-07-31 12:25:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,'KOT-4C2368E6',10,NULL,'Original',1,'Completed','Normal',0,NULL,'Chef Antoine','2026-07-31 12:05:00','Chef Antoine','2026-07-31 12:25:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,'KOT-3E9D8094',11,NULL,'Original',1,'Completed','Normal',0,NULL,'Chef Antoine','2026-07-31 12:05:00','Chef Antoine','2026-07-31 12:25:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,'KOT-E4103646',12,NULL,'Original',1,'Completed','Normal',0,NULL,'Chef Antoine','2026-07-31 12:05:00','Chef Antoine','2026-07-31 12:25:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(10,'KOT-86A290B1',13,NULL,'Original',1,'Completed','Normal',0,NULL,'Chef Antoine','2026-07-31 12:05:00','Chef Antoine','2026-07-31 12:25:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(11,'KOT-DA01191F',14,NULL,'Original',1,'Completed','Normal',0,NULL,'Chef Antoine','2026-07-31 12:05:00','Chef Antoine','2026-07-31 12:25:00',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(12,'KOT-332C2D3C',15,NULL,'Original',1,'Completed','Normal',0,NULL,NULL,NULL,'1','2026-08-06 15:14:56',NULL,'ACTIVE','1','2026-08-01 14:02:02','2026-08-06 15:14:55','1','1','MAIN'),(13,'KOT-09063531',16,NULL,'Original',1,'Completed','Normal',0,NULL,NULL,NULL,'1','2026-08-06 15:14:18',NULL,'ACTIVE','1','2026-08-06 14:38:07','2026-08-06 15:14:17','1','1','MAIN'),(14,'KOT-850F4B7D',17,NULL,'Original',2,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-08-06 15:09:05',NULL,NULL,'1','MAIN'),(15,'KOT-F43BAE1A',18,NULL,'Original',1,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-08-06 15:16:13',NULL,NULL,'1','MAIN'),(16,'KOT-F096E80C',18,NULL,'Original',3,'New','Normal',0,NULL,NULL,NULL,NULL,NULL,NULL,'ACTIVE','1','2026-08-06 15:16:13',NULL,NULL,'1','MAIN');
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
INSERT INTO `menu_category` VALUES (1,'CAT-STARTERS','Starters',NULL,1,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'CAT-MAINS','Main Course',NULL,1,2,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'CAT-BREADS','Breads & Rice',NULL,1,3,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,'CAT-GRILL','Grill & Tandoor',NULL,2,4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,'CAT-DESSERTS','Desserts',NULL,3,5,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,'CAT-BEVERAGES','Beverages',NULL,1,6,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_modifier`
--

LOCK TABLES `menu_modifier` WRITE;
/*!40000 ALTER TABLE `menu_modifier` DISABLE KEYS */;
INSERT INTO `menu_modifier` VALUES (1,5,'Extra Spicy',NULL,'Add-on','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,5,'Less Spicy',NULL,'Add-on','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,9,'Extra Chutney',20,'Add-on','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_recipe`
--

LOCK TABLES `menu_recipe` WRITE;
/*!40000 ALTER TABLE `menu_recipe` DISABLE KEYS */;
INSERT INTO `menu_recipe` VALUES (1,5,1,0.3,'Kg','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,5,7,0.1,'Litre','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,7,2,0.25,'Kg','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,17,1,0.35,'Kg','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,17,3,0.3,'Kg','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,24,9,0.15,'Litre','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,24,8,0.02,'Kg','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,14,4,0.12,'Kg','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,14,10,0.02,'Kg','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_sub_category`
--

LOCK TABLES `menu_sub_category` WRITE;
/*!40000 ALTER TABLE `menu_sub_category` DISABLE KEYS */;
INSERT INTO `menu_sub_category` VALUES (1,2,'CAT-MAINS','SUB-NORTHINDIAN','North Indian',NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,2,'CAT-MAINS','SUB-SOUTHINDIAN','South Indian',NULL,2,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,2,'CAT-MAINS','SUB-CONTINENTAL','Continental',NULL,3,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_variant`
--

LOCK TABLES `menu_variant` WRITE;
/*!40000 ALTER TABLE `menu_variant` DISABLE KEYS */;
INSERT INTO `menu_variant` VALUES (1,17,'Half',180,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,17,'Full',300,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,24,'Regular',60,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,24,'Large',90,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_method`
--

LOCK TABLES `payment_method` WRITE;
/*!40000 ALTER TABLE `payment_method` DISABLE KEYS */;
INSERT INTO `payment_method` VALUES (1,'Cash','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'Card','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'UPI','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill`
--

LOCK TABLES `restaurant_bill` WRITE;
/*!40000 ALTER TABLE `restaurant_bill` DISABLE KEYS */;
INSERT INTO `restaurant_bill` VALUES (1,'BILL-05777386','2026-07-31','12:30:00',7,'ORD-2026-0007',5,'T5',NULL,1,'Rohan Mehta','9845012301',770,6,46.2,6,46.2,NULL,0,5,38.5,NULL,0,0,0.1,901,'Paid','Paid',NULL,'1b46877d-8695-4bb4-ae9e-92f13289a2e7','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'BILL-C39F3278','2026-07-31','12:30:00',8,'ORD-2026-0008',6,'T6',NULL,2,'Priya Nair','9845012302',480,6,28.8,6,28.8,NULL,0,5,24,NULL,0,0,0.4,562,'Paid','Paid',NULL,'a6767b7b-22e3-4c53-913b-8ec5b1075491','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'BILL-FFDCFBFD','2026-07-31','12:30:00',9,'ORD-2026-0009',7,'T7',NULL,3,'Arjun Kapoor','9845012303',1130,6,67.8,6,67.8,NULL,0,5,56.5,'Percentage',5,56.5,0.4,1266,'Paid','Paid',NULL,'c39a261b-564d-4f46-892e-e52dd3711705','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,'BILL-7C662BB2','2026-07-31','12:30:00',10,'ORD-2026-0010',8,'T8',NULL,6,'Neha Gupta','9845012306',980,6,58.8,6,58.8,NULL,0,5,49,NULL,0,0,0.4,1147,'Paid','Paid',NULL,'ff0bc775-ccde-4640-b818-513745d38607','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,'BILL-EDAEAC4E','2026-07-31','12:30:00',11,'ORD-2026-0011',11,'T11',NULL,5,'Vikram Rao','9845012305',390,6,23.4,6,23.4,NULL,0,5,19.5,NULL,0,0,-0.3,456,'Paid','Paid',NULL,'3cb3000c-015b-4022-8d4a-fd51cf5c4dcf','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,'BILL-C1A04F2B','2026-07-31','12:30:00',12,'ORD-2026-0012',12,'T12',NULL,7,'Karan Malhotra','9845012307',500,6,30,6,30,NULL,0,5,25,NULL,0,0,0,585,'Paid','Paid',NULL,'9d4d180f-71fe-4a33-8c02-066396674113','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,'BILL-DA846060','2026-07-31','12:30:00',13,'ORD-2026-0013',NULL,NULL,NULL,9,'Farhan Khan','9845019101',560,6,33.6,6,33.6,NULL,0,5,28,NULL,0,0,-0.2,655,'Paid','Paid',NULL,'d5f56ec9-3eff-477e-8844-7ec979d750d7','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,'BILL-413C3189','2026-07-31','12:30:00',14,'ORD-2026-0014',NULL,NULL,'205',8,'Ananya Iyer','9845012308',760,6,45.6,6,45.6,NULL,0,5,38,NULL,0,0,-0.2,889,'Paid','Paid',NULL,'bec16a63-6d33-4b25-9938-00389b438b4e','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,'BILL-7911053D','2026-08-01','14:02:29',15,'ORD-C8584D7F',6,'T6',NULL,NULL,NULL,NULL,880,6,52.8,6,52.8,NULL,0,0,0,NULL,0,0,0.4,986,'Paid','Paid',NULL,'429fb06d-bcef-445a-ba2f-4f8d06f6ac04','ACTIVE','1','2026-08-01 14:02:29','2026-08-01 14:02:52',NULL,'1','MAIN'),(10,'BILL-5E6896B1','2026-08-06','15:26:49',6,'ORD-2026-0006',10,'T10',NULL,NULL,NULL,NULL,950,2.5,23.75,2.5,23.75,NULL,0,5,47.5,NULL,0,0,0,1045,'Paid','Paid',NULL,'b2c1956e-c532-450c-9eca-571811f8ac9f','ACTIVE','1','2026-08-06 15:26:49','2026-08-06 15:27:08',NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill_item`
--

LOCK TABLES `restaurant_bill_item` WRITE;
/*!40000 ALTER TABLE `restaurant_bill_item` DISABLE KEYS */;
INSERT INTO `restaurant_bill_item` VALUES (1,1,16,5,'Butter Chicken',1,320,320,38.4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,1,17,14,'Butter Naan',2,60,120,14.4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,1,18,15,'Jeera Rice',1,150,150,18,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,1,19,20,'Gulab Jamun',2,90,180,21.6,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,2,20,9,'Masala Dosa',2,150,300,36,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,2,21,22,'Fresh Lime Soda',2,90,180,21.6,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,3,22,18,'Tandoori Chicken',1,350,350,42,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,3,23,19,'Seekh Kebab',1,280,280,33.6,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,3,24,14,'Butter Naan',3,60,180,21.6,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(10,3,25,23,'Mocktail Cooler',2,160,320,38.4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(11,4,26,12,'Grilled Fish',1,380,380,45.6,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(12,4,27,13,'Pasta Alfredo',1,280,280,33.6,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(13,4,28,21,'Chocolate Brownie',2,160,320,38.4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(14,5,29,17,'Chicken Biryani',1,300,300,36,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(15,5,30,20,'Gulab Jamun',1,90,90,10.8,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(16,6,31,7,'Palak Paneer',1,260,260,31.2,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(17,6,32,14,'Butter Naan',2,60,120,14.4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(18,6,33,24,'Masala Chai',2,60,120,14.4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(19,7,34,8,'Chicken Curry',1,290,290,34.8,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(20,7,35,15,'Jeera Rice',1,150,150,18,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(21,7,36,14,'Butter Naan',2,60,120,14.4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(22,8,37,16,'Veg Biryani',1,240,240,28.8,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(23,8,38,6,'Dal Makhani',1,240,240,28.8,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(24,8,39,14,'Butter Naan',2,60,120,14.4,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(25,8,40,21,'Chocolate Brownie',1,160,160,19.2,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(26,9,41,5,'Butter Chicken',2,320,640,76.8,'ACTIVE','1','2026-08-01 14:02:29',NULL,NULL,'1','MAIN'),(27,9,42,14,'Butter Naan',4,60,240,28.8,'ACTIVE','1','2026-08-01 14:02:29',NULL,NULL,'1','MAIN'),(28,10,13,18,'Tandoori Chicken',1,350,350,17.5,'ACTIVE','1','2026-08-06 15:26:49',NULL,NULL,'1','MAIN'),(29,10,14,19,'Seekh Kebab',1,280,280,14,'ACTIVE','1','2026-08-06 15:26:49',NULL,NULL,'1','MAIN'),(30,10,15,23,'Mocktail Cooler',2,160,320,16,'ACTIVE','1','2026-08-06 15:26:49',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_bill_payment`
--

LOCK TABLES `restaurant_bill_payment` WRITE;
/*!40000 ALTER TABLE `restaurant_bill_payment` DISABLE KEYS */;
INSERT INTO `restaurant_bill_payment` VALUES (1,1,2,901,NULL,'2026-07-31','12:32:00','Success',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,2,3,562,NULL,'2026-07-31','12:32:00','Success',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,3,1,1266,NULL,'2026-07-31','12:32:00','Success',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,4,2,1147,NULL,'2026-07-31','12:32:00','Success',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,5,3,456,NULL,'2026-07-31','12:32:00','Success',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,6,1,585,NULL,'2026-07-31','12:32:00','Success',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,7,2,655,NULL,'2026-07-31','12:32:00','Success',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,8,3,889,NULL,'2026-07-31','12:32:00','Success',NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,9,3,986,NULL,'2026-08-01','14:02:53','Success','Full settlement','ACTIVE','1','2026-08-01 14:02:52',NULL,NULL,'1','MAIN'),(10,10,3,1045,NULL,'2026-08-06','15:27:09','Success',NULL,'ACTIVE','1','2026-08-06 15:27:08',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_floor`
--

LOCK TABLES `restaurant_floor` WRITE;
/*!40000 ALTER TABLE `restaurant_floor` DISABLE KEYS */;
INSERT INTO `restaurant_floor` VALUES (1,'MAIN-HALL','Main Dining Hall',1,'Restaurant',NULL,8,32,NULL,NULL,1,'ACTIVE','1','2026-07-31 12:34:09','2026-08-01 16:22:20','1','1','MAIN'),(2,'PATIO','Outdoor Patio',2,'Outdoor',NULL,4,16,NULL,NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'BANQUET','Private Banquet Room',3,'Banquet',NULL,3,12,NULL,NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,'FLR-5B858C01','Main Dining Hall',1,'Restaurant',NULL,5,20,'null',NULL,1,'INACTIVE','1','2026-08-06 14:32:48','2026-08-06 14:33:06','1','1','MAIN'),(5,'FLR-699C5524','Pantry Area',1,'Restaurant',NULL,5,20,'null',NULL,1,'ACTIVE','1','2026-08-06 14:35:08','2026-08-06 14:35:18','1','1','MAIN');
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
INSERT INTO `restaurant_menu` VALUES (1,'ITEM-CB4268D6','Paneer Tikka',NULL,1,NULL,220,88,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'ITEM-92EA644F','Chicken 65',NULL,1,NULL,260,104,12,1,15,1,'Available',0,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'ITEM-EDB691A1','Veg Spring Rolls',NULL,1,NULL,180,72,12,1,15,1,'Available',1,'[]',0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09','2026-08-06 14:26:01','1','1','MAIN'),(4,'ITEM-FA757662','Hara Bhara Kebab',NULL,1,NULL,190,76,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,'ITEM-72C63986','Butter Chicken',NULL,2,1,320,128,12,1,15,1,'Available',0,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,'ITEM-F02779DB','Dal Makhani',NULL,2,1,240,96,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,'ITEM-29BAB7E4','Palak Paneer',NULL,2,1,260,104,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,'ITEM-2E81F79C','Chicken Curry',NULL,2,1,290,116,12,1,15,1,'Available',0,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(9,'ITEM-DC460759','Masala Dosa',NULL,2,2,150,60,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(10,'ITEM-447B3F39','Idli Sambar',NULL,2,2,120,48,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(11,'ITEM-EE77C21A','Chettinad Chicken',NULL,2,2,310,124,12,1,15,1,'Available',0,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(12,'ITEM-D3A2DB3E','Grilled Fish',NULL,2,3,380,152,12,1,15,1,'Available',0,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(13,'ITEM-45CCD437','Pasta Alfredo',NULL,2,3,280,112,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(14,'ITEM-D099F86E','Butter Naan',NULL,3,NULL,60,24,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(15,'ITEM-D34D2C10','Jeera Rice',NULL,3,NULL,150,60,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(16,'ITEM-0A5A3E31','Veg Biryani',NULL,3,NULL,240,96,12,1,15,1,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(17,'ITEM-D64317B0','Chicken Biryani',NULL,3,NULL,300,120,12,1,15,1,'Available',0,NULL,1,NULL,0,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(18,'ITEM-DC1D7361','Tandoori Chicken',NULL,4,NULL,350,140,12,1,15,2,'Available',0,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(19,'ITEM-3DE17CF6','Seekh Kebab',NULL,4,NULL,280,112,12,1,15,2,'Available',0,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(20,'ITEM-7208F4A1','Gulab Jamun',NULL,5,NULL,90,36,12,1,15,3,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(21,'ITEM-8E92BCC4','Chocolate Brownie',NULL,5,NULL,160,64,12,1,15,3,'Available',1,NULL,0,NULL,0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(22,'ITEM-520BF99F','Fresh Lime Soda',NULL,6,NULL,90,36,12,1,15,1,'Available',1,NULL,0,NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(23,'ITEM-EB08A919','Mocktail Cooler',NULL,6,NULL,160,64,12,1,15,1,'Available',1,NULL,0,NULL,1,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(24,'ITEM-1AD26383','Masala Chai',NULL,6,NULL,60,24,12,1,15,1,'Available',1,NULL,1,NULL,1,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(25,'ITM-D01D1233','Seeraga Samba chicken Briyani',NULL,2,2,250,NULL,5,1,30,1,'Available',1,'[]',0,NULL,0,'ACTIVE','1','2026-08-06 14:24:18',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_order`
--

LOCK TABLES `restaurant_order` WRITE;
/*!40000 ALTER TABLE `restaurant_order` DISABLE KEYS */;
INSERT INTO `restaurant_order` VALUES (1,'ORD-2026-0001','2026-07-31','13:25:00','Dine-In',1,'T1',NULL,1,'MAIN-HALL',NULL,NULL,NULL,2,'201','Rakesh Yadav','New','Pending',400,0,0,NULL,0,0,400,NULL,NULL,'2697e975-7e66-471c-8fb5-9f269fc80b8e','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(2,'ORD-2026-0002','2026-07-31','13:27:00','Dine-In',2,'T2',NULL,1,'MAIN-HALL',NULL,NULL,NULL,2,'201','Rakesh Yadav','New','Pending',680,0,0,NULL,0,0,680,NULL,NULL,'e6e67dc7-d0e6-411c-905d-948ff4c8971e','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(3,'ORD-2026-0003','2026-07-31','13:28:00','Dine-In',9,'T9',NULL,2,'PATIO',NULL,NULL,NULL,2,'201','Rakesh Yadav','New','Pending',700,0,0,NULL,0,0,700,NULL,NULL,'131e4d1b-36f5-49d1-84d2-4f8447491b25','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(4,'ORD-2026-0004','2026-07-31','13:08:00','Dine-In',3,'T3',NULL,1,'MAIN-HALL',NULL,NULL,NULL,2,'201','Rakesh Yadav','In Progress','Pending',590,0,0,NULL,0,0,590,NULL,NULL,'4686c559-7d70-420b-9349-c5fac09e6da7','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(5,'ORD-2026-0005','2026-07-31','13:08:00','Dine-In',4,'T4',NULL,1,'MAIN-HALL',NULL,NULL,NULL,2,'201','Rakesh Yadav','In Progress','Pending',550,0,0,NULL,0,0,550,NULL,NULL,'4374a0bf-8372-4e15-9ceb-7ffcd79fbcc9','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(6,'ORD-2026-0006','2026-07-31','13:08:00','Dine-In',10,'T10',NULL,2,'PATIO',NULL,NULL,NULL,2,'201','Rakesh Yadav','Completed','Paid',950,0,0,NULL,0,0,950,NULL,NULL,'b6f21e22-c12b-4d8d-b2c9-31e8e87bf4fb','ACTIVE','1','2026-07-31 12:34:09','2026-08-06 15:27:08',NULL,'1','MAIN'),(7,'ORD-2026-0007','2026-07-31','12:00:00','Dine-In',5,'T5',NULL,1,'MAIN-HALL',1,'Rohan Mehta','9845012301',2,'201','Rakesh Yadav','Completed','Paid',770,0,0,NULL,0,0,770,NULL,NULL,'e84e9fc6-644d-46aa-9ba8-1deab19bfa8b','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(8,'ORD-2026-0008','2026-07-31','12:00:00','Dine-In',6,'T6',NULL,1,'MAIN-HALL',2,'Priya Nair','9845012302',2,'201','Rakesh Yadav','Completed','Paid',480,0,0,NULL,0,0,480,NULL,NULL,'a4d292b6-489f-4468-baec-933686800314','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(9,'ORD-2026-0009','2026-07-31','12:00:00','Dine-In',7,'T7',NULL,1,'MAIN-HALL',3,'Arjun Kapoor','9845012303',2,'201','Rakesh Yadav','Completed','Paid',1130,0,0,NULL,0,0,1130,NULL,NULL,'d0f2e992-eb38-48ba-9332-ee057dd4e0e4','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(10,'ORD-2026-0010','2026-07-31','12:00:00','Dine-In',8,'T8',NULL,1,'MAIN-HALL',6,'Neha Gupta','9845012306',2,'201','Rakesh Yadav','Completed','Paid',980,0,0,NULL,0,0,980,NULL,NULL,'af708515-a463-401d-bd18-47f599c8ab2b','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(11,'ORD-2026-0011','2026-07-31','12:00:00','Dine-In',11,'T11',NULL,2,'PATIO',5,'Vikram Rao','9845012305',2,'201','Rakesh Yadav','Completed','Paid',390,0,0,NULL,0,0,390,NULL,NULL,'881c9971-4c14-4da6-8e7f-bae2fd86a943','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(12,'ORD-2026-0012','2026-07-31','12:00:00','Dine-In',12,'T12',NULL,2,'PATIO',7,'Karan Malhotra','9845012307',2,'201','Rakesh Yadav','Completed','Paid',500,0,0,NULL,0,0,500,NULL,NULL,'455c3253-4afa-4de9-8767-628059488990','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(13,'ORD-2026-0013','2026-07-31','12:00:00','Takeaway',NULL,NULL,NULL,NULL,NULL,9,'Farhan Khan','9845019101',2,'201','Rakesh Yadav','Completed','Paid',560,0,0,NULL,0,0,560,NULL,NULL,'fbf82787-8edd-4e07-8364-80b66d39e573','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(14,'ORD-2026-0014','2026-07-31','12:00:00','Room Service',NULL,NULL,'205',NULL,NULL,8,'Ananya Iyer','9845012308',2,'201','Rakesh Yadav','Completed','Paid',760,0,0,NULL,0,0,760,NULL,NULL,'16d4b150-a404-4b69-99ca-38484a9dd13d','ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(15,'ORD-C8584D7F','2026-08-01','14:01:38','Dine-In',6,'T6',NULL,1,'MAIN-HALL',NULL,NULL,NULL,2,'201','Rakesh Yadav','Completed','Paid',880,0,0,NULL,0,0,880,NULL,NULL,'ab123381-8dbf-4664-9f9b-e828e8e85dfd','ACTIVE','1','2026-08-01 14:01:37','2026-08-01 14:02:52','1','1','MAIN'),(16,'ORD-FAE3729B','2026-08-06','14:37:41','Dine-In',17,'TBL-06F954BA',NULL,5,'FLR-699C5524',NULL,'Rithvik',NULL,5,NULL,NULL,'In Progress','Pending',430,0,0,NULL,0,0,430,NULL,NULL,'125a8354-5138-4e7a-821a-ecb511f840cb','ACTIVE','1','2026-08-06 14:37:41','2026-08-06 14:38:07','1','1','MAIN'),(17,'ORD-512A4833','2026-08-06','15:08:44','Dine-In',13,'T13',NULL,3,'BANQUET',NULL,'Ramesh',NULL,NULL,NULL,NULL,'In Progress','Pending',280,0,0,NULL,0,0,280,NULL,NULL,'1d623324-2f0b-4f52-9f2d-6124919c3d5c','ACTIVE','1','2026-08-06 15:08:43','2026-08-06 15:09:05','1','1','MAIN'),(18,'ORD-BE7EC200','2026-08-06','15:15:33','Dine-In',12,'T12',NULL,2,'PATIO',NULL,NULL,NULL,NULL,NULL,NULL,'In Progress','Pending',440,0,0,NULL,0,0,440,NULL,NULL,'3a066bd5-7902-4d11-a633-55937fc05c7d','ACTIVE','1','2026-08-06 15:15:33','2026-08-06 15:16:13','1','1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_order_item`
--

LOCK TABLES `restaurant_order_item` WRITE;
/*!40000 ALTER TABLE `restaurant_order_item` DISABLE KEYS */;
INSERT INTO `restaurant_order_item` VALUES (1,1,1,1,1,220,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,1,22,1,2,90,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,2,2,1,1,260,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,2,14,1,3,60,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,2,6,1,1,240,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,3,12,1,1,380,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(7,3,23,1,2,160,'Pending',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(8,4,5,1,1,320,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(9,4,15,1,1,150,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(10,4,14,1,2,60,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(11,5,11,1,1,310,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(12,5,10,1,2,120,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(13,6,18,2,1,350,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(14,6,19,2,1,280,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(15,6,23,1,2,160,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(16,7,5,1,1,320,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(17,7,14,1,2,60,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(18,7,15,1,1,150,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(19,7,20,3,2,90,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(20,8,9,1,2,150,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(21,8,22,1,2,90,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(22,9,18,2,1,350,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(23,9,19,2,1,280,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(24,9,14,1,3,60,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(25,9,23,1,2,160,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(26,10,12,1,1,380,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(27,10,13,1,1,280,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(28,10,21,3,2,160,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(29,11,17,1,1,300,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(30,11,20,3,1,90,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(31,12,7,1,1,260,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(32,12,14,1,2,60,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(33,12,24,1,2,60,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(34,13,8,1,1,290,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(35,13,15,1,1,150,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(36,13,14,1,2,60,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(37,14,16,1,1,240,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(38,14,6,1,1,240,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(39,14,14,1,2,60,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(40,14,21,3,1,160,'Served',NULL,NULL,NULL,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(41,15,5,1,2,320,'Ready',NULL,NULL,NULL,'ACTIVE','1','2026-08-01 14:01:53','2026-08-06 15:14:55',NULL,'1','MAIN'),(42,15,14,1,4,60,'Ready',NULL,NULL,NULL,'ACTIVE','1','2026-08-01 14:01:53','2026-08-06 15:14:55',NULL,'1','MAIN'),(43,16,25,1,1,250,'Ready',NULL,NULL,NULL,'ACTIVE','1','2026-08-06 14:37:49','2026-08-06 15:14:12',NULL,'1','MAIN'),(44,16,22,1,1,90,'Ready',NULL,NULL,NULL,'ACTIVE','1','2026-08-06 14:37:54','2026-08-06 15:14:13',NULL,'1','MAIN'),(45,16,22,1,1,90,'Ready',NULL,NULL,NULL,'ACTIVE','1','2026-08-06 14:38:04','2026-08-06 15:14:16',NULL,'1','MAIN'),(46,17,19,2,1,280,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-08-06 15:08:51','2026-08-06 15:09:05',NULL,'1','MAIN'),(47,18,4,1,1,190,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-08-06 15:15:42','2026-08-06 15:16:13',NULL,'1','MAIN'),(48,18,20,3,1,90,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-08-06 15:16:07','2026-08-06 15:16:13',NULL,'1','MAIN'),(49,18,23,1,1,160,'Preparing',NULL,NULL,NULL,'ACTIVE','1','2026-08-06 15:16:12','2026-08-06 15:16:13',NULL,'1','MAIN');
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
INSERT INTO `restaurant_settings` VALUES (1,'opening_time','11:00','OperatingHours','Restaurant daily opening time','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,'closing_time','23:30','OperatingHours','Restaurant daily closing time','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,'cgst_percentage','6','Tax','Default CGST applied on bills','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,'sgst_percentage','6','Tax','Default SGST applied on bills','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,'service_charge_percentage','5','ServiceCharge','Default service charge applied on bills','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,'bill_number_prefix','BILL','Numbering','Prefix used for generated bill numbers','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_staff_assignment`
--

LOCK TABLES `restaurant_staff_assignment` WRITE;
/*!40000 ALTER TABLE `restaurant_staff_assignment` DISABLE KEYS */;
INSERT INTO `restaurant_staff_assignment` VALUES (1,201,'Rakesh Yadav','Waiter','2026-07-31','11:00:00','23:00:00','Main Dining Hall',1,15000,0,'2026-07-31 10:45:00',NULL,NULL,NULL,'On Shift','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(2,202,'Suman Reddy','Waiter','2026-07-31','11:00:00','23:00:00','Outdoor Patio',NULL,15000,0,'2026-07-31 10:45:00',NULL,NULL,NULL,'On Shift','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(3,203,'Imran Sheikh','Waiter','2026-07-31','11:00:00','23:00:00','Main Dining Hall',1,15000,0,'2026-07-31 10:45:00',NULL,NULL,NULL,'On Shift','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(4,204,'Chef Antoine','Chef','2026-07-31','11:00:00','23:00:00',NULL,NULL,15000,0,'2026-07-31 10:45:00',NULL,NULL,NULL,'On Shift','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(5,205,'Geeta Shah','Cashier','2026-07-31','11:00:00','23:00:00',NULL,NULL,15000,0,'2026-07-31 10:45:00',NULL,2000,NULL,'On Shift','ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(6,1,'John Doe','Chef','2026-08-06','09:00:00',NULL,'Bar',NULL,NULL,0,NULL,NULL,NULL,NULL,'Scheduled','ACTIVE','1','2026-08-06 12:29:06','2026-08-06 12:34:24','1','1','MAIN'),(7,3,'Ramesh Ramesh','Manager','2026-08-06','09:00:00',NULL,'Restaurant',NULL,NULL,0,NULL,NULL,NULL,NULL,'Scheduled','ACTIVE','1','2026-08-06 12:29:26','2026-08-06 12:33:18','1','1','MAIN'),(8,2,'Anand  M','Cashier','2026-08-06','09:00:00',NULL,'Hotel',NULL,NULL,0,NULL,NULL,NULL,NULL,'Scheduled','ACTIVE','1','2026-08-06 12:29:38','2026-08-06 12:33:31','1','1','MAIN'),(9,1,'John Doe','Chef','2026-08-06','09:00:00','16:00:00',NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,'Scheduled','ACTIVE','1','2026-08-06 12:33:47',NULL,NULL,'1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_table`
--

LOCK TABLES `restaurant_table` WRITE;
/*!40000 ALTER TABLE `restaurant_table` DISABLE KEYS */;
INSERT INTO `restaurant_table` VALUES (1,'T1','Table 1',1,1,'MAIN-HALL','Standard',4,'Restaurant',1,NULL,NULL,NULL,NULL,NULL,NULL,'Occupied',1,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(2,'T2','Table 2',2,1,'MAIN-HALL','Standard',4,'Restaurant',2,NULL,NULL,NULL,NULL,NULL,NULL,'Occupied',1,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(3,'T3','Table 3',3,1,'MAIN-HALL','Standard',2,'Restaurant',4,NULL,NULL,NULL,NULL,NULL,NULL,'Occupied',1,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(4,'T4','Table 4',4,1,'MAIN-HALL','Standard',4,'Restaurant',5,NULL,NULL,NULL,NULL,NULL,NULL,'Occupied',1,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(5,'T5','Table 5',5,1,'MAIN-HALL','VIP',6,'Restaurant',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Cleaning',0,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(6,'T6','Table 6',6,1,'MAIN-HALL','Standard',4,'Restaurant',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Cleaning',1,'ACTIVE','1','2026-07-31 12:34:09','2026-08-01 14:02:52','1','1','MAIN'),(7,'T7','Table 7',7,1,'MAIN-HALL','Standard',2,'Restaurant',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Cleaning',1,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(8,'T8','Table 8',8,1,'MAIN-HALL','VIP',6,'Restaurant',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Available',0,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(9,'T9','Table 9',9,2,'PATIO','Standard',4,'Outdoor',3,NULL,NULL,NULL,NULL,NULL,NULL,'Occupied',1,'ACTIVE','1','2026-07-31 12:34:09','2026-07-31 12:34:09',NULL,'1','MAIN'),(10,'T10','Table 10',10,2,'PATIO','Standard',4,'Outdoor',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Cleaning',1,'ACTIVE','1','2026-07-31 12:34:09','2026-08-06 15:27:08','1','1','MAIN'),(11,'T11','Table 11',11,2,'PATIO','Standard',2,'Outdoor',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Reserved',1,'ACTIVE','1','2026-07-31 12:34:09','2026-08-06 14:41:58','1','1','MAIN'),(12,'T12','Table 12',12,2,'PATIO','Standard',4,'Outdoor',18,NULL,NULL,NULL,NULL,NULL,NULL,'Occupied',1,'ACTIVE','1','2026-07-31 12:34:09','2026-08-06 15:15:33','1','1','MAIN'),(13,'T13','Table 13',13,3,'BANQUET','Private',10,'Banquet',17,NULL,NULL,NULL,NULL,NULL,NULL,'Occupied',0,'ACTIVE','1','2026-07-31 12:34:09','2026-08-06 15:08:43','1','1','MAIN'),(14,'T14','Table 14',14,3,'BANQUET','Private',10,'Banquet',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Available',0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(15,'T15','Table 15',15,3,'BANQUET','Private',8,'Banquet',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Available',0,'ACTIVE','1','2026-07-31 12:34:09',NULL,NULL,'1','MAIN'),(16,'TBL-F38D36A9','Table No 16',16,5,'FLR-699C5524','Standard',19,'Restaurant',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Available',0,'INACTIVE','1','2026-08-06 14:36:06','2026-08-06 14:36:31','1','1','MAIN'),(17,'TBL-06F954BA','Table 16',16,5,'FLR-699C5524','Standard',20,'Restaurant',16,NULL,NULL,NULL,NULL,NULL,NULL,'Occupied',0,'ACTIVE','1','2026-08-06 14:36:49','2026-08-06 14:41:08','1','1','MAIN');
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_table_reservation`
--

LOCK TABLES `restaurant_table_reservation` WRITE;
/*!40000 ALTER TABLE `restaurant_table_reservation` DISABLE KEYS */;
INSERT INTO `restaurant_table_reservation` VALUES (1,'RSV-CDED45C3','2026-08-07','12:00:00','14:00:00',17,'TBL-06F954BA',5,'FLR-699C5524','Rithvik','8576574563',NULL,5,'Hotel Guest',NULL,NULL,'Completed',NULL,NULL,NULL,NULL,'1e5a84ba-4da0-4f76-8bf6-c05ab44522b2','ACTIVE','1','2026-08-06 14:40:47','2026-08-06 14:41:15','1','1','MAIN'),(2,'RSV-B51DC6DD','2026-08-10','08:00:00','09:00:00',11,'T11',2,'PATIO','Ramesh','7567456433',NULL,6,'Walk-In',NULL,NULL,'Reserved',NULL,NULL,NULL,NULL,'4e28351b-c428-4a41-8145-af15ffa2e94d','ACTIVE','1','2026-08-06 14:41:58',NULL,NULL,'1','MAIN');
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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-06 23:27:34
