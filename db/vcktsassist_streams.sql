-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: vcktsassist
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `streams`
--

DROP TABLE IF EXISTS streams;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE streams (
  streamID varchar(100) NOT NULL,
  streamName varchar(100) NOT NULL,
  streamLevel varchar(100) NOT NULL,
  PRIMARY KEY (streamID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `streams`
--

/*!40000 ALTER TABLE streams DISABLE KEYS */;
INSERT INTO streams (streamID, streamName, streamLevel) VALUES ('100','BSc','UG');
INSERT INTO streams (streamID, streamName, streamLevel) VALUES ('101','BCom','UG');
INSERT INTO streams (streamID, streamName, streamLevel) VALUES ('102','BCA','UG');
INSERT INTO streams (streamID, streamName, streamLevel) VALUES ('103','BA','UG');
INSERT INTO streams (streamID, streamName, streamLevel) VALUES ('104','BBA','UG');
INSERT INTO streams (streamID, streamName, streamLevel) VALUES ('105','BVOC','UG');
INSERT INTO streams (streamID, streamName, streamLevel) VALUES ('106','BCS','UG');
/*!40000 ALTER TABLE streams ENABLE KEYS */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
