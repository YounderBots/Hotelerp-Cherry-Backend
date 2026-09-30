-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: hotelerp_hotel
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
-- Current Database: `hotelerp_hotel`
--

/*!40000 DROP DATABASE IF EXISTS `hotelerp_hotel`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hotelerp_hotel` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hotelerp_hotel`;

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
INSERT INTO `alembic_version` VALUES ('e7d2c4a9b1f0');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `common_complementary_history`
--

DROP TABLE IF EXISTS `common_complementary_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `common_complementary_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reservation_id` varchar(255) NOT NULL,
  `common_complementary_id` varchar(255) NOT NULL,
  `complementary_name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_common_complementary_history_token` (`token`),
  KEY `ix_common_complementary_history_status` (`status`),
  KEY `ix_common_complementary_history_common_complementary_id` (`common_complementary_id`),
  KEY `ix_common_complementary_history_reservation_id` (`reservation_id`),
  KEY `ix_common_complementary_history_company_id` (`company_id`),
  KEY `ix_common_complementary_history_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_complementary_history`
--

LOCK TABLES `common_complementary_history` WRITE;
/*!40000 ALTER TABLE `common_complementary_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `common_complementary_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_data`
--

DROP TABLE IF EXISTS `customer_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` varchar(100) DEFAULT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` varchar(20) NOT NULL,
  `marital_status` varchar(20) NOT NULL,
  `vip_status` varchar(20) NOT NULL,
  `address` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `postal_code` varchar(20) NOT NULL,
  `country` varchar(100) NOT NULL,
  `number_of_guests` int NOT NULL,
  `number_of_adults` int NOT NULL,
  `adult_names` json NOT NULL,
  `number_of_children` int NOT NULL,
  `children_names` json NOT NULL,
  `identification_type_id` varchar(100) NOT NULL,
  `identification_proof` varchar(255) NOT NULL,
  `reservation_id` varchar(100) DEFAULT NULL,
  `check_in_date` date DEFAULT NULL,
  `check_in_time` time DEFAULT NULL,
  `check_out_date` date DEFAULT NULL,
  `check_out_time` time DEFAULT NULL,
  `room_ids` json DEFAULT NULL,
  `room_type_ids` json DEFAULT NULL,
  `bed_type_ids` json DEFAULT NULL,
  `purpose_of_visit` varchar(255) DEFAULT NULL,
  `emergency_name` varchar(100) DEFAULT NULL,
  `emergency_contact` varchar(20) DEFAULT NULL,
  `emergency_relationship` varchar(50) DEFAULT NULL,
  `consent_for_data_use` varchar(10) DEFAULT NULL,
  `acknowledgment_of_hotel_policies` varchar(10) DEFAULT NULL,
  `special_services_info` json DEFAULT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `tax_amount` decimal(12,2) DEFAULT NULL,
  `discount_amount` decimal(12,2) DEFAULT NULL,
  `laundry_amount` decimal(12,2) DEFAULT NULL,
  `bar_amount` decimal(12,2) DEFAULT NULL,
  `cafe_amount` decimal(12,2) DEFAULT NULL,
  `restaurant_amount` decimal(12,2) DEFAULT NULL,
  `special_services_amount` decimal(12,2) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_customer_data_customer_id` (`customer_id`),
  KEY `ix_customer_data_vip_status` (`vip_status`),
  KEY `ix_customer_data_check_in_date` (`check_in_date`),
  KEY `ix_customer_data_city` (`city`),
  KEY `ix_customer_data_last_name` (`last_name`),
  KEY `ix_customer_data_check_out_date` (`check_out_date`),
  KEY `ix_customer_data_state` (`state`),
  KEY `ix_customer_data_email` (`email`),
  KEY `ix_customer_data_status` (`status`),
  KEY `ix_customer_data_postal_code` (`postal_code`),
  KEY `ix_customer_data_mobile` (`mobile`),
  KEY `ix_customer_data_company_id` (`company_id`),
  KEY `ix_customer_data_country` (`country`),
  KEY `ix_customer_data_first_name` (`first_name`),
  KEY `ix_customer_data_gender` (`gender`),
  KEY `ix_customer_data_identification_type_id` (`identification_type_id`),
  KEY `ix_customer_data_id` (`id`),
  KEY `ix_customer_data_marital_status` (`marital_status`),
  KEY `ix_customer_data_reservation_id` (`reservation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_data`
--

LOCK TABLES `customer_data` WRITE;
/*!40000 ALTER TABLE `customer_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hotel_business_date`
--

DROP TABLE IF EXISTS `hotel_business_date`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotel_business_date` (
  `id` int NOT NULL AUTO_INCREMENT,
  `business_date` date NOT NULL,
  `last_audit_at` datetime DEFAULT NULL,
  `last_audit_by` varchar(100) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_business_date_company` (`company_id`),
  KEY `ix_hotel_business_date_business_date` (`business_date`),
  KEY `ix_hotel_business_date_company_id` (`company_id`),
  KEY `ix_hotel_business_date_id` (`id`),
  KEY `ix_hotel_business_date_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hotel_business_date`
--

LOCK TABLES `hotel_business_date` WRITE;
/*!40000 ALTER TABLE `hotel_business_date` DISABLE KEYS */;
INSERT INTO `hotel_business_date` VALUES (1,'2026-09-30','2026-09-30 02:15:00','1','ACTIVE','1','2026-09-29 02:15:00','2026-09-30 02:15:00','1','1');
/*!40000 ALTER TABLE `hotel_business_date` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `housekeeper_task`
--

DROP TABLE IF EXISTS `housekeeper_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `housekeeper_task` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_id` varchar(100) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `schedule_date` date NOT NULL,
  `schedule_time` time NOT NULL,
  `room_no` int NOT NULL,
  `task_type` varchar(100) NOT NULL,
  `assign_staff` varchar(100) NOT NULL,
  `task_status` varchar(50) NOT NULL,
  `room_status` varchar(50) NOT NULL,
  `lost_found` varchar(255) DEFAULT NULL,
  `special_instructions` varchar(255) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` int DEFAULT NULL,
  `company_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_housekeeper_task_company_id` (`company_id`),
  KEY `ix_housekeeper_task_room_status` (`room_status`),
  KEY `ix_housekeeper_task_task_status` (`task_status`),
  KEY `ix_housekeeper_task_room_no` (`room_no`),
  KEY `ix_housekeeper_task_employee_id` (`employee_id`),
  KEY `ix_housekeeper_task_status` (`status`),
  KEY `ix_housekeeper_task_assign_staff` (`assign_staff`),
  KEY `ix_housekeeper_task_id` (`id`),
  KEY `ix_housekeeper_task_schedule_date` (`schedule_date`),
  KEY `ix_housekeeper_task_task_type` (`task_type`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `housekeeper_task`
--

LOCK TABLES `housekeeper_task` WRITE;
/*!40000 ALTER TABLE `housekeeper_task` DISABLE KEYS */;
INSERT INTO `housekeeper_task` VALUES (1,'5','Imran','Khan','2026-09-30','09:00:00',1,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(2,'6','Lakshmi','Iyer','2026-09-30','10:00:00',2,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(3,'5','Imran','Khan','2026-09-30','11:00:00',3,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(4,'6','Lakshmi','Iyer','2026-09-30','12:00:00',11,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(5,'5','Imran','Khan','2026-09-30','09:00:00',15,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(6,'6','Lakshmi','Iyer','2026-09-30','10:00:00',20,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(7,'5','Imran','Khan','2026-09-30','11:00:00',24,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(8,'5','Imran','Khan','2026-09-30','10:30:00',4,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(9,'6','Lakshmi','Iyer','2026-09-30','11:30:00',9,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(10,'5','Imran','Khan','2026-09-30','12:30:00',13,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(11,'6','Lakshmi','Iyer','2026-09-30','13:30:00',16,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(12,'5','Imran','Khan','2026-09-30','14:30:00',17,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1),(13,'6','Lakshmi','Iyer','2026-09-30','10:30:00',21,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-30 08:30:00',NULL,NULL,1);
/*!40000 ALTER TABLE `housekeeper_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hsk_room_incident`
--

DROP TABLE IF EXISTS `hsk_room_incident`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hsk_room_incident` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_no` int DEFAULT NULL,
  `incident_date` date DEFAULT NULL,
  `incident_time` time DEFAULT NULL,
  `incident_description` varchar(255) DEFAULT NULL,
  `involved_staff` varchar(255) DEFAULT NULL,
  `severity` varchar(50) DEFAULT NULL,
  `witnesses` varchar(255) DEFAULT NULL,
  `actions_taken` varchar(255) DEFAULT NULL,
  `reported_by` varchar(100) DEFAULT NULL,
  `report_date` date DEFAULT NULL,
  `attachment_file` varchar(255) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_hsk_room_incident_status` (`status`),
  KEY `ix_hsk_room_incident_severity` (`severity`),
  KEY `ix_hsk_room_incident_incident_date` (`incident_date`),
  KEY `ix_hsk_room_incident_report_date` (`report_date`),
  KEY `ix_hsk_room_incident_involved_staff` (`involved_staff`),
  KEY `ix_hsk_room_incident_room_no` (`room_no`),
  KEY `ix_hsk_room_incident_company_id` (`company_id`),
  KEY `ix_hsk_room_incident_reported_by` (`reported_by`),
  KEY `ix_hsk_room_incident_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hsk_room_incident`
--

LOCK TABLES `hsk_room_incident` WRITE;
/*!40000 ALTER TABLE `hsk_room_incident` DISABLE KEYS */;
INSERT INTO `hsk_room_incident` VALUES (1,12,'2026-09-24','18:20:00','Bathroom tap dripping; floor wet on arrival.','Imran Khan','Medium','Duty Manager','Tap washer replaced, floor dried and room re-inspected.','Imran Khan','2026-09-24','/templates/static/room_incidents/d07d60b0d54c4385b9537f3a85773b73.jpg','ACTIVE','1','2026-09-24 18:20:00',NULL,NULL,'1'),(2,16,'2026-09-27','09:05:00','Guest reported air conditioning not cooling.','Lakshmi Iyer','High','Duty Manager','Maintenance recharged the unit; guest confirmed satisfied.','Lakshmi Iyer','2026-09-27','/templates/static/room_incidents/9b5dd1c2fa5e4a76979a15599459d126.jpg','ACTIVE','1','2026-09-27 09:05:00',NULL,NULL,'1'),(3,8,'2026-09-29','21:40:00','Reading lamp shade cracked in dormitory bay 3.','Imran Khan','Low','Duty Manager','Shade replaced from stores; no charge raised to guest.','Imran Khan','2026-09-29','/templates/static/room_incidents/f6c04208f491478cb542ae72ff687e1b.jpg','ACTIVE','1','2026-09-29 21:40:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `hsk_room_incident` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inquiry`
--

DROP TABLE IF EXISTS `inquiry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inquiry` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inquiry_mode` varchar(50) NOT NULL,
  `guest_name` varchar(255) NOT NULL,
  `response` varchar(255) DEFAULT NULL,
  `follow_up` varchar(255) DEFAULT NULL,
  `incidents` varchar(255) DEFAULT NULL,
  `inquiry_status` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_inquiry_id` (`id`),
  KEY `ix_inquiry_status` (`status`),
  KEY `ix_inquiry_guest_name` (`guest_name`),
  KEY `ix_inquiry_inquiry_status` (`inquiry_status`),
  KEY `ix_inquiry_inquiry_mode` (`inquiry_mode`),
  KEY `ix_inquiry_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inquiry`
--

LOCK TABLES `inquiry` WRITE;
/*!40000 ALTER TABLE `inquiry` DISABLE KEYS */;
INSERT INTO `inquiry` VALUES (1,'Online','Deepak Anand','Asked for tariff on two Deluxe rooms in October.','Rate sheet emailed; awaiting confirmation.',NULL,'In Progress','ACTIVE','1','2026-09-29 11:00:00',NULL,NULL,'1'),(2,'Offline','Sridevi Raman','Walk-in asking about banquet hall for a reception.','Banquet manager to call back with availability.',NULL,'In Progress','ACTIVE','1','2026-09-28 11:00:00',NULL,NULL,'1'),(3,'Online','Michael Fernandes','Airport pickup availability for a late arrival.','Confirmed pickup can be arranged with 12 hours\' notice.',NULL,'Completed','ACTIVE','1','2026-09-27 11:00:00',NULL,NULL,'1'),(4,'Online','Aisha Rahman','Requested a quiet room away from the lift.','Noted on the booking; room 305 allocated.',NULL,'Completed','ACTIVE','1','2026-09-26 11:00:00',NULL,NULL,'1'),(5,'Offline','Ganesh Iyer','Corporate tie-up enquiry for monthly stays.','Corporate rate card shared with the company\'s admin.',NULL,'In Progress','ACTIVE','1','2026-09-25 11:00:00',NULL,NULL,'1'),(6,'Online','Sarah Thomas','Asked whether the pool is open to day guests.','Advised pool access is for in-house guests only.',NULL,'Completed','ACTIVE','1','2026-09-24 11:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `inquiry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `language`
--

DROP TABLE IF EXISTS `language`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `language` (
  `id` int NOT NULL AUTO_INCREMENT,
  `language_name` varchar(100) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_language_language_name` (`language_name`),
  KEY `ix_language_status` (`status`),
  KEY `ix_language_id` (`id`),
  KEY `ix_language_company_id` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `language`
--

LOCK TABLES `language` WRITE;
/*!40000 ALTER TABLE `language` DISABLE KEYS */;
/*!40000 ALTER TABLE `language` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `laundry_items`
--

DROP TABLE IF EXISTS `laundry_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `laundry_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_name` varchar(100) NOT NULL,
  `price` decimal(12,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_laundry_items_item_name` (`item_name`),
  KEY `ix_laundry_items_status` (`status`),
  KEY `ix_laundry_items_id` (`id`),
  KEY `ix_laundry_items_company_id` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `laundry_items`
--

LOCK TABLES `laundry_items` WRITE;
/*!40000 ALTER TABLE `laundry_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `laundry_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `laundry_management`
--

DROP TABLE IF EXISTS `laundry_management`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `laundry_management` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_id` varchar(100) DEFAULT NULL,
  `guest_name` varchar(100) DEFAULT NULL,
  `mobile` varchar(20) NOT NULL,
  `laundry_date` date NOT NULL,
  `items` json NOT NULL,
  `item_counts` json NOT NULL,
  `item_prices` json NOT NULL,
  `total_items` int NOT NULL,
  `net_price` decimal(12,2) NOT NULL,
  `laundry_status` varchar(50) NOT NULL,
  `special_instructions` varchar(255) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_laundry_management_laundry_date` (`laundry_date`),
  KEY `ix_laundry_management_room_id` (`room_id`),
  KEY `ix_laundry_management_mobile` (`mobile`),
  KEY `ix_laundry_management_status` (`status`),
  KEY `ix_laundry_management_id` (`id`),
  KEY `ix_laundry_management_laundry_status` (`laundry_status`),
  KEY `ix_laundry_management_company_id` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `laundry_management`
--

LOCK TABLES `laundry_management` WRITE;
/*!40000 ALTER TABLE `laundry_management` DISABLE KEYS */;
/*!40000 ALTER TABLE `laundry_management` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `night_audit`
--

DROP TABLE IF EXISTS `night_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `night_audit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `night_audit_id` varchar(100) NOT NULL,
  `business_date` date NOT NULL,
  `next_business_date` date DEFAULT NULL,
  `audit_status` varchar(20) NOT NULL,
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `run_by` varchar(100) DEFAULT NULL,
  `error_message` varchar(500) DEFAULT NULL,
  `rooms_total` int DEFAULT NULL,
  `rooms_occupied` int DEFAULT NULL,
  `occupancy_percent` decimal(6,3) DEFAULT NULL,
  `room_nights` int DEFAULT NULL,
  `arrivals_expected` int DEFAULT NULL,
  `arrivals_completed` int DEFAULT NULL,
  `departures_expected` int DEFAULT NULL,
  `departures_completed` int DEFAULT NULL,
  `in_house` int DEFAULT NULL,
  `stayovers` int DEFAULT NULL,
  `no_shows_marked` int DEFAULT NULL,
  `no_show_reservation_ids` json DEFAULT NULL,
  `room_revenue` decimal(12,2) DEFAULT NULL,
  `extra_charges` decimal(12,2) DEFAULT NULL,
  `tax_amount` decimal(12,2) DEFAULT NULL,
  `discount_amount` decimal(12,2) DEFAULT NULL,
  `gross_revenue` decimal(12,2) DEFAULT NULL,
  `payments_collected` decimal(12,2) DEFAULT NULL,
  `payment_breakdown` json DEFAULT NULL,
  `outstanding_balance` decimal(12,2) DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_night_audit_company_date` (`company_id`,`business_date`),
  UNIQUE KEY `ix_night_audit_night_audit_id` (`night_audit_id`),
  UNIQUE KEY `ix_night_audit_token` (`token`),
  KEY `ix_night_audit_audit_status` (`audit_status`),
  KEY `ix_night_audit_business_date` (`business_date`),
  KEY `ix_night_audit_company_id` (`company_id`),
  KEY `ix_night_audit_id` (`id`),
  KEY `ix_night_audit_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `night_audit`
--

LOCK TABLES `night_audit` WRITE;
/*!40000 ALTER TABLE `night_audit` DISABLE KEYS */;
INSERT INTO `night_audit` VALUES (1,'NA-20260929','2026-09-29','2026-09-30','Completed','2026-09-30 02:10:00','2026-09-30 02:15:00','1',NULL,25,7,28.000,6,1,1,0,0,6,6,0,'[]',37437.50,610.00,5611.68,3126.50,40532.68,26179.75,'[{\"amount\": 14896.0, \"payment_method\": \"Cash\"}, {\"amount\": 11283.75, \"payment_method\": \"UPI\"}]',94953.61,'1aa52f93-8e40-4a5c-af40-bf42ee2d54b2','ACTIVE','1','2026-09-30 02:15:00','2026-09-30 02:15:00','1','1');
/*!40000 ALTER TABLE `night_audit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quantity`
--

DROP TABLE IF EXISTS `quantity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quantity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_quantity_status` (`status`),
  KEY `ix_quantity_id` (`id`),
  KEY `ix_quantity_company_id` (`company_id`),
  KEY `ix_quantity_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quantity`
--

LOCK TABLES `quantity` WRITE;
/*!40000 ALTER TABLE `quantity` DISABLE KEYS */;
/*!40000 ALTER TABLE `quantity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_amount_paid_history`
--

DROP TABLE IF EXISTS `reservation_amount_paid_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_amount_paid_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reservation_id` varchar(255) NOT NULL,
  `user_id` varchar(255) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `paid_date` date NOT NULL,
  `payment_method` varchar(100) NOT NULL,
  `token` varchar(36) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_reservation_amount_paid_history_token` (`token`),
  KEY `ix_reservation_amount_paid_history_id` (`id`),
  KEY `ix_reservation_amount_paid_history_company_id` (`company_id`),
  KEY `ix_reservation_amount_paid_history_payment_method` (`payment_method`),
  KEY `ix_reservation_amount_paid_history_user_id` (`user_id`),
  KEY `ix_reservation_amount_paid_history_status` (`status`),
  KEY `ix_reservation_amount_paid_history_paid_date` (`paid_date`),
  KEY `ix_reservation_amount_paid_history_reservation_id` (`reservation_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_amount_paid_history`
--

LOCK TABLES `reservation_amount_paid_history` WRITE;
/*!40000 ALTER TABLE `reservation_amount_paid_history` DISABLE KEYS */;
INSERT INTO `reservation_amount_paid_history` VALUES (1,'RES-202609-0001','1',3175.20,'2026-08-25','UPI','903ab4c9-1a9e-48f2-bb03-81d292e3ac90','ACTIVE','1','2026-08-25 12:15:00',NULL,NULL,'1'),(2,'RES-202609-0001','1',7408.80,'2026-09-11','Credit Card','ba3fdf06-9a25-4af6-9d23-209887f0d5c6','ACTIVE','1','2026-09-11 12:15:00',NULL,NULL,'1'),(3,'RES-202609-0002','1',26432.00,'2026-09-12','Credit Card','6d9107df-a377-4651-b163-e735e92e98a0','ACTIVE','1','2026-09-12 12:15:00',NULL,NULL,'1'),(4,'RES-202609-0003','1',23821.25,'2026-09-15','Bank Transfer','2912fba3-fed6-4f50-9b0a-d1fa1cc229d5','ACTIVE','1','2026-09-15 12:15:00',NULL,NULL,'1'),(5,'RES-202609-0003','1',23821.25,'2026-09-20','Bank Transfer','300e5e11-7aec-4820-9ba6-39832dd90308','ACTIVE','1','2026-09-20 12:15:00',NULL,NULL,'1'),(6,'RES-202609-0004','1',20009.85,'2026-09-18','Cash','f7aaa4de-31c6-488c-af1b-db62c5bcd831','ACTIVE','1','2026-09-18 12:15:00',NULL,NULL,'1'),(7,'RES-202609-0005','1',7526.40,'2026-09-18','UPI','417bdf64-5e58-46f6-8265-53a617aedb39','ACTIVE','1','2026-09-18 12:15:00',NULL,NULL,'1'),(8,'RES-202609-0005','1',11289.60,'2026-09-23','Debit Card','8e2cfb9e-cdad-4040-a5d8-7665eaa03dca','ACTIVE','1','2026-09-23 12:15:00',NULL,NULL,'1'),(9,'RES-202609-0006','1',114932.00,'2026-09-22','Credit Card','de2ddd1e-845d-4666-a407-ea89d36aba71','ACTIVE','1','2026-09-22 12:15:00',NULL,NULL,'1'),(10,'RES-202609-0007','1',18816.00,'2026-09-27','UPI','448b94d6-a20c-4f68-a8fa-055856e95944','ACTIVE','1','2026-09-27 12:15:00',NULL,NULL,'1'),(11,'RES-202609-0008','1',21363.90,'2026-09-28','Corporate Billing','0cb7c229-888d-401e-ac4f-a425f4c94e79','ACTIVE','1','2026-09-28 12:15:00',NULL,NULL,'1'),(12,'RES-202609-0009','1',25113.70,'2026-09-26','Bank Transfer','3aad82be-b5ca-48fb-9edf-ede668cb6aa4','ACTIVE','1','2026-09-26 12:15:00',NULL,NULL,'1'),(13,'RES-202609-0010','1',14896.00,'2026-09-29','Cash','0f932d04-a255-465a-b3c7-8ecd362b08df','ACTIVE','1','2026-09-29 12:15:00',NULL,NULL,'1'),(14,'RES-202609-0011','1',9266.88,'2026-09-28','UPI','1e636834-be33-4d0e-9b26-8abd372965ff','ACTIVE','1','2026-09-28 12:15:00',NULL,NULL,'1'),(15,'RES-202609-0012','1',22567.50,'2026-09-25','Credit Card','8a96e4aa-7705-4fb7-a642-1514ab417f9e','ACTIVE','1','2026-09-25 12:15:00',NULL,NULL,'1'),(16,'RES-202609-0012','1',11283.75,'2026-09-29','UPI','f4c347ad-9e1f-45d5-8741-c99d014658ea','ACTIVE','1','2026-09-29 12:15:00',NULL,NULL,'1'),(17,'RES-202609-0013','1',1960.00,'2026-09-30','UPI','00b97304-a488-459f-9838-13c170b9965d','ACTIVE','1','2026-09-30 12:15:00',NULL,NULL,'1'),(18,'RES-202609-0014','1',5080.32,'2026-09-25','Credit Card','e0360a16-bc4b-4257-a0e2-ed93afca6f8a','ACTIVE','1','2026-09-25 12:15:00',NULL,NULL,'1'),(19,'RES-202609-0015','1',63690.50,'2026-09-23','Bank Transfer','a3a75e24-fe25-40c5-9ff4-1236a2a26d76','ACTIVE','1','2026-09-23 12:15:00',NULL,NULL,'1'),(20,'RES-202609-0016','1',4814.40,'2026-10-02','UPI','7b6cb989-1ab9-427f-a6b1-0cd6a56b527e','ACTIVE','1','2026-10-02 12:15:00',NULL,NULL,'1'),(21,'RES-202609-0018','1',18223.92,'2026-10-06','Credit Card','3c04df1d-525f-440b-96e0-335ed494dd91','ACTIVE','1','2026-10-06 12:15:00',NULL,NULL,'1'),(22,'RES-202609-0022','1',537.60,'2026-10-06','UPI','b038e0dd-ca98-4f8c-8b7f-45156ca75708','ACTIVE','1','2026-10-06 12:15:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `reservation_amount_paid_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_booking`
--

DROP TABLE IF EXISTS `room_booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_booking` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_booking_id` varchar(255) NOT NULL,
  `salutation` varchar(50) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `phone_number` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `arrival_date` date NOT NULL,
  `departure_date` date NOT NULL,
  `no_of_nights` int NOT NULL,
  `room_type` json DEFAULT NULL,
  `no_of_rooms` int DEFAULT NULL,
  `no_of_adults` int DEFAULT NULL,
  `no_of_children` int DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_room_booking_room_booking_id` (`room_booking_id`),
  KEY `ix_room_booking_company_id` (`company_id`),
  KEY `ix_room_booking_arrival_date` (`arrival_date`),
  KEY `ix_room_booking_phone_number` (`phone_number`),
  KEY `ix_room_booking_status` (`status`),
  KEY `ix_room_booking_id` (`id`),
  KEY `ix_room_booking_departure_date` (`departure_date`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_booking`
--

LOCK TABLES `room_booking` WRITE;
/*!40000 ALTER TABLE `room_booking` DISABLE KEYS */;
INSERT INTO `room_booking` VALUES (1,'RB-4052E3AC','Mr.','Deepak','Anand','9840155501','deepak.anand@gmail.com','2026-10-30','2026-11-02',3,'[2, 2]',2,2,0,'ACTIVE','1','2026-09-28 16:20:00',NULL,NULL,'1'),(2,'RB-E570ABE5','Ms.','Sridevi','Raman','9840155502','sridevi.raman@gmail.com','2026-11-03','2026-11-05',2,'[5]',1,2,2,'ACTIVE','1','2026-09-28 16:20:00',NULL,NULL,'1'),(3,'RB-39B50CC1','Mr.','Ganesh','Iyer','9840155503','ganesh.iyer@gmail.com','2026-11-09','2026-11-14',5,'[4]',1,1,0,'ACTIVE','1','2026-09-28 16:20:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `room_booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_complementary_history`
--

DROP TABLE IF EXISTS `room_complementary_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_complementary_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reservation_id` varchar(255) NOT NULL,
  `room_complementary_id` varchar(255) NOT NULL,
  `complementary_name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_room_complementary_history_token` (`token`),
  KEY `ix_room_complementary_history_id` (`id`),
  KEY `ix_room_complementary_history_status` (`status`),
  KEY `ix_room_complementary_history_room_complementary_id` (`room_complementary_id`),
  KEY `ix_room_complementary_history_reservation_id` (`reservation_id`),
  KEY `ix_room_complementary_history_company_id` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_complementary_history`
--

LOCK TABLES `room_complementary_history` WRITE;
/*!40000 ALTER TABLE `room_complementary_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `room_complementary_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_details`
--

DROP TABLE IF EXISTS `room_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_details` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reservation_id` varchar(255) NOT NULL,
  `room_category` varchar(255) NOT NULL,
  `available_rooms` int NOT NULL,
  `total_adults` int NOT NULL,
  `total_children` int NOT NULL,
  `arrival_date` date NOT NULL,
  `departure_date` date NOT NULL,
  `booking_status` varchar(50) DEFAULT NULL,
  `reservation_type` varchar(50) NOT NULL,
  `extra_bed_count` int DEFAULT NULL,
  `extra_bed_cost` decimal(12,2) DEFAULT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `room_complementary` varchar(10) DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_room_details_token` (`token`),
  KEY `ix_room_details_id` (`id`),
  KEY `ix_room_details_reservation_type` (`reservation_type`),
  KEY `ix_room_details_departure_date` (`departure_date`),
  KEY `ix_room_details_company_id` (`company_id`),
  KEY `ix_room_details_reservation_id` (`reservation_id`),
  KEY `ix_room_details_arrival_date` (`arrival_date`),
  KEY `ix_room_details_status` (`status`),
  KEY `ix_room_details_booking_status` (`booking_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_details`
--

LOCK TABLES `room_details` WRITE;
/*!40000 ALTER TABLE `room_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `room_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_lock`
--

DROP TABLE IF EXISTS `room_lock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_lock` (
  `room_id` int NOT NULL,
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_lock`
--

LOCK TABLES `room_lock` WRITE;
/*!40000 ALTER TABLE `room_lock` DISABLE KEYS */;
/*!40000 ALTER TABLE `room_lock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_reservation`
--

DROP TABLE IF EXISTS `room_reservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_reservation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_reservation_id` varchar(255) NOT NULL,
  `salutation` varchar(50) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone_number` varchar(20) NOT NULL,
  `arrival_date` date NOT NULL,
  `departure_date` date NOT NULL,
  `no_of_nights` int NOT NULL,
  `no_of_rooms` int DEFAULT NULL,
  `reservation_status` varchar(100) DEFAULT NULL,
  `identity_type_id` int DEFAULT NULL,
  `proof_document` varchar(255) DEFAULT NULL,
  `room_ids` json DEFAULT NULL,
  `room_type_ids` json DEFAULT NULL,
  `room_no` json DEFAULT NULL,
  `rate_type` json DEFAULT NULL,
  `no_of_adults` int DEFAULT NULL,
  `no_of_children` int DEFAULT NULL,
  `room_complementary` varchar(100) DEFAULT NULL,
  `common_complementary` varchar(100) DEFAULT NULL,
  `tax_type_id` int DEFAULT NULL,
  `discount_type_id` int DEFAULT NULL,
  `room_amount` decimal(12,2) DEFAULT NULL,
  `extra_charges` decimal(12,2) DEFAULT NULL,
  `tax_percentage` decimal(6,3) DEFAULT NULL,
  `tax_amount` decimal(12,2) DEFAULT NULL,
  `discount_percentage` decimal(6,3) DEFAULT NULL,
  `discount_amount` decimal(12,2) DEFAULT NULL,
  `overall_amount` decimal(12,2) DEFAULT NULL,
  `payment_method_id` int DEFAULT NULL,
  `paying_amount` decimal(12,2) DEFAULT NULL,
  `paid_amount` decimal(12,2) DEFAULT NULL,
  `balance_amount` decimal(12,2) DEFAULT NULL,
  `extra_amount` decimal(12,2) DEFAULT NULL,
  `extra_bed_count` int DEFAULT NULL,
  `extra_bed_cost` decimal(12,2) DEFAULT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `booking_status_id` int DEFAULT NULL,
  `reservation_type` varchar(50) NOT NULL,
  `confirmation_code` varchar(100) DEFAULT NULL,
  `token` varchar(36) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  `cancellation_reason` varchar(500) DEFAULT NULL,
  `cancelled_at` datetime DEFAULT NULL,
  `cancelled_by` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_room_reservation_room_reservation_id` (`room_reservation_id`),
  UNIQUE KEY `ix_room_reservation_token` (`token`),
  KEY `ix_room_reservation_phone_number` (`phone_number`),
  KEY `ix_room_reservation_reservation_type` (`reservation_type`),
  KEY `ix_room_reservation_discount_type_id` (`discount_type_id`),
  KEY `ix_room_reservation_payment_method_id` (`payment_method_id`),
  KEY `ix_room_reservation_identity_type_id` (`identity_type_id`),
  KEY `ix_room_reservation_confirmation_code` (`confirmation_code`),
  KEY `ix_room_reservation_company_id` (`company_id`),
  KEY `ix_room_reservation_departure_date` (`departure_date`),
  KEY `ix_room_reservation_id` (`id`),
  KEY `ix_room_reservation_booking_status_id` (`booking_status_id`),
  KEY `ix_room_reservation_status` (`status`),
  KEY `ix_room_reservation_reservation_status` (`reservation_status`),
  KEY `ix_room_reservation_tax_type_id` (`tax_type_id`),
  KEY `ix_room_reservation_arrival_date` (`arrival_date`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_reservation`
--

LOCK TABLES `room_reservation` WRITE;
/*!40000 ALTER TABLE `room_reservation` DISABLE KEYS */;
INSERT INTO `room_reservation` VALUES (1,'RES-202609-0001','Mr.','Rohan','Mehta','rohan.mehta@gmail.com','+14155550001','2026-09-08','2026-09-11',3,1,'Checked-Out',1,'eee4665f-cd1a-4146-90e6-ea184da073b4.jpg','[1]','[1]','[\"101\"]','[\"daily\"]',3,1,'Welcome Drink','',3,1,10500.00,0.00,12.000,1134.00,10.000,1050.00,10584.00,4,10584.00,10584.00,0.00,0.00,0,0.00,10500.00,NULL,'RESERVATION','78363BE5','83047c96-a1b5-43fd-b04e-e950bbb9a561','ACTIVE','1','2026-09-04 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(2,'RES-202609-0002','Ms.','Priya','Nair','priya.nair@gmail.com','+442079460002','2026-09-12','2026-09-16',4,1,'Checked-Out',1,'abe75eb4-e58f-41d4-8be7-4782d19be80a.jpg','[11]','[2]','[\"203\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','Airport Pickup',3,6,22400.00,1200.00,12.000,2832.00,0.000,0.00,26432.00,2,26432.00,26432.00,0.00,0.00,0,0.00,22400.00,NULL,'RESERVATION','787F17E7','206a0ca4-d09e-4dae-a9be-e6ea9780138a','ACTIVE','1','2026-09-07 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(3,'RES-202609-0003','Mr.','Arjun','Kapoor','arjun.kapoor@gmail.com','+971501000003','2026-09-15','2026-09-20',5,1,'Checked-Out',5,'1c9abd95-c2d2-4c11-9f34-e36a05de7467.jpg','[15]','[3]','[\"301\"]','[\"half_board\"]',3,0,'','Evening Tea',4,2,42500.00,0.00,18.000,7267.50,15.000,7125.00,47642.50,6,47642.50,47642.50,0.00,0.00,1,5000.00,42500.00,NULL,'RESERVATION','5DBFA30A','27b47d2f-4a9a-4ba5-8cff-2f80bfdc17cb','ACTIVE','1','2026-09-09 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(4,'RES-202609-0004','Mrs.','Sana','Sheikh','sana.sheikh@gmail.com','+919876500004','2026-09-18','2026-09-20',2,1,'Checked-Out',2,'fc147eac-f5bc-4f3b-934f-ce8abdd49666.jpg','[20]','[4]','[\"401\"]','[\"daily\"]',2,1,'Fruit Basket','',4,3,17000.00,850.00,18.000,3052.35,5.000,892.50,20009.85,1,20009.85,20009.85,0.00,0.00,0,0.00,17000.00,NULL,'RESERVATION','1F381184','1cf6802d-e216-4582-8882-664993e5f208','ACTIVE','1','2026-09-11 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(5,'RES-202609-0005','Mr.','Vikram','Rao','vikram.rao@gmail.com','+14155550005','2026-09-20','2026-09-23',3,2,'Checked-Out',3,'85bd0f07-b10e-4234-92cb-aca044361ce5.jpg','[2, 3]','[1, 1]','[\"102\", \"103\"]','[\"daily\", \"daily\"]',3,2,'','Newspaper',3,4,21000.00,0.00,12.000,2016.00,20.000,4200.00,18816.00,4,18816.00,18816.00,0.00,0.00,0,0.00,21000.00,NULL,'RESERVATION','A216006C','8bbe0327-08f3-4aaa-b7d8-14e34189e322','ACTIVE','1','2026-09-12 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(6,'RES-202609-0006','Ms.','Neha','Gupta','neha.gupta@gmail.com','+442079460006','2026-09-22','2026-09-26',4,1,'Checked-Out',1,'87fea35e-8ccc-48a9-b452-047d3513a7a3.jpg','[24]','[6]','[\"502\"]','[\"full_board\"]',2,0,'Late Checkout','Spa',4,6,82000.00,3400.00,18.000,17532.00,0.000,0.00,114932.00,2,114932.00,114932.00,0.00,0.00,2,6000.00,82000.00,NULL,'RESERVATION','89ABA528','638ecd13-23b9-4c7e-8b07-5d1e8008dda1','ACTIVE','1','2026-09-13 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(7,'RES-202609-0007','Mr.','Karan','Malhotra','karan.malhotra@gmail.com','+971501000007','2026-09-27','2026-10-03',6,1,'Checked-In',4,'dffb9f26-8400-4685-b23e-a2616e919339.jpg','[9]','[2]','[\"201\"]','[\"bed_breakfast\"]',3,1,'Breakfast Buffet','',3,6,33600.00,0.00,12.000,4032.00,0.000,0.00,37632.00,4,18816.00,18816.00,18816.00,0.00,0,0.00,33600.00,NULL,'CHECKIN','0E1F3550','1e35ac90-5740-46f9-a079-70d655739419','ACTIVE','1','2026-09-17 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(8,'RES-202609-0008','Ms.','Ananya','Iyer','ananya.iyer@gmail.com','+919876500008','2026-09-28','2026-10-03',5,1,'Checked-In',1,'af2c9f73-684d-44a3-9900-94729640debf.jpg','[16]','[3]','[\"302\"]','[\"daily\"]',2,2,'','Conference Hall',4,2,34000.00,1500.00,18.000,5431.50,15.000,5325.00,35606.50,7,21363.90,21363.90,14242.60,0.00,0,0.00,34000.00,NULL,'CHECKIN','6820FA90','e45e068d-9a97-4e8d-b7b2-09a90cb00110','ACTIVE','1','2026-09-17 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(9,'RES-202609-0009','Mr.','Farhan','Khan','farhan.khan@gmail.com','+14155550009','2026-09-26','2026-10-04',8,1,'Checked-In',2,'e505dfb2-c2cd-47c0-8c18-e96ee466d8b0.jpg','[21]','[4]','[\"402\"]','[\"weekly\"]',3,0,'Welcome Drink','',4,5,59500.00,0.00,18.000,10945.44,12.000,8292.00,71753.44,6,25113.70,25113.70,46639.74,0.00,1,9600.00,59500.00,NULL,'CHECKIN','09219774','bf8ad630-879c-4648-b7ec-cf607ba0dfb5','ACTIVE','1','2026-09-23 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(10,'RES-202609-0010','Ms.','Divya','Menon','divya.menon@gmail.com','+442079460010','2026-09-29','2026-10-03',4,1,'Checked-In',1,'8d6de461-8b0c-4207-a4a7-5df315856ec3.jpg','[4]','[1]','[\"104\"]','[\"daily\"]',2,1,'','',3,3,14000.00,0.00,12.000,1596.00,5.000,700.00,14896.00,1,14896.00,14896.00,0.00,0.00,0,0.00,14000.00,NULL,'CHECKIN','BF81E99C','ca94ce8e-381e-4143-ba4a-8d7867b6a1fb','ACTIVE','1','2026-09-25 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(11,'RES-202609-0011','Mr.','Aditya','Verma','aditya.verma@gmail.com','+971501000011','2026-09-28','2026-09-30',2,1,'Checked-In',6,'f8aaa469-4ac2-4586-ae55-5e6434c7cacf.jpg','[13]','[2]','[\"205\"]','[\"bed_breakfast\"]',3,2,'Breakfast Buffet','',3,6,11200.00,620.00,12.000,1418.40,0.000,0.00,13238.40,4,9266.88,9266.88,3971.52,0.00,0,0.00,11200.00,NULL,'CHECKIN','FDF68311','a53ea854-a377-48bc-aadc-f5cd25afe95f','ACTIVE','1','2026-09-23 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(12,'RES-202609-0012','Ms.','Ritu','Chawla','ritu.chawla@gmail.com','+919876500012','2026-09-25','2026-09-30',5,1,'Checked-In',5,'93f9e339-d6e7-40c2-9e8f-515541491352.jpg','[17]','[3]','[\"303\"]','[\"half_board\"]',2,0,'','Evening Tea',4,1,42500.00,0.00,18.000,6885.00,10.000,4250.00,45135.00,2,33851.25,33851.25,11283.75,0.00,0,0.00,42500.00,NULL,'CHECKIN','DDE267EA','df0509f3-f7b7-4af4-95be-fc8ef1a1afcd','ACTIVE','1','2026-09-19 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(13,'RES-202609-0013','Mr.','Suresh','Pillai','suresh.pillai@gmail.com','+14155550013','2026-09-30','2026-10-02',2,1,'Confirmed',1,'af59b51b-104e-4e4c-866e-28651577433d.jpg','[5]','[1]','[\"105\"]','[\"daily\"]',3,1,'Welcome Drink','',3,6,7000.00,0.00,12.000,840.00,0.000,0.00,7840.00,4,1960.00,1960.00,5880.00,0.00,0,0.00,7000.00,NULL,'RESERVATION','B712C0C0','17cd1e59-1142-4a38-ada0-87cc9c227937','ACTIVE','1','2026-09-23 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(14,'RES-202609-0014','Ms.','Meera','Desai','meera.desai@gmail.com','+442079460014','2026-09-30','2026-10-03',3,1,'Confirmed',3,'646895db-b856-48a0-9ef0-40afd21c6c62.jpg','[14]','[2]','[\"206\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','Airport Pickup',3,1,16800.00,0.00,12.000,1814.40,10.000,1680.00,16934.40,2,5080.32,5080.32,11854.08,0.00,0,0.00,16800.00,NULL,'RESERVATION','B7E0C2BB','32e07f8f-2901-4b87-9244-287afc58a4a9','ACTIVE','1','2026-09-22 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(15,'RES-202609-0015','Mr.','Ibrahim','Ansari','ibrahim.ansari@gmail.com','+971501000015','2026-09-30','2026-10-04',4,1,'Confirmed',2,'e57da1d6-0c88-4b23-bc21-2f6cf2125697.jpg','[25]','[7]','[\"601\"]','[\"full_board\"]',3,0,'Fruit Basket','Spa',4,2,122000.00,5000.00,18.000,19431.00,15.000,19050.00,127381.00,6,63690.50,63690.50,63690.50,0.00,0,0.00,122000.00,NULL,'RESERVATION','24C6A04E','1dd0d3cd-a64a-46dd-8f12-bb84ab533689','ACTIVE','1','2026-09-21 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(16,'RES-202609-0016','Ms.','Lakshmi','Krishnan','lakshmi.krishnan@gmail.com','+919876500016','2026-10-03','2026-10-06',3,1,'Confirmed',1,'954f8b77-e3c1-4caf-af3f-335ed77a9f2b.jpg','[18]','[3]','[\"304\"]','[\"daily\"]',2,1,'','',4,6,20400.00,0.00,18.000,3672.00,0.000,0.00,24072.00,4,4814.40,4814.40,19257.60,0.00,0,0.00,20400.00,NULL,'RESERVATION','36DB532C','26b12a4d-b4c3-41a7-955f-792050ba360c','ACTIVE','1','2026-09-23 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(17,'RES-202609-0017','Mr.','Yusuf','Sheikh','yusuf.sheikh@gmail.com','+14155550017','2026-10-05','2026-10-07',2,2,'Confirmed',4,'dc90cf51-6ea7-45e7-85e7-7418fb90546a.jpg','[6, 7]','[1, 1]','[\"106\", \"107\"]','[\"daily\", \"daily\"]',3,2,'Welcome Drink','',3,4,14000.00,0.00,12.000,1344.00,20.000,2800.00,12544.00,1,0.00,0.00,12544.00,0.00,0,0.00,14000.00,NULL,'RESERVATION','9B313559','925ba805-b988-4348-b0fd-266d4069ce17','ACTIVE','1','2026-09-24 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(18,'RES-202609-0018','Ms.','Pooja','Bhatt','pooja.bhatt@gmail.com','+442079460018','2026-10-08','2026-10-13',5,1,'Confirmed',1,'01cfca94-e7e2-43e4-ab64-9a0d1ed278b5.jpg','[22]','[4]','[\"403\"]','[\"half_board\"]',2,0,'','Gymnasium',4,5,52500.00,0.00,18.000,9266.40,12.000,7020.00,60746.40,2,18223.92,18223.92,42522.48,0.00,1,6000.00,52500.00,NULL,'RESERVATION','A4ECE958','0c06cd9f-c957-4703-a8ef-d3a0a2567323','ACTIVE','1','2026-10-05 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(19,'RES-202609-0019','Mr.','Rithvik','Prabhu','rithvik.prabhu@gmail.com','+971501000019','2026-10-12','2026-10-16',4,1,'Confirmed',5,'488a9a63-b9e2-48a5-b696-7c5c0f01bec1.jpg','[23]','[5]','[\"501\"]','[\"full_board\"]',3,1,'Late Checkout','Spa',4,6,64000.00,2200.00,18.000,12780.00,0.000,0.00,83780.00,1,0.00,0.00,83780.00,0.00,1,4800.00,64000.00,NULL,'RESERVATION','E02CF9D5','42d846bb-205a-492e-932a-6661b626a2f1','ACTIVE','1','2026-10-08 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(20,'RES-202609-0020','Ms.','Kavya','Reddy','kavya.reddy@gmail.com','+919876500020','2026-10-16','2026-10-19',3,1,'Confirmed',1,'053d9b83-a036-49f4-8219-256f0ddb3dce.jpg','[10]','[2]','[\"202\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','',3,3,16800.00,0.00,12.000,1915.20,5.000,840.00,17875.20,1,0.00,0.00,17875.20,0.00,0,0.00,16800.00,NULL,'RESERVATION','0720E887','6110d2d8-c588-4f86-b1a2-6d93e2fcc86f','ACTIVE','1','2026-10-11 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(21,'RES-202609-0021','Mr.','Nikhil','Joshi','nikhil.joshi@gmail.com','+14155550021','2026-10-06','2026-10-09',3,1,'Cancelled',6,'7102be3f-4452-4644-b555-82a847588272.jpg','[19]','[3]','[\"305\"]','[\"daily\"]',3,0,'','',4,6,20400.00,0.00,18.000,3672.00,0.000,0.00,24072.00,1,0.00,0.00,24072.00,0.00,0,0.00,20400.00,NULL,'RESERVATION','15F70DB0','5da49d63-6cb6-46da-9117-0e39485b215f','ACTIVE','1','2026-09-30 10:30:00',NULL,NULL,'1','Guest request — travel plans changed','2026-10-04 15:40:00','1'),(22,'RES-202609-0022','Ms.','Fatima','Begum','fatima.begum@gmail.com','+442079460022','2026-10-09','2026-10-11',2,1,'Cancelled',2,'27df0d9e-2fac-42cf-81ea-e9f34aa3c096.jpg','[8]','[8]','[\"108\"]','[\"daily\"]',2,1,'','',3,6,2400.00,0.00,12.000,288.00,0.000,0.00,2688.00,4,537.60,537.60,2150.40,0.00,0,0.00,2400.00,NULL,'RESERVATION','60DDD8C7','65f8c660-9cc2-4a43-91ed-affdd3931cac','ACTIVE','1','2026-10-02 10:30:00',NULL,NULL,'1','Duplicate booking — kept RES on 106','2026-10-07 15:40:00','1'),(23,'RES-202609-0023','Mr.','Sandeep','Kulkarni','sandeep.kulkarni@gmail.com','+971501000023','2026-09-24','2026-09-26',2,1,'No-Show',3,'5ac677e7-de44-4027-b2fe-954ca8f40395.jpg','[12]','[2]','[\"204\"]','[\"daily\"]',3,2,'','',3,6,10400.00,0.00,12.000,1248.00,0.000,0.00,11648.00,1,0.00,0.00,11648.00,0.00,0,0.00,10400.00,NULL,'RESERVATION','24A58B45','b99493c1-171f-48e3-a4fc-ad90435436fc','ACTIVE','1','2026-09-16 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(24,'RES-202609-0024','Ms.','Anjali','Saxena','anjali.saxena@gmail.com','+919876500024','2026-10-20','2026-10-23',3,1,'Pending',1,NULL,'[15]','[3]','[\"301\"]','[\"daily\"]',2,0,'','',3,6,20400.00,0.00,12.000,2448.00,0.000,0.00,22848.00,1,0.00,0.00,22848.00,0.00,0,0.00,20400.00,NULL,'RESERVATION','61081D81','fceaabba-e918-4ba9-9077-10cc777fae93','ACTIVE','1','2026-10-11 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(25,'RES-202609-0025','Mr.','Arjun','Kapoor','arjun.kapoor@gmail.com','+14155550025','2026-10-25','2026-10-27',2,1,'On Hold',5,'6b13eb0f-e7f8-4346-9a2e-d720fbb11c5d.jpg','[20]','[4]','[\"401\"]','[\"daily\"]',3,1,'','',4,6,17000.00,0.00,18.000,3060.00,0.000,0.00,20060.00,1,0.00,0.00,20060.00,0.00,0,0.00,17000.00,NULL,'RESERVATION','F79502AD','54c2fc4a-f48c-46da-9aa6-6b6323cb5807','ACTIVE','1','2026-10-15 10:30:00',NULL,NULL,'1',NULL,NULL,NULL);
/*!40000 ALTER TABLE `room_reservation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `themes`
--

DROP TABLE IF EXISTS `themes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `themes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `primary_color` varchar(50) NOT NULL,
  `button_color` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_themes_primary_color` (`primary_color`),
  KEY `ix_themes_id` (`id`),
  KEY `ix_themes_company_id` (`company_id`),
  KEY `ix_themes_button_color` (`button_color`),
  KEY `ix_themes_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `themes`
--

LOCK TABLES `themes` WRITE;
/*!40000 ALTER TABLE `themes` DISABLE KEYS */;
/*!40000 ALTER TABLE `themes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'hotelerp_hotel'
--

--
-- Dumping routines for database 'hotelerp_hotel'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-30 19:32:41
