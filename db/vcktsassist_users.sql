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
-- Table structure for table `users`
--

DROP TABLE IF EXISTS users;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE users (
  subjectID varchar(100) NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  username varchar(100) NOT NULL,
  upassword varchar(100) NOT NULL,
  urole varchar(100) NOT NULL,
  email varchar(100) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY email (email),
  KEY subjectID (subjectID),
  CONSTRAINT users_ibfk_1 FOREIGN KEY (subjectID) REFERENCES subjects (subjectID)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

/*!40000 ALTER TABLE users DISABLE KEYS */;
INSERT INTO users (subjectID, id, username, upassword, urole, email) VALUES ('CSC',3,'Hannah','$5$rounds=535000$rpAaOiPNb9sd34bX$/Qbb9OYrTPXpjX1Ouj.OygxEbVq76cSuGfLGizwFmQ2','teacher','hn@gmail.com');
INSERT INTO users (subjectID, id, username, upassword, urole, email) VALUES ('CSC',4,'eqeqwe','$5$rounds=535000$zaRTcbMJV9GmFA7M$b1stYPxY1fBFpRai935O.mMIQJLeAnFtUY3m3r5ejf7','hod','ekwe@gmail.com');
INSERT INTO users (subjectID, id, username, upassword, urole, email) VALUES ('CSC',5,'eqwe','$5$rounds=535000$EKIyE.ScAxO4ajE6$BcDYqMLki3S1QWFpR1Qdb.67Cox0CwySqsBWX6e8gdD','examiner','eq@gmail.com');
INSERT INTO users (subjectID, id, username, upassword, urole, email) VALUES ('CSC',7,'mwala','$5$rounds=535000$ZXb0CSD5o0wWy/EV$HOGwRfOCCyebVwJtOF.n6vGQDjpuiok2YuhwNudvFPA','teacher','mw@gmail.com');
INSERT INTO users (subjectID, id, username, upassword, urole, email) VALUES ('CSC',8,'Lemons','$5$rounds=535000$isQ5Wq26BOUxYbPC$rFQ5TDO.FDzgh8N0LoBZsicv2XjZu9e3o1bpeKrfFQ3','teacher','lm@gmail.com');
INSERT INTO users (subjectID, id, username, upassword, urole, email) VALUES ('ACC',9,'hassa','$5$rounds=535000$ECWxJmLS5JgnCDIS$uW.sTvyIos5sVwjIiY/yUxgLXy3gxa/bXSSEj.d3OwC','teacher','ha@outlook.com');
INSERT INTO users (subjectID, id, username, upassword, urole, email) VALUES ('ACC',10,'hodBcom','$5$rounds=535000$55Ury37RU40dKPgt$YekACFnunXSVuLfb8Hmf/71pQBMGU85tfgKpdv/r4A6','hod','hat@outlook.com');
/*!40000 ALTER TABLE users ENABLE KEYS */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
