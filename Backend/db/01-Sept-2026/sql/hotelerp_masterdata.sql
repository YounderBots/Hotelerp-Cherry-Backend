-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: hotelerp_masterdata
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
-- Current Database: `hotelerp_masterdata`
--

/*!40000 DROP DATABASE IF EXISTS `hotelerp_masterdata`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hotelerp_masterdata` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hotelerp_masterdata`;

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
INSERT INTO `alembic_version` VALUES ('e564ebcb3f3f');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

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
INSERT INTO `bed_type` VALUES (1,'Single Bed','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Twin Bed','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Double Bed','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Queen Bed','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'King Bed','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Sofa Bed','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Bunk Bed','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Extra Bed','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `countries_currency`
--

LOCK TABLES `countries_currency` WRITE;
/*!40000 ALTER TABLE `countries_currency` DISABLE KEYS */;
INSERT INTO `countries_currency` VALUES (1,'India','Indian Rupee','₹','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'United States','US Dollar','$','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'United Kingdom','Pound Sterling','£','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'United Arab Emirates','UAE Dirham','د.إ','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Singapore','Singapore Dollar','S$','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
INSERT INTO `department` VALUES (1,'Front Office','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Housekeeping','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Food & Beverage','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Kitchen','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Maintenance','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Accounts','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Human Resources','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Security','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(9,'Stores','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(10,'Management','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
INSERT INTO `designation` VALUES (1,'General Manager','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Front Office Manager','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Front Desk Executive','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Reservation Executive','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Housekeeping Supervisor','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Room Attendant','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Restaurant Manager','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Chef','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(9,'Bartender','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(10,'Accountant','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discount_data`
--

LOCK TABLES `discount_data` WRITE;
/*!40000 ALTER TABLE `discount_data` DISABLE KEYS */;
INSERT INTO `discount_data` VALUES (1,'1','Early Bird Discount','10','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'1','Corporate Rate','15','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'1','Loyalty Member','5','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'1','Festive Season Offer','20','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'1','Long Stay (7+ nights)','12','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'1','No Discount','0','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facility`
--

LOCK TABLES `facility` WRITE;
/*!40000 ALTER TABLE `facility` DISABLE KEYS */;
INSERT INTO `facility` VALUES (1,'Air Conditioning','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Free Wi-Fi','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Television','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Mini Bar','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Room Service','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Laundry Service','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Airport Pickup','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Swimming Pool','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(9,'Gymnasium','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(10,'Spa','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(11,'Conference Hall','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(12,'Parking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(13,'Restaurant','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(14,'Bar','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(15,'Doctor on Call','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `identity_proof`
--

LOCK TABLES `identity_proof` WRITE;
/*!40000 ALTER TABLE `identity_proof` DISABLE KEYS */;
INSERT INTO `identity_proof` VALUES (1,'Aadhaar Card','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Passport','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Driving License','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Voter ID Card','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'PAN Card','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Company ID Card','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_methods`
--

LOCK TABLES `payment_methods` WRITE;
/*!40000 ALTER TABLE `payment_methods` DISABLE KEYS */;
INSERT INTO `payment_methods` VALUES (1,'Cash','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Credit Card','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Debit Card','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'UPI','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Net Banking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Bank Transfer','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Corporate Billing','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
INSERT INTO `reservation_status` VALUES (1,'Confirmed','#10B981','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Checked-In','#3B82F6','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Checked-Out','#6B7280','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Cancelled','#EF4444','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'No-Show','#F59E0B','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Pending','#FBBF24','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'On Hold','#8B5CF6','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room`
--

LOCK TABLES `room` WRITE;
/*!40000 ALTER TABLE `room` DISABLE KEYS */;
INSERT INTO `room` VALUES (1,'101','Standard Room 101','1','3','1101','/templates/static/upload_image/f25b5d3e2ab44d2d9514db23b9596fb5.jpg','/templates/static/upload_image/c20e774e64ac4f9bb826332fb312e632.jpg','/templates/static/upload_image/8c512b1e8672469fa0371e01f9ae51f8.jpg','/templates/static/upload_image/f72b4250c2c84017a422ae1f0d991f37.jpg','2','1','Available','Not Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'102','Standard Room 102','1','3','1102','/templates/static/upload_image/f25b5d3e2ab44d2d9514db23b9596fb5.jpg','/templates/static/upload_image/c20e774e64ac4f9bb826332fb312e632.jpg','/templates/static/upload_image/8c512b1e8672469fa0371e01f9ae51f8.jpg','/templates/static/upload_image/f72b4250c2c84017a422ae1f0d991f37.jpg','2','1','Available','Not Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'103','Standard Room 103','1','2','1103','/templates/static/upload_image/f25b5d3e2ab44d2d9514db23b9596fb5.jpg','/templates/static/upload_image/c20e774e64ac4f9bb826332fb312e632.jpg','/templates/static/upload_image/8c512b1e8672469fa0371e01f9ae51f8.jpg','/templates/static/upload_image/f72b4250c2c84017a422ae1f0d991f37.jpg','2','1','Available','Not Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'104','Standard Room 104','1','3','1104','/templates/static/upload_image/f25b5d3e2ab44d2d9514db23b9596fb5.jpg','/templates/static/upload_image/c20e774e64ac4f9bb826332fb312e632.jpg','/templates/static/upload_image/8c512b1e8672469fa0371e01f9ae51f8.jpg','/templates/static/upload_image/f72b4250c2c84017a422ae1f0d991f37.jpg','2','1','Occupied','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'105','Standard Room 105','1','2','1105','/templates/static/upload_image/f25b5d3e2ab44d2d9514db23b9596fb5.jpg','/templates/static/upload_image/c20e774e64ac4f9bb826332fb312e632.jpg','/templates/static/upload_image/8c512b1e8672469fa0371e01f9ae51f8.jpg','/templates/static/upload_image/f72b4250c2c84017a422ae1f0d991f37.jpg','2','1','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'106','Standard Room 106','1','3','1106','/templates/static/upload_image/f25b5d3e2ab44d2d9514db23b9596fb5.jpg','/templates/static/upload_image/c20e774e64ac4f9bb826332fb312e632.jpg','/templates/static/upload_image/8c512b1e8672469fa0371e01f9ae51f8.jpg','/templates/static/upload_image/f72b4250c2c84017a422ae1f0d991f37.jpg','2','1','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'107','Standard Room 107','1','1','1107','/templates/static/upload_image/f25b5d3e2ab44d2d9514db23b9596fb5.jpg','/templates/static/upload_image/c20e774e64ac4f9bb826332fb312e632.jpg','/templates/static/upload_image/8c512b1e8672469fa0371e01f9ae51f8.jpg','/templates/static/upload_image/f72b4250c2c84017a422ae1f0d991f37.jpg','1','0','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'108','Dormitory 108','8','7','1108','/templates/static/upload_image/e72c0d7942844ad4b113295bd21fbad0.jpg','/templates/static/upload_image/35117e0c09414ec588f3e63e8a302110.jpg','/templates/static/upload_image/50f4c410c7cc4249b92c2cf562329252.jpg','/templates/static/upload_image/ac07ee12e9ea40bbbb57da164d703534.jpg','6','0','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(9,'201','Deluxe Room 201','2','4','1201','/templates/static/upload_image/3ebf31f0371b4c418bc8a12f714acd38.jpg','/templates/static/upload_image/b8992f1e709247d99d7ecda09eb5f427.jpg','/templates/static/upload_image/7984a752772549188969c3d76109a054.jpg','/templates/static/upload_image/a5bc6a950cab4f2da8dad28dfd00a7dd.jpg','3','1','Occupied','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(10,'202','Deluxe Room 202','2','4','1202','/templates/static/upload_image/3ebf31f0371b4c418bc8a12f714acd38.jpg','/templates/static/upload_image/b8992f1e709247d99d7ecda09eb5f427.jpg','/templates/static/upload_image/7984a752772549188969c3d76109a054.jpg','/templates/static/upload_image/a5bc6a950cab4f2da8dad28dfd00a7dd.jpg','3','1','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(11,'203','Deluxe Room 203','2','3','1203','/templates/static/upload_image/3ebf31f0371b4c418bc8a12f714acd38.jpg','/templates/static/upload_image/b8992f1e709247d99d7ecda09eb5f427.jpg','/templates/static/upload_image/7984a752772549188969c3d76109a054.jpg','/templates/static/upload_image/a5bc6a950cab4f2da8dad28dfd00a7dd.jpg','2','2','Available','Not Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(12,'204','Deluxe Room 204','2','4','1204','/templates/static/upload_image/3ebf31f0371b4c418bc8a12f714acd38.jpg','/templates/static/upload_image/b8992f1e709247d99d7ecda09eb5f427.jpg','/templates/static/upload_image/7984a752772549188969c3d76109a054.jpg','/templates/static/upload_image/a5bc6a950cab4f2da8dad28dfd00a7dd.jpg','3','1','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(13,'205','Deluxe Room 205','2','3','1205','/templates/static/upload_image/3ebf31f0371b4c418bc8a12f714acd38.jpg','/templates/static/upload_image/b8992f1e709247d99d7ecda09eb5f427.jpg','/templates/static/upload_image/7984a752772549188969c3d76109a054.jpg','/templates/static/upload_image/a5bc6a950cab4f2da8dad28dfd00a7dd.jpg','2','2','Occupied','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(14,'206','Deluxe Room 206','2','4','1206','/templates/static/upload_image/3ebf31f0371b4c418bc8a12f714acd38.jpg','/templates/static/upload_image/b8992f1e709247d99d7ecda09eb5f427.jpg','/templates/static/upload_image/7984a752772549188969c3d76109a054.jpg','/templates/static/upload_image/a5bc6a950cab4f2da8dad28dfd00a7dd.jpg','3','1','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(15,'301','Super Deluxe 301','3','5','1301','/templates/static/upload_image/88c4dbb474634332967718ce6a949c84.jpg','/templates/static/upload_image/92a318b90b4d4ecd97fb686a00b16ca6.jpg','/templates/static/upload_image/d1ead0bb55cf495f872d6bfd824b7a01.jpg','/templates/static/upload_image/ec7269205ee440229223b9ae4c8502a7.jpg','3','2','Available','Not Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(16,'302','Super Deluxe 302','3','5','1302','/templates/static/upload_image/88c4dbb474634332967718ce6a949c84.jpg','/templates/static/upload_image/92a318b90b4d4ecd97fb686a00b16ca6.jpg','/templates/static/upload_image/d1ead0bb55cf495f872d6bfd824b7a01.jpg','/templates/static/upload_image/ec7269205ee440229223b9ae4c8502a7.jpg','3','2','Occupied','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(17,'303','Super Deluxe 303','3','4','1303','/templates/static/upload_image/88c4dbb474634332967718ce6a949c84.jpg','/templates/static/upload_image/92a318b90b4d4ecd97fb686a00b16ca6.jpg','/templates/static/upload_image/d1ead0bb55cf495f872d6bfd824b7a01.jpg','/templates/static/upload_image/ec7269205ee440229223b9ae4c8502a7.jpg','3','1','Occupied','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(18,'304','Super Deluxe 304','3','5','1304','/templates/static/upload_image/88c4dbb474634332967718ce6a949c84.jpg','/templates/static/upload_image/92a318b90b4d4ecd97fb686a00b16ca6.jpg','/templates/static/upload_image/d1ead0bb55cf495f872d6bfd824b7a01.jpg','/templates/static/upload_image/ec7269205ee440229223b9ae4c8502a7.jpg','3','2','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(19,'305','Super Deluxe 305','3','4','1305','/templates/static/upload_image/88c4dbb474634332967718ce6a949c84.jpg','/templates/static/upload_image/92a318b90b4d4ecd97fb686a00b16ca6.jpg','/templates/static/upload_image/d1ead0bb55cf495f872d6bfd824b7a01.jpg','/templates/static/upload_image/ec7269205ee440229223b9ae4c8502a7.jpg','3','1','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(20,'401','Executive Room 401','4','5','1401','/templates/static/upload_image/d142de8e4c6445f2a1adadb7aa720f72.jpg','/templates/static/upload_image/2faa235fc60243e68e6ccf6d22a2258c.jpg','/templates/static/upload_image/41c55a4fb2064e7d8b936d1160222abd.jpg','/templates/static/upload_image/45651737dc5645c88032373ebea2538d.jpg','3','2','Available','Not Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(21,'402','Executive Room 402','4','5','1402','/templates/static/upload_image/d142de8e4c6445f2a1adadb7aa720f72.jpg','/templates/static/upload_image/2faa235fc60243e68e6ccf6d22a2258c.jpg','/templates/static/upload_image/41c55a4fb2064e7d8b936d1160222abd.jpg','/templates/static/upload_image/45651737dc5645c88032373ebea2538d.jpg','3','2','Occupied','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(22,'403','Executive Room 403','4','5','1403','/templates/static/upload_image/d142de8e4c6445f2a1adadb7aa720f72.jpg','/templates/static/upload_image/2faa235fc60243e68e6ccf6d22a2258c.jpg','/templates/static/upload_image/41c55a4fb2064e7d8b936d1160222abd.jpg','/templates/static/upload_image/45651737dc5645c88032373ebea2538d.jpg','3','2','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(23,'501','Family Suite 501','5','5','1501','/templates/static/upload_image/6a60856a1a0c48068627be0935755cb9.jpg','/templates/static/upload_image/017b5cecaf544522be124e39c50bd42a.jpg','/templates/static/upload_image/d348d78b5cce44f6afa8792db4f3e458.jpg','/templates/static/upload_image/d0ac49b865364054aae466750e43eb9e.jpg','4','3','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(24,'502','VIP Suite 502','6','5','1502','/templates/static/upload_image/e1baf27c6f424aae84b2740e7c6bf4bf.jpg','/templates/static/upload_image/63f8ad4bdbf641628e4ab43c060577d1.jpg','/templates/static/upload_image/b55869c9eefc472c915724280ec0682c.jpg','/templates/static/upload_image/08591f3577924d6c996ab812f1209492.jpg','4','2','Available','Not Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(25,'601','Presidential Suite 601','7','5','1601','/templates/static/upload_image/7862019dc7f54ff396a9d64cef27bdcd.jpg','/templates/static/upload_image/bda43070f394454086c631ca792068b0.jpg','/templates/static/upload_image/8c2348df4b4a427eaa51df88bce3395b.jpg','/templates/static/upload_image/208b986c1fad458abafce164c31bcb8e.jpg','4','3','Available','Ready','UnBlocking','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_complementry`
--

LOCK TABLES `room_complementry` WRITE;
/*!40000 ALTER TABLE `room_complementry` DISABLE KEYS */;
INSERT INTO `room_complementry` VALUES (1,'Welcome Drink','Fresh juice or tender coconut on arrival','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Breakfast Buffet','Buffet breakfast for registered occupants','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Airport Pickup','One-way transfer from the airport','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Evening Tea','Tea and snacks served in the lounge','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Fruit Basket','Seasonal fruit placed in the room','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Late Checkout','Checkout extended to 14:00, subject to availability','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Newspaper','Daily newspaper delivered to the room','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_type`
--

LOCK TABLES `room_type` WRITE;
/*!40000 ALTER TABLE `room_type` DISABLE KEYS */;
INSERT INTO `room_type` VALUES (1,'Standard Room',3500,800,'1',3500,21000,3200,3800,4600,5400,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Deluxe Room',5200,1000,'1',5200,31200,4800,5600,6600,7600,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Super Deluxe',6800,1000,'1',6800,40800,6300,7300,8500,9700,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Executive Room',8500,1200,'1',8500,51000,7900,9100,10500,11900,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Family Suite',11000,1200,'1',11000,66000,10200,12000,14000,16000,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'VIP Suite',14500,1500,'1',14500,87000,13500,15700,18100,20500,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Presidential Suite',22000,1500,'1',22000,132000,20500,23500,27000,30500,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Dormitory',1200,400,'1',1200,7200,1100,1500,2100,2700,'ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_hall_names`
--

LOCK TABLES `table_hall_names` WRITE;
/*!40000 ALTER TABLE `table_hall_names` DISABLE KEYS */;
INSERT INTO `table_hall_names` VALUES (1,'Ground Floor','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'First Floor','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Second Floor','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Poolside','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Rooftop Terrace','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Banquet Hall','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Private Dining','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_type`
--

LOCK TABLES `task_type` WRITE;
/*!40000 ALTER TABLE `task_type` DISABLE KEYS */;
INSERT INTO `task_type` VALUES (1,'Daily Cleaning','#3B82F6','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'Deep Cleaning','#8B5CF6','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'Linen Change','#10B981','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'Turndown Service','#F59E0B','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'Maintenance Check','#EF4444','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'Inspection','#6B7280','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(7,'Restocking','#14B8A6','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(8,'Pest Control','#A16207','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
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
INSERT INTO `tax_type` VALUES (1,'1','CGST','6','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(2,'1','SGST','6','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(3,'1','GST 12%','12','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(4,'1','GST 18%','18','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(5,'1','Luxury Tax','28','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1'),(6,'1','No Tax','0','ACTIVE','1','2026-09-01 09:00:00',NULL,NULL,'1');
/*!40000 ALTER TABLE `tax_type` ENABLE KEYS */;
UNLOCK TABLES;

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

-- Dump completed on 2026-09-01 21:03:00
