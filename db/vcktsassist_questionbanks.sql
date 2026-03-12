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
-- Table structure for table `questionbanks`
--

DROP TABLE IF EXISTS questionbanks;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE questionbanks (
  courseID varchar(100) NOT NULL,
  questionBankID int NOT NULL AUTO_INCREMENT,
  questionBankType varchar(100) NOT NULL,
  questionBankName varchar(100) NOT NULL,
  PRIMARY KEY (questionBankID),
  UNIQUE KEY questionBankName (questionBankName),
  KEY courseID (courseID),
  CONSTRAINT questionbanks_ibfk_1 FOREIGN KEY (courseID) REFERENCES courses (courseID)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionbanks`
--

/*!40000 ALTER TABLE questionbanks DISABLE KEYS */;
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('OEL03CSC22',1,'mcq','csc1');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC03CSC11',2,'mcq','csc2');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC03CSC31',3,'saq','csc11');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('OEL03CSC22',5,'laq','web1');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC03CSC54',6,'mcq','javamcq');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC03CSC54',7,'saq','javasaq');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC02ACC52',8,'mcq','bilmcq');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC03CSC63',9,'mcq','itmcq');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC03CSC63',10,'laq','itlaq');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC03CSC63',11,'saq','itsaq');
INSERT INTO questionbanks (courseID, questionBankID, questionBankType, questionBankName) VALUES ('DSC03CSC54',12,'laq','javalaq');
/*!40000 ALTER TABLE questionbanks ENABLE KEYS */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
