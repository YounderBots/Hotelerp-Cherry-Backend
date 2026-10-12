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
INSERT INTO `hotel_business_date` VALUES (1,'2026-10-10','2026-10-10 02:15:00','1','ACTIVE','1','2026-10-09 02:15:00','2026-10-10 02:15:00','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `housekeeper_task`
--

LOCK TABLES `housekeeper_task` WRITE;
/*!40000 ALTER TABLE `housekeeper_task` DISABLE KEYS */;
INSERT INTO `housekeeper_task` VALUES (1,'5','Imran','Khan','2026-10-10','09:00:00',1,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(2,'6','Lakshmi','Iyer','2026-10-10','10:00:00',2,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(3,'5','Imran','Khan','2026-10-10','11:00:00',3,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(4,'6','Lakshmi','Iyer','2026-10-10','12:00:00',11,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(5,'5','Imran','Khan','2026-10-10','09:00:00',15,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(6,'6','Lakshmi','Iyer','2026-10-10','10:00:00',20,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(7,'5','Imran','Khan','2026-10-10','11:00:00',24,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(8,'5','Imran','Khan','2026-10-10','10:30:00',4,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(9,'6','Lakshmi','Iyer','2026-10-10','11:30:00',9,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(10,'5','Imran','Khan','2026-10-10','12:30:00',13,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(11,'6','Lakshmi','Iyer','2026-10-10','13:30:00',16,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(12,'5','Imran','Khan','2026-10-10','14:30:00',17,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(13,'6','Lakshmi','Iyer','2026-10-10','10:30:00',21,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-10 08:30:00',NULL,NULL,1),(14,'10','Ops','Test','2026-10-11','10:00:00',25,'Pest Control','10','Completed','Blocking',NULL,'flow test','INACTIVE',1,'2026-10-11 20:00:07','2026-10-11 20:00:07',1,1),(15,'10','Ops','Test','2026-10-11','10:00:00',25,'Pest Control','10','Completed','Blocking',NULL,'flow test','INACTIVE',1,'2026-10-11 20:04:23','2026-10-11 20:04:24',1,1),(46,'10','Meera','Krishnan','2026-01-26','07:00:00',25,'Pest Control','10','Pending','Blocking','ZZTA note',NULL,'ACTIVE',1,'2026-10-11 22:43:29',NULL,NULL,1),(51,'10','Ops','Test','2026-10-12','10:00:00',25,'Pest Control','10','Completed','Blocking',NULL,'flow test','INACTIVE',1,'2026-10-12 14:16:52','2026-10-12 14:16:53',1,1),(52,'10','Ops','Test','2026-10-12','10:00:00',25,'Pest Control','10','Completed','Blocking',NULL,'flow test','INACTIVE',1,'2026-10-12 14:20:49','2026-10-12 14:20:49',1,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hsk_room_incident`
--

LOCK TABLES `hsk_room_incident` WRITE;
/*!40000 ALTER TABLE `hsk_room_incident` DISABLE KEYS */;
INSERT INTO `hsk_room_incident` VALUES (1,12,'2026-10-04','18:20:00','Bathroom tap dripping; floor wet on arrival.','Imran Khan','Medium','Duty Manager','Tap washer replaced, floor dried and room re-inspected.','Imran Khan','2026-10-04','/templates/static/room_incidents/f6db23a7231c492db8c7ec279a9277aa.jpg','ACTIVE','1','2026-10-04 18:20:00',NULL,NULL,'1'),(2,16,'2026-10-07','09:05:00','Guest reported air conditioning not cooling.','Lakshmi Iyer','High','Duty Manager','Maintenance recharged the unit; guest confirmed satisfied.','Lakshmi Iyer','2026-10-07','/templates/static/room_incidents/40222b14f5e34bad9a81c188d19b38dd.jpg','ACTIVE','1','2026-10-07 09:05:00',NULL,NULL,'1'),(3,8,'2026-10-09','21:40:00','Reading lamp shade cracked in dormitory bay 3.','Imran Khan','Low','Duty Manager','Shade replaced from stores; no charge raised to guest.','Imran Khan','2026-10-09','/templates/static/room_incidents/aa48a61fbd884ee0b2a683d237dc1363.jpg','ACTIVE','1','2026-10-09 21:40:00',NULL,NULL,'1'),(4,25,'2026-10-11','12:30:00','Flow test incident','Ops Test','Low','none','escalated','10','2026-10-11','/templates/static/room_incidents/cd660c67076246ca8227af3925dc6c4a.png','INACTIVE','1','2026-10-11 20:00:08','2026-10-11 20:00:08','1','1'),(5,25,'2026-10-11','12:30:00','Flow test incident','Ops Test','Low','none','escalated','10','2026-10-11','/templates/static/room_incidents/a7d5dbbb6dd740f481511d90295e3866.png','INACTIVE','1','2026-10-11 20:04:24','2026-10-11 20:04:25','1','1'),(26,25,'2026-10-12','12:30:00','Flow test incident','Ops Test','Low','none','escalated','10','2026-10-12','/templates/static/room_incidents/748044844ed2406a99700c572a674e06.png','INACTIVE','1','2026-10-12 14:16:53','2026-10-12 14:16:53','1','1'),(27,25,'2026-10-12','12:30:00','Flow test incident','Ops Test','Low','none','escalated','10','2026-10-12','/templates/static/room_incidents/75b7b3c773d547e1852aae96561fa6dc.png','INACTIVE','1','2026-10-12 14:20:49','2026-10-12 14:20:49','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inquiry`
--

LOCK TABLES `inquiry` WRITE;
/*!40000 ALTER TABLE `inquiry` DISABLE KEYS */;
INSERT INTO `inquiry` VALUES (1,'Online','Deepak Anand','Asked for tariff on two Deluxe rooms in October.','Rate sheet emailed; awaiting confirmation.',NULL,'In Progress','ACTIVE','1','2026-10-09 11:00:00',NULL,NULL,'1'),(2,'Offline','Sridevi Raman','Walk-in asking about banquet hall for a reception.','Banquet manager to call back with availability.',NULL,'In Progress','ACTIVE','1','2026-10-08 11:00:00',NULL,NULL,'1'),(3,'Online','Michael Fernandes','Airport pickup availability for a late arrival.','Confirmed pickup can be arranged with 12 hours\' notice.',NULL,'Completed','ACTIVE','1','2026-10-07 11:00:00',NULL,NULL,'1'),(4,'Online','Aisha Rahman','Requested a quiet room away from the lift.','Noted on the booking; room 305 allocated.',NULL,'Completed','ACTIVE','1','2026-10-06 11:00:00',NULL,NULL,'1'),(5,'Offline','Ganesh Iyer','Corporate tie-up enquiry for monthly stays.','Corporate rate card shared with the company\'s admin.',NULL,'In Progress','ACTIVE','1','2026-10-05 11:00:00',NULL,NULL,'1'),(6,'Online','Sarah Thomas','Asked whether the pool is open to day guests.','Advised pool access is for in-house guests only.',NULL,'Completed','ACTIVE','1','2026-10-04 11:00:00',NULL,NULL,'1'),(7,'Online','Ops Tester','Handled',NULL,NULL,'Completed','INACTIVE','1','2026-10-11 20:00:08','2026-10-11 20:00:08','1','1'),(8,'Online','Ops Tester','Handled',NULL,NULL,'Completed','INACTIVE','1','2026-10-11 20:04:25','2026-10-11 20:04:25','1','1'),(10,'Online','Ops Tester','Handled',NULL,NULL,'Completed','INACTIVE','1','2026-10-12 14:16:53','2026-10-12 14:16:54','1','1'),(11,'Online','Ops Tester','Handled',NULL,NULL,'Completed','INACTIVE','1','2026-10-12 14:20:49','2026-10-12 14:20:49','1','1');
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
INSERT INTO `night_audit` VALUES (1,'NA-20261009','2026-10-09','2026-10-10','Completed','2026-10-10 02:10:00','2026-10-10 02:15:00','1',NULL,25,7,28.000,6,1,1,0,0,6,6,0,'[]',37437.50,610.00,5611.68,3126.50,40532.68,26179.75,'[{\"amount\": 14896.0, \"payment_method\": \"Cash\"}, {\"amount\": 11283.75, \"payment_method\": \"UPI\"}]',94953.61,'82227f24-203b-483e-8bd6-f78363719939','ACTIVE','1','2026-10-10 02:15:00','2026-10-10 02:15:00','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_amount_paid_history`
--

LOCK TABLES `reservation_amount_paid_history` WRITE;
/*!40000 ALTER TABLE `reservation_amount_paid_history` DISABLE KEYS */;
INSERT INTO `reservation_amount_paid_history` VALUES (1,'RES-202610-0001','1',3175.20,'2026-09-04','UPI','8eb8e928-c562-4089-aa35-429508bcf809','ACTIVE','1','2026-09-04 12:15:00',NULL,NULL,'1'),(2,'RES-202610-0001','1',7408.80,'2026-09-21','Credit Card','777ee382-18ec-4f47-9f69-32fa30ab1483','ACTIVE','1','2026-09-21 12:15:00',NULL,NULL,'1'),(3,'RES-202610-0002','1',26432.00,'2026-09-22','Credit Card','4da6e11e-8f29-4e19-85fc-ce0cd6c87268','ACTIVE','1','2026-09-22 12:15:00',NULL,NULL,'1'),(4,'RES-202610-0003','1',23821.25,'2026-09-25','Bank Transfer','872709a4-ec25-4012-85de-31c4e5c9816d','ACTIVE','1','2026-09-25 12:15:00',NULL,NULL,'1'),(5,'RES-202610-0003','1',23821.25,'2026-09-30','Bank Transfer','c094817f-675e-4435-9ae5-397bff9d8c69','ACTIVE','1','2026-09-30 12:15:00',NULL,NULL,'1'),(6,'RES-202610-0004','1',20009.85,'2026-09-28','Cash','95fb73aa-2b6c-469e-bb23-e6e43d361860','ACTIVE','1','2026-09-28 12:15:00',NULL,NULL,'1'),(7,'RES-202610-0005','1',7526.40,'2026-09-28','UPI','c01e0c4f-0bd8-4839-87b9-ede18694890f','ACTIVE','1','2026-09-28 12:15:00',NULL,NULL,'1'),(8,'RES-202610-0005','1',11289.60,'2026-10-03','Debit Card','3f7b9b8c-9c28-4bd3-b5ff-bf02f1d60231','ACTIVE','1','2026-10-03 12:15:00',NULL,NULL,'1'),(9,'RES-202610-0006','1',114932.00,'2026-10-02','Credit Card','fc004ca8-d368-45d1-9c04-f9f5edc723cb','ACTIVE','1','2026-10-02 12:15:00',NULL,NULL,'1'),(10,'RES-202610-0007','1',18816.00,'2026-10-07','UPI','5fb1d286-2689-480c-8ed9-3f4cc34b270c','ACTIVE','1','2026-10-07 12:15:00',NULL,NULL,'1'),(11,'RES-202610-0008','1',21363.90,'2026-10-08','Corporate Billing','29b4777f-5d79-408b-93c0-0374599969ce','ACTIVE','1','2026-10-08 12:15:00',NULL,NULL,'1'),(12,'RES-202610-0009','1',25113.70,'2026-10-06','Bank Transfer','b4f063d9-80e0-429a-8c9e-cfd1077257eb','ACTIVE','1','2026-10-06 12:15:00',NULL,NULL,'1'),(13,'RES-202610-0010','1',14896.00,'2026-10-09','Cash','f603298a-0d63-4201-9fa3-6c3abc7bf0f5','ACTIVE','1','2026-10-09 12:15:00',NULL,NULL,'1'),(14,'RES-202610-0011','1',9266.88,'2026-10-08','UPI','aa76e921-43ba-4568-81f5-612770872fd6','ACTIVE','1','2026-10-08 12:15:00',NULL,NULL,'1'),(15,'RES-202610-0012','1',22567.50,'2026-10-05','Credit Card','5cb6502b-0bbf-4b8b-8187-74eb63234f89','ACTIVE','1','2026-10-05 12:15:00',NULL,NULL,'1'),(16,'RES-202610-0012','1',11283.75,'2026-10-09','UPI','e216c0ee-2760-49dc-a1a9-53083d580bcf','ACTIVE','1','2026-10-09 12:15:00',NULL,NULL,'1'),(17,'RES-202610-0013','1',1960.00,'2026-10-10','UPI','6b38674a-757e-401e-a097-d5320a5620f4','ACTIVE','1','2026-10-10 12:15:00',NULL,NULL,'1'),(18,'RES-202610-0014','1',5080.32,'2026-10-05','Credit Card','eb26d2a1-eff1-4038-96a6-c249886efe67','ACTIVE','1','2026-10-05 12:15:00',NULL,NULL,'1'),(19,'RES-202610-0015','1',63690.50,'2026-10-03','Bank Transfer','595768bc-2a3e-4998-94e0-7c92c7284398','ACTIVE','1','2026-10-03 12:15:00',NULL,NULL,'1'),(20,'RES-202610-0016','1',4814.40,'2026-10-12','UPI','4905f1c9-d038-42eb-a10e-f01080fb4f92','ACTIVE','1','2026-10-12 12:15:00',NULL,NULL,'1'),(21,'RES-202610-0018','1',18223.92,'2026-10-16','Credit Card','8c70ad0e-759a-455a-9d78-4969a9eff245','ACTIVE','1','2026-10-16 12:15:00',NULL,NULL,'1'),(22,'RES-202610-0022','1',537.60,'2026-10-16','UPI','e1153d50-d735-4e82-a54e-311983cf0945','ACTIVE','1','2026-10-16 12:15:00',NULL,NULL,'1'),(23,'RES-20261011-C32E88','1',3500.00,'2026-10-11','Corporate Billing','4300533c-58e7-4e04-8a41-73f0c0e144b9','ACTIVE','1','2026-10-11 20:00:04',NULL,NULL,'1'),(24,'RES-20261011-C32E88','1',3500.00,'2026-10-11','Corporate Billing','e725667d-53af-4621-92bd-1fc6105ebc15','ACTIVE','1','2026-10-11 20:00:04',NULL,NULL,'1'),(25,'RES-20261011-D2ED33','1',3500.00,'2026-10-11','Corporate Billing','a7364424-6a0c-4593-be64-80b0015d1e75','ACTIVE','1','2026-10-11 20:04:17',NULL,NULL,'1'),(26,'RES-20261011-D2ED33','1',3500.00,'2026-10-11','Corporate Billing','821d6ab9-abb3-467a-945c-707bedea42d0','ACTIVE','1','2026-10-11 20:04:17',NULL,NULL,'1'),(27,'RES-20261012-241FD5','1',3500.00,'2026-10-12','Corporate Billing','84b93d70-b00b-4b66-9b73-9f39e6dc2193','ACTIVE','1','2026-10-12 14:16:24',NULL,NULL,'1'),(28,'RES-20261012-241FD5','1',3500.00,'2026-10-12','Corporate Billing','86c7cc87-4d96-4e0f-b26a-cec1cc649e08','ACTIVE','1','2026-10-12 14:16:25',NULL,NULL,'1'),(29,'RES-20261012-66B3FB','1',3500.00,'2026-10-12','Corporate Billing','d5c6e516-e824-40a1-9053-e974f25107f6','ACTIVE','1','2026-10-12 14:20:45',NULL,NULL,'1'),(30,'RES-20261012-66B3FB','1',3500.00,'2026-10-12','Corporate Billing','b35893eb-51f2-4b61-a100-123bff203727','ACTIVE','1','2026-10-12 14:20:45',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_booking`
--

LOCK TABLES `room_booking` WRITE;
/*!40000 ALTER TABLE `room_booking` DISABLE KEYS */;
INSERT INTO `room_booking` VALUES (1,'RB-8B42A691','Mr.','Deepak','Anand','9840155501','deepak.anand@gmail.com','2026-11-09','2026-11-12',3,'[2, 2]',2,2,0,'ACTIVE','1','2026-10-08 16:20:00',NULL,NULL,'1'),(2,'RB-70582031','Ms.','Sridevi','Raman','9840155502','sridevi.raman@gmail.com','2026-11-13','2026-11-15',2,'[5]',1,2,2,'ACTIVE','1','2026-10-08 16:20:00',NULL,NULL,'1'),(3,'RB-3B36E032','Mr.','Ganesh','Iyer','9840155503','ganesh.iyer@gmail.com','2026-11-19','2026-11-24',5,'[4]',1,1,0,'ACTIVE','1','2026-10-08 16:20:00',NULL,NULL,'1');
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
INSERT INTO `room_lock` VALUES (1),(2),(3),(5),(6),(20);
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
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_reservation`
--

LOCK TABLES `room_reservation` WRITE;
/*!40000 ALTER TABLE `room_reservation` DISABLE KEYS */;
INSERT INTO `room_reservation` VALUES (1,'RES-202610-0001','Mr.','Rohan','Mehta','rohan.mehta@gmail.com','+14155550001','2026-09-18','2026-09-21',3,1,'Checked-Out',1,'311f90e5-be88-480f-bb29-168ac8b7547d.jpg','[1]','[1]','[\"101\"]','[\"daily\"]',3,1,'Welcome Drink','',3,1,10500.00,0.00,12.000,1134.00,10.000,1050.00,10584.00,4,10584.00,10584.00,0.00,0.00,0,0.00,10500.00,NULL,'RESERVATION','FDF25042','e363a938-d62d-49d9-8083-e2bf224c3c68','ACTIVE','1','2026-09-14 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(2,'RES-202610-0002','Ms.','Priya','Nair','priya.nair@gmail.com','+442079460002','2026-09-22','2026-09-26',4,1,'Checked-Out',1,'35225eee-d0bb-4517-8a4e-544849bad250.jpg','[11]','[2]','[\"203\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','Airport Pickup',3,6,22400.00,1200.00,12.000,2832.00,0.000,0.00,26432.00,2,26432.00,26432.00,0.00,0.00,0,0.00,22400.00,NULL,'RESERVATION','D9497565','5e451f1d-61a6-48ee-a989-47b6b0c3f6ce','ACTIVE','1','2026-09-17 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(3,'RES-202610-0003','Mr.','Arjun','Kapoor','arjun.kapoor@gmail.com','+971501000003','2026-09-25','2026-09-30',5,1,'Checked-Out',5,'719e7c7f-eaf4-46a3-b6d8-e5bf5f3847de.jpg','[15]','[3]','[\"301\"]','[\"half_board\"]',3,0,'','Evening Tea',4,2,42500.00,0.00,18.000,7267.50,15.000,7125.00,47642.50,6,47642.50,47642.50,0.00,0.00,1,5000.00,42500.00,NULL,'RESERVATION','989F82B1','c268cff3-1249-46ec-b61e-dbddb1065718','ACTIVE','1','2026-09-19 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(4,'RES-202610-0004','Mrs.','Sana','Sheikh','sana.sheikh@gmail.com','+919876500004','2026-09-28','2026-09-30',2,1,'Checked-Out',2,'10c75802-64b3-4a23-bc88-0d76b7202c17.jpg','[20]','[4]','[\"401\"]','[\"daily\"]',2,1,'Fruit Basket','',4,3,17000.00,850.00,18.000,3052.35,5.000,892.50,20009.85,1,20009.85,20009.85,0.00,0.00,0,0.00,17000.00,NULL,'RESERVATION','0BA38CD5','29194672-5c75-44b2-846d-5a566080e2bf','ACTIVE','1','2026-09-21 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(5,'RES-202610-0005','Mr.','Vikram','Rao','vikram.rao@gmail.com','+14155550005','2026-09-30','2026-10-03',3,2,'Checked-Out',3,'0afb242c-1770-4a00-9b94-f9692e091768.jpg','[2, 3]','[1, 1]','[\"102\", \"103\"]','[\"daily\", \"daily\"]',3,2,'','Newspaper',3,4,21000.00,0.00,12.000,2016.00,20.000,4200.00,18816.00,4,18816.00,18816.00,0.00,0.00,0,0.00,21000.00,NULL,'RESERVATION','2BB98B28','923764d6-8790-4198-a010-533895288855','ACTIVE','1','2026-09-22 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(6,'RES-202610-0006','Ms.','Neha','Gupta','neha.gupta@gmail.com','+442079460006','2026-10-02','2026-10-06',4,1,'Checked-Out',1,'e63e3735-f50a-41e0-a6d0-9a0904014a2d.jpg','[24]','[6]','[\"502\"]','[\"full_board\"]',2,0,'Late Checkout','Spa',4,6,82000.00,3400.00,18.000,17532.00,0.000,0.00,114932.00,2,114932.00,114932.00,0.00,0.00,2,6000.00,82000.00,NULL,'RESERVATION','81AC813A','f3933783-b233-4f66-8699-dd41e8089055','ACTIVE','1','2026-09-23 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(7,'RES-202610-0007','Mr.','Karan','Malhotra','karan.malhotra@gmail.com','+971501000007','2026-10-07','2026-10-13',6,1,'Checked-In',4,'c4a1712d-7a7b-42b0-9146-65217504637e.jpg','[9]','[2]','[\"201\"]','[\"bed_breakfast\"]',3,1,'Breakfast Buffet','',3,6,33600.00,0.00,12.000,4032.00,0.000,0.00,37632.00,4,18816.00,18816.00,18816.00,0.00,0,0.00,33600.00,NULL,'CHECKIN','1BA4E830','5c357c93-fe09-4044-8b10-c23bbca726f1','ACTIVE','1','2026-09-27 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(8,'RES-202610-0008','Ms.','Ananya','Iyer','ananya.iyer@gmail.com','+919876500008','2026-10-08','2026-10-13',5,1,'Checked-In',1,'61743662-f38e-410e-ab90-f25823043620.jpg','[16]','[3]','[\"302\"]','[\"daily\"]',2,2,'','Conference Hall',4,2,34000.00,1500.00,18.000,5431.50,15.000,5325.00,35606.50,7,21363.90,21363.90,14242.60,0.00,0,0.00,34000.00,NULL,'CHECKIN','6098A95F','404b4a22-3cf4-4409-bfcf-776095357d1d','ACTIVE','1','2026-09-27 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(9,'RES-202610-0009','Mr.','Farhan','Khan','farhan.khan@gmail.com','+14155550009','2026-10-06','2026-10-14',8,1,'Checked-In',2,'ad937277-5d05-4588-b109-0407a1878041.jpg','[21]','[4]','[\"402\"]','[\"weekly\"]',3,0,'Welcome Drink','',4,5,59500.00,0.00,18.000,10945.44,12.000,8292.00,71753.44,6,25113.70,25113.70,46639.74,0.00,1,9600.00,59500.00,NULL,'CHECKIN','F3C1C2EF','137b08cc-47ab-4e7f-88a4-99a090c94feb','ACTIVE','1','2026-10-03 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(10,'RES-202610-0010','Ms.','Divya','Menon','divya.menon@gmail.com','+442079460010','2026-10-09','2026-10-13',4,1,'Checked-In',1,'1988abda-046f-4d98-a686-1d8a6808907e.jpg','[4]','[1]','[\"104\"]','[\"daily\"]',2,1,'','',3,3,14000.00,0.00,12.000,1596.00,5.000,700.00,14896.00,1,14896.00,14896.00,0.00,0.00,0,0.00,14000.00,NULL,'CHECKIN','A2B4FA9A','66f56776-e4a4-4756-8817-485b3fa60e33','ACTIVE','1','2026-10-05 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(11,'RES-202610-0011','Mr.','Aditya','Verma','aditya.verma@gmail.com','+971501000011','2026-10-08','2026-10-10',2,1,'Checked-In',6,'711664ae-f416-4848-9391-d86167e551c2.jpg','[13]','[2]','[\"205\"]','[\"bed_breakfast\"]',3,2,'Breakfast Buffet','',3,6,11200.00,620.00,12.000,1418.40,0.000,0.00,13238.40,4,9266.88,9266.88,3971.52,0.00,0,0.00,11200.00,NULL,'CHECKIN','0D970BBE','5b13586e-005f-489d-838d-426b02c03b33','ACTIVE','1','2026-10-03 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(12,'RES-202610-0012','Ms.','Ritu','Chawla','ritu.chawla@gmail.com','+919876500012','2026-10-05','2026-10-10',5,1,'Checked-In',5,'06299680-fa40-4f5f-8154-810176a6570d.jpg','[17]','[3]','[\"303\"]','[\"half_board\"]',2,0,'','Evening Tea',4,1,42500.00,0.00,18.000,6885.00,10.000,4250.00,45135.00,2,33851.25,33851.25,11283.75,0.00,0,0.00,42500.00,NULL,'CHECKIN','898AF765','0d478fec-274f-490f-b4d4-5defc6bf6966','ACTIVE','1','2026-09-29 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(13,'RES-202610-0013','Mr.','Suresh','Pillai','suresh.pillai@gmail.com','+14155550013','2026-10-10','2026-10-12',2,1,'Confirmed',1,'e7437960-c371-4278-9b31-0a8d7bf45a17.jpg','[5]','[1]','[\"105\"]','[\"daily\"]',3,1,'Welcome Drink','',3,6,7000.00,0.00,12.000,840.00,0.000,0.00,7840.00,4,1960.00,1960.00,5880.00,0.00,0,0.00,7000.00,NULL,'RESERVATION','CC5AE182','efd9b2d1-d4ee-4083-a84f-81556399989d','ACTIVE','1','2026-10-03 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(14,'RES-202610-0014','Ms.','Meera','Desai','meera.desai@gmail.com','+442079460014','2026-10-10','2026-10-13',3,1,'Confirmed',3,'e6790146-0798-4b2f-802f-0224e5bae308.jpg','[14]','[2]','[\"206\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','Airport Pickup',3,1,16800.00,0.00,12.000,1814.40,10.000,1680.00,16934.40,2,5080.32,5080.32,11854.08,0.00,0,0.00,16800.00,NULL,'RESERVATION','6F37B30E','c2ead8a9-0eb5-4bdc-952d-ebaa846a683e','ACTIVE','1','2026-10-02 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(15,'RES-202610-0015','Mr.','Ibrahim','Ansari','ibrahim.ansari@gmail.com','+971501000015','2026-10-10','2026-10-14',4,1,'Confirmed',2,'519da691-4a9d-4da0-bdf4-3e1dd63a7b9b.jpg','[25]','[7]','[\"601\"]','[\"full_board\"]',3,0,'Fruit Basket','Spa',4,2,122000.00,5000.00,18.000,19431.00,15.000,19050.00,127381.00,6,63690.50,63690.50,63690.50,0.00,0,0.00,122000.00,NULL,'RESERVATION','E5ECC784','bc3d2ba3-ffdd-4de2-9e8c-9349a38e2808','ACTIVE','1','2026-10-01 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(16,'RES-202610-0016','Ms.','Lakshmi','Krishnan','lakshmi.krishnan@gmail.com','+919876500016','2026-10-13','2026-10-16',3,1,'Confirmed',1,'4b1e5a6f-5d80-493f-818d-788ca2804c79.jpg','[18]','[3]','[\"304\"]','[\"daily\"]',2,1,'','',4,6,20400.00,0.00,18.000,3672.00,0.000,0.00,24072.00,4,4814.40,4814.40,19257.60,0.00,0,0.00,20400.00,NULL,'RESERVATION','A382D8B3','6856159e-0996-4800-bf20-787414fe5abd','ACTIVE','1','2026-10-03 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(17,'RES-202610-0017','Mr.','Yusuf','Sheikh','yusuf.sheikh@gmail.com','+14155550017','2026-10-15','2026-10-17',2,2,'Confirmed',4,'81d947b4-5398-4959-9f00-2fa4ef975ecc.jpg','[6, 7]','[1, 1]','[\"106\", \"107\"]','[\"daily\", \"daily\"]',3,2,'Welcome Drink','',3,4,14000.00,0.00,12.000,1344.00,20.000,2800.00,12544.00,1,0.00,0.00,12544.00,0.00,0,0.00,14000.00,NULL,'RESERVATION','62C2899F','32341ae2-5a73-475c-b162-a86501c33286','ACTIVE','1','2026-10-04 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(18,'RES-202610-0018','Ms.','Pooja','Bhatt','pooja.bhatt@gmail.com','+442079460018','2026-10-18','2026-10-23',5,1,'Confirmed',1,'2f74f112-128b-4a5c-a0c7-b12b1912bfb4.jpg','[22]','[4]','[\"403\"]','[\"half_board\"]',2,0,'','Gymnasium',4,5,52500.00,0.00,18.000,9266.40,12.000,7020.00,60746.40,2,18223.92,18223.92,42522.48,0.00,1,6000.00,52500.00,NULL,'RESERVATION','E7578044','87a748a7-6cfe-4949-a022-03afeb0cf74b','ACTIVE','1','2026-10-15 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(19,'RES-202610-0019','Mr.','Rithvik','Prabhu','rithvik.prabhu@gmail.com','+971501000019','2026-10-22','2026-10-26',4,1,'Confirmed',5,'71d1dafe-8c74-4ef4-98af-60057742cb22.jpg','[23]','[5]','[\"501\"]','[\"full_board\"]',3,1,'Late Checkout','Spa',4,6,64000.00,2200.00,18.000,12780.00,0.000,0.00,83780.00,1,0.00,0.00,83780.00,0.00,1,4800.00,64000.00,NULL,'RESERVATION','CB7848CB','c3cac065-7471-4eb9-a522-9ee14114e77a','ACTIVE','1','2026-10-18 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(20,'RES-202610-0020','Ms.','Kavya','Reddy','kavya.reddy@gmail.com','+919876500020','2026-10-26','2026-10-29',3,1,'Confirmed',1,'7ac90bfe-ae30-4978-baa4-6e60dd4c8ffe.jpg','[10]','[2]','[\"202\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','',3,3,16800.00,0.00,12.000,1915.20,5.000,840.00,17875.20,1,0.00,0.00,17875.20,0.00,0,0.00,16800.00,NULL,'RESERVATION','3EC2CE08','bdba6088-d85a-4e1b-abf8-82dc9eff240a','ACTIVE','1','2026-10-21 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(21,'RES-202610-0021','Mr.','Nikhil','Joshi','nikhil.joshi@gmail.com','+14155550021','2026-10-16','2026-10-19',3,1,'Cancelled',6,'777d97bb-e041-4304-a840-dcbe373bbc6c.jpg','[19]','[3]','[\"305\"]','[\"daily\"]',3,0,'','',4,6,20400.00,0.00,18.000,3672.00,0.000,0.00,24072.00,1,0.00,0.00,24072.00,0.00,0,0.00,20400.00,NULL,'RESERVATION','CE17BBED','0aadedca-2fe7-44c4-926f-98df331e41c9','ACTIVE','1','2026-10-10 10:30:00',NULL,NULL,'1','Guest request — travel plans changed','2026-10-14 15:40:00','1'),(22,'RES-202610-0022','Ms.','Fatima','Begum','fatima.begum@gmail.com','+442079460022','2026-10-19','2026-10-21',2,1,'Cancelled',2,'b4e4b621-6062-4951-b442-bc4aef60e377.jpg','[8]','[8]','[\"108\"]','[\"daily\"]',2,1,'','',3,6,2400.00,0.00,12.000,288.00,0.000,0.00,2688.00,4,537.60,537.60,2150.40,0.00,0,0.00,2400.00,NULL,'RESERVATION','5B4ED3C9','fc356c6e-31ca-4ec8-9cd8-6719d09904ef','ACTIVE','1','2026-10-12 10:30:00',NULL,NULL,'1','Duplicate booking — kept RES on 106','2026-10-17 15:40:00','1'),(23,'RES-202610-0023','Mr.','Sandeep','Kulkarni','sandeep.kulkarni@gmail.com','+971501000023','2026-10-04','2026-10-06',2,1,'No-Show',3,'66fa8ecf-0976-4f8e-ae03-bd8daf9bae0d.jpg','[12]','[2]','[\"204\"]','[\"daily\"]',3,2,'','',3,6,10400.00,0.00,12.000,1248.00,0.000,0.00,11648.00,1,0.00,0.00,11648.00,0.00,0,0.00,10400.00,NULL,'RESERVATION','59C97725','301a3f87-ea1b-4935-b264-73d28b82618f','ACTIVE','1','2026-09-26 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(24,'RES-202610-0024','Ms.','Anjali','Saxena','anjali.saxena@gmail.com','+919876500024','2026-10-30','2026-11-02',3,1,'Pending',1,NULL,'[15]','[3]','[\"301\"]','[\"daily\"]',2,0,'','',3,6,20400.00,0.00,12.000,2448.00,0.000,0.00,22848.00,1,0.00,0.00,22848.00,0.00,0,0.00,20400.00,NULL,'RESERVATION','B73FE650','1067fe42-440d-4264-bddd-8acc69d09957','ACTIVE','1','2026-10-21 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(25,'RES-202610-0025','Mr.','Arjun','Kapoor','arjun.kapoor@gmail.com','+14155550025','2026-11-04','2026-11-06',2,1,'On Hold',5,'e66855cd-463c-451e-8e9d-965d1b58495c.jpg','[20]','[4]','[\"401\"]','[\"daily\"]',3,1,NULL,NULL,NULL,NULL,17000.00,0.00,0.000,0.00,0.000,0.00,17000.00,1,0.00,0.00,17000.00,0.00,0,0.00,17000.00,7,'RESERVATION','3942C0A2','9a4226bc-a7e0-4cd0-aaad-5c6c26657bb2','ACTIVE','1','2026-10-25 10:30:00','2026-10-10 20:06:36','1','1',NULL,NULL,NULL),(26,'RES-20261011-C32E88','Mr','Flow','Test','flow919876505003@example.com','+919876505003','2026-10-11','2026-10-13',2,1,'Checked-Out',6,'704a4c46-4720-47fb-99e4-59bc2056a4d8.png','[1]','[1]','[\"101\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,7000.00,0.00,0.00,0,0.00,7000.00,3,'RESERVATION','6944E3AA','fd4f3ef7-f7a1-46de-bf55-b325a8de4740','ACTIVE','1','2026-10-11 20:00:03','2026-10-11 20:00:04','1','1',NULL,NULL,NULL),(27,'RES-20261011-5C454B','Mr','Flow','Test','flow919876505010@example.com','+919876505010','2026-10-11','2026-10-13',2,1,'Cancelled',6,'6ea38502-5f94-4b1f-bf27-3ae56fa524fa.png','[2]','[1]','[\"102\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,0.00,7000.00,0.00,0,0.00,7000.00,4,'RESERVATION','AC7390B7','1531497a-0f55-4a92-bc43-6c70d060e4b6','ACTIVE','1','2026-10-11 20:00:05','2026-10-11 20:00:05','1','1','Guest called','2026-10-11 20:00:05','1'),(28,'RES-20261011-D2ED33','Mr','Flow','Test','flow919876505003@example.com','+919876505003','2026-10-11','2026-10-13',2,1,'Checked-Out',6,'2b3dcf10-ea27-4844-89d9-8940552815b0.png','[2]','[1]','[\"102\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,7000.00,0.00,0.00,0,0.00,7000.00,3,'RESERVATION','AD65849C','cd21e1f7-5d2e-4ffe-9941-97c6f826f325','ACTIVE','1','2026-10-11 20:04:15','2026-10-11 20:04:17','1','1',NULL,NULL,NULL),(29,'RES-20261011-77DB4B','Mr','Flow','Test','flow919876505010@example.com','+919876505010','2026-10-11','2026-10-13',2,1,'Cancelled',6,'5c86879e-179c-4cfe-864d-2f2e49c9c5ae.png','[3]','[1]','[\"103\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,0.00,7000.00,0.00,0,0.00,7000.00,4,'RESERVATION','5E103918','75f0c909-b7e3-4ac4-a8ac-93e729b7ebf8','ACTIVE','1','2026-10-11 20:04:18','2026-10-11 20:04:18','1','1','Guest called','2026-10-11 20:04:19','1'),(30,'RES-20261012-241FD5','Mr','Flow','Test','flow919876505003@example.com','+919876505003','2026-10-12','2026-10-14',2,1,'Checked-Out',6,'676c4a5f-ca45-4993-adf8-cd041803b0ae.png','[3]','[1]','[\"103\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,7000.00,0.00,0.00,0,0.00,7000.00,3,'RESERVATION','5EE3DFB6','cb251af9-e75f-4e94-b05d-ed15d932a293','ACTIVE','1','2026-10-12 14:16:22','2026-10-12 14:16:25','1','1',NULL,NULL,NULL),(31,'RES-20261012-30C3E6','Mr','Flow','Test','flow919876505010@example.com','+919876505010','2026-10-12','2026-10-14',2,1,'Cancelled',6,'978f1ede-0737-417a-9916-bfcce8304e3f.png','[5]','[1]','[\"105\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,0.00,7000.00,0.00,0,0.00,7000.00,4,'RESERVATION','283FC54A','c433c9be-d5cd-4c1c-888f-9c2efb5b7037','ACTIVE','1','2026-10-12 14:16:26','2026-10-12 14:16:26','1','1','Guest called','2026-10-12 14:16:26','1'),(32,'RES-20261012-66B3FB','Mr','Flow','Test','flow919876505003@example.com','+919876505003','2026-10-12','2026-10-14',2,1,'Checked-Out',6,'e10b243c-f1bc-418a-b484-e936b2ba1cfd.png','[5]','[1]','[\"105\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,7000.00,0.00,0.00,0,0.00,7000.00,3,'RESERVATION','AFD36C5B','51c7c875-b8c6-4c3f-b3a6-4401ffc20ee7','ACTIVE','1','2026-10-12 14:20:44','2026-10-12 14:20:45','1','1',NULL,NULL,NULL),(33,'RES-20261012-5E4B3E','Mr','Flow','Test','flow919876505010@example.com','+919876505010','2026-10-12','2026-10-14',2,1,'Cancelled',6,'f726e3ca-3d5b-4230-b235-2d6f4bab1db1.png','[6]','[1]','[\"106\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,0.00,7000.00,0.00,0,0.00,7000.00,4,'RESERVATION','3C53D4B2','f90add1d-111c-464c-a767-3c83cb8f02f1','ACTIVE','1','2026-10-12 14:20:46','2026-10-12 14:20:46','1','1','Guest called','2026-10-12 14:20:46','1');
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

-- Dump completed on 2026-10-12 15:15:26
