CREATE DATABASE  IF NOT EXISTS `hotelerp_masterdata` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `hotelerp_masterdata`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: hotelerp_masterdata
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
-- Table structure for table `bed_type`
--

DROP TABLE IF EXISTS `bed_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bed_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Type_Name` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_bed_type_id` (`id`),
  KEY `ix_bed_type_updated_by` (`updated_by`),
  KEY `ix_bed_type_status` (`status`),
  KEY `ix_bed_type_created_by` (`created_by`),
  KEY `ix_bed_type_Type_Name` (`Type_Name`),
  KEY `ix_bed_type_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bed_type`
--

LOCK TABLES `bed_type` WRITE;
/*!40000 ALTER TABLE `bed_type` DISABLE KEYS */;
INSERT INTO `bed_type` VALUES (1,'King Bed','INACTIVE','1','2026-01-26 13:44:29','2026-01-26 14:01:10','1','1'),(2,'Updated King Bed','INACTIVE','1','2026-01-26 13:52:08','2026-02-04 19:13:30','1','1'),(3,'Single Bed','ACTIVE','1','2026-02-04 19:13:56',NULL,NULL,'1'),(4,'Double Bed','ACTIVE','1','2026-02-04 19:14:01',NULL,NULL,'1'),(5,'Queen Size Bed','ACTIVE','1','2026-02-04 19:14:05',NULL,NULL,'1'),(6,'King Size Bed','ACTIVE','1','2026-02-04 19:14:10',NULL,NULL,'1'),(7,'Twin Bed','ACTIVE','1','2026-02-04 19:14:15',NULL,NULL,'1');
/*!40000 ALTER TABLE `bed_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `countries_currency`
--

DROP TABLE IF EXISTS `countries_currency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries_currency` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Country_Name` varchar(100) NOT NULL,
  `Currency_Name` varchar(100) NOT NULL,
  `Symbol` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_countries_currency_updated_by` (`updated_by`),
  KEY `ix_countries_currency_Symbol` (`Symbol`),
  KEY `ix_countries_currency_Country_Name` (`Country_Name`),
  KEY `ix_countries_currency_created_by` (`created_by`),
  KEY `ix_countries_currency_id` (`id`),
  KEY `ix_countries_currency_company_id` (`company_id`),
  KEY `ix_countries_currency_status` (`status`),
  KEY `ix_countries_currency_Currency_Name` (`Currency_Name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `countries_currency`
--

LOCK TABLES `countries_currency` WRITE;
/*!40000 ALTER TABLE `countries_currency` DISABLE KEYS */;
INSERT INTO `countries_currency` VALUES (1,'India','INR','₹','INACTIVE','1','2026-01-27 14:17:59','2026-02-04 19:21:13','1','1'),(2,'India','₹','Indian Rupee','ACTIVE','1','2026-02-04 19:21:59',NULL,NULL,'1'),(3,'United States','$','US Dollar','ACTIVE','1','2026-02-04 19:22:11',NULL,NULL,'1'),(4,'United Arab Emirates','AED','UAE Dirham','ACTIVE','1','2026-02-04 19:22:23',NULL,NULL,'1');
/*!40000 ALTER TABLE `countries_currency` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Department_Name` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_department_company_id` (`company_id`),
  KEY `ix_department_id` (`id`),
  KEY `ix_department_updated_by` (`updated_by`),
  KEY `ix_department_status` (`status`),
  KEY `ix_department_created_by` (`created_by`),
  KEY `ix_department_Department_Name` (`Department_Name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'Luxury Swimming Pool','INACTIVE','1','2026-01-28 15:22:14','2026-01-28 15:42:14','1','1'),(2,'Luxury Swimming Po','ACTIVE','1','2026-01-28 15:32:47',NULL,NULL,'1');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `designation`
--

DROP TABLE IF EXISTS `designation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `designation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Designation_Name` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_designation_id` (`id`),
  KEY `ix_designation_updated_by` (`updated_by`),
  KEY `ix_designation_status` (`status`),
  KEY `ix_designation_created_by` (`created_by`),
  KEY `ix_designation_Designation_Name` (`Designation_Name`),
  KEY `ix_designation_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `designation`
--

LOCK TABLES `designation` WRITE;
/*!40000 ALTER TABLE `designation` DISABLE KEYS */;
INSERT INTO `designation` VALUES (1,'Luxury Swimming Pool','INACTIVE','1','2026-01-28 15:48:36','2026-01-28 15:51:01','1','1');
/*!40000 ALTER TABLE `designation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discount_data`
--

DROP TABLE IF EXISTS `discount_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discount_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Country_ID` varchar(100) NOT NULL,
  `Discount_Name` varchar(100) NOT NULL,
  `Discount_Percentage` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_discount_data_updated_by` (`updated_by`),
  KEY `ix_discount_data_Discount_Percentage` (`Discount_Percentage`),
  KEY `ix_discount_data_Country_ID` (`Country_ID`),
  KEY `ix_discount_data_created_by` (`created_by`),
  KEY `ix_discount_data_id` (`id`),
  KEY `ix_discount_data_Discount_Name` (`Discount_Name`),
  KEY `ix_discount_data_company_id` (`company_id`),
  KEY `ix_discount_data_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discount_data`
--

LOCK TABLES `discount_data` WRITE;
/*!40000 ALTER TABLE `discount_data` DISABLE KEYS */;
INSERT INTO `discount_data` VALUES (1,'IN','Festival Offer Updated','25.0','INACTIVE','1','2026-01-27 11:41:58','2026-01-27 12:07:54','1','1'),(2,'IN','Seasonal Discount','10.0','ACTIVE','1','2026-02-04 19:20:10',NULL,NULL,'1'),(3,'IN','Corporate Booking Discount','15.0','ACTIVE','1','2026-02-04 19:20:21',NULL,NULL,'1'),(4,'IN','Long Stay Discount','20.0','ACTIVE','1','2026-02-04 19:20:34',NULL,NULL,'1');
/*!40000 ALTER TABLE `discount_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facility`
--

DROP TABLE IF EXISTS `facility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facility` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Facility_Name` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_facility_Facility_Name` (`Facility_Name`),
  KEY `ix_facility_updated_by` (`updated_by`),
  KEY `ix_facility_id` (`id`),
  KEY `ix_facility_created_by` (`created_by`),
  KEY `ix_facility_status` (`status`),
  KEY `ix_facility_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facility`
--

LOCK TABLES `facility` WRITE;
/*!40000 ALTER TABLE `facility` DISABLE KEYS */;
INSERT INTO `facility` VALUES (1,'GYM','INACTIVE','1','2026-01-26 14:19:28','2026-02-04 19:06:04','1','1'),(2,'Free High-Speed Wi-Fi','ACTIVE','1','2026-02-04 19:06:10',NULL,NULL,'1'),(3,'24×7 Room Service','ACTIVE','1','2026-02-04 19:06:16',NULL,NULL,'1'),(4,'Swimming Pool','ACTIVE','1','2026-02-04 19:06:24',NULL,NULL,'1'),(5,'Fitness Center (Gym)','ACTIVE','1','2026-02-04 19:06:31',NULL,NULL,'1'),(6,'Airport Pickup & Drop','ACTIVE','1','2026-02-04 19:06:35',NULL,NULL,'1');
/*!40000 ALTER TABLE `facility` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `identity_proof`
--

DROP TABLE IF EXISTS `identity_proof`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `identity_proof` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Proof_Name` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_identity_proof_updated_by` (`updated_by`),
  KEY `ix_identity_proof_status` (`status`),
  KEY `ix_identity_proof_created_by` (`created_by`),
  KEY `ix_identity_proof_Proof_Name` (`Proof_Name`),
  KEY `ix_identity_proof_company_id` (`company_id`),
  KEY `ix_identity_proof_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `identity_proof`
--

LOCK TABLES `identity_proof` WRITE;
/*!40000 ALTER TABLE `identity_proof` DISABLE KEYS */;
INSERT INTO `identity_proof` VALUES (1,'Passport','INACTIVE','1','2026-01-27 16:29:18','2026-01-27 16:36:58','1','1'),(2,'Hii','INACTIVE','1','2026-02-04 16:55:58','2026-02-04 19:24:02','1','1'),(3,'Aadhaar Card','ACTIVE','1','2026-02-04 19:24:23',NULL,NULL,'1'),(4,'Passport','ACTIVE','1','2026-02-04 19:24:27',NULL,NULL,'1'),(5,'Driving License','ACTIVE','1','2026-02-04 19:24:31',NULL,NULL,'1'),(6,'Voter ID','ACTIVE','1','2026-02-04 19:24:36',NULL,NULL,'1'),(7,'PAN Card','ACTIVE','1','2026-02-04 19:24:40',NULL,NULL,'1');
/*!40000 ALTER TABLE `identity_proof` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_methods`
--

DROP TABLE IF EXISTS `payment_methods`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_methods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `payment_method` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_payment_methods_id` (`id`),
  KEY `ix_payment_methods_updated_by` (`updated_by`),
  KEY `ix_payment_methods_status` (`status`),
  KEY `ix_payment_methods_created_by` (`created_by`),
  KEY `ix_payment_methods_payment_method` (`payment_method`),
  KEY `ix_payment_methods_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_methods`
--

LOCK TABLES `payment_methods` WRITE;
/*!40000 ALTER TABLE `payment_methods` DISABLE KEYS */;
INSERT INTO `payment_methods` VALUES (1,'UPI','INACTIVE','1','2026-01-27 14:33:03','2026-01-27 14:38:27','1','1'),(2,'Cash','ACTIVE','1','2026-02-04 19:23:39',NULL,NULL,'1'),(3,'Credit Card','ACTIVE','1','2026-02-04 19:23:43',NULL,NULL,'1'),(4,'Debit Card','ACTIVE','1','2026-02-04 19:23:48',NULL,NULL,'1'),(5,'UPI','ACTIVE','1','2026-02-04 19:23:53',NULL,NULL,'1'),(6,'Bank Transfer','ACTIVE','1','2026-02-04 19:23:58',NULL,NULL,'1');
/*!40000 ALTER TABLE `payment_methods` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_status`
--

DROP TABLE IF EXISTS `reservation_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Reservation_Status` varchar(100) NOT NULL,
  `Color` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_reservation_status_Color` (`Color`),
  KEY `ix_reservation_status_company_id` (`company_id`),
  KEY `ix_reservation_status_status` (`status`),
  KEY `ix_reservation_status_Reservation_Status` (`Reservation_Status`),
  KEY `ix_reservation_status_updated_by` (`updated_by`),
  KEY `ix_reservation_status_id` (`id`),
  KEY `ix_reservation_status_created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_status`
--

LOCK TABLES `reservation_status` WRITE;
/*!40000 ALTER TABLE `reservation_status` DISABLE KEYS */;
INSERT INTO `reservation_status` VALUES (1,'Arrived','#2ECC71','INACTIVE','1','2026-01-27 11:33:18','2026-01-27 11:41:47','1','1'),(2,'Arrived','#22c55e','INACTIVE','1','2026-02-04 11:24:50','2026-02-04 13:56:08','1','1'),(3,'Booked','#214ac4','ACTIVE','1','2026-02-04 13:56:34',NULL,NULL,'1'),(4,'Checked-In','#22c55e','ACTIVE','1','2026-02-04 13:56:39',NULL,NULL,'1'),(5,'Checked-Out','#c42191','ACTIVE','1','2026-02-04 13:56:47',NULL,NULL,'1'),(6,'Cancelled','#c43a21','ACTIVE','1','2026-02-04 13:56:54',NULL,NULL,'1'),(7,'No Show','#c4a121','ACTIVE','1','2026-02-04 13:57:02',NULL,NULL,'1');
/*!40000 ALTER TABLE `reservation_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room`
--

DROP TABLE IF EXISTS `room`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Room_No` varchar(100) NOT NULL,
  `Room_Name` varchar(100) NOT NULL,
  `Room_Type_ID` varchar(100) NOT NULL,
  `Bed_Type_ID` varchar(100) NOT NULL,
  `Room_Telephone` varchar(100) NOT NULL,
  `Room_Image_1` varchar(255) NOT NULL,
  `Room_Image_2` varchar(255) NOT NULL,
  `Room_Image_3` varchar(255) NOT NULL,
  `Room_Image_4` varchar(255) NOT NULL,
  `Max_Adult_Occupy` varchar(100) NOT NULL,
  `Max_Child_Occupy` varchar(100) NOT NULL,
  `Room_Booking_status` varchar(100) NOT NULL,
  `Room_Working_status` varchar(100) NOT NULL,
  `Room_Status` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_room_Room_Type_ID` (`Room_Type_ID`),
  KEY `ix_room_status` (`status`),
  KEY `ix_room_Room_No` (`Room_No`),
  KEY `ix_room_Room_Booking_status` (`Room_Booking_status`),
  KEY `ix_room_company_id` (`company_id`),
  KEY `ix_room_Room_Telephone` (`Room_Telephone`),
  KEY `ix_room_updated_by` (`updated_by`),
  KEY `ix_room_Room_Status` (`Room_Status`),
  KEY `ix_room_id` (`id`),
  KEY `ix_room_Max_Child_Occupy` (`Max_Child_Occupy`),
  KEY `ix_room_Bed_Type_ID` (`Bed_Type_ID`),
  KEY `ix_room_created_by` (`created_by`),
  KEY `ix_room_Room_Working_status` (`Room_Working_status`),
  KEY `ix_room_Room_Name` (`Room_Name`),
  KEY `ix_room_Max_Adult_Occupy` (`Max_Adult_Occupy`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room`
--

LOCK TABLES `room` WRITE;
/*!40000 ALTER TABLE `room` DISABLE KEYS */;
INSERT INTO `room` VALUES (1,'101','Deluxe 101','1','3','0442345','8b2b9879-fdde-4acb-98f6-4b29b59eb8de.jpeg','ece413ac-58ae-4da4-9939-56582e18426f.jpeg','96e8f0d4-d411-4f60-bebe-94c26fc597f0.jpeg','b898b187-2b95-4402-a99c-36ec74890214.jpeg','2','1','Available','Not Assigne','ok','INACTIVE','1','2026-01-27 11:22:50','2026-01-27 11:34:00','1','1'),(2,'204','Deluxe','4','2','1234567890','c7971930-ba31-44bd-a2e7-4a4321018b90.jpeg','15dcd251-8f38-4b51-a546-e8dfc7c3cbe7.jpeg','2a2f5baa-5751-442f-b747-0c205868a5fb.png','c138c2ec-4214-480e-ad47-b2712497f1b3.png','1','2','Available','Not Assigne','UnBlocking','INACTIVE','1','2026-02-03 16:41:57','2026-02-04 19:15:42','1','1'),(3,'101','Standard Room 101','7','7','101','cd444bb5-1629-4eb0-8c4f-65236e7e99e5.png','483c0ea4-a8af-4028-a92f-8ee573bd70d4.jpeg','87f9a4dd-8266-4616-ac2f-cea1c26a74e6.jpeg','dcd8390d-895a-481d-8ae3-9941dd509052.png','2','1','Available','Not Assigne','UnBlocking','ACTIVE','1','2026-02-04 19:16:57',NULL,NULL,'1'),(4,'201','Deluxe Room 201','6','6','201','e70e6f6c-e7f0-49b4-811b-46e3e4b800a1.png','39011871-4222-4998-b34f-2d5e4bbf5f28.jpeg','db227d02-3c9e-494b-8761-80fc864f11f0.png','dc39e654-c241-4e36-9b10-41fa12561124.png','2','2','Available','Not Assigne','UnBlocking','ACTIVE','1','2026-02-04 19:19:30',NULL,NULL,'1');
/*!40000 ALTER TABLE `room` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_complementry`
--

DROP TABLE IF EXISTS `room_complementry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_complementry` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Complementry_Name` varchar(255) NOT NULL,
  `Description` varchar(255) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_room_complementry_Description` (`Description`),
  KEY `ix_room_complementry_company_id` (`company_id`),
  KEY `ix_room_complementry_status` (`status`),
  KEY `ix_room_complementry_Complementry_Name` (`Complementry_Name`),
  KEY `ix_room_complementry_updated_by` (`updated_by`),
  KEY `ix_room_complementry_id` (`id`),
  KEY `ix_room_complementry_created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_complementry`
--

LOCK TABLES `room_complementry` WRITE;
/*!40000 ALTER TABLE `room_complementry` DISABLE KEYS */;
INSERT INTO `room_complementry` VALUES (1,'Free Breakfast','Complimentary breakfast for all guests','INACTIVE','1','2026-01-27 12:14:57','2026-02-04 19:07:47','1','1'),(2,'Complimentary Breakfast','Daily breakfast provided free of charge during the stay.','ACTIVE','1','2026-02-04 19:08:07',NULL,NULL,'1'),(3,'Complimentary Bottled Water','Free bottled drinking water available in the room.','ACTIVE','1','2026-02-04 19:08:20',NULL,NULL,'1'),(4,'Complimentary Tea & Coffee Kit','Tea, coffee sachets with electric kettle provided.','ACTIVE','1','2026-02-04 19:08:30',NULL,NULL,'1'),(5,'Complimentary Toiletries','Basic toiletries including soap, shampoo, and dental kit.','ACTIVE','1','2026-02-04 19:08:38',NULL,NULL,'1'),(6,'Complimentary Wi-Fi Access','High-speed wireless internet access available in the room.','ACTIVE','1','2026-02-04 19:08:47',NULL,NULL,'1');
/*!40000 ALTER TABLE `room_complementry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_type`
--

DROP TABLE IF EXISTS `room_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Type_Name` varchar(100) NOT NULL,
  `Room_Cost` float NOT NULL,
  `Bed_Cost` float NOT NULL,
  `Complementry` varchar(100) NOT NULL,
  `Daily_Rate` float DEFAULT NULL,
  `Weekly_Rate` float DEFAULT NULL,
  `Bed_Only_Rate` float DEFAULT NULL,
  `Bed_And_Breakfast_Rate` float DEFAULT NULL,
  `Half_Board_Rate` float DEFAULT NULL,
  `Full_Board_Rate` float DEFAULT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_room_type_Type_Name` (`Type_Name`),
  KEY `ix_room_type_created_by` (`created_by`),
  KEY `ix_room_type_Room_Cost` (`Room_Cost`),
  KEY `ix_room_type_Weekly_Rate` (`Weekly_Rate`),
  KEY `ix_room_type_Bed_Only_Rate` (`Bed_Only_Rate`),
  KEY `ix_room_type_Bed_And_Breakfast_Rate` (`Bed_And_Breakfast_Rate`),
  KEY `ix_room_type_Complementry` (`Complementry`),
  KEY `ix_room_type_Full_Board_Rate` (`Full_Board_Rate`),
  KEY `ix_room_type_updated_by` (`updated_by`),
  KEY `ix_room_type_id` (`id`),
  KEY `ix_room_type_Half_Board_Rate` (`Half_Board_Rate`),
  KEY `ix_room_type_Bed_Cost` (`Bed_Cost`),
  KEY `ix_room_type_status` (`status`),
  KEY `ix_room_type_Daily_Rate` (`Daily_Rate`),
  KEY `ix_room_type_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_type`
--

LOCK TABLES `room_type` WRITE;
/*!40000 ALTER TABLE `room_type` DISABLE KEYS */;
INSERT INTO `room_type` VALUES (1,'Premium Deluxe',3000,700,'1',3000,19000,2100,2600,3200,3600,'ACTIVE','admin','2026-01-24 15:55:53','2026-01-24 16:02:59',NULL,'COMP001'),(2,'Updated Deluxe Room',4000,900,'1',4000,26000,3200,3600,4200,4600,'INACTIVE','1','2026-01-26 12:21:39','2026-02-04 19:06:52','1','1'),(3,'Deluxe Room',2500,500,'1',2500,16000,1800,2200,2800,3200,'INACTIVE','1','2026-01-26 13:35:33','2026-02-04 19:06:50','1','1'),(4,'Deluexe Room',2500,500,'1',2500,16000,1800,2200,2800,3200,'INACTIVE','1','2026-01-30 14:29:37','2026-02-04 19:06:48','1','1'),(5,'Standard Room',2000,500,'6',2200,14000,2000,2200,2600,3000,'ACTIVE','1','2026-02-04 19:12:12',NULL,NULL,'1'),(6,'Deluxe Room',3000,700,'6',3300,21000,3000,3300,3800,4300,'ACTIVE','1','2026-02-04 19:12:48',NULL,NULL,'1'),(7,'Executive Room',4500,1000,'5',4800,32000,4500,4800,5400,6000,'ACTIVE','1','2026-02-04 19:13:22',NULL,NULL,'1');
/*!40000 ALTER TABLE `room_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_hall_names`
--

DROP TABLE IF EXISTS `table_hall_names`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `table_hall_names` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hall_name` varchar(255) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_table_hall_names_status` (`status`),
  KEY `ix_table_hall_names_created_by` (`created_by`),
  KEY `ix_table_hall_names_hall_name` (`hall_name`),
  KEY `ix_table_hall_names_company_id` (`company_id`),
  KEY `ix_table_hall_names_id` (`id`),
  KEY `ix_table_hall_names_updated_by` (`updated_by`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_hall_names`
--

LOCK TABLES `table_hall_names` WRITE;
/*!40000 ALTER TABLE `table_hall_names` DISABLE KEYS */;
INSERT INTO `table_hall_names` VALUES (1,'Updated First Floor','INACTIVE','1','2026-01-26 15:15:43','2026-01-27 10:09:56','1','1'),(2,'Ground Floor Dining Hall','ACTIVE','1','2026-02-04 19:14:49',NULL,NULL,'1'),(3,'First Floor Restaurant Hall','ACTIVE','1','2026-02-04 19:14:53',NULL,NULL,'1'),(4,'Rooftop Dining Area','ACTIVE','1','2026-02-04 19:14:57',NULL,NULL,'1'),(5,'Banquet Hall','ACTIVE','1','2026-02-04 19:15:02',NULL,NULL,'1'),(6,'Private Dining Lounge','ACTIVE','1','2026-02-04 19:15:06',NULL,NULL,'1');
/*!40000 ALTER TABLE `table_hall_names` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_type`
--

DROP TABLE IF EXISTS `task_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Type_Name` varchar(100) NOT NULL,
  `Color` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_task_type_id` (`id`),
  KEY `ix_task_type_created_by` (`created_by`),
  KEY `ix_task_type_Color` (`Color`),
  KEY `ix_task_type_company_id` (`company_id`),
  KEY `ix_task_type_status` (`status`),
  KEY `ix_task_type_Type_Name` (`Type_Name`),
  KEY `ix_task_type_updated_by` (`updated_by`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_type`
--

LOCK TABLES `task_type` WRITE;
/*!40000 ALTER TABLE `task_type` DISABLE KEYS */;
INSERT INTO `task_type` VALUES (1,'Deep Cleaning','#1ABC9C','INACTIVE','1','2026-01-27 16:45:49','2026-01-27 16:51:44','1','1'),(2,'Room Cleanings','#413070ff','INACTIVE','1','2026-01-30 12:01:32','2026-02-04 19:24:45','1','1'),(3,'Cleaning','#22c55e','ACTIVE','1','2026-02-04 19:25:10',NULL,NULL,'1'),(4,'Inspection','#214ac4','ACTIVE','1','2026-02-04 19:25:18',NULL,NULL,'1'),(5,'Maintenance','#c45a21','ACTIVE','1','2026-02-04 19:25:28',NULL,NULL,'1'),(6,'Turn Down Service','#c4213a','ACTIVE','1','2026-02-04 19:25:38',NULL,NULL,'1'),(7,'Deep Cleaning','#219bc4','ACTIVE','1','2026-02-04 19:25:50','2026-02-04 19:26:00','1','1');
/*!40000 ALTER TABLE `task_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tax_type`
--

DROP TABLE IF EXISTS `tax_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tax_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Country_ID` varchar(100) NOT NULL,
  `Tax_Name` varchar(100) NOT NULL,
  `Tax_Percentage` varchar(100) NOT NULL,
  `status` varchar(100) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `company_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_tax_type_status` (`status`),
  KEY `ix_tax_type_Tax_Name` (`Tax_Name`),
  KEY `ix_tax_type_updated_by` (`updated_by`),
  KEY `ix_tax_type_Tax_Percentage` (`Tax_Percentage`),
  KEY `ix_tax_type_Country_ID` (`Country_ID`),
  KEY `ix_tax_type_created_by` (`created_by`),
  KEY `ix_tax_type_id` (`id`),
  KEY `ix_tax_type_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tax_type`
--

LOCK TABLES `tax_type` WRITE;
/*!40000 ALTER TABLE `tax_type` DISABLE KEYS */;
INSERT INTO `tax_type` VALUES (1,'1','PF','20.0','INACTIVE','1','2026-01-27 15:15:49','2026-02-04 19:20:59','1','1'),(2,'1','GS','18.0','INACTIVE','1','2026-01-27 15:22:13','2026-02-04 19:20:57','1','1'),(3,'2','GST','12.0','ACTIVE','1','2026-02-04 19:22:40',NULL,NULL,'1'),(4,'2','Service Charge','5.0','ACTIVE','1','2026-02-04 19:22:56',NULL,NULL,'1'),(5,'2','Luxury Tax','8.0','ACTIVE','1','2026-02-04 19:23:13',NULL,NULL,'1');
/*!40000 ALTER TABLE `tax_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'hotelerp_masterdata'
--

--
-- Dumping routines for database 'hotelerp_masterdata'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-04 19:34:09
