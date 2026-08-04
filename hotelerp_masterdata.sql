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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bed_type`
--

LOCK TABLES `bed_type` WRITE;
/*!40000 ALTER TABLE `bed_type` DISABLE KEYS */;
INSERT INTO `bed_type` VALUES (1,'Single Bed','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Double Bed','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Queen Bed','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'King Bed','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Twin Beds','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'Bunk Bed','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(7,'Sofa Bed','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(8,'E2E Test Bed Updated','INACTIVE','1','2026-07-31 22:56:41','2026-07-31 22:57:14','1','1');
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
INSERT INTO `countries_currency` VALUES (1,'India','INR','Rs.','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'United States','USD','$','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'United Kingdom','GBP','GBP','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'United Arab Emirates','AED','AED','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'Front Office','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Housekeeping','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Food & Beverage Service','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'Kitchen','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Bar','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'Maintenance & Engineering','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(7,'Security','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(8,'Administration','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(9,'Human Resources','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(10,'Sales & Marketing','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `designation`
--

LOCK TABLES `designation` WRITE;
/*!40000 ALTER TABLE `designation` DISABLE KEYS */;
INSERT INTO `designation` VALUES (1,'General Manager','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Front Office Manager','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Supervisor','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'Executive','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Chef','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'Bartender','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(7,'Waiter','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(8,'Housekeeper','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(9,'Receptionist','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(10,'Accountant','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
INSERT INTO `discount_data` VALUES (1,'1','Early Bird Discount','10','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'1','Corporate Discount','15','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'1','Loyalty Member Discount','5','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'1','Festive Season Offer','20','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facility`
--

LOCK TABLES `facility` WRITE;
/*!40000 ALTER TABLE `facility` DISABLE KEYS */;
INSERT INTO `facility` VALUES (1,'WiFi','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Swimming Pool','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Gymnasium','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'Spa & Wellness Centre','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Free Parking','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'24-Hour Room Service','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(7,'Conference Hall','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(8,'Airport Shuttle','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(9,'Laundry Service','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(10,'Rooftop Restaurant','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
INSERT INTO `identity_proof` VALUES (1,'Aadhaar Card','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Passport','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Driving License','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'Voter ID Card','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'PAN Card','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'Company ID Card','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(7,'Ration Card','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
INSERT INTO `payment_methods` VALUES (1,'Cash','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Credit Card','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Debit Card','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'UPI','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Net Banking','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'Room Posting','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
INSERT INTO `reservation_status` VALUES (1,'Confirmed','#10B981','ACTIVE','1','2026-07-31 06:58:10',NULL,NULL,'1'),(2,'Checked-In','#3B82F6','ACTIVE','1','2026-07-31 06:58:10',NULL,NULL,'1'),(3,'Checked-Out','#6B7280','ACTIVE','1','2026-07-31 06:58:10',NULL,NULL,'1'),(4,'Cancelled','#EF4444','ACTIVE','1','2026-07-31 06:58:10',NULL,NULL,'1'),(5,'No-Show','#F59E0B','ACTIVE','1','2026-07-31 06:58:10',NULL,NULL,'1'),(6,'Pending','#FBBF24','ACTIVE','1','2026-07-31 06:58:10',NULL,NULL,'1'),(7,'On Hold','#8B5CF6','ACTIVE','1','2026-07-31 06:58:10',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room`
--

LOCK TABLES `room` WRITE;
/*!40000 ALTER TABLE `room` DISABLE KEYS */;
INSERT INTO `room` VALUES (1,'101','Standard Room 101','1','1','080-4100-1001','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','1','0','Occupied','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'102','Standard Room 102','1','2','080-4100-1002','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Occupied','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'103','Standard Room 103','1','2','080-4100-1003','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'104','Standard Room 104','1','5','080-4100-1004','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','0','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'105','Deluxe Room 105','2','3','080-4100-1005','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Occupied','Not Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'106','Deluxe Room 106','2','3','080-4100-1006','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Reserved','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(7,'107','Deluxe Room 107','2','2','080-4100-1007','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','0','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(8,'108','Standard Room 108','1','1','080-4100-1008','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','1','0','Reserved','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(9,'201','Standard Room 201','1','2','080-4100-1009','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Reserved','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(10,'202','Standard Room 202','1','5','080-4100-1010','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','0','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(11,'203','Deluxe Room 203','2','3','080-4100-1011','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Occupied','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(12,'204','Deluxe Room 204','2','3','080-4100-1012','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(13,'205','Super Deluxe Room 205','3','4','080-4100-1013','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','2','Occupied','Not Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(14,'206','Super Deluxe Room 206','3','4','080-4100-1014','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','2','Reserved','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(15,'207','Deluxe Room 207','2','2','080-4100-1015','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','0','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(16,'208','Standard Room 208','1','1','080-4100-1016','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','1','0','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(17,'301','Super Deluxe Room 301','3','4','080-4100-1017','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','2','Occupied','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(18,'302','Super Deluxe Room 302','3','4','080-4100-1018','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(19,'303','Executive Suite 303','4','4','080-4100-1019','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','3','2','Occupied','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(20,'304','Executive Suite 304','4','4','080-4100-1020','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','3','2','Reserved','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(21,'305','Executive Suite 305','4','7','080-4100-1021','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(22,'306','Presidential Suite 306','5','4','080-4100-1022','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','4','2','Occupied','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(23,'307','Deluxe Room 307','2','3','080-4100-1023','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','1','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(24,'308','Standard Room 308','1','5','080-4100-1024','/assets/rooms/placeholder-1.jpg','/assets/rooms/placeholder-2.jpg','/assets/rooms/placeholder-3.jpg','/assets/rooms/placeholder-4.jpg','2','0','Available','Ready','ACTIVE','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
INSERT INTO `room_complementry` VALUES (1,'Breakfast Included','Complimentary breakfast for all registered guests','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Airport Pickup & Drop','Complimentary airport transfer, subject to availability','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Welcome Drink','Welcome mocktail served on arrival','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'Late Checkout','Checkout extended to 2 PM at no extra cost','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Spa Voucher','One complimentary 30-minute spa session','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'Dinner Included','Complimentary set dinner at the in-house restaurant','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_type`
--

LOCK TABLES `room_type` WRITE;
/*!40000 ALTER TABLE `room_type` DISABLE KEYS */;
INSERT INTO `room_type` VALUES (1,'Standard Room',3500,500,'1',3500,22750,2975,3850,4550,5250,'ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Deluxe Room',5000,600,'2',5000,32500,4250,5500,6500,7500,'ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Super Deluxe Room',7000,700,'3',7000,45500,5950,7700,9100,10500,'ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'Executive Suite',11000,900,'5',11000,71500,9350,12100,14300,16500,'ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Presidential Suite',18000,1200,'6',18000,117000,15300,19800,23400,27000,'ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_hall_names`
--

LOCK TABLES `table_hall_names` WRITE;
/*!40000 ALTER TABLE `table_hall_names` DISABLE KEYS */;
INSERT INTO `table_hall_names` VALUES (1,'Grand Ballroom','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Garden Lawn','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Conference Room A','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'Conference Room B','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Rooftop Terrace','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
INSERT INTO `task_type` VALUES (1,'Bed Making','#3B82F6','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'Room Cleaning','#10B981','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'Bathroom Cleaning','#06B6D4','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'Linen Change','#8B5CF6','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'Deep Cleaning','#F59E0B','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'Turndown Service','#EC4899','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(7,'Maintenance Check','#EF4444','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tax_type`
--

LOCK TABLES `tax_type` WRITE;
/*!40000 ALTER TABLE `tax_type` DISABLE KEYS */;
INSERT INTO `tax_type` VALUES (1,'1','CGST','6','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(2,'1','SGST','6','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(3,'1','GST','12','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(4,'1','GST (Luxury)','18','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(5,'1','Luxury Tax','28','ACTIVE','1','2026-07-31 12:28:09',NULL,NULL,'1'),(6,'4','E2E Test Tax','5.0','INACTIVE','1','2026-07-31 23:15:54','2026-07-31 23:21:22','1','1');
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

-- Dump completed on 2026-08-04 14:36:49
