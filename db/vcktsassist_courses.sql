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
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS courses;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE courses (
  subjectID varchar(100) NOT NULL,
  courseID varchar(100) NOT NULL,
  courseSem varchar(100) NOT NULL,
  courseName varchar(100) NOT NULL,
  marksInternal int DEFAULT NULL,
  marksExternal int DEFAULT NULL,
  marksPractical int DEFAULT NULL,
  PRIMARY KEY (courseID),
  KEY subjectID (subjectID),
  CONSTRAINT courses_ibfk_1 FOREIGN KEY (subjectID) REFERENCES subjects (subjectID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

/*!40000 ALTER TABLE courses DISABLE KEYS */;
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('ACC','DSC02ACC52','V','Business and Industrial Law',20,80,0);
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('CSC','DSC03CSC11','I','Problem Solving using Computers-I',10,40,25);
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('CSC','DSC03CSC12','I','Introduction to DBMS-I',10,40,0);
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('CSC','DSC03CSC31','III','Operating System-I',10,40,0);
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('CSC','DSC03CSC54','VI','Introduction to JAVA',10,40,0);
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('CSC','DSC03CSC63','V','Internet Technologies-II',10,40,0);
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('CSC','MIN03CSC31 ','III','Introduction to Operating System-I',10,40,0);
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('ELE','MIN03ELE61','VI','IoT System Design',10,40,25);
INSERT INTO courses (subjectID, courseID, courseSem, courseName, marksInternal, marksExternal, marksPractical) VALUES ('CSC','OEL03CSC22','II','Introduction to Web-II',10,40,0);
/*!40000 ALTER TABLE courses ENABLE KEYS */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
