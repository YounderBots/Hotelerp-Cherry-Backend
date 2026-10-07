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
INSERT INTO `hotel_business_date` VALUES (1,'2026-10-06','2026-10-06 02:15:00','1','ACTIVE','1','2026-10-05 02:15:00','2026-10-06 02:15:00','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `housekeeper_task`
--

LOCK TABLES `housekeeper_task` WRITE;
/*!40000 ALTER TABLE `housekeeper_task` DISABLE KEYS */;
INSERT INTO `housekeeper_task` VALUES (1,'5','Imran','Khan','2026-10-06','09:00:00',1,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(2,'6','Lakshmi','Iyer','2026-10-06','10:00:00',2,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(3,'5','Imran','Khan','2026-10-06','11:00:00',3,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(4,'6','Lakshmi','Iyer','2026-10-06','12:00:00',11,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(5,'5','Imran','Khan','2026-10-06','09:00:00',15,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(6,'6','Lakshmi','Iyer','2026-10-06','10:00:00',20,'Deep Cleaning','6','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(7,'5','Imran','Khan','2026-10-06','11:00:00',24,'Deep Cleaning','5','Pending','Unblocking',NULL,'Departure clean before the room is re-sold.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(8,'5','Imran','Khan','2026-10-06','10:30:00',4,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(9,'6','Lakshmi','Iyer','2026-10-06','11:30:00',9,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(10,'5','Imran','Khan','2026-10-06','12:30:00',13,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(11,'6','Lakshmi','Iyer','2026-10-06','13:30:00',16,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(12,'5','Imran','Khan','2026-10-06','14:30:00',17,'Daily Cleaning','5','Completed','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(13,'6','Lakshmi','Iyer','2026-10-06','10:30:00',21,'Daily Cleaning','6','In-Progress','Unblocking',NULL,'Guest in house — service while the room is vacant.','ACTIVE',1,'2026-10-06 08:30:00',NULL,NULL,1),(14,'10','Ops','Test','2026-10-06','10:00:00',25,'Pest Control','10','Completed','Blocking',NULL,'flow test','INACTIVE',1,'2026-10-06 18:42:01','2026-10-06 18:42:02',1,1),(15,'10','Ops','Test','2026-10-06','10:00:00',25,'Pest Control','10','Completed','Blocking',NULL,'flow test','INACTIVE',1,'2026-10-06 23:57:10','2026-10-06 23:57:11',1,1),(16,'10','Ops','Test','2026-10-07','10:00:00',25,'Pest Control','10','Completed','Blocking',NULL,'flow test','INACTIVE',1,'2026-10-07 00:41:19','2026-10-07 00:41:19',1,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hsk_room_incident`
--

LOCK TABLES `hsk_room_incident` WRITE;
/*!40000 ALTER TABLE `hsk_room_incident` DISABLE KEYS */;
INSERT INTO `hsk_room_incident` VALUES (1,12,'2026-09-30','18:20:00','Bathroom tap dripping; floor wet on arrival.','Imran Khan','Medium','Duty Manager','Tap washer replaced, floor dried and room re-inspected.','Imran Khan','2026-09-30','/templates/static/room_incidents/fbfde3ce00de40ea8ec2d6be61a68416.jpg','ACTIVE','1','2026-09-30 18:20:00',NULL,NULL,'1'),(2,16,'2026-10-03','09:05:00','Guest reported air conditioning not cooling.','Lakshmi Iyer','High','Duty Manager','Maintenance recharged the unit; guest confirmed satisfied.','Lakshmi Iyer','2026-10-03','/templates/static/room_incidents/d9c9ad7429604fd5bbee618e67b50eb8.jpg','ACTIVE','1','2026-10-03 09:05:00',NULL,NULL,'1'),(3,8,'2026-10-05','21:40:00','Reading lamp shade cracked in dormitory bay 3.','Imran Khan','Low','Duty Manager','Shade replaced from stores; no charge raised to guest.','Imran Khan','2026-10-05','/templates/static/room_incidents/9a5de3b4cc764989851d7b7be269513c.jpg','ACTIVE','1','2026-10-05 21:40:00',NULL,NULL,'1'),(4,25,'2026-10-06','12:30:00','Flow test incident','Ops Test','Low','none','escalated','10','2026-10-06','/templates/static/room_incidents/b6369edfe36b473abd8df60511d3b919.png','INACTIVE','1','2026-10-06 18:42:02','2026-10-06 18:42:03','1','1'),(5,25,'2026-10-06','12:30:00','Flow test incident','Ops Test','Low','none','escalated','10','2026-10-06','/templates/static/room_incidents/8ce5a8c294f24aabb154011868577514.png','INACTIVE','1','2026-10-06 23:57:11','2026-10-06 23:57:11','1','1'),(6,25,'2026-10-07','12:30:00','Flow test incident','Ops Test','Low','none','escalated','10','2026-10-07','/templates/static/room_incidents/ef8cbaf7a31a428ab19f87aa686fda9d.png','INACTIVE','1','2026-10-07 00:41:20','2026-10-07 00:41:20','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inquiry`
--

LOCK TABLES `inquiry` WRITE;
/*!40000 ALTER TABLE `inquiry` DISABLE KEYS */;
INSERT INTO `inquiry` VALUES (1,'Online','Deepak Anand','Asked for tariff on two Deluxe rooms in October.','Rate sheet emailed; awaiting confirmation.',NULL,'In Progress','ACTIVE','1','2026-10-05 11:00:00',NULL,NULL,'1'),(2,'Offline','Sridevi Raman','Walk-in asking about banquet hall for a reception.','Banquet manager to call back with availability.',NULL,'In Progress','ACTIVE','1','2026-10-04 11:00:00',NULL,NULL,'1'),(3,'Online','Michael Fernandes','Airport pickup availability for a late arrival.','Confirmed pickup can be arranged with 12 hours\' notice.',NULL,'Completed','ACTIVE','1','2026-10-03 11:00:00',NULL,NULL,'1'),(4,'Online','Aisha Rahman','Requested a quiet room away from the lift.','Noted on the booking; room 305 allocated.',NULL,'Completed','ACTIVE','1','2026-10-02 11:00:00',NULL,NULL,'1'),(5,'Offline','Ganesh Iyer','Corporate tie-up enquiry for monthly stays.','Corporate rate card shared with the company\'s admin.',NULL,'In Progress','ACTIVE','1','2026-10-01 11:00:00',NULL,NULL,'1'),(6,'Online','Sarah Thomas','Asked whether the pool is open to day guests.','Advised pool access is for in-house guests only.',NULL,'Completed','ACTIVE','1','2026-09-30 11:00:00',NULL,NULL,'1'),(7,'Online','Ops Tester','Handled',NULL,NULL,'Completed','INACTIVE','1','2026-10-06 18:42:03','2026-10-06 18:42:03','1','1'),(8,'Online','Ops Tester','Handled',NULL,NULL,'Completed','INACTIVE','1','2026-10-06 23:57:11','2026-10-06 23:57:11','1','1'),(9,'Online','Ops Tester','Handled',NULL,NULL,'Completed','INACTIVE','1','2026-10-07 00:41:20','2026-10-07 00:41:20','1','1');
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
INSERT INTO `night_audit` VALUES (1,'NA-20261005','2026-10-05','2026-10-06','Completed','2026-10-06 02:10:00','2026-10-06 02:15:00','1',NULL,25,7,28.000,6,1,1,0,0,6,6,0,'[]',37437.50,610.00,5611.68,3126.50,40532.68,26179.75,'[{\"amount\": 14896.0, \"payment_method\": \"Cash\"}, {\"amount\": 11283.75, \"payment_method\": \"UPI\"}]',94953.61,'6246600a-0bed-4ef5-b49e-a74725972d5b','ACTIVE','1','2026-10-06 02:15:00','2026-10-06 02:15:00','1','1');
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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_amount_paid_history`
--

LOCK TABLES `reservation_amount_paid_history` WRITE;
/*!40000 ALTER TABLE `reservation_amount_paid_history` DISABLE KEYS */;
INSERT INTO `reservation_amount_paid_history` VALUES (1,'RES-202610-0001','1',3175.20,'2026-08-31','UPI','d4b1c66a-a5ed-45b5-a303-803bb462a6e2','ACTIVE','1','2026-08-31 12:15:00',NULL,NULL,'1'),(2,'RES-202610-0001','1',7408.80,'2026-09-17','Credit Card','bc4bb7f8-998d-4edd-8610-30fffd7f98e9','ACTIVE','1','2026-09-17 12:15:00',NULL,NULL,'1'),(3,'RES-202610-0002','1',26432.00,'2026-09-18','Credit Card','ff3c35ed-b1fd-46cc-9ff8-b12b4b4294ef','ACTIVE','1','2026-09-18 12:15:00',NULL,NULL,'1'),(4,'RES-202610-0003','1',23821.25,'2026-09-21','Bank Transfer','9d27abc5-1067-4c72-aae5-fade91b37081','ACTIVE','1','2026-09-21 12:15:00',NULL,NULL,'1'),(5,'RES-202610-0003','1',23821.25,'2026-09-26','Bank Transfer','43ea74dd-558e-4325-84b5-29fcdd4c9a41','ACTIVE','1','2026-09-26 12:15:00',NULL,NULL,'1'),(6,'RES-202610-0004','1',20009.85,'2026-09-24','Cash','d989d077-3342-41a5-a699-466f1fe7872e','ACTIVE','1','2026-09-24 12:15:00',NULL,NULL,'1'),(7,'RES-202610-0005','1',7526.40,'2026-09-24','UPI','759292d7-4445-4194-afcc-e07f532b63d1','ACTIVE','1','2026-09-24 12:15:00',NULL,NULL,'1'),(8,'RES-202610-0005','1',11289.60,'2026-09-29','Debit Card','4909d2dd-c24c-4d02-ac46-2b5d96870593','ACTIVE','1','2026-09-29 12:15:00',NULL,NULL,'1'),(9,'RES-202610-0006','1',114932.00,'2026-09-28','Credit Card','de85ce2b-403d-494b-811c-2d2ffe9d75ff','ACTIVE','1','2026-09-28 12:15:00',NULL,NULL,'1'),(10,'RES-202610-0007','1',18816.00,'2026-10-03','UPI','3daadfc5-60f3-4998-ae36-2bbe4c3074a3','ACTIVE','1','2026-10-03 12:15:00',NULL,NULL,'1'),(11,'RES-202610-0008','1',21363.90,'2026-10-04','Corporate Billing','c07c1288-62e0-41b6-a76b-59d92e345fe2','ACTIVE','1','2026-10-04 12:15:00',NULL,NULL,'1'),(12,'RES-202610-0009','1',25113.70,'2026-10-02','Bank Transfer','68b8b91e-4a37-4e73-b3ad-7847bd80169c','ACTIVE','1','2026-10-02 12:15:00',NULL,NULL,'1'),(13,'RES-202610-0010','1',14896.00,'2026-10-05','Cash','131379e3-3817-44e4-a366-f8f643dbcf50','ACTIVE','1','2026-10-05 12:15:00',NULL,NULL,'1'),(14,'RES-202610-0011','1',9266.88,'2026-10-04','UPI','37d6cda0-bf52-4ac1-8dd0-b483d61441c2','ACTIVE','1','2026-10-04 12:15:00',NULL,NULL,'1'),(15,'RES-202610-0012','1',22567.50,'2026-10-01','Credit Card','8db813ea-de1e-4dd7-bc62-4ec84232562f','ACTIVE','1','2026-10-01 12:15:00',NULL,NULL,'1'),(16,'RES-202610-0012','1',11283.75,'2026-10-05','UPI','1b4bc7f6-0f3e-4539-8a36-ca113635d372','ACTIVE','1','2026-10-05 12:15:00',NULL,NULL,'1'),(17,'RES-202610-0013','1',1960.00,'2026-10-06','UPI','567fc2a5-d548-460d-a6d4-ae2d303d6007','ACTIVE','1','2026-10-06 12:15:00',NULL,NULL,'1'),(18,'RES-202610-0014','1',5080.32,'2026-10-01','Credit Card','94c272c2-4660-479b-b325-54763698dd05','ACTIVE','1','2026-10-01 12:15:00',NULL,NULL,'1'),(19,'RES-202610-0015','1',63690.50,'2026-09-29','Bank Transfer','681ebc17-03db-4b88-968f-dba20d585a12','ACTIVE','1','2026-09-29 12:15:00',NULL,NULL,'1'),(20,'RES-202610-0016','1',4814.40,'2026-10-08','UPI','7f015adc-83bf-4766-bc74-a9f3c5267892','ACTIVE','1','2026-10-08 12:15:00',NULL,NULL,'1'),(21,'RES-202610-0018','1',18223.92,'2026-10-12','Credit Card','d8294f42-561a-4338-9115-3421727788df','ACTIVE','1','2026-10-12 12:15:00',NULL,NULL,'1'),(22,'RES-202610-0022','1',537.60,'2026-10-12','UPI','a89654e7-55a1-4ddf-aae4-53600214c637','ACTIVE','1','2026-10-12 12:15:00',NULL,NULL,'1'),(23,'RES-20261006-25D577','1',3500.00,'2026-10-06','Corporate Billing','cdc33084-dbf3-4f29-aebd-3bfd829f1373','ACTIVE','1','2026-10-06 18:41:34',NULL,NULL,'1'),(24,'RES-20261006-25D577','1',3500.00,'2026-10-06','Corporate Billing','a021c06c-dcca-4a6c-af27-5d6df6259848','ACTIVE','1','2026-10-06 18:41:34',NULL,NULL,'1'),(25,'RES-20261006-7DBCC5','1',3500.00,'2026-10-06','Corporate Billing','37fbbd64-6b9d-4923-b3e4-11c69d7b3c5a','ACTIVE','1','2026-10-06 23:57:07',NULL,NULL,'1'),(26,'RES-20261006-7DBCC5','1',3500.00,'2026-10-06','Corporate Billing','48b66b2d-322d-4168-b145-680dfd6ad3c7','ACTIVE','1','2026-10-06 23:57:07',NULL,NULL,'1'),(27,'RES-20261007-E92143','1',3500.00,'2026-10-07','Corporate Billing','4035e348-00d7-4ed3-821c-ee88abc47275','ACTIVE','1','2026-10-07 00:40:55',NULL,NULL,'1'),(28,'RES-20261007-E92143','1',3500.00,'2026-10-07','Corporate Billing','4d2b1b57-fa07-4e08-8353-a0d240cc15bf','ACTIVE','1','2026-10-07 00:40:56',NULL,NULL,'1');
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
INSERT INTO `room_booking` VALUES (1,'RB-2BA4441E','Mr.','Deepak','Anand','9840155501','deepak.anand@gmail.com','2026-11-05','2026-11-08',3,'[2, 2]',2,2,0,'ACTIVE','1','2026-10-04 16:20:00',NULL,NULL,'1'),(2,'RB-73CA01D9','Ms.','Sridevi','Raman','9840155502','sridevi.raman@gmail.com','2026-11-09','2026-11-11',2,'[5]',1,2,2,'ACTIVE','1','2026-10-04 16:20:00',NULL,NULL,'1'),(3,'RB-640E5E2D','Mr.','Ganesh','Iyer','9840155503','ganesh.iyer@gmail.com','2026-11-15','2026-11-20',5,'[4]',1,1,0,'ACTIVE','1','2026-10-04 16:20:00',NULL,NULL,'1');
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
INSERT INTO `room_lock` VALUES (1),(2),(3),(6);
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
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_reservation`
--

LOCK TABLES `room_reservation` WRITE;
/*!40000 ALTER TABLE `room_reservation` DISABLE KEYS */;
INSERT INTO `room_reservation` VALUES (1,'RES-202610-0001','Mr.','Rohan','Mehta','rohan.mehta@gmail.com','+14155550001','2026-09-14','2026-09-17',3,1,'Checked-Out',1,'653e185e-f40a-4cc6-af8e-e54dbc6c04e8.jpg','[1]','[1]','[\"101\"]','[\"daily\"]',3,1,'Welcome Drink','',3,1,10500.00,0.00,12.000,1134.00,10.000,1050.00,10584.00,4,10584.00,10584.00,0.00,0.00,0,0.00,10500.00,NULL,'RESERVATION','47697F23','b159204f-3b7a-465d-b0f3-4bdce56b4656','ACTIVE','1','2026-09-10 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(2,'RES-202610-0002','Ms.','Priya','Nair','priya.nair@gmail.com','+442079460002','2026-09-18','2026-09-22',4,1,'Checked-Out',1,'acc68146-8103-4514-a044-2530ff48f7f1.jpg','[11]','[2]','[\"203\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','Airport Pickup',3,6,22400.00,1200.00,12.000,2832.00,0.000,0.00,26432.00,2,26432.00,26432.00,0.00,0.00,0,0.00,22400.00,NULL,'RESERVATION','DDAE5A54','fb9bd69b-337a-4272-9008-1dd5dccc5474','ACTIVE','1','2026-09-13 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(3,'RES-202610-0003','Mr.','Arjun','Kapoor','arjun.kapoor@gmail.com','+971501000003','2026-09-21','2026-09-26',5,1,'Checked-Out',5,'9dbf6206-0fd5-4bd2-b113-db9d33cd5e8a.jpg','[15]','[3]','[\"301\"]','[\"half_board\"]',3,0,'','Evening Tea',4,2,42500.00,0.00,18.000,7267.50,15.000,7125.00,47642.50,6,47642.50,47642.50,0.00,0.00,1,5000.00,42500.00,NULL,'RESERVATION','A43F30D4','0c121e39-d46e-47b0-88b1-915ef55a2e51','ACTIVE','1','2026-09-15 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(4,'RES-202610-0004','Mrs.','Sana','Sheikh','sana.sheikh@gmail.com','+919876500004','2026-09-24','2026-09-26',2,1,'Checked-Out',2,'d888bf9c-3880-47fa-836d-90618c6c5882.jpg','[20]','[4]','[\"401\"]','[\"daily\"]',2,1,'Fruit Basket','',4,3,17000.00,850.00,18.000,3052.35,5.000,892.50,20009.85,1,20009.85,20009.85,0.00,0.00,0,0.00,17000.00,NULL,'RESERVATION','F55B82E1','f369fdde-00c0-4dba-9e89-5db477fe87d6','ACTIVE','1','2026-09-17 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(5,'RES-202610-0005','Mr.','Vikram','Rao','vikram.rao@gmail.com','+14155550005','2026-09-26','2026-09-29',3,2,'Checked-Out',3,'cd816e8d-7e24-429d-949f-9fa999c0121a.jpg','[2, 3]','[1, 1]','[\"102\", \"103\"]','[\"daily\", \"daily\"]',3,2,'','Newspaper',3,4,21000.00,0.00,12.000,2016.00,20.000,4200.00,18816.00,4,18816.00,18816.00,0.00,0.00,0,0.00,21000.00,NULL,'RESERVATION','C7129824','03f53d56-e002-4129-9898-66b3852c79ab','ACTIVE','1','2026-09-18 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(6,'RES-202610-0006','Ms.','Neha','Gupta','neha.gupta@gmail.com','+442079460006','2026-09-28','2026-10-02',4,1,'Checked-Out',1,'5514c72d-dd0c-48ea-89f3-ddadfe036742.jpg','[24]','[6]','[\"502\"]','[\"full_board\"]',2,0,'Late Checkout','Spa',4,6,82000.00,3400.00,18.000,17532.00,0.000,0.00,114932.00,2,114932.00,114932.00,0.00,0.00,2,6000.00,82000.00,NULL,'RESERVATION','730E811C','94357fe0-9ce8-4d9b-9c0a-a6751e2555f4','ACTIVE','1','2026-09-19 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(7,'RES-202610-0007','Mr.','Karan','Malhotra','karan.malhotra@gmail.com','+971501000007','2026-10-03','2026-10-09',6,1,'Checked-In',4,'e8691a55-2e63-4018-991f-5c39c7aab30d.jpg','[9]','[2]','[\"201\"]','[\"bed_breakfast\"]',3,1,'Breakfast Buffet','',3,6,33600.00,0.00,12.000,4032.00,0.000,0.00,37632.00,4,18816.00,18816.00,18816.00,0.00,0,0.00,33600.00,NULL,'CHECKIN','4D591BF9','712a1df7-acf3-4415-8235-236570c3c15e','ACTIVE','1','2026-09-23 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(8,'RES-202610-0008','Ms.','Ananya','Iyer','ananya.iyer@gmail.com','+919876500008','2026-10-04','2026-10-09',5,1,'Checked-In',1,'5e3298de-49a1-4b2a-b1ea-e74b60d6651c.jpg','[16]','[3]','[\"302\"]','[\"daily\"]',2,2,'','Conference Hall',4,2,34000.00,1500.00,18.000,5431.50,15.000,5325.00,35606.50,7,21363.90,21363.90,14242.60,0.00,0,0.00,34000.00,NULL,'CHECKIN','013D6D86','17c39eef-f0e6-471b-994e-af2ab1ea1e61','ACTIVE','1','2026-09-23 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(9,'RES-202610-0009','Mr.','Farhan','Khan','farhan.khan@gmail.com','+14155550009','2026-10-02','2026-10-10',8,1,'Checked-In',2,'d952cea5-6426-43c5-8b12-f8ff2fdd31fa.jpg','[21]','[4]','[\"402\"]','[\"weekly\"]',3,0,'Welcome Drink','',4,5,59500.00,0.00,18.000,10945.44,12.000,8292.00,71753.44,6,25113.70,25113.70,46639.74,0.00,1,9600.00,59500.00,NULL,'CHECKIN','46D4051B','9ba67760-4345-481b-9548-2664f34dcb2c','ACTIVE','1','2026-09-29 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(10,'RES-202610-0010','Ms.','Divya','Menon','divya.menon@gmail.com','+442079460010','2026-10-05','2026-10-09',4,1,'Checked-In',1,'e23cda16-ffde-4982-b0ed-4d73054f0bc4.jpg','[4]','[1]','[\"104\"]','[\"daily\"]',2,1,'','',3,3,14000.00,0.00,12.000,1596.00,5.000,700.00,14896.00,1,14896.00,14896.00,0.00,0.00,0,0.00,14000.00,NULL,'CHECKIN','3E8DAA34','388f6ce3-badd-471f-bac5-2562fc54d0c6','ACTIVE','1','2026-10-01 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(11,'RES-202610-0011','Mr.','Aditya','Verma','aditya.verma@gmail.com','+971501000011','2026-10-04','2026-10-06',2,1,'Checked-In',6,'59bb9b5d-2ddc-442e-9f14-4c844f64cb6b.jpg','[13]','[2]','[\"205\"]','[\"bed_breakfast\"]',3,2,'Breakfast Buffet','',3,6,11200.00,620.00,12.000,1418.40,0.000,0.00,13238.40,4,9266.88,9266.88,3971.52,0.00,0,0.00,11200.00,NULL,'CHECKIN','13BC2F4E','49222524-d9ed-4e90-b61e-e813ec1b650d','ACTIVE','1','2026-09-29 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(12,'RES-202610-0012','Ms.','Ritu','Chawla','ritu.chawla@gmail.com','+919876500012','2026-10-01','2026-10-06',5,1,'Checked-In',5,'5dd0140a-4de7-49a3-b354-e0e1cb459545.jpg','[17]','[3]','[\"303\"]','[\"half_board\"]',2,0,'','Evening Tea',4,1,42500.00,0.00,18.000,6885.00,10.000,4250.00,45135.00,2,33851.25,33851.25,11283.75,0.00,0,0.00,42500.00,NULL,'CHECKIN','728079D4','81c5e81a-6001-40ac-89f6-5b7cbfdf67d2','ACTIVE','1','2026-09-25 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(13,'RES-202610-0013','Mr.','Suresh','Pillai','suresh.pillai@gmail.com','+14155550013','2026-10-06','2026-10-08',2,1,'Confirmed',1,'4004beeb-8054-4043-8e8c-f9da209f85ff.jpg','[5]','[1]','[\"105\"]','[\"daily\"]',3,1,'Welcome Drink','',3,6,7000.00,0.00,12.000,840.00,0.000,0.00,7840.00,4,1960.00,1960.00,5880.00,0.00,0,0.00,7000.00,NULL,'RESERVATION','53D7E89A','b6ad25e1-5fa1-4f30-a1b0-efe2493257b3','ACTIVE','1','2026-09-29 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(14,'RES-202610-0014','Ms.','Meera','Desai','meera.desai@gmail.com','+442079460014','2026-10-06','2026-10-09',3,1,'Confirmed',3,'d854f4bd-cfcc-45cd-af17-0bbeabc48b29.jpg','[14]','[2]','[\"206\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','Airport Pickup',3,1,16800.00,0.00,12.000,1814.40,10.000,1680.00,16934.40,2,5080.32,5080.32,11854.08,0.00,0,0.00,16800.00,NULL,'RESERVATION','09DA171E','c3af2226-8ed8-4b00-834c-80f50c2008c7','ACTIVE','1','2026-09-28 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(15,'RES-202610-0015','Mr.','Ibrahim','Ansari','ibrahim.ansari@gmail.com','+971501000015','2026-10-06','2026-10-10',4,1,'Confirmed',2,'947914be-813b-4bae-a55f-544da9065a45.jpg','[25]','[7]','[\"601\"]','[\"full_board\"]',3,0,'Fruit Basket','Spa',4,2,122000.00,5000.00,18.000,19431.00,15.000,19050.00,127381.00,6,63690.50,63690.50,63690.50,0.00,0,0.00,122000.00,NULL,'RESERVATION','4C0BC344','da283e12-ec01-430e-a745-053d7448e2bc','ACTIVE','1','2026-09-27 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(16,'RES-202610-0016','Ms.','Lakshmi','Krishnan','lakshmi.krishnan@gmail.com','+919876500016','2026-10-09','2026-10-12',3,1,'Confirmed',1,'20b9bae5-5530-439c-9f27-177e2b3fd8da.jpg','[18]','[3]','[\"304\"]','[\"daily\"]',2,1,'','',4,6,20400.00,0.00,18.000,3672.00,0.000,0.00,24072.00,4,4814.40,4814.40,19257.60,0.00,0,0.00,20400.00,NULL,'RESERVATION','ADD5AB76','9aaab4c4-c659-4dc0-b01f-3bd4bbf205fc','ACTIVE','1','2026-09-29 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(17,'RES-202610-0017','Mr.','Yusuf','Sheikh','yusuf.sheikh@gmail.com','+14155550017','2026-10-11','2026-10-13',2,2,'Confirmed',4,'6c6f43f0-1885-4f79-ac8f-c749196c6ff9.jpg','[6, 7]','[1, 1]','[\"106\", \"107\"]','[\"daily\", \"daily\"]',3,2,'Welcome Drink','',3,4,14000.00,0.00,12.000,1344.00,20.000,2800.00,12544.00,1,0.00,0.00,12544.00,0.00,0,0.00,14000.00,NULL,'RESERVATION','D3E917FF','73051b42-de52-4b56-ba62-0cf8e00d6dcc','ACTIVE','1','2026-09-30 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(18,'RES-202610-0018','Ms.','Pooja','Bhatt','pooja.bhatt@gmail.com','+442079460018','2026-10-14','2026-10-19',5,1,'Confirmed',1,'8837a51a-a883-4a1b-bb6a-1123ee4655f1.jpg','[22]','[4]','[\"403\"]','[\"half_board\"]',2,0,'','Gymnasium',4,5,52500.00,0.00,18.000,9266.40,12.000,7020.00,60746.40,2,18223.92,18223.92,42522.48,0.00,1,6000.00,52500.00,NULL,'RESERVATION','1214A89B','f9182933-a326-4604-9960-35841e09bb9f','ACTIVE','1','2026-10-11 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(19,'RES-202610-0019','Mr.','Rithvik','Prabhu','rithvik.prabhu@gmail.com','+971501000019','2026-10-18','2026-10-22',4,1,'Confirmed',5,'93c5f085-ffc9-416d-a578-41139f5f8737.jpg','[23]','[5]','[\"501\"]','[\"full_board\"]',3,1,'Late Checkout','Spa',4,6,64000.00,2200.00,18.000,12780.00,0.000,0.00,83780.00,1,0.00,0.00,83780.00,0.00,1,4800.00,64000.00,NULL,'RESERVATION','D274BEF1','8668600a-b52a-4e33-8f1f-c9e1c176bfde','ACTIVE','1','2026-10-14 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(20,'RES-202610-0020','Ms.','Kavya','Reddy','kavya.reddy@gmail.com','+919876500020','2026-10-22','2026-10-25',3,1,'Confirmed',1,'83f77121-b8bc-42fb-9c3d-93864effefbe.jpg','[10]','[2]','[\"202\"]','[\"bed_breakfast\"]',2,2,'Breakfast Buffet','',3,3,16800.00,0.00,12.000,1915.20,5.000,840.00,17875.20,1,0.00,0.00,17875.20,0.00,0,0.00,16800.00,NULL,'RESERVATION','2D69C37A','b17741ff-affd-4ce1-a56d-e389ada6aece','ACTIVE','1','2026-10-17 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(21,'RES-202610-0021','Mr.','Nikhil','Joshi','nikhil.joshi@gmail.com','+14155550021','2026-10-12','2026-10-15',3,1,'Cancelled',6,'f4da1639-a3ba-45e5-b75e-00746be67556.jpg','[19]','[3]','[\"305\"]','[\"daily\"]',3,0,'','',4,6,20400.00,0.00,18.000,3672.00,0.000,0.00,24072.00,1,0.00,0.00,24072.00,0.00,0,0.00,20400.00,NULL,'RESERVATION','7BAC2FA6','c5a1def5-2c5b-49f7-8547-a8b84295c5f3','ACTIVE','1','2026-10-06 10:30:00',NULL,NULL,'1','Guest request — travel plans changed','2026-10-10 15:40:00','1'),(22,'RES-202610-0022','Ms.','Fatima','Begum','fatima.begum@gmail.com','+442079460022','2026-10-15','2026-10-17',2,1,'Cancelled',2,'60b7dfc6-7e48-49a9-ae8e-6665b9b21ea7.jpg','[8]','[8]','[\"108\"]','[\"daily\"]',2,1,'','',3,6,2400.00,0.00,12.000,288.00,0.000,0.00,2688.00,4,537.60,537.60,2150.40,0.00,0,0.00,2400.00,NULL,'RESERVATION','B58F8BF0','23156136-e7f6-46c0-8e72-de1d1aa5ab10','ACTIVE','1','2026-10-08 10:30:00',NULL,NULL,'1','Duplicate booking — kept RES on 106','2026-10-13 15:40:00','1'),(23,'RES-202610-0023','Mr.','Sandeep','Kulkarni','sandeep.kulkarni@gmail.com','+971501000023','2026-09-30','2026-10-02',2,1,'No-Show',3,'5bb5ee4d-f0f8-4516-bd6e-c1995be0c945.jpg','[12]','[2]','[\"204\"]','[\"daily\"]',3,2,'','',3,6,10400.00,0.00,12.000,1248.00,0.000,0.00,11648.00,1,0.00,0.00,11648.00,0.00,0,0.00,10400.00,NULL,'RESERVATION','9C84C4EE','9d6bbb6b-9f3f-49d0-a053-09714fb1651f','ACTIVE','1','2026-09-22 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(24,'RES-202610-0024','Ms.','Anjali','Saxena','anjali.saxena@gmail.com','+919876500024','2026-10-26','2026-10-29',3,1,'Pending',1,NULL,'[15]','[3]','[\"301\"]','[\"daily\"]',2,0,'','',3,6,20400.00,0.00,12.000,2448.00,0.000,0.00,22848.00,1,0.00,0.00,22848.00,0.00,0,0.00,20400.00,NULL,'RESERVATION','084CB99B','a6f4bd51-fe51-4556-aa57-75900a3bd00d','ACTIVE','1','2026-10-17 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(25,'RES-202610-0025','Mr.','Arjun','Kapoor','arjun.kapoor@gmail.com','+14155550025','2026-10-31','2026-11-02',2,1,'On Hold',5,'bf954300-0a95-47bb-91e5-81d897f1b7fc.jpg','[20]','[4]','[\"401\"]','[\"daily\"]',3,1,'','',4,6,17000.00,0.00,18.000,3060.00,0.000,0.00,20060.00,1,0.00,0.00,20060.00,0.00,0,0.00,17000.00,NULL,'RESERVATION','A9DE8923','ad6b50fd-8851-43aa-b6ae-70ab562bf85c','ACTIVE','1','2026-10-21 10:30:00',NULL,NULL,'1',NULL,NULL,NULL),(26,'RES-20261006-25D577','Mr','Flow','Test','flow919876505003@example.com','+919876505003','2026-10-06','2026-10-08',2,1,'Checked-Out',6,'8e6e18c7-1c40-429f-8046-78d303aaaf8b.png','[1]','[1]','[\"101\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,7000.00,0.00,0.00,0,0.00,7000.00,3,'RESERVATION','AFC52F19','43c3c020-ce5e-4f40-8629-3ff98fdae9c2','ACTIVE','1','2026-10-06 18:41:31','2026-10-06 18:41:35','1','1',NULL,NULL,NULL),(27,'RES-20261006-B7A0C3','Mr','Flow','Test','flow919876505010@example.com','+919876505010','2026-10-06','2026-10-08',2,1,'Cancelled',6,'33b90a56-819c-4ad0-9871-841b1dea7fec.png','[2]','[1]','[\"102\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,0.00,7000.00,0.00,0,0.00,7000.00,4,'RESERVATION','5D203B40','01803429-bf09-47f5-841a-22c6597f9ac6','ACTIVE','1','2026-10-06 18:41:35','2026-10-06 18:41:36','1','1','Guest called','2026-10-06 18:41:36','1'),(28,'RES-20261006-7DBCC5','Mr','Flow','Test','flow919876505003@example.com','+919876505003','2026-10-06','2026-10-08',2,1,'Checked-Out',6,'31220377-bd2a-47b0-9390-48a0f1b062bc.png','[2]','[1]','[\"102\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,7000.00,0.00,0.00,0,0.00,7000.00,3,'RESERVATION','C1A3450B','76a4cae2-5a94-4381-86a2-a21542a79da3','ACTIVE','1','2026-10-06 23:57:06','2026-10-06 23:57:07','1','1',NULL,NULL,NULL),(29,'RES-20261006-A10BA8','Mr','Flow','Test','flow919876505010@example.com','+919876505010','2026-10-06','2026-10-08',2,1,'Cancelled',6,'1539dca5-c7c7-4dec-8df3-d84fb3feb174.png','[3]','[1]','[\"103\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,0.00,7000.00,0.00,0,0.00,7000.00,4,'RESERVATION','BC8B8747','4b04956d-4760-4345-8836-6a7c08228f24','ACTIVE','1','2026-10-06 23:57:07','2026-10-06 23:57:07','1','1','Guest called','2026-10-06 23:57:08','1'),(30,'RES-20261007-E92143','Mr','Flow','Test','flow919876505003@example.com','+919876505003','2026-10-07','2026-10-09',2,1,'Checked-Out',6,'9c5af05a-2b73-470d-9e84-dd3b25378835.png','[3]','[1]','[\"103\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,7000.00,0.00,0.00,0,0.00,7000.00,3,'RESERVATION','F63F0819','ea2599ac-402c-42ee-8269-5c1f0a897835','ACTIVE','1','2026-10-07 00:40:55','2026-10-07 00:40:56','1','1',NULL,NULL,NULL),(31,'RES-20261007-CF125A','Mr','Flow','Test','flow919876505010@example.com','+919876505010','2026-10-07','2026-10-09',2,1,'Cancelled',6,'60d922d5-f511-4108-ad23-6d72679e9d7c.png','[6]','[1]','[\"106\"]','[\"daily\"]',1,0,NULL,NULL,6,NULL,7000.00,0.00,0.000,0.00,0.000,0.00,7000.00,7,0.00,0.00,7000.00,0.00,0,0.00,7000.00,4,'RESERVATION','72104366','0e989efd-fd09-4bb8-987f-f4720a4a64e5','ACTIVE','1','2026-10-07 00:40:56','2026-10-07 00:40:56','1','1','Guest called','2026-10-07 00:40:57','1');
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

-- Dump completed on 2026-10-07  6:04:10
