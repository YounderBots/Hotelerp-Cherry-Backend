CREATE DATABASE  IF NOT EXISTS `hotelerp_hotel` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `hotelerp_hotel`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: hotelerp_hotel
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `housekeeper_task`
--

LOCK TABLES `housekeeper_task` WRITE;
/*!40000 ALTER TABLE `housekeeper_task` DISABLE KEYS */;
INSERT INTO `housekeeper_task` VALUES (1,'2','Anand','K','2026-07-31','10:00:00',10,'Room Cleaning','2','Completed','Unblocking',NULL,NULL,'ACTIVE',1,'2026-07-31 12:30:55',NULL,NULL,1),(2,'2','Anand','K','2026-07-31','10:00:00',12,'Deep Cleaning','2','In-Progress','Blocking',NULL,NULL,'ACTIVE',1,'2026-07-31 12:30:55',NULL,NULL,1),(3,'2','Anand','K','2026-07-31','10:00:00',15,'Linen Change','2','Completed','Unblocking',NULL,NULL,'ACTIVE',1,'2026-07-31 12:30:55',NULL,NULL,1),(4,'2','Anand','K','2026-07-31','10:00:00',13,'Turndown Service','2','Pending','Unblocking',NULL,NULL,'ACTIVE',1,'2026-07-31 12:30:55',NULL,NULL,1),(5,'2','Anand','K','2026-07-31','10:00:00',22,'Bed Making','2','Completed','Unblocking',NULL,NULL,'ACTIVE',1,'2026-07-31 12:30:55',NULL,NULL,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hsk_room_incident`
--

LOCK TABLES `hsk_room_incident` WRITE;
/*!40000 ALTER TABLE `hsk_room_incident` DISABLE KEYS */;
INSERT INTO `hsk_room_incident` VALUES (1,13,'2026-07-30','14:30:00','Minor water leak reported near bathroom sink','Housekeeping - Floor 2','Medium',NULL,'Maintenance notified, plumber dispatched','1','2026-07-30',NULL,'ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(2,6,'2026-07-31','09:15:00','Guest reported broken reading lamp','Maintenance','Low',NULL,'Replacement lamp installed same day','1','2026-07-31',NULL,'ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inquiry`
--

LOCK TABLES `inquiry` WRITE;
/*!40000 ALTER TABLE `inquiry` DISABLE KEYS */;
INSERT INTO `inquiry` VALUES (1,'Online','Sameer Bhatia','Sent rate card for Deluxe rooms, awaiting confirmation','Call back within 24 hours',NULL,'In Progress','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(2,'Offline','Fatima Sheikh','Discussed banquet hall availability for a wedding','Call back within 24 hours',NULL,'In Progress','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(3,'Online','Tarun Oberoi','Confirmed availability, converted to booking BOOK-2026-0001','Call back within 24 hours',NULL,'Completed','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(4,'Online','Deepa Ramanathan','Requested airport pickup details','Call back within 24 hours',NULL,'Completed','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_amount_paid_history`
--

LOCK TABLES `reservation_amount_paid_history` WRITE;
/*!40000 ALTER TABLE `reservation_amount_paid_history` DISABLE KEYS */;
INSERT INTO `reservation_amount_paid_history` VALUES (1,'RES-2026-0001','1',15680,'2026-07-29','Credit Card','3458a1c0-4c93-4f00-a55e-9fa353ad84f2','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(2,'RES-2026-0002','1',7840,'2026-07-30','UPI','e9918755-1ce1-477d-86ef-86045578f4f8','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(3,'RES-2026-0003','1',10700,'2026-07-31','Credit Card','a90b76e2-fb8d-457e-b0f0-727279b0f794','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(4,'RES-2026-0004','1',44800,'2026-07-28','UPI','d3e66d37-9a83-41df-8f22-584eee8ac063','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(5,'RES-2026-0005','1',23520,'2026-07-29','Credit Card','688b1a34-d2e4-48d4-8f7c-fe3613a0e730','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(6,'RES-2026-0006','1',33950,'2026-07-30','UPI','f1ecb401-8ce8-4722-af89-35fed09bf120','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(7,'RES-2026-0007','1',73920,'2026-07-31','Credit Card','d3883f57-504e-4a2c-b8d4-f7e0ac93baa8','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(8,'RES-2026-0008','1',115560,'2026-07-27','UPI','d5d34cec-640c-4023-bedd-caaaffbc661a','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(9,'RES-2026-0009','1',5040,'2026-07-31','Credit Card','b0192d1e-2ff9-4314-99d5-9d3560a748ad','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(10,'RES-2026-0010','1',2352,'2026-07-31','UPI','3b121ff4-a6c9-4788-85f1-3aff13db5f94','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(11,'RES-2026-0011','1',3528,'2026-07-31','Credit Card','813f47d4-edef-4b2c-9598-577afdcfffde','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(12,'RES-2026-0012','1',6426,'2026-07-31','UPI','b9b84059-e346-4909-ada1-bab28da46b11','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(13,'RES-2026-0013','1',7392,'2026-07-31','Credit Card','b685f5bc-84b6-4987-8c1f-6d1203521697','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(14,'RES-2026-0014','1',15680,'2026-07-27','UPI','b5ebf572-14e9-44fa-b447-11182ca8e90e','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(15,'RES-2026-0015','1',28000,'2026-07-25','Credit Card','ee83fc2f-1f61-4b6f-aef6-af9e0b482346','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(16,'RES-2026-0016','1',28000,'2026-07-20','UPI','dd0368f6-1326-49e2-a963-de38af4baa61','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1');
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
INSERT INTO `room_booking` VALUES (1,'BOOK-2026-0001','Mr.','Rajesh','Kumar','9845019001','rajesh.kumar@example.com','2026-08-03','2026-08-05',2,'[\"Deluxe Room\"]',1,2,0,'ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(2,'BOOK-2026-0002','Ms.','Anita','Joshi','9845019002','anita.joshi@example.com','2026-08-07','2026-08-09',2,'[\"Deluxe Room\"]',1,2,0,'ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(3,'BOOK-2026-0003','Mr.','Manoj','Tiwari','9845019003','manoj.tiwari@example.com','2026-08-10','2026-08-12',2,'[\"Deluxe Room\"]',1,2,0,'ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_reservation`
--

LOCK TABLES `room_reservation` WRITE;
/*!40000 ALTER TABLE `room_reservation` DISABLE KEYS */;
INSERT INTO `room_reservation` VALUES (1,'RES-2026-0001','Mr.','Rohan','Mehta','rohan.mehta@example.com','9845012301','2026-07-29','2026-08-02',4,1,'Checked-In',1,'/uploads/identity/RES-2026-0001.jpg','[1]','[1]','[\"101\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,14000,0,12,1680,0,0,15680,2,15680,15680,0,0,0,0,15680,2,'Reservation','CNF2026001','b851d6e0-4f0d-49be-99a6-3fab5960d3c1','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(2,'RES-2026-0002','Ms.','Priya','Nair','priya.nair@example.com','9845012302','2026-07-30','2026-08-01',2,1,'Checked-In',1,'/uploads/identity/RES-2026-0002.jpg','[2]','[1]','[\"102\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,7000,0,12,840,0,0,7840,4,7840,7840,0,0,0,0,7840,2,'Reservation','CNF2026002','4ea081d9-f7c1-4a4e-9143-33d89507012d','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(3,'RES-2026-0003','Mr.','Arjun','Kapoor','arjun.kapoor@example.com','9845012303','2026-07-31','2026-08-02',2,1,'Checked-In',1,'/uploads/identity/RES-2026-0003.jpg','[5]','[2]','[\"105\"]','[\"Daily\"]',2,1,'No',NULL,3,3,10000,0,12,1200,5,500,10700,2,10700,10700,0,0,0,0,10700,2,'Reservation','CNF2026003','f24635e1-a0f0-4604-8740-c60837ed5430','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(4,'RES-2026-0004','Ms.','Sana','Sheikh','sana.sheikh@example.com','9845012304','2026-07-28','2026-08-05',8,1,'Checked-In',1,'/uploads/identity/RES-2026-0004.jpg','[11]','[2]','[\"203\"]','[\"Daily\"]',2,0,'Yes',NULL,3,NULL,40000,0,12,4800,0,0,44800,4,44800,44800,0,0,0,0,44800,2,'Reservation','CNF2026004','4d753db5-b8a8-44e5-bde7-8f7bb6484c73','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(5,'RES-2026-0005','Mr.','Vikram','Rao','vikram.rao@example.com','9845012305','2026-07-29','2026-08-01',3,1,'Checked-In',1,'/uploads/identity/RES-2026-0005.jpg','[13]','[3]','[\"205\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,21000,0,12,2520,0,0,23520,2,23520,23520,0,0,0,0,23520,2,'Reservation','CNF2026005','89791f8e-4ce7-47ad-844a-6cf12c1b6d5d','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(6,'RES-2026-0006','Ms.','Neha','Gupta','neha.gupta@example.com','9845012306','2026-07-30','2026-08-04',5,1,'Checked-In',1,'/uploads/identity/RES-2026-0006.jpg','[17]','[3]','[\"301\"]','[\"Daily\"]',2,1,'No',NULL,3,2,35000,0,12,4200,15,5250,33950,4,33950,33950,0,0,0,0,33950,2,'Reservation','CNF2026006','1d609d30-42f5-4593-ab55-dcdb9390269b','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(7,'RES-2026-0007','Mr.','Karan','Malhotra','karan.malhotra@example.com','9845012307','2026-07-31','2026-08-06',6,1,'Checked-In',1,'/uploads/identity/RES-2026-0007.jpg','[19]','[4]','[\"303\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,66000,0,12,7920,0,0,73920,2,73920,73920,0,0,0,0,73920,2,'Reservation','CNF2026007','c1eb5bd6-25e3-4c42-95cc-2e2dc5184e5c','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(8,'RES-2026-0008','Ms.','Ananya','Iyer','ananya.iyer@example.com','9845012308','2026-07-27','2026-08-02',6,1,'Checked-In',1,'/uploads/identity/RES-2026-0008.jpg','[22]','[5]','[\"306\"]','[\"Daily\"]',2,0,'Yes',NULL,3,3,108000,0,12,12960,5,5400,115560,4,115560,115560,0,0,0,0,115560,2,'Reservation','CNF2026008','40edc847-b0a7-48e8-9eb9-8efceb7aee20','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(9,'RES-2026-0009','Mr.','Farhan','Khan','farhan.khan@example.com','9845012309','2026-07-31','2026-08-03',3,1,'Confirmed',1,'/uploads/identity/RES-2026-0009.jpg','[6]','[2]','[\"106\"]','[\"Daily\"]',2,1,'No',NULL,3,NULL,15000,0,12,1800,0,0,16800,2,5040,5040,11760,0,0,0,16800,1,'Reservation','CNF2026009','bcbb44d6-ee36-4378-9098-7972291d9f64','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(10,'RES-2026-0010','Ms.','Divya','Menon','divya.menon@example.com','9845012310','2026-07-31','2026-08-02',2,1,'Confirmed',1,'/uploads/identity/RES-2026-0010.jpg','[8]','[1]','[\"108\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,7000,0,12,840,0,0,7840,4,2352,2352,5488,0,0,0,7840,1,'Reservation','CNF2026010','0a18cf5a-bf3b-4728-86c7-25e8004ed3b3','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(11,'RES-2026-0011','Mr.','Aditya','Verma','aditya.verma@example.com','9845012311','2026-08-01','2026-08-04',3,1,'Confirmed',1,'/uploads/identity/RES-2026-0011.jpg','[9]','[1]','[\"201\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,10500,0,12,1260,0,0,11760,2,3528,3528,8232,0,0,0,11760,1,'Reservation','CNF2026011','14d32dc8-c1fd-4c7d-838d-630f797bd01b','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(12,'RES-2026-0012','Ms.','Ritu','Chawla','ritu.chawla@example.com','9845012312','2026-08-02','2026-08-05',3,1,'Confirmed',1,'/uploads/identity/RES-2026-0012.jpg','[14]','[3]','[\"206\"]','[\"Daily\"]',2,1,'Yes',NULL,3,1,21000,0,12,2520,10,2100,21420,4,6426,6426,14994,0,0,0,21420,1,'Reservation','CNF2026012','3bb1ce63-4643-454a-a509-d0a287f0fc81','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(13,'RES-2026-0013','Mr.','Suresh','Pillai','suresh.pillai@example.com','9845012313','2026-08-01','2026-08-03',2,1,'Confirmed',1,'/uploads/identity/RES-2026-0013.jpg','[20]','[4]','[\"304\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,22000,0,12,2640,0,0,24640,2,7392,7392,17248,0,0,0,24640,1,'Reservation','CNF2026013','f0e42576-cb26-4e8d-b409-89e1cd14b06c','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(14,'RES-2026-0014','Ms.','Meera','Desai','meera.desai@example.com','9845012314','2026-07-27','2026-07-31',4,1,'Checked-Out',1,'/uploads/identity/RES-2026-0014.jpg','[10]','[1]','[\"202\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,14000,0,12,1680,0,0,15680,4,15680,15680,0,0,0,0,15680,3,'Reservation','CNF2026014','1133e0c0-633d-4993-bc90-c13e70ffa3f7','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(15,'RES-2026-0015','Mr.','Ibrahim','Ansari','ibrahim.ansari@example.com','9845012315','2026-07-25','2026-07-30',5,1,'Checked-Out',1,'/uploads/identity/RES-2026-0015.jpg','[12]','[2]','[\"204\"]','[\"Daily\"]',2,1,'No',NULL,3,NULL,25000,0,12,3000,0,0,28000,2,28000,28000,0,0,0,0,28000,3,'Reservation','CNF2026015','133ba218-62fa-4171-9e48-866b9906fe3e','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(16,'RES-2026-0016','Ms.','Lakshmi','Krishnan','lakshmi.krishnan@example.com','9845012316','2026-07-20','2026-07-25',5,1,'Checked-Out',1,'/uploads/identity/RES-2026-0016.jpg','[15]','[2]','[\"207\"]','[\"Daily\"]',2,0,'Yes',NULL,3,NULL,25000,0,12,3000,0,0,28000,4,28000,28000,0,0,0,0,28000,3,'Reservation','CNF2026016','15d354b6-3c4d-4e7a-93b4-abcbedc9c494','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(17,'RES-2026-0017','Mr.','Yusuf','Sheikh','yusuf.sheikh@example.com','9845012317','2026-08-05','2026-08-08',3,1,'Cancelled',1,'/uploads/identity/RES-2026-0017.jpg','[16]','[1]','[\"208\"]','[\"Daily\"]',2,0,'No',NULL,3,NULL,10500,0,12,1260,0,0,11760,2,0,0,11760,0,0,0,11760,4,'Reservation','CNF2026017','b3f9798a-e793-4ab7-b8ad-7ae6a04bf1d3','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(18,'RES-2026-0018','Ms.','Pooja','Bhatt','pooja.bhatt@example.com','9845012318','2026-07-29','2026-07-31',2,1,'No-Show',1,'/uploads/identity/RES-2026-0018.jpg','[18]','[3]','[\"302\"]','[\"Daily\"]',2,1,'No',NULL,3,NULL,14000,0,12,1680,0,0,15680,4,0,0,15680,0,0,0,15680,5,'Reservation','CNF2026018','c967ddae-cca7-4423-b698-7797afdc7423','ACTIVE','1','2026-07-31 12:30:55',NULL,NULL,'1'),(19,'RES-20260731173329-UDD6N6','Mr.','E2E','Tester','e2e.tester@example.com','9998887771','2026-08-15','2026-08-18',3,1,'On Hold',7,'6566154a-3f22-492d-bdf7-e39767fa34a2.png','[24]','[1]',NULL,'[\"daily\"]',1,0,'','',NULL,NULL,10500,0,0,0,0,0,10500,6,NULL,0,10500,0,0,1500,10500,7,'RESERVATION','30A473C6','81dc149b-b329-49bb-9787-65d197fe47a7','INACTIVE','1','2026-07-31 23:03:29','2026-07-31 23:05:00','1','1');
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

-- Dump completed on 2026-08-04 14:36:27
