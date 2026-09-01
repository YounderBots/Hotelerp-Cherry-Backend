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
INSERT INTO `alembic_version` VALUES ('c4f1a7e93b52');
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
  `total_amount` float DEFAULT NULL,
  `tax_amount` float DEFAULT NULL,
  `discount_amount` float DEFAULT NULL,
  `laundry_amount` float DEFAULT NULL,
  `bar_amount` float DEFAULT NULL,
  `cafe_amount` float DEFAULT NULL,
  `restaurant_amount` float DEFAULT NULL,
  `special_services_amount` float DEFAULT NULL,
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
INSERT INTO `hotel_business_date` VALUES (1,'2026-09-01','2026-09-01 02:15:00','1','ACTIVE','1','2026-08-31 02:15:00','2026-09-01 02:15:00','1','1');
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
INSERT INTO `housekeeper_task` VALUES (1,'5','Imran','Khan','2026-09-01','09:00:00',101,'Deep Cleaning','Imran Khan','Pending','Not Ready',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(2,'6','Lakshmi','Iyer','2026-09-01','10:00:00',102,'Deep Cleaning','Lakshmi Iyer','Pending','Not Ready',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(3,'5','Imran','Khan','2026-09-01','11:00:00',103,'Deep Cleaning','Imran Khan','Pending','Not Ready',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(4,'6','Lakshmi','Iyer','2026-09-01','12:00:00',203,'Deep Cleaning','Lakshmi Iyer','Pending','Not Ready',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(5,'5','Imran','Khan','2026-09-01','09:00:00',301,'Deep Cleaning','Imran Khan','Pending','Not Ready',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(6,'6','Lakshmi','Iyer','2026-09-01','10:00:00',401,'Deep Cleaning','Lakshmi Iyer','Pending','Not Ready',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(7,'5','Imran','Khan','2026-09-01','11:00:00',502,'Deep Cleaning','Imran Khan','Pending','Not Ready',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(8,'5','Imran','Khan','2026-09-01','10:30:00',104,'Daily Cleaning','Imran Khan','Completed','Occupied',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(9,'6','Lakshmi','Iyer','2026-09-01','11:30:00',201,'Daily Cleaning','Lakshmi Iyer','In Progress','Occupied',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(10,'5','Imran','Khan','2026-09-01','12:30:00',205,'Daily Cleaning','Imran Khan','Completed','Occupied',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(11,'6','Lakshmi','Iyer','2026-09-01','13:30:00',302,'Daily Cleaning','Lakshmi Iyer','In Progress','Occupied',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(12,'5','Imran','Khan','2026-09-01','14:30:00',303,'Daily Cleaning','Imran Khan','Completed','Occupied',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1),(13,'6','Lakshmi','Iyer','2026-09-01','10:30:00',402,'Daily Cleaning','Lakshmi Iyer','In Progress','Occupied',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-09-01 08:30:00',NULL,NULL,1);
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
INSERT INTO `hsk_room_incident` VALUES (1,204,'2026-08-26','18:20:00','Bathroom tap dripping; floor wet on arrival.','Imran Khan','Medium','Duty Manager','Tap washer replaced, floor dried and room re-inspected.','Imran Khan','2026-08-26','a4174cdfbfa9446f96eeb9ca0ab07380.jpg','ACTIVE','1','2026-08-26 18:20:00',NULL,NULL,'1'),(2,302,'2026-08-29','09:05:00','Guest reported air conditioning not cooling.','Lakshmi Iyer','High','Duty Manager','Maintenance recharged the unit; guest confirmed satisfied.','Lakshmi Iyer','2026-08-29','4c53919635c4432db81b8526c82cdf5d.jpg','ACTIVE','1','2026-08-29 09:05:00',NULL,NULL,'1'),(3,108,'2026-08-31','21:40:00','Reading lamp shade cracked in dormitory bay 3.','Imran Khan','Low','Duty Manager','Shade replaced from stores; no charge raised to guest.','Imran Khan','2026-08-31','602966bc7a594cb19600317e7f526977.jpg','ACTIVE','1','2026-08-31 21:40:00',NULL,NULL,'1');
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
INSERT INTO `inquiry` VALUES (1,'Online','Deepak Anand','Asked for tariff on two Deluxe rooms in October.','Rate sheet emailed; awaiting confirmation.',NULL,'In Progress','ACTIVE','1','2026-08-31 11:00:00',NULL,NULL,'1'),(2,'Offline','Sridevi Raman','Walk-in asking about banquet hall for a reception.','Banquet manager to call back with availability.',NULL,'In Progress','ACTIVE','1','2026-08-30 11:00:00',NULL,NULL,'1'),(3,'Online','Michael Fernandes','Airport pickup availability for a late arrival.','Confirmed pickup can be arranged with 12 hours\' notice.',NULL,'Completed','ACTIVE','1','2026-08-29 11:00:00',NULL,NULL,'1'),(4,'Online','Aisha Rahman','Requested a quiet room away from the lift.','Noted on the booking; room 305 allocated.',NULL,'Completed','ACTIVE','1','2026-08-28 11:00:00',NULL,NULL,'1'),(5,'Offline','Ganesh Iyer','Corporate tie-up enquiry for monthly stays.','Corporate rate card shared with the company\'s admin.',NULL,'In Progress','ACTIVE','1','2026-08-27 11:00:00',NULL,NULL,'1'),(6,'Online','Sarah Thomas','Asked whether the pool is open to day guests.','Advised pool access is for in-house guests only.',NULL,'Completed','ACTIVE','1','2026-08-26 11:00:00',NULL,NULL,'1');
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
  `price` float NOT NULL,
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
  `net_price` float NOT NULL,
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
  `occupancy_percent` float DEFAULT NULL,
  `room_nights` int DEFAULT NULL,
  `arrivals_expected` int DEFAULT NULL,
  `arrivals_completed` int DEFAULT NULL,
  `departures_expected` int DEFAULT NULL,
  `departures_completed` int DEFAULT NULL,
  `in_house` int DEFAULT NULL,
  `stayovers` int DEFAULT NULL,
  `no_shows_marked` int DEFAULT NULL,
  `no_show_reservation_ids` json DEFAULT NULL,
  `room_revenue` float DEFAULT NULL,
  `extra_charges` float DEFAULT NULL,
  `tax_amount` float DEFAULT NULL,
  `discount_amount` float DEFAULT NULL,
  `gross_revenue` float DEFAULT NULL,
  `payments_collected` float DEFAULT NULL,
  `payment_breakdown` json DEFAULT NULL,
  `outstanding_balance` float DEFAULT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `night_audit`
--

LOCK TABLES `night_audit` WRITE;
/*!40000 ALTER TABLE `night_audit` DISABLE KEYS */;
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
  `amount` float NOT NULL,
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
INSERT INTO `reservation_amount_paid_history` VALUES (1,'RES-202609-0001','1',3175.2,'2026-07-27','UPI','91ba5da8-b184-4263-91c3-bf369b967111','ACTIVE','1','2026-07-27 12:15:00',NULL,NULL,'1'),(2,'RES-202609-0001','1',7408.8,'2026-08-13','Credit Card','edd9f22e-b27a-4969-9c74-ddbb347c58c7','ACTIVE','1','2026-08-13 12:15:00',NULL,NULL,'1'),(3,'RES-202609-0002','1',26432,'2026-08-14','Credit Card','40550333-bfb3-41dd-894b-bc45c86f1881','ACTIVE','1','2026-08-14 12:15:00',NULL,NULL,'1'),(4,'RES-202609-0003','1',23821.2,'2026-08-17','Bank Transfer','5498cb3e-42e4-4cc1-8f70-801e6981c862','ACTIVE','1','2026-08-17 12:15:00',NULL,NULL,'1'),(5,'RES-202609-0003','1',23821.2,'2026-08-22','Bank Transfer','3e22d4bb-6ca3-499c-8578-2e7d5fe7edc4','ACTIVE','1','2026-08-22 12:15:00',NULL,NULL,'1'),(6,'RES-202609-0004','1',20009.8,'2026-08-20','Cash','7f6c2834-0292-4eca-8aed-9880a663ecff','ACTIVE','1','2026-08-20 12:15:00',NULL,NULL,'1'),(7,'RES-202609-0005','1',7526.4,'2026-08-20','UPI','d9481a3c-03fc-4a63-9e00-48ba6801aa4d','ACTIVE','1','2026-08-20 12:15:00',NULL,NULL,'1'),(8,'RES-202609-0005','1',11289.6,'2026-08-25','Debit Card','363052c1-433e-4fb3-a49e-81d590353c2b','ACTIVE','1','2026-08-25 12:15:00',NULL,NULL,'1'),(9,'RES-202609-0006','1',114932,'2026-08-24','Credit Card','858a28b1-b158-4cf2-a9a0-f9a40b4f8389','ACTIVE','1','2026-08-24 12:15:00',NULL,NULL,'1'),(10,'RES-202609-0007','1',18816,'2026-08-29','UPI','3586b95f-cea9-47da-8904-e628f699c400','ACTIVE','1','2026-08-29 12:15:00',NULL,NULL,'1'),(11,'RES-202609-0008','1',21363.9,'2026-08-30','Corporate Billing','e7ba9f1d-9228-4ef3-8e07-db0931fa3786','ACTIVE','1','2026-08-30 12:15:00',NULL,NULL,'1'),(12,'RES-202609-0009','1',25113.7,'2026-08-28','Bank Transfer','c9663692-9e60-41ec-b9d6-d8038f4594e7','ACTIVE','1','2026-08-28 12:15:00',NULL,NULL,'1'),(13,'RES-202609-0010','1',14896,'2026-08-31','Cash','687b72c7-c82f-4856-9ed7-fac4f11abebc','ACTIVE','1','2026-08-31 12:15:00',NULL,NULL,'1'),(14,'RES-202609-0011','1',9266.88,'2026-08-30','UPI','39cc9959-f7fd-408a-92ab-5a02ad11e14e','ACTIVE','1','2026-08-30 12:15:00',NULL,NULL,'1'),(15,'RES-202609-0012','1',22567.5,'2026-08-27','Credit Card','0b82efb9-4070-41b3-a573-c332098f372d','ACTIVE','1','2026-08-27 12:15:00',NULL,NULL,'1'),(16,'RES-202609-0012','1',11283.8,'2026-08-31','UPI','6d7c1673-fd02-4845-bccf-a8f63ed570c1','ACTIVE','1','2026-08-31 12:15:00',NULL,NULL,'1'),(17,'RES-202609-0013','1',1960,'2026-09-01','UPI','8345a897-5227-4370-9162-ae79ff2d7534','ACTIVE','1','2026-09-01 12:15:00',NULL,NULL,'1'),(18,'RES-202609-0014','1',5080.32,'2026-08-27','Credit Card','b5b50be2-f0e7-4f22-a3ee-f681a5a29ad6','ACTIVE','1','2026-08-27 12:15:00',NULL,NULL,'1'),(19,'RES-202609-0015','1',63690.5,'2026-08-25','Bank Transfer','fb5771bf-d9f5-4d85-9b4d-6a417572c8cb','ACTIVE','1','2026-08-25 12:15:00',NULL,NULL,'1'),(20,'RES-202609-0016','1',4814.4,'2026-09-03','UPI','6cca12ba-79e3-48bf-9165-58ab2d932aa4','ACTIVE','1','2026-09-03 12:15:00',NULL,NULL,'1'),(21,'RES-202609-0018','1',18223.9,'2026-09-07','Credit Card','5e5ca6d0-94fc-4903-824a-6fab8ec6d095','ACTIVE','1','2026-09-07 12:15:00',NULL,NULL,'1'),(22,'RES-202609-0022','1',537.6,'2026-09-07','UPI','9aa4e4a1-4467-4bee-9498-0dd701cff63e','ACTIVE','1','2026-09-07 12:15:00',NULL,NULL,'1');
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
INSERT INTO `room_booking` VALUES (1,'RB-40DC9F2B','Mr.','Deepak','Anand','9840155501','deepak.anand@example.com','2026-10-01','2026-10-04',3,'[2, 2]',2,2,0,'ACTIVE','1','2026-08-30 16:20:00',NULL,NULL,'1'),(2,'RB-7178ACDA','Ms.','Sridevi','Raman','9840155502','sridevi.raman@example.com','2026-10-05','2026-10-07',2,'[5]',1,2,2,'ACTIVE','1','2026-08-30 16:20:00',NULL,NULL,'1'),(3,'RB-D7CD1EBA','Mr.','Ganesh','Iyer','9840155503','ganesh.iyer@example.com','2026-10-11','2026-10-16',5,'[4]',1,1,0,'ACTIVE','1','2026-08-30 16:20:00',NULL,NULL,'1');
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
  `extra_bed_cost` float DEFAULT NULL,
  `total_amount` float DEFAULT NULL,
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
  `room_amount` float DEFAULT NULL,
  `extra_charges` float DEFAULT NULL,
  `tax_percentage` float DEFAULT NULL,
  `tax_amount` float DEFAULT NULL,
  `discount_percentage` float DEFAULT NULL,
  `discount_amount` float DEFAULT NULL,
  `overall_amount` float DEFAULT NULL,
  `payment_method_id` int DEFAULT NULL,
  `paying_amount` float DEFAULT NULL,
  `paid_amount` float DEFAULT NULL,
  `balance_amount` float DEFAULT NULL,
  `extra_amount` float DEFAULT NULL,
  `extra_bed_count` int DEFAULT NULL,
  `extra_bed_cost` float DEFAULT NULL,
  `total_amount` float DEFAULT NULL,
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
INSERT INTO `room_reservation` VALUES (1,'RES-202609-0001','Mr.','Rohan','Mehta','rohan.mehta@example.com','9840000137','2026-08-10','2026-08-13',3,1,'Checked-Out',1,'dae58418-e91f-4cad-bb9c-9e0fdaef02a8.jpg','[1]','[1]','[\"101\"]','[\"daily\"]',3,1,'Welcome Drink','',3,1,10500,0,12,1134,10,1050,10584,4,10584,10584,0,0,0,0,10500,NULL,'RESERVATION','44202FF2','81873592-7617-4be3-9acf-191d7cc7c817','ACTIVE','1','2026-08-06 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(2,'RES-202609-0002','Ms.','Priya','Nair','priya.nair@example.com','9840000274','2026-08-14','2026-08-18',4,1,'Checked-Out',1,'2e2f085b-7a85-48ca-b2b9-a4e5eca1a8f4.jpg','[11]','[2]','[\"203\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','Airport Pickup',3,6,22400,1200,12,2832,0,0,26432,2,26432,26432,0,0,0,0,22400,NULL,'RESERVATION','D6D1986C','f8557458-a1de-4ee2-aa48-6702e8025f01','ACTIVE','1','2026-08-09 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(3,'RES-202609-0003','Mr.','Arjun','Kapoor','arjun.kapoor@example.com','9840000411','2026-08-17','2026-08-22',5,1,'Checked-Out',5,'5c9af39b-7d44-4f99-a424-929e04131431.jpg','[15]','[3]','[\"301\"]','[\"half_board\"]',3,0,'','Evening Tea',4,2,42500,0,18,7267.5,15,7125,47642.5,6,47642.5,47642.5,0,0,1,5000,42500,NULL,'RESERVATION','15B25CC7','fe00f859-32b2-4eac-9f6d-49cd0fc1aad1','ACTIVE','1','2026-08-11 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(4,'RES-202609-0004','Mrs.','Sana','Sheikh','sana.sheikh@example.com','9840000548','2026-08-20','2026-08-22',2,1,'Checked-Out',2,'99763810-9488-4f87-8c56-509858dfc4c0.jpg','[20]','[4]','[\"401\"]','[\"daily\"]',2,1,'Fruit Basket','',4,3,17000,850,18,3052.35,5,892.5,20009.8,1,20009.8,20009.8,0,0,0,0,17000,NULL,'RESERVATION','0B3E27C3','617654b4-914a-4370-b274-6d48e3a544d5','ACTIVE','1','2026-08-13 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(5,'RES-202609-0005','Mr.','Vikram','Rao','vikram.rao@example.com','9840000685','2026-08-22','2026-08-25',3,2,'Checked-Out',3,'733c8d21-d0eb-4b08-a07b-9a95aab4f206.jpg','[2, 3]','[1, 1]','[\"102\", \"103\"]','[\"daily\", \"daily\"]',3,2,'','Newspaper',3,4,21000,0,12,2016,20,4200,18816,4,18816,18816,0,0,0,0,21000,NULL,'RESERVATION','343097E5','dd51a019-7a65-41a5-9916-f0dc844763bc','ACTIVE','1','2026-08-14 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(6,'RES-202609-0006','Ms.','Neha','Gupta','neha.gupta@example.com','9840000822','2026-08-24','2026-08-28',4,1,'Checked-Out',1,'c811388c-ba48-41a4-b1c4-19e548d2da00.jpg','[24]','[6]','[\"502\"]','[\"full_board\"]',2,0,'Late Checkout','Spa',4,6,82000,3400,18,17532,0,0,114932,2,114932,114932,0,0,2,12000,82000,NULL,'RESERVATION','92CB1BB4','b694e701-b837-4a8e-98a7-bd5779678c41','ACTIVE','1','2026-08-15 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(7,'RES-202609-0007','Mr.','Karan','Malhotra','karan.malhotra@example.com','9840000959','2026-08-29','2026-09-04',6,1,'Checked-In',4,'5fd10d2b-c7a5-4bf7-bc1d-a94f6f24cbf7.jpg','[9]','[2]','[\"201\"]','[\"bed_breakfast\"]',3,1,'Breakfast Buffet','',3,6,33600,0,12,4032,0,0,37632,4,18816,18816,18816,0,0,0,33600,NULL,'CHECKIN','B3B2859D','23db0559-e96e-4173-92a6-32c067bcc57a','ACTIVE','1','2026-08-19 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(8,'RES-202609-0008','Ms.','Ananya','Iyer','ananya.iyer@example.com','9840001096','2026-08-30','2026-09-04',5,1,'Checked-In',1,'71d352a2-a877-42d1-bdec-b23ecef961c1.jpg','[16]','[3]','[\"302\"]','[\"daily\"]',2,2,'','Conference Hall',4,2,34000,1500,18,5431.5,15,5325,35606.5,7,21363.9,21363.9,14242.6,0,0,0,34000,NULL,'CHECKIN','80491342','99e160eb-7094-4894-9ba8-f76da487d842','ACTIVE','1','2026-08-19 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(9,'RES-202609-0009','Mr.','Farhan','Khan','farhan.khan@example.com','9840001233','2026-08-28','2026-09-05',8,1,'Checked-In',2,'19a7f98c-23b0-4aec-bef1-7bbafad0f335.jpg','[21]','[4]','[\"402\"]','[\"weekly\"]',3,0,'Welcome Drink','',4,5,59500,0,18,10945.4,12,8292,71753.4,6,25113.7,25113.7,46639.7,0,1,9600,59500,NULL,'CHECKIN','5A84B038','d65d4901-19f4-4b5f-a2eb-ecebba3e1f08','ACTIVE','1','2026-08-25 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(10,'RES-202609-0010','Ms.','Divya','Menon','divya.menon@example.com','9840001370','2026-08-31','2026-09-04',4,1,'Checked-In',1,'956c802c-275f-4801-8bb8-6830c60ad93f.jpg','[4]','[1]','[\"104\"]','[\"daily\"]',2,1,'','',3,3,14000,0,12,1596,5,700,14896,1,14896,14896,0,0,0,0,14000,NULL,'CHECKIN','A9182759','afd112ec-d591-4cb3-bc09-b42143001e7e','ACTIVE','1','2026-08-27 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(11,'RES-202609-0011','Mr.','Aditya','Verma','aditya.verma@example.com','9840001507','2026-08-30','2026-09-01',2,1,'Checked-In',6,'dc34dac7-c1e2-4665-ad5e-e27f256c387d.jpg','[13]','[2]','[\"205\"]','[\"bed_breakfast\"]',3,2,'Breakfast Buffet','',3,6,11200,620,12,1418.4,0,0,13238.4,4,9266.88,9266.88,3971.52,0,0,0,11200,NULL,'CHECKIN','AE8486FD','78833760-8d4e-4559-ba9f-1139ccc47ec6','ACTIVE','1','2026-08-25 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(12,'RES-202609-0012','Ms.','Ritu','Chawla','ritu.chawla@example.com','9840001644','2026-08-27','2026-09-01',5,1,'Checked-In',5,'e3625dc2-9f82-4c94-a349-add0344caac2.jpg','[17]','[3]','[\"303\"]','[\"half_board\"]',2,0,'','Evening Tea',4,1,42500,0,18,6885,10,4250,45135,2,33851.2,33851.2,11283.8,0,0,0,42500,NULL,'CHECKIN','9C818FEC','f612d3e2-1565-4dc8-abbc-b8656c05ab25','ACTIVE','1','2026-08-21 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(13,'RES-202609-0013','Mr.','Suresh','Pillai','suresh.pillai@example.com','9840001781','2026-09-01','2026-09-03',2,1,'Confirmed',1,'c3bfe0ab-e625-4219-a4d4-7649555f0cdd.jpg','[5]','[1]','[\"105\"]','[\"daily\"]',3,1,'Welcome Drink','',3,6,7000,0,12,840,0,0,7840,4,1960,1960,5880,0,0,0,7000,NULL,'RESERVATION','5411751B','6086f63d-8d4b-475a-94bb-03fd80b5940a','ACTIVE','1','2026-08-25 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(14,'RES-202609-0014','Ms.','Meera','Desai','meera.desai@example.com','9840001918','2026-09-01','2026-09-04',3,1,'Confirmed',3,'993b83b4-4f44-433c-a66d-122f8badc451.jpg','[14]','[2]','[\"206\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','Airport Pickup',3,1,16800,0,12,1814.4,10,1680,16934.4,2,5080.32,5080.32,11854.1,0,0,0,16800,NULL,'RESERVATION','60D850C3','5ed2a6a2-b1da-4b03-988f-023a6e07b219','ACTIVE','1','2026-08-24 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(15,'RES-202609-0015','Mr.','Ibrahim','Ansari','ibrahim.ansari@example.com','9840002055','2026-09-01','2026-09-05',4,1,'Confirmed',2,'09f7e709-4d13-4d41-8e2f-61135006725c.jpg','[25]','[7]','[\"601\"]','[\"full_board\"]',3,0,'Fruit Basket','Spa',4,2,122000,5000,18,19431,15,19050,127381,6,63690.5,63690.5,63690.5,0,0,0,122000,NULL,'RESERVATION','94CBC6F7','4b7aff42-4393-4a55-9a38-d0abd023e2d4','ACTIVE','1','2026-08-23 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(16,'RES-202609-0016','Ms.','Lakshmi','Krishnan','lakshmi.krishnan@example.com','9840002192','2026-09-04','2026-09-07',3,1,'Confirmed',1,'c719d460-ed9a-448c-8573-01f3780235ce.jpg','[18]','[3]','[\"304\"]','[\"daily\"]',2,1,'','',4,6,20400,0,18,3672,0,0,24072,4,4814.4,4814.4,19257.6,0,0,0,20400,NULL,'RESERVATION','95906898','65f47b2f-05f0-4bc4-a311-b49e86c0e60a','ACTIVE','1','2026-08-25 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(17,'RES-202609-0017','Mr.','Yusuf','Sheikh','yusuf.sheikh@example.com','9840002329','2026-09-06','2026-09-08',2,2,'Confirmed',4,'03b547d8-846e-4686-ac79-d052081d9157.jpg','[6, 7]','[1, 1]','[\"106\", \"107\"]','[\"daily\", \"daily\"]',3,2,'Welcome Drink','',3,4,14000,0,12,1344,20,2800,12544,1,0,0,12544,0,0,0,14000,NULL,'RESERVATION','A3C6661F','d4cfe601-a5c9-4364-ab0d-6ffc99ef8904','ACTIVE','1','2026-08-26 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(18,'RES-202609-0018','Ms.','Pooja','Bhatt','pooja.bhatt@example.com','9840002466','2026-09-09','2026-09-14',5,1,'Confirmed',1,'e5152b59-2eab-40f2-9678-12b8e642f1ba.jpg','[22]','[4]','[\"403\"]','[\"half_board\"]',2,0,'','Gymnasium',4,5,52500,0,18,9266.4,12,7020,60746.4,2,18223.9,18223.9,42522.5,0,1,6000,52500,NULL,'RESERVATION','A95B0B50','6c536fe1-627e-4a9a-9242-8258257f72f4','ACTIVE','1','2026-09-06 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(19,'RES-202609-0019','Mr.','Rithvik','Prabhu','rithvik.prabhu@example.com','9840002603','2026-09-13','2026-09-17',4,1,'Confirmed',5,'af1ca74b-2c69-42f9-a337-aa7f1f883b93.jpg','[23]','[5]','[\"501\"]','[\"full_board\"]',3,1,'Late Checkout','Spa',4,6,64000,2200,18,12780,0,0,83780,1,0,0,83780,0,1,4800,64000,NULL,'RESERVATION','29D6E2B9','0c356ae6-9bdb-4f9a-8162-ca20255787f0','ACTIVE','1','2026-09-09 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(20,'RES-202609-0020','Ms.','Kavya','Reddy','kavya.reddy@example.com','9840002740','2026-09-17','2026-09-20',3,1,'Confirmed',1,'46b2dfea-4359-4ed3-b1cb-04c50d0b2872.jpg','[10]','[2]','[\"202\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','',3,3,16800,0,12,1915.2,5,840,17875.2,1,0,0,17875.2,0,0,0,16800,NULL,'RESERVATION','E166225D','e13a1ff7-7e0d-4a6c-8345-1e22e62c1461','ACTIVE','1','2026-09-12 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(21,'RES-202609-0021','Mr.','Nikhil','Joshi','nikhil.joshi@example.com','9840002877','2026-09-07','2026-09-10',3,1,'Cancelled',6,'a057d963-127d-4199-a51d-fb403e48ae90.jpg','[19]','[3]','[\"305\"]','[\"daily\"]',3,0,'','',4,6,20400,0,18,3672,0,0,24072,1,0,0,24072,0,0,0,20400,NULL,'RESERVATION','764ED476','fc120843-c741-4710-b676-e360dcc6c286','ACTIVE','1','2026-09-01 10:30:00',NULL,NULL,'1','Guest request — travel plans changed','2026-09-05 15:40:00','1'),(22,'RES-202609-0022','Ms.','Fatima','Begum','fatima.begum@example.com','9840003014','2026-09-10','2026-09-12',2,1,'Cancelled',2,'b3566956-925f-4849-bc6a-1ae460e9fc1c.jpg','[8]','[8]','[\"108\"]','[\"daily\"]',2,1,'','',3,6,2400,0,12,288,0,0,2688,4,537.6,537.6,2150.4,0,0,0,2400,NULL,'RESERVATION','ABF87A60','30199e30-e051-473a-a679-6cd27c2dde34','ACTIVE','1','2026-09-03 10:30:00',NULL,NULL,'1','Duplicate booking — kept RES on 106','2026-09-08 15:40:00','1'),(23,'RES-202609-0023','Mr.','Sandeep','Kulkarni','sandeep.kulkarni@example.com','9840003151','2026-08-26','2026-08-28',2,1,'No-Show',3,'ab5f4bb9-9408-4694-856e-346a2c757bdc.jpg','[12]','[2]','[\"204\"]','[\"daily\"]',3,2,'','',3,6,10400,0,12,1248,0,0,11648,1,0,0,11648,0,0,0,10400,NULL,'RESERVATION','61E2F580','27d68428-8417-4b61-af2d-4ee52f5b3e86','ACTIVE','1','2026-08-18 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(24,'RES-202609-0024','Ms.','Anjali','Saxena','anjali.saxena@example.com','9840003288','2026-09-21','2026-09-24',3,1,'Pending',1,NULL,'[15]','[3]','[\"301\"]','[\"daily\"]',2,0,'','',3,6,20400,0,12,2448,0,0,22848,1,0,0,22848,0,0,0,20400,NULL,'RESERVATION','718AD534','13d400b7-f43d-4ed8-8ac2-ee5715fcc402','ACTIVE','1','2026-09-12 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(25,'RES-202609-0025','Mr.','Arjun','Kapoor','arjun.kapoor@example.com','9840003425','2026-09-26','2026-09-28',2,1,'On Hold',5,'c772b7dd-d33f-48ee-abe6-1d9b3881b0ce.jpg','[20]','[4]','[\"401\"]','[\"daily\"]',3,1,'','',4,6,17000,0,18,3060,0,0,20060,1,0,0,20060,0,0,0,17000,NULL,'RESERVATION','B8C1E80A','0272fb2b-bcf8-4d2e-8002-405770de0c5a','ACTIVE','1','2026-09-16 10:30:00',NULL,NULL,'1',NULL,NULL,NULL);
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

-- Dump completed on 2026-09-01 19:57:07
